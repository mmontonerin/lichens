#!/bin/bash
#BSUB -o ./log/basidiomycota-hifiasm-%J-%I-output.log
#BSUB -e ./log/basidiomycota-hifiasm-%J-%I-error.log 
#BSUB -J hifiasm[5-38]
#BSUB -q long
#BSUB -G team301
#BSUB -n 32
#BSUB -M 100000
#BSUB -R "select[mem>100000] rusage[mem=100000]"
#BSUB -W 24:00

shopt -s nullglob

module load conda
conda activate bioinfo

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_extracted_reads"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/genome_assemblies"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/genome_assembly/01_array_config_basidiomycota.txt"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
fasta=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $3}' ${path_config})
filename=$(basename ${fasta} ".fasta")

out=${output_dir}/${sp}
mkdir -p ${out}

hifiasm -o ${out}/${filename}.asm -t 16 ${fasta}