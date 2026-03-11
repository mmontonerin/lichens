#!/bin/bash
#BSUB -o ./log/taxonid-%J-output.log
#BSUB -e ./log/taxonid-%J-error.log 
#BSUB -J taxonid
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -W 12:00
#BSUB -M 25000
#BSUB -R "select[mem>25000] rusage[mem=25000]"

input_csv="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db/13059_2020_2155_MOESM2_ESM.csv"
output_csv="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/db/13059_2020_2155_MOESM2_ESM_translated.csv"

module load conda
conda activate eukcc

export TAXONKIT_DB="/data/tol/resources/taxonomy/latest/new_taxdump"

# make header
{ IFS= read -r header
  printf "%s,lineage_names\n" "${header}"

  # for each data row: extract tax_id (2nd column), look up lineage, paste back
  awk -F',' 'NR>1{print $0}' "${input_csv}" \
  | paste -d',' - <(
      awk -F',' 'NR>1{print $2}' "${input_csv}" \
      | taxonkit lineage --show-name \
      | cut -f2
  )
} < "${input_csv}" > "${output_csv}"