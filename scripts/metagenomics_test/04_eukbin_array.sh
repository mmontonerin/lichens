#!/bin/bash
#BSUB -o ./log/eukbin-%J-%I-output.log
#BSUB -e ./log/eukbin-%J-%I-error.log 
#BSUB -J eukbin[1-38]
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 48:00
#BSUB -M 40000
#BSUB -R "select[mem>40000] rusage[mem=40000]"

shopt -s nullglob
module load conda
conda activate eukbin

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/04_array_config.txt"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

out=${sp}/bins/fasta/eukbin
mkdir -p ${out}

species=$(basename ${sp})
assembly_folder=${sp}/assembly
assembly=${assembly_folder}/fasta/${species}_metamdbg.contigs.fasta.gz

filename=$(basename ${assembly} ".contigs.fasta.gz")
        
python -m eukbin run --fasta ${assembly} \ 
--depth ${assembly_folder}/depth/${filename}_depth.tsv \
--busco ${assembly_folder}/busco/run_eukaryota_odb10/full_table.tsv \
--tiara ${assembly_folder}/tiara/tiara_out.txt \
--gff ${assembly_folder}/prodigal/${filename}.contigs_prodigal.gff \
--out ${out} \
--threads 8