#!/bin/bash
#BSUB -o ./log/diamond-%J-output.log
#BSUB -e ./log/diamond-%J-error.log 
#BSUB -J diamond_blastx
#BSUB -q week
#BSUB -G team301
#BSUB -n 16
#BSUB -W 168:00
#BSUB -M 20000
#BSUB -R "select[mem>20000] rusage[mem=20000]"

module load conda
conda activate bioinfo

db="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db/organelle_proteins.dmnd"

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    mkdir -p ${assembly_folder}/diamond_organelle

    for mito_contig in ${assembly_folder}/tiara/mitochondrion_*
    do
        filename=$(basename ${mito_contig} ".fasta.gz")
        
        # Format 102 to output only taxonomy.
        diamond blastx --query ${mito_contig} --db ${db} -f 102 --include-lineage --threads 16 \
        -o ${assembly_folder}/diamond_organelle/${filename}_diamond.out
    done

    for plast_contig in ${assembly_folder}/tiara/plastid_*
    do
        filename=$(basename ${plast_contig} ".fasta.gz")
        
        # Format 102 to output only taxonomy.
        diamond blastx --query ${plast_contig} --db ${db} -f 102 --include-lineage --threads 16 \
        -o ${assembly_folder}/diamond_organelle/${filename}_diamond.out
    done
done