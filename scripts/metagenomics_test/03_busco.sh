#!/bin/bash
#BSUB -o ./log/busco-assembly-%J-output.log
#BSUB -e ./log/busco-assembly-%J-error.log 
#BSUB -J busco_meta
#BSUB -q long
#BSUB -G team301
#BSUB -n 16
#BSUB -W 48:00
#BSUB -M 80000
#BSUB -R "select[mem>80000] rusage[mem=80000]"

module load conda
conda activate busco

busco_db="/nfs/users/nfs_m/mn16/db/busco/latest"
lineage="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/eukaryota_odb10"

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    mkdir -p ${assembly_folder}/busco
    out=${assembly_folder}/busco
    
    for assembly in ${assembly_folder}/fasta/*.fasta.gz
    do
        filename=$(basename ${assembly} ".fasta.gz")
        
        busco -i ${assembly} -m genome -l ${lineage} \
        -c 16 --out_path ${out} -o ${filename} \
        --offline --download_path ${busco_db}
    done
done