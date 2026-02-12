#!/bin/bash
#BSUB -o ./log/prodigal-meta-%J-output.log
#BSUB -e ./log/prodigal-meta-%J-error.log 
#BSUB -J prodigal
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 48:00
#BSUB -M 20000
#BSUB -R "select[mem>20000] rusage[mem=20000]"

module load conda
conda activate bioinfo

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    mkdir -p ${assembly_folder}/prodigal
    out=${assembly_folder}/prodigal
    
    for assembly in ${assembly_folder}/fasta/*.fasta.gz
    do
        filename=$(basename ${assembly} ".fasta.gz")
        
        prodigal -i ${assembly} -o ${out}/${filename}_prodigal.gff \
        -p meta  -f gff
    done
done