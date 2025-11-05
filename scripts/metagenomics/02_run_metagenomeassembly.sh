#!/bin/bash
#BSUB -o metaass-%J-%I-output.log
#BSUB -e metaass-%J-%I-error.log 
#BSUB -J metagenomeassembly[1-38]
#BSUB -q oversubscribed
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1400
#BSUB -R "select[mem>1400] rusage[mem=1400]"

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/yamls"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/02_array_config.txt"

export LSB_DEFAULT_USERGROUP=team301
export NXF_OPTS='-Xms128m -Xmx1024m'
module load nextflow/25.04.6-5954
module load ISG/singularity/3.11.4

yaml=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
sp=$(basename ${yaml} ".yaml")

#To avoid logs writting all in the same place, we set a launch place per array id
launch_base="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/launch/${LSB_JOBID}_${LSB_JOBINDEX}"
mkdir -p ${launch_base}
cd ${launch_base}
work_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/logs/${LSB_JOBID}_${LSB_JOBINDEX}"

nextflow run sanger-tol/metagenomeassembly -profile singularity,sanger \
-work-dir ${work_dir} --input ${yaml} --outdir ${output_dir}/${sp} \
--gtdbtk_db /lustre/scratch122/tol/resources/gtdb/v226/ --ncbi_taxonomy_dir /lustre/scratch122/tol/resources/taxonomy/latest/new_taxdump/ \
--checkm2_db /lustre/scratch122/tol/resources/checkm2/latest/uniref100.KO.1.dmnd --genomad_db /lustre/scratch122/tol/resources/geNomad/latest/

