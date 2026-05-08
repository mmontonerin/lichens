#!/bin/bash
#BSUB -o ./log/investigation_kraken-%J-output.log
#BSUB -e ./log/investigation_kraken-%J-error.log 
#BSUB -J kraken2_nt_investigation
#BSUB -q hugemem
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1000000
#BSUB -R "select[mem>1000000] rusage[mem=1000000]"
#BSUB -W 12:00

shopt -s nullglob
module load conda

database="/nfs/users/nfs_m/mn16/db/nt_kraken2/latest"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation"

mkdir -p ${output_dir}

conda run -n bioinfo kraken2-inspect --db ${database} --report-zero-counts > ${output_dir}/kraken2_db_report.txt