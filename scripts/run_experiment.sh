#This exits the script if any command fails
set -e

LLAMA_ET="./../LLaMA-Efficient-Tuning"
DEMONSTRATIONS_DIR="./../demonstrations"
RESULTS_DIR="./../results_out_dir"
SRC_DIR="./../src"
SBATCH_OUT="./../sbatch_out"
PROCESSED_DIR="./../process_out_dir"

mkdir -p "$SBATCH_OUT"

#################

#only get the names of files in the demonstrations directory (without including the path)
#all_results=($(ls -d ${DEMONSTRATIONS_DIR}/* | xargs -n 1 basename))

#all_results=("shots_with_instruction_2shotv1" "shots_with_instruction_2shotv2" "shots_with_instruction_2shotv3")
#all_results=("summarize_instruction_2shotv1" "summarize_instruction_2shotv2" "summarize_instruction_2shotv3")
#all_results=("extra_language_2shotv1" "extra_language_2shotv2" "extra_language_2shotv3")
#all_results=("dummy_rationale_2shotv1" "dummy_rationale_2shotv2" "dummy_rationale_2shotv3")
#all_results=("random_label_2shotv1" "random_label_2shotv2" "random_label_2shotv3")
#all_results=("random_rationale_and_label_2shotv1" "random_rationale_and_label_2shotv2" "random_rationale_and_label_2shotv3")
#all_results=("shots_with_summarized_instruction_2shotv1" "shots_with_summarized_instruction_2shotv2" "shots_with_summarized_instruction_2shotv3")
all_results=("label_first_2shotv1" "label_first_2shotv2" "label_first_2shotv3")



exclude_experiment=""

dataset_name="snli"
#Note: Please make sure to update data/dataset_info with corresponding dataset

num_examples=500
gpu_devices=0

#DO NOT EDIT AFTER THIS

for exp_file_name in "${all_results[@]}"; do
  if [ "$exp_file_name" = "$exclude_experiment" ]; then
    continue
  fi

  #remove the .txt from the end of the file name
  exp_file_name="${exp_file_name%.*}"

  out_name=$exp_file_name #Note: this is the output of sbatch and results

  #create the output directory.
  out="${RESULTS_DIR}/$out_name"
  mkdir -p $out

  #Moving out one level because we set the cwd to be LLaMA-Efficient-Tuning
#  out="./../${out}" #this is now commented out because scripts is also one directory in

  #setting sbatch_out
  sbatch_out="${SBATCH_OUT}/${out_name}.out"

  sbatch --output=$sbatch_out sbatch_launch.sh $LLAMA_ET $exp_file_name $dataset_name $num_examples $gpu_devices $out

done

