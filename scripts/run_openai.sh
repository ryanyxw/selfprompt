#This exits the script if any command fails
set -e

LLAMA_ET="./../LLaMA-Efficient-Tuning"
DEMONSTRATIONS_DIR="./../demonstrations"
RESULTS_DIR="./../results_out_dir"
SRC_DIR="./../src"
SBATCH_OUT="./../sbatch_out"
PROCESSED_DIR="./../process_out_dir"


all_results=("gpt4_demonstrations_gpt4.txt")

seed=42

exclude_experiment=""

num_evaluations=500

#DO NOT EDIT AFTER THIS

for exp_file_name in "${all_results[@]}"; do
  if [ "$exp_file_name" = "$exclude_experiment" ]; then
    continue
  fi

  #remove the .txt from the end of the file name
  exp_file_name="${exp_file_name%.*}"

  out_name=$exp_file_name #Note: this is the output of results

  #create the output directory.
  out="${RESULTS_DIR}/$out_name"
  mkdir -p $out

  #Moving out one level because we set the cwd to be LLaMA-Efficient-Tuning
#  out="./../${out}" #this is now commented out because scripts is also one directory in

  #setting sbatch_out
  python ${SRC_DIR}/query_openai_script.py\
    --exp_name "${exp_file_name}"\
    --demonstration_file "${DEMONSTRATIONS_DIR}/${exp_file_name}.txt"\
    --num_evaluations "${num_evaluations}"\
    --out "${out}"\
    --seed "${seed}"
done

