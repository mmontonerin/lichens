#!/bin/bash
#BSUB -J markerscan[1-38]
#BSUB -o ./log/markerscan-%J-%I.out
#BSUB -e ./log/markerscan-%J-%I.err
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 32000
#BSUB -R "select[mem>32000] rusage[mem=32000]"

##############################################
# MarkerScan LSF Wrapper
##############################################

# -------- SETTINGS --------
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/01c_array_config.txt"
THREADS=8
SIF_FILE="/lustre/scratch127/tol/teams/blaxter/users/jm77/scripts/MarkerScan/markerscan_pr-15.sif"
# ------------------------------------------------------

# Set NCBI API key here
export NCBI_API_KEY="e0debbca6075e7ea2479da0a4db952fffc09"

# Pass it into the Singularity container
export SINGULARITYENV_NCBI_API_KEY=${NCBI_API_KEY}
# -------------------------------------

# 1. Bind project folder so the container can see it
export SINGULARITY_BIND="/lustre:/lustre,/software/treeoflife/conda:/software/treeoflife/conda"

# Array yamls
yaml=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})
sp=$(basename ${yaml} ".yaml")

export TMPDIR=/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/tmp
mkdir -p ${TMPDIR}/${sp}_${LSB_JOBINDEX}
export SINGULARITYENV_TMPDIR=${TMPDIR}/${sp}_${LSB_JOBINDEX}
export SINGULARITYENV_TEMP=${TMPDIR}/${sp}_${LSB_JOBINDEX}
export SINGULARITYENV_TMP=${TMPDIR}/${sp}_${LSB_JOBINDEX}

# 2. Run MarkerScan inside the container
singularity exec \
  ${SIF_FILE} snakemake \
  --cores ${THREADS} \
  --use-conda \
  --conda-prefix /opt/conda/envs \
  -s /Marker_pipeline/Snakefile \
  --configfile ${yaml} \
  --latency-wait 60