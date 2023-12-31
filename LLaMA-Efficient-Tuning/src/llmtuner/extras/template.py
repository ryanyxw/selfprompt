import tiktoken
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from llmtuner.extras.logging import get_logger

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizer


logger = get_logger(__name__)


@dataclass
class Template:

    prefix: List[Union[str, Dict[str, str]]]
    prompt: List[Union[str, Dict[str, str]]]
    system: str
    sep: List[Union[str, Dict[str, str]]]
    stop_words: List[str]
    use_history: bool
    efficient_eos: bool

    def encode_oneturn(
        self,
        tokenizer: "PreTrainedTokenizer",
        query: str,
        resp: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        r"""
        Returns a single pair of token ids representing prompt and response respectively.
        """

        #._format encorporates the (query, resp) pair into the last entry of history
        system, history = self._format(query, resp, history, system)
        encoded_pairs = self._encode(tokenizer, system, history)
        prompt_ids = []
        for query_ids, resp_ids in encoded_pairs[:-1]:
            prompt_ids = prompt_ids + query_ids + resp_ids
        prompt_ids, answer_ids = prompt_ids + encoded_pairs[-1][0], encoded_pairs[-1][1]
        return prompt_ids, answer_ids

    def encode_multiturn(
        self,
        tokenizer: "PreTrainedTokenizer",
        query: str,
        resp: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None
    ) -> List[Tuple[List[int], List[int]]]:
        r"""
        Returns multiple pairs of token ids representing prompts and responses respectively.
        """
        system, history = self._format(query, resp, history, system)
        encoded_pairs = self._encode(tokenizer, system, history)
        return encoded_pairs

    def _format(
        self,
        query: str,
        resp: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None
    ) -> Tuple[str, List[Tuple[str, str]]]:
        r"""
        Aligns inputs to the standard format.
        """
        system = system or self.system # use system if provided
        history = history if (history and self.use_history) else []
        history = history + [(query, resp)]
        return system, history

    def _get_special_ids(
        self,
        tokenizer: "PreTrainedTokenizer"
    ) -> Tuple[List[int], List[int]]:
        if tokenizer.bos_token_id is not None and getattr(tokenizer, "add_bos_token", True):
            bos_ids = [tokenizer.bos_token_id]
        else: # baichuan, qwen and gpt2 models have no bos token
            bos_ids = []

        if tokenizer.eos_token_id is None:
            raise ValueError("EOS token is required.")

        if self.efficient_eos: # used in baichuan, qwen, chatglm, etc.
            eos_ids = []
        else:
            eos_ids = [tokenizer.eos_token_id]

        return bos_ids, eos_ids

    def _encode(
        self,
        tokenizer: "PreTrainedTokenizer",
        system: str,
        history: List[Tuple[str, str]]
    ) -> List[Tuple[List[int], List[int]]]:
        r"""
        Encodes formatted inputs to pairs of token ids.
        Turn 0: bos + prefix + sep + query    resp + eos
        Turn t: sep + bos + query             resp + eos
        """
        bos_ids, eos_ids = self._get_special_ids(tokenizer)
        sep_ids = self._convert_inputs_to_ids(tokenizer, context=self.sep)
        encoded_pairs = []
        for turn_idx, (query, resp) in enumerate(history):
            if turn_idx == 0:
                prefix_ids = self._convert_inputs_to_ids(tokenizer, context=self.prefix, system=system)
                if len(prefix_ids) != 0: # has prefix
                    prefix_ids = bos_ids + prefix_ids + sep_ids
                else:
                    prefix_ids = bos_ids
            else:
                prefix_ids = sep_ids + bos_ids

            query_ids = self._convert_inputs_to_ids(tokenizer, context=self.prompt, query=query, idx=str(turn_idx))
            resp_ids = self._convert_inputs_to_ids(tokenizer, context=[resp])
            encoded_pairs.append((prefix_ids + query_ids, resp_ids + eos_ids))
        return encoded_pairs

    def _convert_inputs_to_ids(
        self,
        tokenizer: "PreTrainedTokenizer",
        context: List[Union[str, Dict[str, str]]],
        system: Optional[str] = None,
        query: Optional[str] = None,
        idx: Optional[str] = None
    ) -> List[int]:
        r"""
        Converts context to token ids.
        """
        if isinstance(getattr(tokenizer, "tokenizer", None), tiktoken.Encoding): # for tiktoken tokenizer (Qwen)
            kwargs = dict(allowed_special="all")
        else:
            kwargs = dict(add_special_tokens=False)

        token_ids = []
        for elem in context:
            if isinstance(elem, str):
                elem = elem.replace("{{system}}", system, 1) if system is not None else elem
                elem = elem.replace("{{query}}", query, 1) if query is not None else elem
                elem = elem.replace("{{idx}}", idx, 1) if idx is not None else elem
                if len(elem) != 0:
                    token_ids = token_ids + tokenizer.encode(elem, **kwargs)
            elif isinstance(elem, dict):
                token_ids = token_ids + [tokenizer.convert_tokens_to_ids(elem.get("token"))]
            else:
                raise ValueError("Input must be string or dict[str, str], got {}".format(type(elem)))

        return token_ids


@dataclass
class Llama2Template(Template):

    def _encode(
        self,
        tokenizer: "PreTrainedTokenizer",
        system: str,
        history: List[Tuple[str, str]]
    ) -> List[Tuple[List[int], List[int]]]:
        r"""
        Encodes formatted inputs to pairs of token ids.
        Turn 0: bos + prefix + query    resp + eos
        Turn t: bos + query             resp + eos
        """
        bos_ids, eos_ids = self._get_special_ids(tokenizer)
        encoded_pairs = []
        for turn_idx, (query, resp) in enumerate(history):
            if turn_idx == 0: # llama2 template has no sep_ids
                query = self.prefix[0].replace("{{system}}", system) + query
            query_ids = self._convert_inputs_to_ids(tokenizer, context=self.prompt, query=query)
            resp_ids = self._convert_inputs_to_ids(tokenizer, context=[resp])
            encoded_pairs.append((bos_ids + query_ids, resp_ids + eos_ids))
        return encoded_pairs


templates: Dict[str, Template] = {}


def register_template(
    name: str,
    prefix: List[Union[str, Dict[str, str]]],
    prompt: List[Union[str, Dict[str, str]]],
    system: str,
    sep: List[Union[str, Dict[str, str]]],
    stop_words: Optional[List[str]] = [],
    use_history: Optional[bool] = True,
    efficient_eos: Optional[bool] = False
) -> None:
    template_class = Llama2Template if "llama2" in name else Template
    templates[name] = template_class(
        prefix=prefix,
        prompt=prompt,
        system=system,
        sep=sep,
        stop_words=stop_words,
        use_history=use_history,
        efficient_eos=efficient_eos
    )


def get_template_and_fix_tokenizer(
    name: str,
    tokenizer: "PreTrainedTokenizer"
) -> Template:
    if tokenizer.eos_token_id is None:
        tokenizer.eos_token = "<|endoftext|>"
        logger.info("Add eos token: {}".format(tokenizer.eos_token))

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
        logger.info("Add pad token: {}".format(tokenizer.pad_token))

    if name is None:
        return None

    template = templates.get(name, None)
    assert template is not None, "Template {} does not exist.".format(name)
    tokenizer.add_special_tokens(
        dict(additional_special_tokens=template.stop_words),
        replace_additional_special_tokens=False
    )
    return template


r"""
Supports language model inference without histories.
"""
register_template(
    name="vanilla",
    prefix=[],
    prompt=[
        "{{query}}"
    ],
    system="",
    sep=[],
    use_history=False
)


r"""
Default template.
"""
register_template(
    name="default",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "Human: {{query}}\nAssistant: "
    ],
    system=(
        "A chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions."
    ),
    sep=[
        "\n"
    ]
)


