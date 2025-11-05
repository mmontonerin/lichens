#!/bin/bash
#BSUB -o ./log/organiser-%J-output.log
#BSUB -e ./log/organiser-%J-error.log 
#BSUB -J organise_files
#BSUB -q small
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1000
#BSUB -R "select[mem>1000] rusage[mem=1000]"
#BSUB -W 00:01

shopt -s nullglob

results_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_results"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_nt_read_reports"

rm -r ${output_dir} 
mkdir -p ${output_dir}

for sample in ${results_dir}/*/*
do  
    [ -d ${sample} ] || continue
    sp=$(basename ${sample})

    # Count reports present in each sample directory
    reports=( ${sample}/*nt_report.out )
    count=${#reports[@]}

    # First report gets no number
    cp ${reports[0]} ${output_dir}/${sp}.nt_report.out

    # The subsequent reports get _2, _3, etc
    for ((i=1; i<count; i++)); do
        num=$((i+1))
        cp ${reports[i]} ${output_dir}/${sp}_${num}.nt_report.out
    done
done
