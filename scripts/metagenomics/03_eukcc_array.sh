#!/bin/bash
#BSUB -o eukcc-%J-%I-output.log
#BSUB -e eukcc-%J-%I-error.log 
#BSUB -J eukcc[1-29]
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 24:00
#BSUB -M 30000
#BSUB -R "select[mem>30000] rusage[mem=30000]"

shopt -s nullglob

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/03c_array_config.txt"

module load conda
conda activate eukcc
export EUKCC2_DB=/lustre/scratch127/tol/teams/blaxter/users/mn16/db/eukcc2_db_ver_1.2

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

output_dir=${sp}/bins/taxonomy_eukcc
mkdir -p ${output_dir}

gunzip ${sp}/bins/fasta/metabat2/*.fa.gz

eukcc folder --out ${output_dir} --threads 8 ${sp}/bins/fasta/metabat2

gzip ${sp}/bins/fasta/metabat2/*.fa   

