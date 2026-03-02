#!/bin/bash
#BSUB -o ./log/eukbin-%J-%I-output.log
#BSUB -e ./log/eukbin-%J-%I-error.log 
#BSUB -J eukbin[1-38]
#BSUB -q long
#BSUB -G team301
#BSUB -n 8
#BSUB -W 48:00
#BSUB -M 40000
#BSUB -R "select[mem>40000] rusage[mem=40000]"

shopt -s nullglob
module load conda
conda activate eukbin

data="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
path_config="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/04_array_config.txt"

sp=$(awk -v line=${LSB_JOBINDEX} 'NR==line {print $2}' ${path_config})

out=${sp}/bins/fasta/eukbin
mkdir -p ${out}

species=$(basename ${sp})
assembly_folder=${sp}/assembly
assembly=${assembly_folder}/fasta/${species}_metamdbg.contigs.fasta.gz
assembly_fa=${assembly_folder}/fasta/${species}_metamdbg.contigs.fasta

gunzip -kc ${assembly} > ${assembly_fa}

filename=$(basename ${assembly} ".contigs.fasta.gz")

# Tiara has complete contig names, including spaces, which causes an error
tiara_in=${assembly_folder}/tiara/tiara_out.txt
tiara_fixed=${assembly_folder}/tiara/tiara_out.eukbin.tsv

awk -F'\t' 'BEGIN{OFS="\t"}
NR==1 {print; next}
{
  # Normalize contig id (first token)
  split($1, a, " ");
  $1 = a[1];

  fst = tolower($2);
  snd = tolower($3);

  # Rewrite class_fst_stage to what EukBin expects
  if (fst == "eukarya")            $2 = "euk";
  else if (fst == "bacteria")      $2 = "bac";
  else if (fst == "archaea")       $2 = "arc";
  else if (fst == "organelle") {
    if (snd ~ /mitochond/)         $2 = "mit";
    else if (snd ~ /plastid/)      $2 = "pla";
    else                           $2 = "org";  # fallback
  } else if (fst ~ /^unk/)         $2 = "unk";
  else                             $2 = fst;

  print
}' ${tiara_in} > ${tiara_fixed}     

python -m eukbin run --fasta ${assembly_fa} \
    --depth ${assembly_folder}/depth/${filename}_depth.tsv \
    --busco ${assembly_folder}/busco/${filename}.contigs/run_eukaryota_odb10/full_table.tsv \
    --tiara ${tiara_fixed} \
    --gff ${assembly_folder}/prodigal/${filename}.contigs_prodigal.gff \
    --out ${out} --threads 8
