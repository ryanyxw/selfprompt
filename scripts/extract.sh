#This exits the script if any command fails
set -e

LLAMA_ET="./../LLaMA-Efficient-Tuning"
DEMONSTRATIONS_DIR="./../demonstrations"
RESULTS_DIR="./../results_out_dir"
SRC_DIR="./../src"
SBATCH_OUT="./../sbatch_out"
PROCESSED_DIR="./../process_out_dir"

#extracts demonstrations and sends them to demo_out_dir

demonstration_pool=1000

#choose from: "dummy_rationale", "random_label", "random_rationale_and_label"
exp_name="label_first"

shots=(2)
versions=3


#Do not change below:

for shot in "${shots[@]}"; do
  #loop version number of times
  for ((i=1; i<=versions; i++)); do
    out_name="${exp_name}_${shot}shotv${i}"
    num_demonstration=$((shot*3))
    seed=$((42+i))

    mkdir -p "$DEMONSTRATIONS_DIR"
    out_file="${DEMONSTRATIONS_DIR}/${out_name}.txt"

    if [ -e "$out_file" ]; then
      rm "$out_file"
    fi

    python ${SRC_DIR}/extract_shots_script.py\
      --exp_name "${exp_name}"\
      --demonstration_pool "${demonstration_pool}"\
      --num_demonstration "${num_demonstration}" \
      --seed "${seed}" >> "$out_file"
  done
done




