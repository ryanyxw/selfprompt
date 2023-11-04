LLAMA_ET=LLaMA-Efficient-Tuning

#CUDA_VISIBLE_DEVICES=0 python ${LLAMA_ET}/src/train_bash.py \
#    --stage sft \
#    --model_name_or_path NousResearch/Llama-2-7b-hf \
#    --do_predict \
#    --dataset alpaca_gpt4_en \
#    --template default \
#    --finetuning_type lora \
#    --output_dir path_to_predict_result \
#    --per_device_eval_batch_size 1 \
#    --max_samples 100 \
#    --predict_with_generate


CUDA_VISIBLE_DEVICES=0 python ${LLAMA_ET}/src/train_bash.py \
    --stage sft \
    --model_name_or_path NousResearch/Nous-Hermes-llama-2-7b \
    --do_predict \
    --dataset snli \
    --template exp0 \
    --finetuning_type lora \
    --output_dir exp0_v2 \
    --per_device_eval_batch_size 1 \
    --max_samples 640 \
    --fp16\
    --predict_with_generate