#!/bin/bash
#BSUB -o ./log/eukcc-%J-%I-output.log
#BSUB -e ./log/eukcc-%J-%I-error.log 
#BSUB -J eukcc[1-39]
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 48:00
#BSUB -M 30000
#BSUB -R "select[mem>30000] rusage[mem=30000]"

shopt -s nullglob

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_individual"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/04b_array_config.txt"

module load conda
conda activate eukcc
export EUKCC2_DB=/lustre/scratch127/tol/teams/blaxter/users/mn16/db/eukcc2_db_ver_1.2

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

#eukbin_output_dir=${sp}/bins/taxonomy_eukcc_eukbin
#mkdir -p ${eukbin_output_dir}
#remag_output_dir=${sp}/bins/taxonomy_eukcc_remag
#mkdir -p ${remag_output_dir}
metabat2_output_dir=${sp}/bins/taxonomy_eukcc_metabat2
#mkdir -p ${metabat2_output_dir}

#eukcc folder --out ${eukbin_output_dir} --threads 8 ${sp}/bins/fasta/eukbin/bins
#eukcc folder --out ${remag_output_dir} --threads 8 ${sp}/bins/fasta/remag/bins

gunzip ${sp}/bins/fasta/metabat2/*.fa.gz
eukcc folder --out ${metabat2_output_dir} --threads 8 ${sp}/bins/fasta/metabat2
gzip ${sp}/bins/fasta/metabat2/*.fa  