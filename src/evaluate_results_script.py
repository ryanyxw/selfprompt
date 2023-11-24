import argparse
from evaluations.utils import evaluate_json, get_json_path

import os, sys
#add the src of LLaMA-Efficient-Tuning to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), os.path.join("LLaMA-Efficient-Tuning", "src")))

def main(args):
    path_to_results = get_json_path(args)
    num_correct, tot_num = evaluate_json(path_to_results)
    print(num_correct / tot_num)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--exp_name',
        required=True,
        choices=["dummy_rationale", "random_label", "random_rationale_and_label"],
        help="the name of the experiment"
    )

    parser.add_argument(
        '--num_score',
        required=True,
        type=int,
        help="the number of examples to score"
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