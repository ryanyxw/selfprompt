import argparse
from selfinstruct.demonstrations.utils import setup_dataset, get_target_distribution, match_target_distribution

import sys, os
#add the src of LLaMA-Efficient-Tuning to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), os.path.join("LLaMA-Efficient-Tuning", "src")))

def main(args):

    new_dataset = setup_dataset(args)
    final_text = ""
    if (args.exp_name == "vanilla_esnli"):
        #load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import vanilla_esnli_demonstration_formatting
        instruction = vanilla_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += vanilla_esnli_demonstration_formatting(found_premises[random_array[i]],
                                                         found_hypotheses[random_array[i]],
                                                         found_labels[random_array[i]],
                                                         found_rationales[random_array[i]])

    #this experiment repeats the instruction for every shot, to remind the model of the instruction each time
    if (args.exp_name == "shots_with_instruction"):
        #load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import shots_with_instruction_demonstration_formatting
        instruction = vanilla_instruction
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += shots_with_instruction_demonstration_formatting\
                                                        (found_premises[random_array[i]],
                                                         found_hypotheses[random_array[i]],
                                                         found_labels[random_array[i]],
                                                         found_rationales[random_array[i]],
                                                         instruction)
        #add the instruction for the query
        final_text += f"### Instruction:\n{instruction}\n\n"

    # this experiment asks the model to repeat the instruction, to remind model
    if (args.exp_name == "summarize_instruction"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import summarize_instruction
        from selfinstruct.demonstrations.formatting import summarize_instruction_demonstration_formatting
        instruction = summarize_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += summarize_instruction_demonstration_formatting \
                (found_premises[random_array[i]],
                 found_hypotheses[random_array[i]],
                 found_labels[random_array[i]],
                 found_rationales[random_array[i]])

    # this experiment asks the model to repeat the instruction, to remind model
    if (args.exp_name == "shots_with_summarized_instruction"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import summarize_instruction
        from selfinstruct.demonstrations.formatting import shots_with_summarized_instruction_demonstration_formatting
        instruction = summarize_instruction
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)

        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += shots_with_summarized_instruction_demonstration_formatting \
                (found_premises[random_array[i]],
                 found_hypotheses[random_array[i]],
                 found_labels[random_array[i]],
                 found_rationales[random_array[i]],
                 instruction)

    if (args.exp_name == "extra_language"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import extra_language_demonstration_formatting
        instruction = vanilla_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += extra_language_demonstration_formatting(found_premises[random_array[i]],
                                                                 found_hypotheses[random_array[i]],
                                                                 found_labels[random_array[i]],
                                                                 found_rationales[random_array[i]])

    if (args.exp_name == "dummy_rationale"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import dummy_rationale_demonstration_formatting
        instruction = vanilla_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += dummy_rationale_demonstration_formatting(found_premises[random_array[i]],
                                                                 found_hypotheses[random_array[i]],
                                                                 found_labels[random_array[i]])

    if (args.exp_name == "random_label"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import random_label_demonstration_formatting
        instruction = vanilla_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)

        #create a random mapping, and always add 1 to get next label
        random_label_arr = list(range(3))
        random.shuffle(random_label_arr)
        mapping_label = {random_label_arr[0]: "entailment", random_label_arr[1]: "neutral", random_label_arr[2]: "contradiction"}
        mapping_label_inverse = {v: k for k, v in mapping_label.items()}
        def get_new_label(prev_label):
            return mapping_label[(mapping_label_inverse[prev_label] + 1) % 3]

        for i in range(len(found_labels)):
            final_text += random_label_demonstration_formatting(found_premises[random_array[i]],
                                                                 found_hypotheses[random_array[i]],
                                                                 get_new_label(found_labels[random_array[i]]),
                                                                 found_rationales[random_array[i]])

    if (args.exp_name == "random_rationale_and_label"):
        # load the correct instruction
        from selfinstruct.demonstrations.instructions import vanilla_instruction
        from selfinstruct.demonstrations.formatting import random_rationale_and_label_demonstration_formatting
        instruction = vanilla_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)

        # create a random mapping, and always add 1 to get next label
        random_label_arr = list(range(3))
        random.shuffle(random_label_arr)
        mapping_label = {random_label_arr[0]: "entailment", random_label_arr[1]: "neutral",
                         random_label_arr[2]: "contradiction"}
        mapping_label_inverse = {v: k for k, v in mapping_label.items()}

        def get_new_label(prev_label):
            return mapping_label[(mapping_label_inverse[prev_label] + 1) % 3]

        for i in range(len(found_labels)):
            final_text += random_rationale_and_label_demonstration_formatting(found_premises[random_array[i]],
                                                                found_hypotheses[random_array[i]],
                                                                get_new_label(found_labels[random_array[i]]),
                                                                found_rationales[(random_array[i] + 1) % len(found_rationales)])
    if (args.exp_name == "label_first"):
        #load the correct instruction
        from selfinstruct.demonstrations.instructions import label_first_instruction
        from selfinstruct.demonstrations.formatting import label_first_demonstration_formatting
        instruction = label_first_instruction
        final_text = f"### Instruction:\n{instruction}\n\n"
        target_distrib = get_target_distribution(args)
        found_premises, found_hypotheses, found_labels, found_rationales = match_target_distribution(target_distrib,
                                                                                                     new_dataset)
        # shuffle
        import random
        # seed the random number generator
        random.seed(args.seed)
        random_array = list(range(len(found_labels)))
        random.shuffle(random_array)
        for i in range(len(found_labels)):
            final_text += label_first_demonstration_formatting(found_premises[random_array[i]],
                                                         found_hypotheses[random_array[i]],
                                                         found_labels[random_array[i]],
                                                         found_rationales[random_array[i]])


    # #format into a python string variable
    # final_text = "demonstrations = " + '"""' + final_text + '"""'
    print(final_text)
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--exp_name',
        required=True,
        # choices=["dummy_rationale",
        #          "random_label",
        #          "random_rationale_and_label",
        #          "vanilla_esnli",
        #          "extra_language"],
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