#!/bin/bash
#BSUB -o ./log/k2-tocsv-%J-output.log
#BSUB -e ./log/k2-tocsv-%J-error.log 
#BSUB -J kraken-tocsv
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 2000
#BSUB -R "select[mem>2000] rusage[mem=2000]"
#BSUB -W 04:00

module load conda
conda activate bioinfo 
reports_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_nt_read_reports"
metadata="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens.csv"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads"

#python 04a_kraken2report_tocsv_byrank_parentsincluded.py -d ${reports_dir} -m ${metadata} -o ${output_dir}

#python 04b_combine_rank_files.py ${output_dir}

#python 04c_nolowmatches.py ${output_dir}

python 04d_bp_number.py ${output_dir} 