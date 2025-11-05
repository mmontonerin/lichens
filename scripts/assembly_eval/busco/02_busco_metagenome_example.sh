#!/bin/bash
#BSUB -o ./log/extra_busco-%J-output.log
#BSUB -e ./log/extra_busco-%J-error.log 
#BSUB -J busco
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 4000
#BSUB -R "select[mem>4000] rusage[mem=4000]"
#BSUB -W 12:00

shopt -s nullglob
dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/assembly_eval/metagenome"
#input="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Ricasolia_virens"
#input="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Lobaria_pulmonaria"
input="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa"
busco_db="/nfs/users/nfs_m/mn16/db/busco/latest"
lineage_a="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/ascomycota_odb12"
lineage_c="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/cyanobacteriota_odb12"
lineage_t="/nfs/users/nfs_m/mn16/db/busco/latest/lineages/trebouxiophyceae_odb12"
#sp="Ricasolia_virens"
#sp="Lobaria_pulmonaria"
sp="Cladonia_squamosa"

module load conda
conda activate busco

out=${dir}/busco
mkdir -p ${out}

#busco -i ${input}/bin_selection/ascomycota/merged.0_c99.25_co2.63_Parmeliaceae.fa \
#-m genome -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota --offline --download_path ${busco_db}

#busco -i ${input}/bin_selection/chlorophyta/merged.1_c100.0_co0.0_Trebouxiophyceae.fa \
#-m genome -l ${lineage_t} -c 8 --out_path ${out} -o ${sp}_trebouxiophyceae --offline --download_path ${busco_db}

#zcat /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Ricasolia_virens/bin_selection/cyanobacteriota/Ricasolia_virens_metamdbg_dastool_4_comp90.79_Cyanobacteriota_Nostocaceae.fa.gz \
#    > /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Ricasolia_virens/bin_selection/cyanobacteriota/Ricasolia_virens_metamdbg_dastool_4_comp90.79_Cyanobacteriota_Nostocaceae.fa
#busco -i /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Ricasolia_virens/bin_selection/cyanobacteriota/Ricasolia_virens_metamdbg_dastool_4_comp90.79_Cyanobacteriota_Nostocaceae.fa \
#-m genome -f -l ${lineage_c} -c 8 --out_path ${out} -o Ricasolia_virens_cyanobacteriota --offline --download_path ${busco_db}

#zcat ${input}/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.49_c31.95_co4.89_Parmeliaceae.fa.gz \
#  > ${input}/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.49_c31.95_co4.89_Parmeliaceae.fa
#busco -i ${input}/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.49_c31.95_co4.89_Parmeliaceae.fa \
#-m genome -f -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota1 --offline --download_path ${busco_db}

#zcat /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Lobaria_pulmonaria/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.59_c78.2_co0.75_Parmeliaceae.fa.gz > /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Lobaria_pulmonaria/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.59_c78.2_co0.75_Parmeliaceae.fa
#busco -i /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Lobaria_pulmonaria/bin_selection/ascomycota/Lobaria_pulmonaria_metamdbg_metabat2.59_c78.2_co0.75_Parmeliaceae.fa \
#-m genome -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota2 --offline --download_path ${busco_db}

#zcat ${input}/bin_selection/chlorophyta/Lobaria_pulmonaria_metamdbg_metabat2.26_c100.0_co0.0_Trebouxiophyceae.fa.gz \
#    > ${input}/bin_selection/chlorophyta/Lobaria_pulmonaria_metamdbg_metabat2.26_c100.0_co0.0_Trebouxiophyceae.fa
#busco -i ${input}/bin_selection/chlorophyta/Lobaria_pulmonaria_metamdbg_metabat2.26_c100.0_co0.0_Trebouxiophyceae.fa \
#-m genome -f -l ${lineage_t} -c 8 --out_path ${out} -o ${sp}_trebouxiophyceae --offline --download_path ${busco_db}


#zcat /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.453_c78.95_co40.98_Parmeliaceae.fa.gz > /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.453_c78.95_co40.98_Parmeliaceae.fa
#busco -i /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.453_c78.95_co40.98_Parmeliaceae.fa \
#-m genome -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota1 --offline --download_path ${busco_db}

#zcat /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.97_c15.04_co0.0_Parmeliaceae.fa.gz > /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.97_c15.04_co0.0_Parmeliaceae.fa
#busco -i /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.97_c15.04_co0.0_Parmeliaceae.fa \
#-m genome -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota2 --offline --download_path ${busco_db}

zcat /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.270_c19.92_co3.76_Parmeliaceae.fa.gz > /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.270_c19.92_co3.76_Parmeliaceae.fa
busco -i /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Cladonia_squamosa/bin_selection/ascomycota/Cladonia_squamosa_metamdbg_metabat2.270_c19.92_co3.76_Parmeliaceae.fa \
-m genome -l ${lineage_a} -c 8 --out_path ${out} -o ${sp}_ascomycota3 --offline --download_path ${busco_db}