#!/bin/bash
#BSUB -o ./log/eukbin-%J-output.log
#BSUB -e ./log/eukbin-%J-error.log 
#BSUB -J eukbin
#BSUB -q week
#BSUB -G team301
#BSUB -n 16
#BSUB -W 168:00
#BSUB -M 100000
#BSUB -R "select[mem>100000] rusage[mem=100000]"

module load conda
conda activate eukbin

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    mkdir -p ${assembly_folder}/prodigal
    out=${assembly_folder}/prodigal
    
    for assembly in ${assembly_folder}/fasta/*.fasta.gz
    do
        filename=$(basename ${assembly} ".contigs.fasta.gz")
        
        python -m eukbin run --fasta ${assembly} \
        --depth ${assembly_folder}/depth/${filename}_depth.tsv \
        --busco ${assembly_folder}/busco/run_eukaryota_odb10/full_table.tsv \
        --tiara ${assembly_folder}/tiara/tiara_out.txt \
        --gff ${assembly_folder}/prodigal/${filename}.contigs_prodigal.gff \
        --out ${assembly_folder}/eukbin \
        --threads 16
    done
done