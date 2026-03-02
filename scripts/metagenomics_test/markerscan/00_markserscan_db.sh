#!/bin/bash
#BSUB -J copy_marker_database
#BSUB -q transfer
#BSUB -o ./log/copy_marker_database-%J.out
#BSUB -e ./log/-%J.err
#BSUB -G team301
#BSUB -n 1
#BSUB -M 200
#BSUB -R "select[mem>200] rusage[mem=200]"

SRC="/lustre/scratch122/tol/resources/marker/"
DEST="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/db"

echo "Starting rsync at $(date)"
rsync -avh --info=progress2 ${SRC} ${DEST}
echo "Finished at $(date)"

touch -c -m -a /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/db
find /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/db -exec touch -c {} +