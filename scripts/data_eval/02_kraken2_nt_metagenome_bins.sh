#!/bin/bash
#BSUB -o kraken2meta-bin-%J-output.log
#BSUB -e kraken2meta-bin-%J-error.log 
#BSUB -J kraken2_nt_meta-bin
#BSUB -q hugemem
#BSUB -G team301
#BSUB -n 10
#BSUB -M 1200000
#BSUB -R "select[mem>1200000] rusage[mem=1200000]"
#BSUB -W 100:00

shopt -s nullglob

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
database="/nfs/users/nfs_m/mn16/db/nt_kraken2/latest"
#database="/nfs/users/nfs_m/mn16/db/refseq_kraken2/latest"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/01_nt_reports_metagenomes_bins"

module load conda

mkdir -p ${output_dir}

for metamdbg in ${data_dir}/*/bins/fasta/metabat2/*fa.gz
do
    filename=$(basename ${metamdbg} ".fa.gz")

    conda run -n bioinfo kraken2 --db ${database} --threads 10 \
    --output ${output_dir}/${filename}_kraken_nt.out \
    --report ${output_dir}/${filename}_kraken_nt_report.out \
    ${metamdbg}
done   