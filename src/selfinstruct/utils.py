#load the dataset with document-level wikitext
def load_dataset(dataset_name, split_name, num_examples, seed=42):
    from datasets import load_dataset
    dataset = load_dataset(dataset_name)
    demonstration_dataset = dataset[split_name].filter(lambda example: example["label"] != -1, keep_in_memory=True).shuffle(seed=seed, keep_in_memory=True).select(range(num_examples), keep_in_memory=True)
    convert_dict = {0: "entailment", 1: "neutral", 2: "contradiction"}

    def convert_labels(row):
        row["gold_label"] = convert_dict[row["label"]]
        return row

    new_dataset = demonstration_dataset.map(convert_labels, keep_in_memory=True)
    return new_dataset
