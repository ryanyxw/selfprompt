
def get_instruction(args):
    instruction = "Given a premise and a hypothesis, determine whether the hypothesis and the premise has an entailment, contradiction, or neutral relationship. Give your final answer in one word at the end of your response."
    return instruction


#load the dataset with document-level wikitext
def setup_dataset(args):
    from datasets import load_dataset
    dataset = load_dataset("esnli")
    demonstration_dataset = dataset["train"].filter(lambda example: example["label"] != -1, keep_in_memory=True).shuffle(seed=args.seed, keep_in_memory=True).select(range(args.demonstration_pool), keep_in_memory=True)
    convert_dict = {0: "entailment", 1: "neutral", 2: "contradiction"}

    def convert_labels(row):
        row["gold_label"] = convert_dict[row["label"]]
        return row

    new_dataset = demonstration_dataset.map(convert_labels, keep_in_memory=True)
    return new_dataset

def template_demonstration_formatting(premise, hypothesis, gold_label):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\n{gold_label}"

def dummy_demonstration_formatting(premise, hypothesis, gold_label):
    verb = {
        "entailment": "entails",
        "neutral": "is neutral for",
        "contradiction": "contradicts"
    }[gold_label]
    cleaned_premise = premise.strip(". ")
    cleaned_hypothesis = hypothesis.strip(". ")
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\nBecause the premise \"{cleaned_premise}\" {verb} \"{cleaned_hypothesis}\", the answer is {gold_label}. {gold_label}\n\n"

def esnli_demonstration_formatting(premise, hypothesis, gold_label, rationale):
    return f"### Input:\nPremise: \n{premise}\nHypothesis: \n{hypothesis}\n\n### Response:\n{rationale} The answer is {gold_label}. {gold_label}\n\n"


def get_target_distribution(args):
    min_examples = args.num_demonstrations // 3
    if (args.num_demonstrations % 3 == 0):
        return [min_examples, min_examples, min_examples]
    elif (args.num_demonstrations % 3 == 1):
        return [min_examples, min_examples, min_examples + 1]
    else:
        return [min_examples, min_examples + 1, min_examples + 1]