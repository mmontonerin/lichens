#!/bin/bash
#BSUB -o ./log/gz-%J-output.log
#BSUB -e ./log/gz-%J-error.log 
#BSUB -J gz
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 4000
#BSUB -R "select[mem>4000] rusage[mem=4000]"
#BSUB -W 12:00


for gz in /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/*/bin_selection/*/*gz
do
    gunzip ${gz}
done