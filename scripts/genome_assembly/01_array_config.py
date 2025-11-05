import os
import glob

# Base directory containing the species folders with sets of reads inside (categorised)
base_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken2_extracted_reads"

# Output directory for the config files
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/genome_assembly"
os.makedirs(output_dir, exist_ok=True)

# Categories to process
lineages = ["ascomycota", "basidiomycota", "cyanobacteriota", "viridiplantae"]

# Loop over each lineage to create its own config file
for lineage in lineages:
    path = os.path.join(base_dir, "*", f"*_{lineage}.fasta")
    fasta_files = sorted(glob.glob(path))
    
    config_file = os.path.join(output_dir, f"01_array_config_{lineage}.txt")
    
    with open(config_file, 'w') as f:
        for job_number, fasta in enumerate(fasta_files, start=1):
            folder_name = os.path.basename(os.path.dirname(fasta))
            f.write(f"{job_number}\t{folder_name}\t{fasta}\n")
    
    print(f"Created config for {lineage}")
