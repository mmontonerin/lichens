#!/bin/bash
#BSUB -o ./log/fastaconv-%J-output.log
#BSUB -e ./log/fastaconv-%J-error.log 
#BSUB -J fastaconverter
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 8000
#BSUB -R "select[mem>8000] rusage[mem=8000]"
#BSUB -W 04:00

shopt -s nullglob

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/genome_assemblies"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/assembly_eval"

for category in basidiomycota cyanobacteriota viridiplantae
do
    out=${output_dir}/${category}
    mkdir -p ${out} 

    for gfa in ${input_dir}/*/*_${category}*_ctg.gfa
    do
        filename=$(basename ${gfa} ".gfa")
        awk '/^S/{print ">"$2;print $3}' ${gfa} > ${out}/${filename}.fasta
    done
done