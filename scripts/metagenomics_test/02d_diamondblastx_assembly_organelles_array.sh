#!/bin/bash
#BSUB -o ./log/diamond-assembly-%J-%I-output.log
#BSUB -e ./log/diamond-assembly-%J-%I-error.log 
#BSUB -J diamond_blastx[1-38]
#BSUB -q long
#BSUB -G team301
#BSUB -n 16
#BSUB -W 36:00
#BSUB -M 30000
#BSUB -R "select[mem>30000] rusage[mem=30000]"

module load conda
conda activate bioinfo

db="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db/organelle_proteins.dmnd"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/04_array_config.txt"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

species=$(basename ${sp})
assembly_folder=${sp}/assembly
assembly=${assembly_folder}/fasta/${species}_metamdbg.contigs.fasta.gz
filename=$(basename ${assembly} ".contigs.fasta.gz")

# Format 102 to output only taxonomy.
diamond blastx --query ${assembly} --db ${db} -f 102 --include-lineage --threads 16 \
    -o ${assembly_folder}/diamond_organelle/${filename}_diamond.out