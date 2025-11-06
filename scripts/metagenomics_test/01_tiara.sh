#!/bin/bash
#BSUB -o ./log/tiara-%J-output.log
#BSUB -e ./log/tiara-%J-error.log 
#BSUB -J tiara
#BSUB -q long
#BSUB -G team301
#BSUB -n 4
#BSUB -W 48:00
#BSUB -M 50000
#BSUB -R "select[mem>50000] rusage[mem=50000]"

module load conda
conda activate tiara

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for sp in ${input_dir}/*
do
    fasta=${sp}/assembly/fasta/*fasta.gz
    mkdir -p ${sp}/assembly/tiara
    t_dir=${sp}/assembly/tiara
    cd ${t_dir} # change directory so that output fasta files get saved in the correct place (no output directory can be specified)

    # Tiara command
    # all classifications output to fasta files - classifications are:
    # mit - mitochondria, pla - plastid, bac - bacteria, arc - archea, euk - eukarya, unk - unknown, pro - prokarya, all - all classes present in input fasta
    # Show probabilities in the tiara_out.txt of individual classes for each sequence
    tiara -i ${fasta} -o ${t_dir}/tiara_out.txt --to_fasta all -t 4 --probabilities -v
done