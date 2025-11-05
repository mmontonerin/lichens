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

input_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

module load conda
conda activate eukcc

export TAXONKIT_DB="/data/tol/resources/taxonomy/latest/new_taxdump"

#for path in ${input_dir}/*/bins/taxonomy_eukcc
for path in ${input_dir}/Xanthoria_parietina/bins/taxonomy_eukcc ${input_dir}/Cystocoleus_ebeneus/bins/taxonomy_eukcc 
do  
    in=${path}/eukcc.csv
    out=${path}/eukcc_lineage_names.csv

    # make header
    { IFS= read -r header
    printf "%s\t%s\n" "${header}" "lineage_names"
  
    # for each row: extract last taxid, fetch lineage names, and paste back
    # 1) grab the ncbi_lng column (4th), split on '-', take last field (leaf taxid)
    # 2) taxonkit lineage gives "taxid\tlineage" (names); cut to lineage only
    # 3) paste lineage back to the original row
    awk -F'\t' 'NR>1{print $0}' "${in}" \
    | paste -d'\t' - <(
        cut -f4 "${in}" | awk -F'\t' 'NR>1{print $1}' \
        | awk -F'-' '{print $NF}' \
        | taxonkit lineage --show-name \
        | cut -f2
        )
    } < "${in}" > "${out}"
done    