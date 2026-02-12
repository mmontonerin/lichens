#!/bin/bash
#BSUB -o ./log/diamond_mkdb-%J-output.log
#BSUB -e ./log/diamond_mkdb-%J-error.log 
#BSUB -J diamond_mkdb
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -W 10:00
#BSUB -M 250000
#BSUB -R "select[mem>250000] rusage[mem=250000]"

module load conda
conda activate bioinfo

db="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db"

diamond makedb --in ${db}/organelle_proteins.faa --db ${db}/organelle_proteins \
--taxonmap ${db}/prot.accession2taxid.FULL.gz --taxonnodes ${db}/nodes.dmp --taxonnames ${db}/names.dmp 