#load the dataset with document-level wikitext
def setup_dataset(args):
    from selfinstruct.utils import load_dataset
    return load_dataset("esnli", "train", args.demonstration_pool, args.seed)


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