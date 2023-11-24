SRC_DIR=src

#extracts demonstrations and sends them to demo_out_dir

exp_name="random_rationale_and_label"
num_score=5

python ${SRC_DIR}/evaluate_results_script.py\
  --exp_name ${exp_name}\
  --num_score ${num_score}\
