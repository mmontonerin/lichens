#!/bin/bash
#BSUB -o ./log/btk-%J-%I-output.log
#BSUB -e ./log/btk-%J-%I-error.log 
#BSUB -J btk[1-38]
#BSUB -q oversubscribed
#BSUB -G team301
#BSUB -n 1
#BSUB -M 1400
#BSUB -R "select[mem>1400] rusage[mem=1400]"

output_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/03_array_config.txt"

export LSB_DEFAULT_USERGROUP=team301
export NXF_OPTS='-Xms128m -Xmx1024m'
module load nextflow/25.04.6-5954
module load ISG/singularity/3.11.4

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
samplesheet=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $3}' ${path_config})
assembly=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $4}' ${path_config})
taxid=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $5}' ${path_config})

#To avoid logs writting all in the same place, we set a launch place per array id
launch_base="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/launch/${LSB_JOBID}_${LSB_JOBINDEX}"
mkdir -p ${launch_base}
cd ${launch_base}
work_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/working_directory/${LSB_JOBID}_${LSB_JOBINDEX}"

nextflow run /nfs/treeoflife-01/teams/tola/users/yy5/btk_current/blobtoolkit/main.nf \
    -profile sanger,singularity -ansi-log false -with-weblog http://logstash.tol.sanger.ac.uk/http \
    --taxdump /lustre/scratch122/tol/resources/taxonomy/latest/new_taxdump \
    --busco /lustre/scratch122/tol/resources/busco/latest \
    --blastp /lustre/scratch122/tol/resources/uniprot_reference_proteomes/latest/reference_proteomes.dmnd \
    --blastx /lustre/scratch122/tol/resources/uniprot_reference_proteomes/latest/reference_proteomes.dmnd \
    --blastn /data/tol/resources/nt/latest --fasta ${assembly} --input ${samplesheet} \
    --busco_lineages lepidoptera_odb10,ascomycota_odb10,basidiomycota_odb10,cyanobacteria_odb10,chlorophyta_odb10,metazoa_odb10,viridiplantae_odb10,fungi_odb10 \
    --taxon ${taxid} --align --outdir ${output_dir}/${sp}/btk_new -w ${work_dir} --mask