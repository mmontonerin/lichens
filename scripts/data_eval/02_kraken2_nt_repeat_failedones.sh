#!/bin/bash
#BSUB -o ./log/kraken_repeat-%J-output.log
#BSUB -e ./log/kraken_repeat-%J-error.log 
#BSUB -J kraken2_nt
#BSUB -q hugemem
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1000000
#BSUB -R "select[mem>1000000] rusage[mem=1000000]"
#BSUB -W 12:00

shopt -s nullglob

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens"
database="/nfs/users/nfs_m/mn16/db/nt_kraken2/latest"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_results"

module load conda

for lichen in ${data_dir}/Ionaspis_lacustris ${data_dir}/Pseudevernia_furfuracea 
do
    [ -d ${lichen} ] || continue
    sp=$(basename ${lichen})
    mkdir -p ${output_dir}/${sp}_new
    out="${output_dir}/${sp}_new" 

    for dataset in ${lichen}/genomic_data/g*
    do
        [ -d ${dataset} ] || continue
        data=$(basename ${dataset})
        out_sub="${out}/${data}"
        mkdir -p ${out_sub}

        fasta_glob=(${dataset}/pacbio/fasta/*.fasta.gz)
        if (( ${#fasta_glob[@]} == 0 )); then
            continue
        fi

        for fasta in ${fasta_glob[@]}
        do 
            filename=$(basename ${fasta} ".fasta.gz")

            conda run -n bioinfo kraken2 --db ${database} --threads 1 \
            --output ${output_dir}/${sp}/${data}/${filename}_kraken_nt.out \
            --report ${output_dir}/${sp}/${data}/${filename}_kraken_nt_report.out \
            ${fasta}
        done
    done
done   
