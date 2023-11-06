LLAMA_ET=LLaMA-Efficient-Tuning

#################

exp_file_name="exp_template"
#Note: Please make sure to update src/llmtuner/extras/template.py with corresponding template name

dataset_name="gsm8k"
#Note: Please make sure to update data/dataset_info with corresponding dataset

out_name="exp_template_out"
num_examples=100
gpu_devices=0

#################

#create the output directory. Exit if it already exists
out="out/$out_name"
mkdir -p $out


CUDA_VISIBLE_DEVICES="$gpu_devices" python ${LLAMA_ET}/src/train_bash.py \
    --stage sft \
    --model_name_or_path NousResearch/Nous-Hermes-llama-2-7b \
    --do_predict \
    --dataset $dataset_name \
    --template $exp_file_name \
    --finetuning_type lora \
    --output_dir $out \
    --per_device_eval_batch_size 1 \
    --max_samples $num_examples \
    --fp16\
    --predict_with_generate