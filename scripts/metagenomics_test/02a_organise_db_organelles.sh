#!/bin/bash
#BSUB -o ./log/ftpdownload-%J-output.log
#BSUB -e ./log/ftpdownload-%J-error.log 
#BSUB -J ncbi_ftpdownload
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -W 04:00
#BSUB -M 10000
#BSUB -R "select[mem>10000] rusage[mem=10000]"

rsync -av --timeout=600 rsync://ftp.ncbi.nlm.nih.gov/refseq/release/plastid/ refseq_plastid/
rsync -av --timeout=600 rsync://ftp.ncbi.nlm.nih.gov/refseq/release/mitochondrion/ refseq_mitochondrion/

mkdir db
mv refseq* db/

cp db/refseq*/*protein.faa.gz db/ 
gunzip db/*protein.faa.gz

cat db/*faa > db/organelle_proteins.faa

rm db/*.protein.faa
