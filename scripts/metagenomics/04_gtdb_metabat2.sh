#!/bin/bash
#BSUB -o ./log/gtdbv2-%J-%I-output.log
#BSUB -e ./log/gtdbv2-%J-%I-error.log 
#BSUB -J gtdb[1-38]
#BSUB -q long
#BSUB -G team301
#BSUB -n 16
#BSUB -W 24:00
#BSUB -M 160000
#BSUB -R "select[mem>160000] rusage[mem=160000]"

shopt -s nullglob

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/04b_array_config_gtdb.txt"

module load conda
conda activate gtdb
gtdb_db="/nfs/users/nfs_m/mn16/db/gtdb/latest" #v226 on 16 oct 2025
export GTDB_DATA_PATH="/nfs/users/nfs_m/mn16/db/gtdb/latest"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
path=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $3}' ${path_config})

output_dir=${path}/bins/taxonomy_gtdb
mkdir -p ${output_dir}

gtdbtk classify_wf --extension gz --genome_dir ${path}/bins/fasta/metabat2 \
--prefix gtdbk_${sp} --out_dir ${output_dir} --cpus 16 --skip_ani_screen 

gtdb_to_ncbi_majority_vote.py --gtdbtk_output_dir ${output_dir} --bac120_metadata_file ${gtdb_db}/bac120_metadata_r220.tsv.gz \
--ar53_metadata_file ${gtdb_db}/ar53_metadata_r220.tsv.gz --gtdbtk_prefix gtdbtk_${sp} --output_file gtdbtk_${sp}_ncbi.tsv
