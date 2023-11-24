SRC_DIR=src
LLAMA_OUT=LLaMA-Efficient-Tuning/src/llmtuner/experiments

#extracts demonstrations and sends them to demo_out_dir

demonstration_pool=1000
num_demonstration=5
#choose from: "dummy_rationale", "random_label", "random_rationale_and_label"
exp_name="random_label"

#Do not change below:
mkdir -p $LLAMA_OUT

if [ -e ${LLAMA_OUT}/${exp_name}.py ]; then
  rm ${LLAMA_OUT}/${exp_name}.py
fi

python ${SRC_DIR}/extract_shots_script.py\
  --exp_name ${exp_name}\
  --demonstration_pool ${demonstration_pool}\
  --num_demonstration ${num_demonstration} >> ${LLAMA_OUT}/${exp_name}.py

