#!/bin/bash
#BSUB -o ./log/busco-assembly-%J-%I-output.log
#BSUB -e ./log/busco-assembly-%J-%I-error.log 
#BSUB -J busco_meta[1-38]
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -W 12:00
#BSUB -M 80000
#BSUB -R "select[mem>80000] rusage[mem=80000]"

module load conda
conda activate busco

busco_db="/nfs/users/nfs_m/mn16/db/busco/latest"
lineage="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/lepidoptera_odb10"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/04_array_config.txt"

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

species=$(basename ${sp})
assembly_folder=${sp}/assembly
assembly=${assembly_folder}/fasta/${species}_metamdbg.contigs.fasta.gz

out=${assembly_folder}/busco
    
filename=$(basename ${assembly} ".fasta.gz")
        
busco -i ${assembly} -m genome -l ${lineage} \
    -c 8 --out_path ${out} -o ${filename}_lepidoptera \
    --offline --download_path ${busco_db}