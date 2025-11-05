#!/usr/bin/env python3
import os
import sys
import glob
import yaml

# Directories
input_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
out_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/yamls"

# Find directories with pacbio data - fasta files
def find_pacbio_fastas(genomic_dir):
    fastas = []
    subdirs = [
        os.path.join(genomic_dir, d)
        for d in os.listdir(genomic_dir)
        if os.path.isdir(os.path.join(genomic_dir, d))
    ]
    for sub in subdirs:
        fasta_dir = os.path.join(sub, "pacbio", "fasta")
        if os.path.isdir(fasta_dir):
            fastas.extend(glob.glob(os.path.join(fasta_dir, "*.fasta.gz")))
    return sorted(fastas)

# Find directories with hi-c data - cram files
def find_hic_crams(genomic_dir):
    crams = []
    subdirs = [
        os.path.join(genomic_dir, d)
        for d in os.listdir(genomic_dir)
        if os.path.isdir(os.path.join(genomic_dir, d))
    ]
    for sub in subdirs:
        hic_dir = os.path.join(sub, "hic-arima2")
        if os.path.isdir(hic_dir):
            crams.extend(glob.glob(os.path.join(hic_dir, "*.cram")))
    return sorted(crams)

# Build yaml dictionary for config file
'''
# Example yaml file shown in: https://pipelines.tol.sanger.ac.uk/metagenomeassembly
# Hi-C data is optional
# Enzymes from datasets "hic-arima2" are always
    - DpnII
    - HinfI
    - DdeI
    - MseI
'''
'''
id: SampleName
pacbio:
  fasta:
    - /path/to/pacbio/file1.fasta.gz
    - /path/to/pacbio/file2.fasta.gz
    - ...
hic:
  cram:
    - /path/to/hic/hic1.cram
    - /path/to/hic/hic2.cram
    - ...
  enzymes:
    - enzyme_name_1 (e.g. DpnII)
    - enzyme_name_1 (e.g. HinfI)
    - ...
'''

def build_yaml_dict(sample_name, pacbio_fastas, hic_crams):
    data = {
        "id": sample_name,
        "pacbio": {"fasta": pacbio_fastas},
    }
    if hic_crams:
        data["hic"] = {
            "cram": hic_crams, 
            "enzymes": ("DpnII", "HinfI", "DdeI", "MseI")
        }
    return data

# Create the yaml file
def write_yaml(sample_name, data):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{sample_name}.yaml")
    with open(out_path, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)
    return out_path

# Get lichen names from the directories to be SampleName, as well as SampleName.yaml
# Look for pacbio folders and add those file paths to the yaml
# If there is Hi-C data, add those file paths to the yaml
def main(base_dir):
    lichen_names = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    made = skipped = 0
    for lichen in sorted(lichen_names):
        lichen_dir = os.path.join(base_dir, lichen)
        genomic_dir = os.path.join(lichen_dir, "genomic_data")

        # Use pacbio find function and skip if no pacbio found
        pacbio_fastas = find_pacbio_fastas(genomic_dir)
        if not pacbio_fastas:
            print(f"[SKIP] {lichen}: no pacbio/fasta/*.fasta.gz found under genomic_data/*/", file=sys.stderr)
            skipped += 1
            continue

        # Find Hi-C cram files if pacbio files were present
        hic_crams = find_hic_crams(genomic_dir)
        data = build_yaml_dict(lichen, pacbio_fastas, hic_crams)
        out_path = write_yaml(lichen, data)
        print(f"[OK]  {lichen}: wrote {out_path} (pacbio={len(pacbio_fastas)}"
              f"{'; hic='+str(len(hic_crams)) if hic_crams else ''})")
        made += 1

    print(f"\nDone. Wrote {made} YAML file(s). Skipped {skipped} folder(s).")

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else input_dir
    main(base)
