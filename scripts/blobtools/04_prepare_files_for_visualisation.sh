#!/bin/bash
#BSUB -o ./log/move-%J-output.log
#BSUB -e ./log/move-%J-error.log 
#BSUB -J btk-moveresults
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1400
#BSUB -W 00:30
#BSUB -R "select[mem>1400] rusage[mem=1400]"

path="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for btk_out in ${path}/*/assembly/btk_nomasking/blobtoolkit/*.contigs
do 
    ln -sfn ${btk_out} /lustre/scratch122/tol/share/team301-btk-prod/blobplots/
done
