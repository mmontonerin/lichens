#!/bin/bash
#BSUB -o ./log/rvirens_quast-%J-output.log
#BSUB -e ./log/rvirend_quast-%J-error.log 
#BSUB -J quast
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 4000
#BSUB -R "select[mem>4000] rusage[mem=4000]"
#BSUB -W 12:00

shopt -s nullglob
dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/assembly_eval/metagenome"
input="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa"
sp="Cladonia_Squamosa"

module load conda
conda activate quast

out=${dir}/quast
mkdir -p ${out}

#quast -o ${out}/${sp}_ascomycota -t 8 --no-plots --no-html ${input}/bin_selection/ascomycota/merged.0_c99.25_co2.63_Parmeliaceae.fa
#quast -o ${out}/${sp}_trebouxiophyceae -t 8 --no-plots --no-html ${input}/bin_selection/chlorophyta/merged.1_c100.0_co0.0_Trebouxiophyceae.fa
#quast -o ${out}/${sp}_cyanobacteriota -t 8 --no-plots --no-html ${input}/bin_selection/cyanobacteriota/Ricasolia_virens_metamdbg_dastool_4_comp90.79_Cyanobacteriota_Nostocaceae.fa.gz

#quast -o ${out}/${sp}_ascomycota1 -t 8 --no-plots --no-html ${input}/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.49_c31.95_co4.89_Parmeliaceae.fa
#quast -o ${out}/${sp}_ascomycota2 -t 8 --no-plots --no-html /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Lobaria_pulmonaria/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.59_c78.2_co0.75_Parmeliaceae.fa
#quast -o ${out}/${sp}_trebouxiophyceae -t 8 --no-plots --no-html ${input}/bin_selection/chlorophyta/Lobaria_pulmonaria_metamdbg_metabat2.26_c100.0_co0.0_Trebouxiophyceae.fa

quast -o ${out}/${sp}_ascomycota1 -t 8 --no-plots --no-html /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.453_c78.95_co40.98_Parmeliaceae.fa
quast -o ${out}/${sp}_ascomycota2 -t 8 --no-plots --no-html /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.97_c15.04_co0.0_Parmeliaceae.fa
quast -o ${out}/${sp}_ascomycota3 -t 8 --no-plots --no-html /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.270_c19.92_co3.76_Parmeliaceae.fa