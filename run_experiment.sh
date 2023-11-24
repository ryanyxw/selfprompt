#This exits the script if any command fails
set -e

LLAMA_ET=LLaMA-Efficient-Tuning

#################

exp_file_name="random_rationale_and_label" #Note: Please make sure to update src/llmtuner/extras/template.py with corresponding template name
out_name="random_rationale_and_label" #Note: this is the output of sbatch and results

dataset_name="snli"
#Note: Please make sure to update data/dataset_info with corresponding dataset

num_examples=5
gpu_devices=0

################# Do not edit after this

#create the output directory.
out="results_out_dir/$out_name"
mkdir -p $out

#Moving out one level because we set the cwd to be LLaMA-Efficient-Tuning
out="./../${out}"

#setting sbatch_out
mkdir -p "sbatch_out"
sbatch_out="sbatch_out/${out_name}.out"

sbatch --output=${sbatch_out} sbatch_launch.sh $LLAMA_ET $exp_file_name $dataset_name $num_examples $gpu_devices $out