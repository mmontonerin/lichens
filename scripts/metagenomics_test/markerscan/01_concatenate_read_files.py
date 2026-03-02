#!/usr/bin/env python3
import os
import sys
import glob
import subprocess

# Directories
reads_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
reads_out_base = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_test/markerscan/reads"


def find_pacbio_fastas(genomic_dir):
    """Find all pacbio fasta.gz files under genomic_data/*/pacbio/fasta/"""
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


def find_shortname(genomic_dir):
    """Get shortname from genomic_data/<shortname>/pacbio/"""
    subdirs = [
        d for d in os.listdir(genomic_dir)
        if os.path.isdir(os.path.join(genomic_dir, d))
    ]
    for sub in subdirs:
        pacbio_dir = os.path.join(genomic_dir, sub, "pacbio")
        if os.path.isdir(pacbio_dir):
            return sub
    return None


def prepare_reads(species, shortname, fastas, out_base):
    """Copy or concatenate reads into reads_out_base/Species/shortname/reads.fasta.gz"""
    out_dir = os.path.join(out_base, species, shortname)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "reads.fasta.gz")

    if os.path.exists(out_file):
        print(f"[SKIP] {species}: {out_file} already exists, skipping.")
        return out_file

    if len(fastas) == 1:
        print(f"[COPY] {species}: copying {fastas[0]} -> {out_file}")
        subprocess.run(["cp", fastas[0], out_file], check=True)
    else:
        print(f"[CAT]  {species}: concatenating {len(fastas)} files -> {out_file}")
        part_file = out_file + ".part"
        with open(part_file, "wb") as out_fh:
            for f in fastas:
                with open(f, "rb") as in_fh:
                    out_fh.write(in_fh.read())
        os.rename(part_file, out_file)

    return out_file


def main(base_dir=reads_base):
    species_list = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    done = skipped = failed = 0

    for species in sorted(species_list):
        genomic_dir = os.path.join(base_dir, species, "genomic_data")

        if not os.path.isdir(genomic_dir):
            print(f"[SKIP] {species}: no genomic_data/ folder found", file=sys.stderr)
            skipped += 1
            continue

        fastas = find_pacbio_fastas(genomic_dir)
        if not fastas:
            print(f"[SKIP] {species}: no pacbio/fasta/*.fasta.gz found", file=sys.stderr)
            skipped += 1
            continue

        shortname = find_shortname(genomic_dir)
        if not shortname:
            print(f"[SKIP] {species}: could not determine shortname", file=sys.stderr)
            skipped += 1
            continue

        try:
            out_file = prepare_reads(species, shortname, fastas, reads_out_base)
            print(f"         -> {out_file}")
            done += 1
        except Exception as e:
            print(f"[ERROR] {species}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nDone. Prepared {done} sample(s). Skipped {skipped}. Failed {failed}.")


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else reads_base
    main(base)