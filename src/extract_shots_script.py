import argparse
from demonstrations.utils import get_instruction, setup_dataset, dummy_demonstration_formatting, esnli_demonstration_formatting, get_target_distribution

import sys, os
#add the src of LLaMA-Efficient-Tuning to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), os.path.join("LLaMA-Efficient-Tuning", "src")))

def main(args):

    new_dataset = setup_dataset(args)
    instruction = get_instruction(args)
    final_text = f"### Instruction:\n{instruction}\n\n"

    if (args.exp_name == "dummy_rationale"):
        target_distrib = get_target_distribution(args)
        #extract demonstration until we've gotten one shot of each one
        for i in range(len(new_dataset)):
            if (target_distrib[new_dataset[i]["label"]] > 0):
                target_distrib[new_dataset[i]["label"]] -= 1
                final_text += dummy_demonstration_formatting(new_dataset[i]["premise"],
                                                             new_dataset[i]["hypothesis"], new_dataset[i]["gold_label"])
            if (target_distrib == [0, 0, 0]):
                break
    if (args.exp_name == "random_label"):
        target_distrib = get_target_distribution(args)
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

        # shuffle the found_labels and found_rationales in the same way
        import random
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)

        for i in range(len(found_labels)):
            final_text += esnli_demonstration_formatting(found_premises[i], found_hypotheses[i],
                                                         found_labels[i],
                                                         found_rationales[random_array[i]])

    if (args.exp_name == "random_rationale_and_label"):
        target_distrib = get_target_distribution(args)
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

        # shuffle the found_labels and found_rationales in the same way
        import random
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)

        for i in range(len(found_labels)):
            final_text += esnli_demonstration_formatting(found_premises[i], found_hypotheses[i], found_labels[random_array[i]],
                                                         found_rationales[random_array[i]])

    #format into a python string variable
    final_text = "demonstrations = " + '"""' + final_text + '"""'
    print(final_text)
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--exp_name',
        required=True,
        choices=["dummy_rationale", "random_label", "random_rationale_and_label"],
        help="the name of the experiment"
    )

    parser.add_argument(
        '--demonstration_pool',
        required=True,
        type=int,
        help="the range to sample from the test set"
    )

    parser.add_argument(
        '--num_demonstrations',
        required=True,
        type=int,
        help="the number of demonstrations to sample from the test set"
    )

    parser.add_argument(
        '--seed',
        default=42,
        type=int,
        help="the seed to use"
    )

    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    main(args)