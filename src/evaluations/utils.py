
#assumes cwd is at bash script level (root)
def get_json_path(args):
    import os
    return os.path.join("results_out_dir", args.exp_name, "generated_predictions.jsonl")

def is_correct(prediction, label):
    import re
    def strip_non_alpha_from_end(s):
        return re.sub(r'[^a-zA-Z]*$', '', s)

    stripped_prediction = strip_non_alpha_from_end(prediction).lower()
    stripped_label = label.lower() #assume the label is "neutral", "entailment" or "contradiction"

    #we first check if the model has outputted its answer at the end (making sure that it is a single word)
    if stripped_prediction.endswith(". " + stripped_label):
        return True

    #we next check if the correct label is present in the prediction (and none of the other two labels are present
    label_options = ["neutral", "entail", "contradict"]
    label_mapping = {"neutral": 0, "entailment": 1, "contradiction": 2}
    present_arr = [l in stripped_prediction for l in label_options]
    if (present_arr[label_mapping[stripped_label]] == 1 and sum(present_arr) == 1):
        return True
    return False


def evaluate_json(path_to_results):

    import json
    num_correct = 0
    tot_num = 0

    with open(path_to_results, 'r') as f:
        for line in f:
            tot_num += 1
            data = json.loads(line)
            num_correct += is_correct(data["predict"], data["label"])
    return num_correct, tot_num