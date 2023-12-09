
#assumes cwd is at bash script level (root)
def get_json_path(args):
    import os
    return os.path.join(args.exp_name, "generated_predictions.jsonl")

def get_prediction(prediction):
    import re
    def strip_non_alpha_from_end(s):
        return re.sub(r'[^a-zA-Z]*$', '', s)

    stripped_prediction = strip_non_alpha_from_end(prediction).lower()
    simplified_labels = ["neutral", "entail", "contradict"]
    original_labels = ["neutral", "entailment", "contradiction"]

    #if the final output is the label, we directly return it
    for label in original_labels:
        if stripped_prediction.endswith(". " + label):
            return label

    #we next check if the correct label is present in the prediction (and none of the other two labels are present
    present_arr = [l in stripped_prediction for l in simplified_labels]
    if (sum(present_arr) == 1):
        return original_labels[present_arr.index(True)]
    return "none"

def is_correct(prediction, label):
    return get_prediction(prediction) == label.lower()


def evaluate_json(args, path_to_results):

    import csv
    import json

    with open(path_to_results, 'r') as f:
        with open(args.output_csv, 'w') as f_out:
            writer = csv.writer(f_out)
            tot_len = 0
            for line in f:
                data = json.loads(line)
                # num_correct += is_correct(data["predict"], data["label"])
                row = [get_prediction(data['predict']), data['label']]
                tot_len += len(data["predict"])
                writer.writerow(row)
            # print(f"{path_to_results} has length {tot_len}")

#this function gets the average length of the predictions, along with the number of predictions that does not end with the proper format
def get_length_information(args, path_to_results):
    import json
    # print("getting the length for " + path_to_results)
    tot_len = 0
    num_incorrect_formatted = 0

    with open(path_to_results, 'r') as f:
        for line in f:
            data = json.loads(line)
            tot_len += len(data["predict"])
            if (not (data["predict"].endswith(". entailment") or data["predict"].endswith(". neutral") or data["predict"].endswith(". contradiction"))):
                num_incorrect_formatted += 1
    return tot_len, num_incorrect_formatted