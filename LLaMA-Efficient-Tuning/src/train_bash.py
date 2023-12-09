from llmtuner import run_exp
import sys
import os

#EDITED
if os.getcwd().split("/")[-1] != "LLaMa-Efficient-Tuning":
    print(f"prefore cwd = {os.getcwd()}")
    os.chdir(os.path.join(os.path.dirname(os.getcwd()), "LLaMA-Efficient-Tuning"))
    print(f"after cwd = {os.getcwd()}")


def main():
    run_exp()


def _mp_fn(index):
    # For xla_spawn (TPUs)
    main()


if __name__ == "__main__":
    main()
