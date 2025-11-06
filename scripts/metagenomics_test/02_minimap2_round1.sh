#!/bin/bash
#BSUB -o ./log/minimap2_v1-%J-output.log
#BSUB -e ./log/minimap2_v1-%J-error.log 
#BSUB -J minimap2_v1
#BSUB -q long
#BSUB -G team301
#BSUB -n 4
#BSUB -W 48:00
#BSUB -M 50000
#BSUB -R "select[mem>50000] rusage[mem=50000]"

module load conda
conda activate tiara

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

for sp in ${input_dir}/*
do
    minimap2 -x map-hifi -I1.0G -t 16 \


    # Merge prok and arch
    # Merge euk and unknown
    # call on all the reads from the yaml file

    # Example from metagenome assembly pipeline
    minimap2 \
    -x map-hifi -I1.0G \
    -t 16 \
    Allantoparmelia_alpicola_metamdbg.contigs.fasta.gz \
    m84098_241008_112920_s4.ccs.bc2007.rmdup.trim.fasta.gz \
     \
     \
    -a | samtools sort -@ 15 -o Allantoparmelia_alpicola_metamdbg.minimap2.hifi.bam##idx##Allantoparmelia_alpicola_metamdbg.minimap2.hifi.bam.csi --write-index 

    # Add extract reads that mapped
    samtools view -b -F 4 alignment.bam > mapped.bam
    # -b output in bam
    # -F 4 exclude unmapped reads (only mapped reads)
    # -f 4 would target the unmapped reads instead
    samtools fasta mapped.bam > mapped.fasta

done