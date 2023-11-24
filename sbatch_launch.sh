#!/bin/bash
#SBATCH --time=3-0:00
#SBATCH --nodelist=ink-titan
#SBATCH --job-name=sbatch
#SBATCH --gres=gpu:1

#This exits the script if any command fails
set -e

echo $CONDA_DEFAULT_ENV

LLAMA_ET="$1"
exp_file_name="$2"
dataset_name="$3"
num_examples="$4"
gpu_devices="$5"
out="$6"


CUDA_VISIBLE_DEVICES="$gpu_devices" python ${LLAMA_ET}/src/train_bash.py \
    --stage sft \
    --model_name_or_path NousResearch/Nous-Hermes-llama-2-7b \
    --do_predict \
    --dataset $dataset_name \
    --split test \
    --template $exp_file_name \
    --finetuning_type lora \
    --output_dir $out \
    --per_device_eval_batch_size 1 \
    --max_samples $num_examples \
    --fp16\
    --predict_with_generate