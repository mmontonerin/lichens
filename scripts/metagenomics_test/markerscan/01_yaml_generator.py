#!/usr/bin/env python3
import os
import sys
import glob
import yaml

# Directories
species_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
metagenome_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
reads_out_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/reads"
out_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/yamls"
db_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/db"


def find_shortname(species):
    """
    Get shortname and reads path from reads_out_base/Species/shortname/reads.fasta.gz
    (created by prep_markerscan_reads.py)
    """
    species_reads_dir = os.path.join(reads_out_base, species)
    if not os.path.isdir(species_reads_dir):
        return None, None
    subdirs = [
        d for d in os.listdir(species_reads_dir)
        if os.path.isdir(os.path.join(species_reads_dir, d))
    ]
    for sub in subdirs:
        reads_file = os.path.join(species_reads_dir, sub, "reads.fasta.gz")
        if os.path.isfile(reads_file):
            return sub, reads_file
    return None, None


def find_metagenome_fasta(species):
    """
    Find assembly fasta at:
    metagenome_base/<species>/assembly/fasta/<species>_metamdbg.contigs.fasta
    """
    fasta_path = os.path.join(
        metagenome_base, species, "assembly", "fasta",
        f"{species}_metamdbg.contigs.fasta"
    )
    if os.path.isfile(fasta_path):
        return fasta_path
    return None


def build_yaml_dict(species, shortname, reads_file, genome_fasta):
    working_dir = os.path.join(metagenome_base, species, "assembly", "markerscan")
    data = {
        "datadir": db_dir,
        "full": 0,
        "genome": genome_fasta,
        "reads": reads_file,
        "sci_name": species.replace("_", " "),
        "shortname": shortname,
        "workingdirectory": working_dir,
    }
    return data


def write_yaml(species, data):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{species}.yaml")
    with open(out_path, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)
    return out_path


def main():
    species_list = [
        d for d in os.listdir(species_base)
        if os.path.isdir(os.path.join(species_base, d))
    ]

    made = skipped = 0

    for species in sorted(species_list):

        # Get shortname and consolidated reads path from prep output
        shortname, reads_file = find_shortname(species)
        if not shortname:
            print(f"[SKIP] {species}: no prepared reads found in {reads_out_base}/{species}/", file=sys.stderr)
            skipped += 1
            continue

        # Get metagenome assembly fasta
        genome_fasta = find_metagenome_fasta(species)
        if not genome_fasta:
            print(f"[SKIP] {species}: no metagenome assembly fasta found at expected path", file=sys.stderr)
            skipped += 1
            continue

        data = build_yaml_dict(species, shortname, reads_file, genome_fasta)
        out_path = write_yaml(species, data)
        print(f"[OK]  {species}: wrote {out_path} (shortname={shortname})")
        made += 1

    print(f"\nDone. Wrote {made} YAML file(s). Skipped {skipped} folder(s).")


if __name__ == "__main__":
    main()