#!/bin/bash
#BSUB -o ./log/kraken-btk-%J-output.log
#BSUB -e ./log/kraken-btk-%J-error.log 
#BSUB -J kraken-btk
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -W 12:00
#BSUB -M 25000
#BSUB -R "select[mem>25000] rusage[mem=25000]"
 
module load conda
conda activate eukcc
 
export TAXONKIT_DB="/data/tol/resources/taxonomy/latest/new_taxdump"
 
INDIR="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/01_nt_reports_metagenomes"
OUTDIR="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/01_kraken_translated_btk"
 
mkdir -p "$OUTDIR"
 
for INPUT in "$INDIR"/*nt.out; do
    SAMPLE=$(basename "$INPUT" .nt.out)
    OUTPUT="$OUTDIR/${SAMPLE}_lineage.tsv"
 
    echo "Processing $SAMPLE..."
 
    awk '$1 == "C" {print $2 "\t" $3}' "$INPUT" > /tmp/ctg_taxid.tsv
 
    # sort -u before taxonkit to avoid duplicate lineage rows per taxid
    cut -f2 /tmp/ctg_taxid.tsv \
        | sort -u \
        | taxonkit lineage \
        | taxonkit reformat --fill-miss-rank --format "{k}\t{p}\t{c}\t{o}\t{f}\t{g}\t{s}" -I 1 \
        | cut -f1,3- \
        > /tmp/taxid_lineage.tsv
 
    echo -e "contig_id\ttaxid\tsuperkingdom\tphylum\tclass\torder\tfamily\tgenus\tspecies" > "$OUTPUT"
 
    join -t $'\t' -1 2 -2 1 \
        <(sort -t $'\t' -k2 /tmp/ctg_taxid.tsv) \
        <(sort -t $'\t' -k1 /tmp/taxid_lineage.tsv) \
        | awk -F'\t' '{print $2 "\t" $1 "\t" $3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9}' \
        >> "$OUTPUT"
done
 