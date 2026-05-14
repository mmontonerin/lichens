#!/bin/bash
#BSUB -o ./log/wget_coreNT-%J-output.log
#BSUB -e ./log/wget_coreNT-%J-error.log 
#BSUB -J wget_core_nt
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 8000
#BSUB -R "select[mem>8000] rusage[mem=8000]"
#BSUB -W 12:00

cd /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/kraken_investigation/db

#Remove previous try (killed due to time limit)
rm k2_core_nt_20251015.tar.gz

wget https://genome-idx.s3.amazonaws.com/kraken/k2_core_nt_20251015.tar.gz

tar -xvzf k2_core_nt_20251015.tar.gz