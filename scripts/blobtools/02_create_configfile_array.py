import glob
import os
import csv

# Folder with the yaml files
samplesheet_files = glob.glob("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/samplesheets/*.csv")

config_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/03_array_config.txt"

assembly_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

metadata_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/lichens_taxid.csv"

# Create config file with the following format:
# 1 Species_name /path/to/csv1 /path/to/assembly1 taxonid1
# 2 Species_name /path/to/csv2 /path/to/assembly2 taxonid2
# ...

# Load taxon IDs from metadata: {Species_name: taxon_id}
taxon_ids = {}
with open(metadata_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        taxon_ids[row["species"]] = row["taxon"]

with open(config_file, 'w') as f:
    for job_number, csv in enumerate(samplesheet_files, start=1):
        # Extract Species_name from filename: Species_name_samplesheet.csv -> Species_name
        basename = os.path.basename(csv)                      # Species_name_samplesheet.csv
        species_name = basename.replace("_samplesheet.csv", "")  # Species_name

        assembly = f"{assembly_base}/{species_name}/assembly/fasta/{species_name}_metamdbg.contigs.fasta.gz"

        taxon_id = taxon_ids.get(species_name, "NA")

        f.write(f"{job_number} {species_name} {csv} {assembly} {taxon_id}\n")

print(f"Config written to {config_file}")