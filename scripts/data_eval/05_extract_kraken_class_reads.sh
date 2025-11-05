#!/bin/bash
#BSUB -o ./log/extract-reads-%J-output.log
#BSUB -e ./log/extract-reads-%J-error.log 
#BSUB -J extract-reads
#BSUB -q long
#BSUB -G team301
#BSUB -n 1
#BSUB -M 10000
#BSUB -R "select[mem>10000] rusage[mem=10000]"
#BSUB -W 48:00

shopt -s nullglob

results_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_results"
reads_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_extracted_reads"

rm -r ${output_dir} 
mkdir -p ${output_dir}

module load conda
conda activate bioinfo

for species in ${results_dir}/*
do  
    [ -d ${species} ] || continue
    sp=$(basename ${species})

    mkdir -p ${output_dir}/${sp}
    out=${output_dir}/${sp}

    for sample in ${species}/*
    do  
        [ -d ${sample} ] || continue
        tolid=$(basename ${sample})

        for output in ${sample}/*nt.out
        do
            read_name=$(basename ${output} "_kraken_nt.out")
            reads=${reads_dir}/${sp}/genomic_data/${tolid}/pacbio/fasta/${read_name}.fasta.gz

            # Ascomycota: 4890
            python ./KrakenTools/extract_kraken_reads.py -k ${output} -s ${reads} -o ${out}/${sp}_ascomycota.fasta \
            -t 4890 --include-children --append -r ${sample}/${read_name}_kraken_nt_report.out  

            # Basidiomycota: 5204
            python ./KrakenTools/extract_kraken_reads.py -k ${output} -s ${reads} -o ${out}/${sp}_basidiomycota.fasta \
            -t 5204 --include-children --append -r ${sample}/${read_name}_kraken_nt_report.out  
            
            # Cyanobacteriota: 1117
            python ./KrakenTools/extract_kraken_reads.py -k ${output} -s ${reads} -o ${out}/${sp}_cyanobacteriota.fasta \
            -t 1117 --include-children --append -r ${sample}/${read_name}_kraken_nt_report.out  

            # Viridiplantae: 33090
            python ./KrakenTools/extract_kraken_reads.py -k ${output} -s ${reads} -o ${out}/${sp}_viridiplantae.fasta \
            -t 33090 --include-children --append -r ${sample}/${read_name}_kraken_nt_report.out  

            # Append so that all read data gets pulled together from the same species
            # taxid includes children taxa -> report needed (-r)
        done
    done
done
