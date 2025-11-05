#!/bin/bash
#BSUB -o ./log/metaass-%JXan-output.log
#BSUB -e ./log/metaass-%JXan-error.log 
#BSUB -J metagenomeassembly
#BSUB -q oversubscribed
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1400
#BSUB -R "select[mem>1400] rusage[mem=1400]"

yaml="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/yamls/Xanthoria_parietina.yaml"
output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/Xanthoria_parietina"

export LSB_DEFAULT_USERGROUP=team301
export NXF_OPTS='-Xms128m -Xmx1024m'
module load nextflow/25.04.6-5954
module load ISG/singularity/3.11.4

sp=$(basename ${yaml} ".yaml")

#To avoid logs writting all in the same place, we set a launch place per array id
launch_base="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/launch/${LSB_JOBID}_Xparietina"
mkdir -p ${launch_base}
cd ${launch_base}
work_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/log/${LSB_JOBID}_Xparietina"

nextflow run sanger-tol/metagenomeassembly -profile singularity,sanger -r dev \
-work-dir ${work_dir} --input ${yaml} --outdir ${output_dir} \
--gtdbtk_db /lustre/scratch122/tol/resources/gtdb/v226/ --ncbi_taxonomy_dir /lustre/scratch122/tol/resources/taxonomy/latest/new_taxdump/ \
--checkm2_db /lustre/scratch122/tol/resources/checkm2/latest/uniref100.KO.1.dmnd --genomad_db /lustre/scratch122/tol/resources/geNomad/latest/

