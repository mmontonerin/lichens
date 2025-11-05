#!/bin/bash
#BSUB -o kraken-%J-output.log
#BSUB -e kraken-%J-error.log 
#BSUB -J kraken2_ref
#BSUB -q normal
#BSUB -G team301
#BSUB -n 4
#BSUB -M 10000
#BSUB -R "select[mem>10000] rusage[mem=10000]"
#BSUB -W 12:00

shopt -s nullglob

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens"
#database="/nfs/users/nfs_m/mn16/db/nt_kraken2/latest"
database="/nfs/users/nfs_m/mn16/db/refseq_kraken2/latest"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results"

module load conda

echo "[INFO] Starting: $(date)"
echo "[INFO] Data dir: ${data_dir}"
echo "[INFO] DB: ${database}"
echo "[INFO] Output dir: ${output_dir}"

for lichen in ${data_dir}/*
do
    [ -d ${lichen} ] || continue
    sp=$(basename ${lichen})
    mkdir -p ${output_dir}/${sp} 

    for dataset in ${lichen}/genomic_data/g*
    do
        [ -d ${dataset} ] || continue
        data=$(basename ${dataset})
        out_sub="${output_dir}/${sp}/${data}"
        mkdir -p ${out_sub}

        fasta_glob=(${dataset}/pacbio/fasta/*.fasta.gz)
        if (( ${#fasta_glob[@]} == 0 )); then
            echo "[WARN] No .fasta.gz files in ${dataset}/pacbio/fasta — skipping."
            continue
        fi

        for fasta in ${fasta_glob[@]}
        do 
            filename=$(basename ${fasta} ".fasta.gz")
            echo "[INFO] Processing ${sp}/${data}/${filename} at $(date)"

            conda run -n bioinfo kraken2 --db ${database} --threads 4 \
            --output ${output_dir}/${sp}/${data}/${filename}_kraken_refseq.out \
            --report ${output_dir}/${sp}/${data}/${filename}_kraken_refseq_report.out \
            ${fasta}

            echo "[INFO] Done ${sp}/${data}/${filename} at $(date)"
        done
    done
done   
