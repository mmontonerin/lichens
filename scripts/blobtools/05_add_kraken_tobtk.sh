#!/bin/bash
#BSUB -o ./log/addkraken-%J-output.log
#BSUB -e ./log/addkraken-%J-error.log 
#BSUB -J btk-addkraken
#BSUB -q normal
#BSUB -G team301
#BSUB -n 1
#BSUB -M 5000
#BSUB -W 08:00
#BSUB -R "select[mem>5000] rusage[mem=5000]"

module load conda
conda activate btk

path="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
kraken_path="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/01_kraken_translated_btk"

for sp in ${path}/*
do
    species=$(basename ${sp})
    kraken_btk=${kraken_path}/${species}_metamdbg.contigs_kraken_nt.out_lineage.tsv

    btk_path=${sp}/assembly/btk_nomasking/blobtoolkit/${species}_metamdbg.contigs

    blobtools add --text ${kraken_btk} --text-delimiter "\t" \
        --text-cols contig_id=identifiers,taxid=taxid,superkingdom=superkingdom,phylum=phylum,class=class,order=order,family=family,genus=genus,species=species \
        --text-header ${btk_path}
done