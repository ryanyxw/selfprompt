#This exits the script if any command fails
set -e

LLAMA_ET="./../LLaMA-Efficient-Tuning"
DEMONSTRATIONS_DIR="./../demonstrations"
RESULTS_DIR="./../results_out_dir"
SRC_DIR="./../src"
SBATCH_OUT="./../sbatch_out"
PROCESSED_DIR="./../process_out_dir"

#extracts demonstrations and sends them to demo_out_dir

#list all the files in a directory
#all_experiments=($(ls -d $RESULTS_DIR/* | xargs -n 1 basename))

#all_experiments=("vanilla_esnli_4shotv1" "vanilla_esnli_4shotv2" "vanilla_esnli_4shotv3")

# Define all individual arrays
vanilla_esnli_1shot=("vanilla_esnli_1shotv1" "vanilla_esnli_1shotv2" "vanilla_esnli_1shotv3")
vanilla_esnli_2shot=("vanilla_esnli_2shotv1" "vanilla_esnli_2shotv2" "vanilla_esnli_2shotv3")
shots_with_instruction=("shots_with_instruction_2shotv1" "shots_with_instruction_2shotv2" "shots_with_instruction_2shotv3")
summarize_instruction=("summarize_instruction_2shotv1" "summarize_instruction_2shotv2" "summarize_instruction_2shotv3")
extra_language=("extra_language_2shotv1" "extra_language_2shotv2" "extra_language_2shotv3")
dummy_rationale=("dummy_rationale_2shotv1" "dummy_rationale_2shotv2" "dummy_rationale_2shotv3")
random_label=("random_label_2shotv1" "random_label_2shotv2" "random_label_2shotv3")
random_rationale_and_label=("random_rationale_and_label_2shotv1" "random_rationale_and_label_2shotv2" "random_rationale_and_label_2shotv3")
shots_with_summarized_instruction=("shots_with_summarized_instruction_2shotv1" "shots_with_summarized_instruction_2shotv2" "shots_with_summarized_instruction_2shotv3")
label_first=("label_first_2shotv1" "label_first_2shotv2" "label_first_2shotv3")

# Concatenate all arrays into one
all_experiments=("${vanilla_esnli_1shot[@]}" "${vanilla_esnli_2shot[@]}" "${shots_with_instruction[@]}" "${summarize_instruction[@]}" "${extra_language[@]}" "${dummy_rationale[@]}" "${random_label[@]}" "${random_rationale_and_label[@]}" "${shots_with_summarized_instruction[@]}" "${label_first[@]}")
#all_experiments=("${shots_with_instruction[@]}")

#combine all the lines above into one array

exclude_experiments=("")

num_score=500

####DO NOT CHANGE AFTER THIS

mkdir -p $PROCESSED_DIR

for exp_name in "${all_experiments[@]}"; do
  for excluded_experiments in "${exclude_experiments[@]}"; do
    if [ "$exp_name" = "$excluded_experiments" ]; then
      continue 2
    fi
  done
  #prepend results_dir to exp_name
  input_exp_name="${RESULTS_DIR}/${exp_name}"
  output_exp_name="${PROCESSED_DIR}/${exp_name}.csv"

  python ${SRC_DIR}/evaluate_results_script.py\
    --exp_name "${input_exp_name}"\
    --num_score "${num_score}"\
    --output_csv "${output_exp_name}"
done
