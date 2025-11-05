#!/bin/bash
#BSUB -o ./log/busco-%J-output.log
#BSUB -e ./log/busco-%J-error.log 
#BSUB -J busco
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 4000
#BSUB -R "select[mem>4000] rusage[mem=4000]"
#BSUB -W 12:00

shopt -s nullglob
dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/assembly_eval/viridiplantae"
busco_db="/nfs/users/nfs_m/mn16/db/busco/latest"
lineage="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/viridiplantae_odb12"
lineage2="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/trebouxiophyceae_odb12"
lineage3="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/chlorophyta_odb12"
lineage4="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/chlorophyceae_odb12"

module load conda
conda activate busco

out=${dir}/busco
mkdir -p ${out}

for fasta in ${dir}/assemblies/*fasta
do
    filename=$(basename ${fasta} ".fasta")
    busco -i ${fasta} -m genome -l ${lineage} -c 8 --out_path ${out}_viridiplantae -o ${filename} --offline --download_path ${busco_db}
done

for fasta in ${dir}/assemblies/*fasta
do
    filename=$(basename ${fasta} ".fasta")
    busco -i ${fasta} -m genome -l ${lineage2} -c 8 --out_path ${out}_trebouxiophyceae -o ${filename} --offline --download_path ${busco_db}
done

for fasta in ${dir}/assemblies/*fasta
do
    filename=$(basename ${fasta} ".fasta")
    busco -i ${fasta} -m genome -l ${lineage3} -c 8 --out_path ${out}_chlorophyta -o ${filename} --offline --download_path ${busco_db}
done

for fasta in ${dir}/assemblies/*fasta
do
    filename=$(basename ${fasta} ".fasta")
    busco -i ${fasta} -m genome -l ${lineage4} -c 8 --out_path ${out}_chlorophyceae -o ${filename} --offline --download_path ${busco_db}
done