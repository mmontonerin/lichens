#!/bin/bash
#BSUB -o ./log/quast-%J-output.log
#BSUB -e ./log/quast-%J-error.log 
#BSUB -J quast
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 4000
#BSUB -R "select[mem>4000] rusage[mem=4000]"
#BSUB -W 12:00

shopt -s nullglob
dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/assembly_eval/cyanobacteriota"

module load conda
conda activate quast

out=${dir}/quast
mkdir -p ${out}

for fasta in ${dir}/assemblies/*fasta
do
    filename=$(basename ${fasta} ".fasta")
    quast -o ${out}/${filename} -t 8 --no-plots --no-html ${fasta}
done