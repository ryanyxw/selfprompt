import argparse
from selfinstruct.evaluations.openai import query_openai

import sys, os
#add the src of LLaMA-Efficient-Tuning to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), os.path.join("LLaMA-Efficient-Tuning", "src")))

def main(args):
    query_openai(args)
def parse_args():
    parser = argparse.ArgumentParser()

    #ie. the dataset that we are testing on
    parser.add_argument(
        '--exp_name',
        required=True,
        help="the name of the experiment"
    )

    parser.add_argument(
        '--num_evaluations',
        required=True,
        type=int,
        help="the number of examples from the test set that we are evaluating on"
    )

    parser.add_argument(
        '--out',
        help="the path to the file that we are going to be outputting to"
    )

    parser.add_argument(
        '--demonstration_file',
        required=True,
        help="the name of file that contains the demonstrations that we are goign to use to query gpt4"
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