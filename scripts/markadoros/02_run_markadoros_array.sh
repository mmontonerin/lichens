#!/bin/bash
#BSUB -o ./log/markadoros-%J_%I-output.log
#BSUB -e ./log/markadoros-%J_%I-error.log 
#BSUB -J markadoros[1-63]%21
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -M 50000
#BSUB -R "select[mem>50000] rusage[mem=50000]"
#BSUB -W 48:00

shopt -s nullglob

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/markadoros"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/markadoros/01_array_config.txt"
db_path="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/markadoros/db"

module load conda
conda activate markadoros

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

out="${output_dir}/${sp}"
mkdir -p ${out}

reads=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $3}' ${path_config})

#COI - Cytochrome C mitochondria subunit of Complex IV 
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.COI ${reads} \
    --threads 8 --prefix ${sp}_COI --outdir ${out} --save-contigs

#CYTB - Cytochrome B mitochondria subunit of Complex III
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.CYTB ${reads} \
    --threads 8 --prefix ${sp}_cytB --outdir ${out} --save-contigs

#rbcL - large subunit of RuBisCO, chloroplast
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.rbcL ${reads} \
    --threads 8 --prefix ${sp}_rbcL --outdir ${out} --save-contigs

#matK - Megakaryocyte-associated tyrosine kinase gene, chloroplast
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.matK ${reads} \
    --threads 8 --prefix ${sp}_matK --outdir ${out} --save-contigs

#18S
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.18S ${reads} \
    --threads 8 --prefix ${sp}_18S --outdir ${out} --save-contigs

#28S
markadoros search -x pacbio --index ${db_path}/db.json --db BOLD.28S ${reads} \
    --threads 8 --prefix ${sp}_28S --outdir ${out} --save-contigs

#LSU
markadoros search -x pacbio --index ${db_path}/db.json --db SILVA.LSU ${reads} \
    --threads 8 --prefix ${sp}_LSU --outdir ${out} --save-contigs

#SSU
markadoros search -x pacbio --index ${db_path}/db.json --db SILVA.SSU ${reads} \
    --threads 8 --prefix ${sp}_SSU --outdir ${out} --save-contigs

#ITS
markadoros search -x pacbio --index ${db_path}/db.json --db UNITE.ITS ${reads} \
    --threads 8 --prefix ${sp}_ITS --outdir ${out} --save-contigs