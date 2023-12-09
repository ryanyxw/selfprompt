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


def get_target_distribution(args):
    min_examples = args.num_demonstrations // 3
    if (args.num_demonstrations % 3 == 0):
        return [min_examples, min_examples, min_examples]
    elif (args.num_demonstrations % 3 == 1):
        return [min_examples, min_examples, min_examples + 1]
    else:
        return [min_examples, min_examples + 1, min_examples + 1]

def match_target_distribution(target_distrib, new_dataset):
    # extract demonstration until we've gotten one shot of each one
    found_premises = []
    found_hypotheses = []
    found_labels = []
    found_rationales = []
    for i in range(len(new_dataset)):
        if (target_distrib[new_dataset[i]["label"]] > 0):
            target_distrib[new_dataset[i]["label"]] -= 1
            found_premises.append(new_dataset[i]["premise"])
            found_hypotheses.append(new_dataset[i]["hypothesis"])
            found_labels.append(new_dataset[i]["gold_label"])
            found_rationales.append(new_dataset[i]["explanation_1"])
        if (target_distrib == [0, 0, 0]):
            break
    return found_premises, found_hypotheses, found_labels, found_rationales