r"""
Supports: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
          https://huggingface.co/meta-llama/Llama-2-13b-chat-hf
          https://huggingface.co/meta-llama/Llama-2-70b-chat-hf
"""
register_template(
    name="llama2",
    prefix=[
        "<<SYS>>\n{{system}}\n<</SYS>>\n\n"
    ],
    prompt=[
        "[INST] {{query}} [/INST] "
    ],
    system=(
        "You are a helpful, respectful and honest assistant. "
        "Always answer as helpfully as possible, while being safe.  "
        "Your answers should not include any harmful, unethical, "
        "racist, sexist, toxic, dangerous, or illegal content. "
        "Please ensure that your responses are socially unbiased and positive in nature.\n\n"
        "If a question does not make any sense, or is not factually coherent, "
        "explain why instead of answering something not correct. "
        "If you don't know the answer to a question, please don't share false information."
    ),
    sep=[]
)


#"First explain your reasonoing, then give your answer as the last word.

register_template(
    name="llama2_snli",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. Limit your response to one word.  \n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

##############Baselines


register_template(
    name="exp0",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

demon_entail_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady murdered her husband.\n\n\n###Response: \nEntailment. This relationship is an entailment because the old lady's murder explains why she's captured."
demon_contr_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady hanged out with her friends.\n\n\n###Response: \nContradiction. This is a contradiction because the old lady could not get captured and hang out at the same time."
demon_neutr_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady was smiling at the press.\n\n\n###Response: \nNeutral. This is neutral because being captured and smiling is not contradictory, and smiling does not entails being captured."


register_template(
    name="exp1",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp1 + "\n\n" + demon_contr_exp1 + "\n\n" +  demon_neutr_exp1 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)


################Baseline ends

demon_entail_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady murdered her husband.\n\n\n###Response: \nEntailment. This relationship is an entailment because the old lady's murder explains why she's captured."
demon_contr_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady hanged out with her friends.\n\n\n###Response: \nContradiction. This is a contradiction because the old lady could not get captured and hang out at the same time."
demon_neutr_exp1 = "premise: \nThe old lady was captured.\nhypothesis: \nThe old lady was smiling at the press.\n\n\n###Response: \nNeutral. This is neutral because being captured and smiling is not contradictory, and smiling does not entails being captured."


register_template(
    name="exp1",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp1 + "\n\n" + demon_contr_exp1 + "\n\n" +  demon_neutr_exp1 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)


######################

demon_entail_exp2 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is swimming.\n\n\n###Response: \nEntailment. The premise entails the hypothesis because if the furry brown dog is swimming in the ocean, then a dog must be swimming."
demon_contr_exp2 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is running around the yard.\n\n\n###Response: \nContradiction. The premise contradicts with the hypothesis because the activity \"swimming in the ocean\" and \"being around the yard\" are contradictory in nature and cannot take place at the same time."
demon_neutr_exp2 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is chasing a fish.\n\n\n###Response: \nNeutral. The premise is neutral to the hypothesis because \"swimming in the ocean\" in the premise neither entails nor contradict with \"chasing a fish\" in the hypothesis."


register_template(
    name="exp2",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp2 + "\n\n" + demon_contr_exp2 + "\n\n" +  demon_neutr_exp2 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

######################

demon_entail_exp3 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is swimming.\n\n\n###Response: \nEntailment. The premise entails the hypothesis. The premise provides specific details and describes a specific situation where a furry brown dog is swimming in the ocean. The hypothesis, on the other hand, is more general and states that a dog is swimming without mentioning any specific details such as its color or location. Since the first sentence provides more information and is a specific case of a dog swimming, it can be concluded that if the first sentence is true, then the second sentence must also be true. Therefore, the first sentence entails the second sentence."
demon_contr_exp3 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is running around the yard.\n\n\n###Response: \nContradiction. The premise contradicts the hypothesis. The premise states that a furry brown dog is swimming in the ocean, implying that the dog is engaged in an activity related to being in water. On the other hand, the hypothesis claims that a dog is running around the yard, implying that the dog is engaged in an activity related to being on land and moving quickly. These activities, swimming and running, are different and contradictory in nature. Therefore, based on the information provided, the premise and hypothesis conflict with each other and cannot both be true simultaneously."
demon_neutr_exp3 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is chasing a fish.\n\n\n###Response: \nNeutral. The premise is neutral to the hypothesis. The premise does not entail the hypothesis because the dog is not necessarily \"chasing a fish\" given that it is \"swimming in the ocean\". It might be doing some other things like escaping from a shark. The premise does not contradict with the hypothesis because \"chasing a fish\" is something the dog might do if it were \"swimming in the ocean\". Thus, the premise neither entails nor contradicts the hypothesis, so the premise is neutral to the hypothesis."


register_template(
    name="exp3",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp3 + "\n\n" + demon_contr_exp3 + "\n\n" +  demon_neutr_exp3 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

######################

demon_entail_exp4 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is swimming.\n\n\n###Response: \nEntailment. The premise entails the hypothesis because if the furry brown dog is swimming in the ocean, then a dog must be swimming."
demon_contr_exp4 = "premise: \nA man and a woman are walking on a street at the top of a hill.\nhypothesis: \nTwo men play catch on a hill.\n\n\n###Response: \nContradiction. The premise contradicts the hypothesis because the premise states that there is \"a man and a woman\", which contradicts with the hypothesis which suggests that there are \"two men\"."
demon_neutr_exp4 = "premise: \nChildren going home from school.\nhypothesis: \nThe children are walking in the afternoon.\n\n\n###Response: \nNeutral. The premise is neutral to the hypothesis because children \"going home from school\" in the premise neither entails nor contradicts with children \"walking in the afternoon\" in the hypothesis."


register_template(
    name="exp4",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp4 + "\n\n" + demon_contr_exp4 + "\n\n" +  demon_neutr_exp4 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

######################

demon_entail_exp5 = "premise: \nThe furry brown dog is swimming in the ocean.\nhypothesis: \nA dog is swimming.\n\n\n###Response: \nEntailment. The premise entails the hypothesis. The premise provides specific details and describes a specific situation where a furry brown dog is swimming in the ocean. The hypothesis, on the other hand, is more general and states that a dog is swimming without mentioning any specific details such as its color or location. Since the first sentence provides more information and is a specific case of a dog swimming, it can be concluded that if the first sentence is true, then the second sentence must also be true. Therefore, the first sentence entails the second sentence."
demon_contr_exp5 = "premise: \nA man and a woman are walking on a street at the top of a hill.\nhypothesis: \nTwo men play catch on a hill.\n\n\n###Response: \nContradiction. The premise contradicts with the hypothesis. The premise contradicts the hypothesis because it states that a man and a woman are walking on a street at the top of a hill. This implies that there are only two individuals, one man, and one woman, involved in the described activity and that they are walking on a street. On the other hand, the hypothesis claims that two men are playing catch on a hill, implying that there are two men engaged in an activity of playing catch, specifically on a hill. Here, the number of individuals involved (two men) and the activity being performed (playing catch) differ from those described in the premise. Therefore, based on the information provided, the premise and the hypothesis conflict with each other as they present different scenarios involving different numbers of people and distinct activities taking place in different locations. Thus, the premise contradicts the hypothesis."
demon_neutr_exp5 = "premise: \nChildren going home from school.\nhypothesis: \nThe children are walking in the afternoon.\n\n\n###Response: \nNeutral. The premise is neutral to the hypothesis. The premise does not entail the hypothesis because the children are not necessarily \"walking in the afternoon\" given that they are \"going home from school.\" It might be that the children are still studying in classrooms in the afternoon. The premise does not contradict with the hypothesis because \"walking in the afternoon\" is something the children might do when they are \"going home\" from school on that day. Thus, the premise neither entails nor contradicts with the hypothesis, so the premise is neutral to the hypothesis."


register_template(
    name="exp5",
    prefix=[
        "### Instruction:\nGiven a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. First provide your answer in one word, then explain how you arrived at your answer.  \n\n" + demon_entail_exp5 + "\n\n" + demon_contr_exp5 + "\n\n" +  demon_neutr_exp5 + "\n\n",
    ],
    prompt=[
        "{{query}}\n\n### Response:\n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)

######################

exp_template_instruction="Solve the following math problem in a step by step manner, concluding with the final answer."

exp_template_demonstrations = \
"""### Input: 
Ivan has a bird feeder in his yard that holds two cups of birdseed. Every week, he has to refill the emptied feeder. Each cup of birdseed can feed fourteen birds, but Ivan is constantly chasing away a hungry squirrel that steals half a cup of birdseed from the feeder every week. How many birds does Ivan’s bird feeder feed weekly?

###Response: 
Let's think step by step
The squirrel steals 1/2 cup of birdseed every week, so the birds eat 2 - 1/2 = 1 1/2 cups of birdseed.
Each cup feeds 14 birds, so Ivan’s bird feeder feeds 14 * 1 1/2 = 21 birds weekly.
The answer is 21"""

register_template(
    name="exp_template",
    prefix=[
        f"### Instruction:\n{exp_template_instruction}\n\n" + exp_template_demonstrations + "\n\n",
    ],
    prompt=[
        "### Input: \n{{query}}\n\n### Response: \n"
    ],
    system="",
    sep=[
        "\n"
    ],
    use_history=False
)





r"""
Supports: https://github.com/ymcui/Chinese-LLaMA-Alpaca-2
          https://huggingface.co/ziqingyang/chinese-alpaca-2-7b
"""
register_template(
    name="llama2_zh",
    prefix=[
        "<<SYS>>\n{{system}}\n<</SYS>>\n\n"
    ],
    prompt=[
        "[INST] {{query}} [/INST] "
    ],
    system="You are a helpful assistant. 你是一个乐于助人的助手。",
    sep=[]
)


r"""
Supports: https://huggingface.co/tatsu-lab/alpaca-7b-wdiff
          https://github.com/ymcui/Chinese-LLaMA-Alpaca
"""
register_template(
    name="alpaca",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "### Instruction:\n{{query}}\n\n### Response:\n"
    ],
    system=(
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request."
    ),
    sep=[
        "\n\n"
    ]
)


r"""
Supports: https://huggingface.co/lmsys/vicuna-7b-delta-v1.1
          https://huggingface.co/lmsys/vicuna-13b-delta-v1.1
"""
register_template(
    name="vicuna",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "USER: {{query}} ASSISTANT: "
    ],
    system=(
        "A chat between a curious user and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the user's questions."
    ),
    sep=[]
)


r"""
Supports: https://huggingface.co/BelleGroup/BELLE-LLaMA-EXT-13B
"""
register_template(
    name="belle",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "Human: {{query}}\n\nBelle: "
    ],
    system="",
    sep=[
        "\n\n"
    ]
)


r"""
Supports: https://github.com/CVI-SZU/Linly
"""
register_template(
    name="linly",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "User: {{query}}\nBot: "
    ],
    system="",
    sep=[
        "\n"
    ]
)


r"""
Supports: https://github.com/Neutralzz/BiLLa
"""
register_template(
    name="billa",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "Human: {{query}}\nAssistant: "
    ],
    system="",
    sep=[
        "\n"
    ]
)


r"""
Supports: https://huggingface.co/IDEA-CCNL/Ziya-LLaMA-13B-v1
"""
register_template(
    name="ziya",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        {"token": "<human>"},
        ":{{query}}\n",
        {"token": "<bot>"},
        ":"
    ],
    system="",
    sep=[
        "\n"
    ]
)


r"""
Supports: https://huggingface.co/BAAI/AquilaChat-7B
"""
register_template(
    name="aquila",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "Human: {{query}}###Assistant: "
    ],
    system=(
        "A chat between a curious human and an artificial intelligence assistant. "
        "The assistant gives helpful, detailed, and polite answers to the human's questions."
    ),
    sep=[
        "###"
    ],
    stop_words=[
        "</s>"
    ],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/internlm/internlm-chat-7b
"""
register_template(
    name="intern",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "<|User|>:{{query}}",
        {"token": "<eoh>"},
        "\n<|Bot|>:"
    ],
    system="",
    sep=[
        {"token": "<eoa>"},
        "\n"
    ],
    stop_words=[
        "<eoa>"
    ],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/baichuan-inc/Baichuan-13B-Chat
"""
register_template(
    name="baichuan",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        {"token": "<reserved_102>"}, # user token
        "{{query}}",
        {"token": "<reserved_103>"}  # assistant token
    ],
    system="",
    sep=[],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/baichuan-inc/Baichuan2-7B-Chat
          https://huggingface.co/baichuan-inc/Baichuan2-13B-Chat
"""
register_template(
    name="baichuan2",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        {"token": "<reserved_106>"}, # user token
        "{{query}}",
        {"token": "<reserved_107>"}  # assistant token
    ],
    system="",
    sep=[],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/HuggingFaceH4/starchat-alpha
          https://huggingface.co/HuggingFaceH4/starchat-beta
"""
register_template(
    name="starchat",
    prefix=[
        {"token": "<|system|>"},
        "\n{{system}}",
    ],
    prompt=[
        {"token": "<|user|>"},
        "\n{{query}}",
        {"token": "<|end|>"},
        "\n",
        {"token": "<|assistant|>"}
    ],
    system="",
    sep=[
        {"token": "<|end|>"},
        "\n"
    ],
    stop_words=[
        "<|end|>"
    ],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/Qwen/Qwen-7B-Chat
"""
register_template(
    name="chatml",
    prefix=[
        {"token": "<|im_start|>"},
        "system\n{{system}}"
    ],
    prompt=[
        {"token": "<|im_start|>"},
        "user\n{{query}}",
        {"token": "<|im_end|>"},
        "\n",
        {"token": "<|im_start|>"},
        "assistant\n"
    ],
    system="You are a helpful assistant.",
    sep=[
        {"token": "<|im_end|>"},
        "\n"
    ],
    stop_words=[
        "<|im_end|>"
    ],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/THUDM/chatglm2-6b
"""
register_template(
    name="chatglm2",
    prefix=[
        {"token": "[gMASK]"},
        {"token": "sop"},
        "{{system}}"
    ],
    prompt=[
        "[Round {{idx}}]\n\n问：{{query}}\n\n答："
    ],
    system="",
    sep=[
        "\n\n"
    ],
    efficient_eos=True
)


r"""
Supports: https://huggingface.co/xverse/XVERSE-13B-Chat
"""
register_template(
    name="xverse",
    prefix=[
        "{{system}}"
    ],
    prompt=[
        "Human: {{query}}\n\nAssistant: "
    ],
    system="",
    sep=[]
)
