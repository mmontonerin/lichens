import os
import glob
from collections import defaultdict

data_dir="/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"

config_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/markadoros/01_array_config.txt"


sp_total = defaultdict(int)
for lichen in sorted(glob.glob(f"{data_dir}/*")):
    for dataset in sorted(glob.glob(f"{lichen}/genomic_data/g*")):
        sp_total[os.path.basename(lichen)] += len(glob.glob(f"{dataset}/pacbio/fasta/*.fasta.gz"))


entries = []
sp_num = defaultdict(int)

for lichen in sorted(glob.glob(f"{data_dir}/*")):
    if not os.path.isdir(lichen):
        continue
    sp = os.path.basename(lichen)

    for dataset in sorted(glob.glob(f"{lichen}/genomic_data/g*")):
        if not os.path.isdir(dataset):
            continue

        fasta_files = sorted(glob.glob(f"{dataset}/pacbio/fasta/*.fasta.gz"))
        if not fasta_files:
            continue

        for fasta in fasta_files:
            sp_num[sp] += 1
            sp_label = f"{sp}{sp_num[sp]}" if sp_total[sp] > 1 else sp
            entries.append((sp_label, fasta))

with open(config_file, 'w') as f:
    for job_number, (sp_label, fasta_path) in enumerate(entries, start=1):
        f.write(f"{job_number} {sp_label} {fasta_path}\n")
