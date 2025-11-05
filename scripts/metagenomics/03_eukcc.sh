#!/bin/bash
#BSUB -o eukcc-%J-%I-output.log
#BSUB -e eukcc-%J-%I-error.log 
#BSUB -J eukcc
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -W 10:00
#BSUB -M 30000
#BSUB -R "select[mem>30000] rusage[mem=30000]"

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

module load conda
conda activate eukcc
export EUKCC2_DB=/lustre/scratch127/tol/teams/blaxter/users/mn16/db/eukcc2_db_ver_1.2

#for sp in ${input_dir}/*
for sp in ${input_dir}/Xanthoria_parietina
do  
    output_dir=${sp}/bins/taxonomy_eukcc
    mkdir -p ${output_dir}

    gunzip ${sp}/bins/fasta/metabat2/*.fa.gz

    eukcc folder --out ${output_dir} --threads 8 ${sp}/bins/fasta/metabat2

    gzip ${sp}/bins/fasta/metabat2/*.fa
done    

