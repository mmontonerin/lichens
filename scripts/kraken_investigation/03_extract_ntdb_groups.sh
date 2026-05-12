#!/bin/bash
#BSUB -o ./log/db_extract_groups-%J-output.log
#BSUB -e ./log/db_extract_groups-%J-error.log 
#BSUB -J db_extract_groups
#BSUB -q long
#BSUB -G team301
#BSUB -n 1
#BSUB -M 50000
#BSUB -R "select[mem>50000] rusage[mem=50000]"
#BSUB -W 24:00

nt_db="/nfs/users/nfs_m/mn16/db/nt_blast/2025-06-03T00:00:00"
out_fa="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation/nt_groups"

module load conda
conda activate bioinfo

export BLASTDB=/lustre/scratch122/tol/resources/nt/2025-06-03T00:00:00

cd ${nt_db}

Extract all lepidoptera sequences
blastdbcmd -db ${BLASTDB}/nt -taxids 7088 -out ${out_fa}/lepidoptera.fasta -outfmt %f

#Extract bacteria
#blastdbcmd -db ${BLASTDB}/nt -taxids 2 -out ${out_fa}/bacteria.fasta -outfmt %f

#Extract fungi
#blastdbcmd -db ${BLASTDB}/nt -taxids 4751 -out ${out_fa}/fungi.fasta -outfmt %f

#Extract plants
#blastdbcmd -db ${BLASTDB}/nt -taxids 3193 -out ${out_fa}/viridiplantae.fasta -outfmt %f

#Extract metazoa without lepidoptera
#blastdbcmd -db ${BLASTDB}/nt -taxids 33208 -out ${out_fa}/metazoa.fasta -outfmt %f

#Extract metazoa without hexapoda
#blastdbcmd -db ${BLASTDB}/nt -taxids 6960 -out ${out_fa}/hexapoda.fasta -outfmt %f

#Extract metazoa without arthropods
#blastdbcmd -db ${BLASTDB}/nt -taxids 6656 -out ${out_fa}/arthropoda.fasta -outfmt %f