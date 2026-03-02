#!/bin/bash
#BSUB -J concatenate_reads
#BSUB -q normal
#BSUB -o ./log/concatenate_reads-%J.out
#BSUB -e ./log/concatenate_reads-%J.err
#BSUB -G team301
#BSUB -n 1
#BSUB -M 10000
#BSUB -W 08:00
#BSUB -R "select[mem>10000] rusage[mem=10000]"

module load conda
conda activate bioinfo

cd /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan

python 01_concatenate_read_files.py
