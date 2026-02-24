#!/bin/bash
#BSUB -o ./log/diamond-assembly-%J-output.log
#BSUB -e ./log/diamond-assembly-%J-error.log 
#BSUB -J diamond_blastx
#BSUB -q week
#BSUB -G team301
#BSUB -n 16
#BSUB -W 160:00
#BSUB -M 30000
#BSUB -R "select[mem>30000] rusage[mem=30000]"

module load conda
conda activate bioinfo

db="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db/organelle_proteins.dmnd"

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    for assembly in ${assembly_folder}/fasta/*.fasta.gz
    do
        filename=$(basename ${assembly} ".fasta.gz")
        
        # Format 102 to output only taxonomy.
        diamond blastx --query ${assembly} --db ${db} -f 102 --include-lineage --threads 16 \
        -o ${assembly_folder}/diamond_organelle/${filename}_diamond.out
    done
done