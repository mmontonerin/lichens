#!/bin/bash
#BSUB -o ./log/depth-%J-output.log
#BSUB -e ./log/depth-%J-error.log 
#BSUB -J depth
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 48:00
#BSUB -M 100000
#BSUB -R "select[mem>100000] rusage[mem=100000]"

module load conda
conda activate eukbin

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for assembly_folder in ${data}/*/assembly
do
    mkdir -p ${assembly_folder}/depth
    out=${assembly_folder}/depth
    
    for map in ${assembly_folder}/mapping/*.hifi.bam
    do
        filename=$(basename ${map} ".minimap2.hifi.bam")
        
        jgi_summarize_bam_contig_depths --outputDepth ${out}/${filename}_depth.tsv ${map}
    done
done