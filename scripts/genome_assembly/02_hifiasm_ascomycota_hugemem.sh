#!/bin/bash
#BSUB -o ./log/acomycota-hifiasm-mem2-%J-%I-output.log
#BSUB -e ./log/acomycota-hifiasm-mem2-%J-%I-error.log 
#BSUB -J hifiasm[5,6,7,9,27,29]
#BSUB -q hugemem
#BSUB -G team301
#BSUB -n 32
#BSUB -M 750000
#BSUB -R "select[mem>750000] rusage[mem=750000]"
#BSUB -W 100:00

shopt -s nullglob

module load conda
conda activate bioinfo

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_extracted_reads"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/genome_assemblies"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/genome_assembly/01_array_config_ascomycota.txt"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
fasta=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $3}' ${path_config})
filename=$(basename ${fasta} ".fasta")

out=${output_dir}/${sp}
mkdir -p ${out}

hifiasm -o ${out}/${filename}.asm -t 32 ${fasta}