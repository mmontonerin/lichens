#!/usr/bin/env python3
import os
import sys
import glob
import csv

# Directories
input_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"
out_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/blobtools/samplesheets"

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
            # Capture (sample_name, cram_path) tuples
            for cram in glob.glob(os.path.join(hic_dir, "*.cram")):
                sample_name = os.path.basename(sub)  # e.g. nxBunTrig17
                crams.append((sample_name, cram))
    return sorted(crams)

# Build rows for CSV samplesheet
'''
# Format:
# sample,datatype,datafile,library_layout
# <sample_name>,hic,/path/to/file.cram,PAIRED
# <sample_name>,pacbio,/path/to/file.fasta.gz,SINGLE
'''
def build_rows(pacbio_fastas, hic_crams):
    rows = []

    # Track per-sample counters so every row gets a unique suffix
    # e.g. nxBunTrig17 -> nxBunTrig171, nxBunTrig172, ...
    counters = {}

    def next_name(sample_name):
        counters[sample_name] = counters.get(sample_name, 0) + 1
        return f"{sample_name}{counters[sample_name]}"

    # HiC rows: one row per (sample, cram) pair
    for sample_name, cram_path in hic_crams:
        rows.append({
            "sample": next_name(sample_name),
            "datatype": "hic",
            "datafile": cram_path,
            "library_layout": "PAIRED",
        })

    # PacBio rows: derive sample name from the path
    # Expected structure: .../genomic_data/<sample_name>/pacbio/fasta/<file>.fasta.gz
    for fasta_path in pacbio_fastas:
        parts = fasta_path.split(os.sep)
        try:
            gd_idx = parts.index("genomic_data")
            sample_name = parts[gd_idx + 1]
        except (ValueError, IndexError):
            # Fallback: use the fasta filename stem
            sample_name = os.path.basename(fasta_path).replace(".fasta.gz", "")
        rows.append({
            "sample": next_name(sample_name),
            "datatype": "pacbio",
            "datafile": fasta_path,
            "library_layout": "SINGLE",
        })

    return rows

# Write CSV samplesheet
def write_csv(species_name, rows):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{species_name}_samplesheet.csv")
    fieldnames = ["sample", "datatype", "datafile", "library_layout"]
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out_path

def main(base_dir):
    species_names = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    made = skipped = 0
    for species in sorted(species_names):
        species_dir = os.path.join(base_dir, species)
        genomic_dir = os.path.join(species_dir, "genomic_data")

        if not os.path.isdir(genomic_dir):
            print(f"[SKIP] {species}: no genomic_data/ directory found", file=sys.stderr)
            skipped += 1
            continue

        # Use pacbio find function and skip if no pacbio found
        pacbio_fastas = find_pacbio_fastas(genomic_dir)
        if not pacbio_fastas:
            print(f"[SKIP] {species}: no pacbio/fasta/*.fasta.gz found under genomic_data/*/", file=sys.stderr)
            skipped += 1
            continue

        # Find Hi-C cram files
        hic_crams = find_hic_crams(genomic_dir)

        rows = build_rows(pacbio_fastas, hic_crams)
        out_path = write_csv(species, rows)
        print(f"[OK]  {species}: wrote {out_path} "
              f"(pacbio={len(pacbio_fastas)}"
              f"{'; hic='+str(len(hic_crams)) if hic_crams else ''})")
        made += 1

    print(f"\nDone. Wrote {made} samplesheet(s). Skipped {skipped} folder(s).")

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else input_dir
    main(base)