#!/bin/bash
#BSUB -o ./log/kraken-%J-output.log
#BSUB -e ./log/kraken-%J-error.log 
#BSUB -J kraken2_nt
#BSUB -q hugemem
#BSUB -G team301
#BSUB -n 10
#BSUB -M 400000
#BSUB -R "select[mem>400000] rusage[mem=400000]"
#BSUB -W 100:00

shopt -s nullglob

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
database="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/kraken_investigation/db/20251015_kraken2_core_nt"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/02_core_nt_reports_reads"

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
            continue
        fi

        for fasta in ${fasta_glob[@]}
        do 
            filename=$(basename ${fasta} ".fasta.gz")
            echo "Processing ${sp}/${data}/${filename} at $(date)"

            conda run -n bioinfo kraken2 --db ${database} --threads 10 \
            --output ${output_dir}/${sp}/${data}/${filename}_kraken_nt.out \
            --report ${output_dir}/${sp}/${data}/${filename}_kraken_nt_report.out \
            ${fasta}

            echo "Done ${sp}/${data}/${filename} at $(date)"
        done
    done
done   
