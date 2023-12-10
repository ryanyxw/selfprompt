def template_demonstration_formatting(premise, hypothesis, gold_label):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\n{gold_label}"


def vanilla_esnli_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\n{rationale} The answer is {gold_label}. {gold_label}\n\n"

def shots_with_instruction_demonstration_formatting(premise, hypothesis, gold_label, rationale, instruction):
    return f"### Instruction:\n{instruction}\n\n### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\n{rationale} The answer is {gold_label}. {gold_label}\n\n"

def summarize_instruction_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nThe objective is to answer the relationship between the input premise and input hypothesis. {rationale} The answer is {gold_label}. {gold_label}\n\n"

def shots_with_summarized_instruction_demonstration_formatting(premise, hypothesis, gold_label, rationale, instruction):
    return f"### Instruction:\n{instruction}\n\n### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nThe objective is to answer the relationship between the input premise and input hypothesis. {rationale} The answer is {gold_label}. {gold_label}\n\n"


def extra_language_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nLet's think step by step. {rationale} The answer is {gold_label}. {gold_label}\n\n"

def dummy_rationale_demonstration_formatting(premise, hypothesis, gold_label):
    verb = {
        "entailment": "entails",
        "neutral": "is neutral for",
        "contradiction": "contradicts"
    }[gold_label]
    cleaned_premise = premise.strip(". ")
    cleaned_hypothesis = hypothesis.strip(". ")
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nBecause the premise \"{cleaned_premise}\" {verb} \"{cleaned_hypothesis}\", the answer is {gold_label}. {gold_label}\n\n"

def random_label_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return vanilla_esnli_demonstration_formatting(premise, hypothesis, gold_label, rationale)

def random_rationale_and_label_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return vanilla_esnli_demonstration_formatting(premise, hypothesis, gold_label, rationale)

def label_first_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nThe answer is {gold_label}. {rationale} \n\n"
