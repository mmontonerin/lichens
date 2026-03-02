#!/bin/bash
#BSUB -J markerscan
#BSUB -o markerscan-%J.out
#BSUB -e markerscan-%J.err
#BSUB -q normal
#BSUB -G team301
#BSUB -n 8
#BSUB -M 32000
#BSUB -R "select[mem>32000] rusage[mem=32000]"

##############################################
# MarkerScan LSF Wrapper
##############################################

# -------- SETTINGS --------
PROJECT_DIR="/lustre/scratch127/tol/teams/blaxter/users/jm77/results/markerscan_outputs"
CONFIG_FILE="/lustre/scratch127/tol/teams/blaxter/users/jm77/scripts/MarkerScan/yamls/icCliFoss2.yaml"
THREADS=8
SIF_FILE="/lustre/scratch127/tol/teams/blaxter/users/jm77/scripts/MarkerScan/markerscan_pr-15.sif"
# ------------------------------------------------------

# Set NCBI API key here
export NCBI_API_KEY="e0debbca6075e7ea2479da0a4db952fffc09"

# Pass it into the Singularity container
export SINGULARITYENV_NCBI_API_KEY=${NCBI_API_KEY}
# -------------------------------------

export TMPDIR=/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/tmp
mkdir -p ${TMPDIR}
export SINGULARITYENV_TMPDIR=${TMPDIR}
export SINGULARITYENV_TEMP=${TMPDIR}
export SINGULARITYENV_TMP=${TMPDIR}


# 1. Bind project folder so the container can see it
export SINGULARITY_BIND="/lustre:/lustre,/software/treeoflife/conda:/software/treeoflife/conda"


# 2. Run MarkerScan inside the container
singularity exec \
  "$SIF_FILE" snakemake \
  --cores "$THREADS" \
  --use-conda \
  --conda-prefix /opt/conda/envs \
  -s /Marker_pipeline/Snakefile \
  --configfile "$CONFIG_FILE" \
  --latency-wait 60 \
  >> markerscan_output-${LSB_JOBID}.log 2>&1