#!/usr/bin/env python3
import sys, csv, gzip, glob, os
from pathlib import Path

# Root with species genomic data
BASE_DIR = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/data/lichens_genomicdata"

# Cache totals across files so we don't recount the same species repeatedly
_SPECIES_TOTAL_CACHE = {}

def count_bases_in_fasta_gz(path):
    """Stream a .fasta.gz and count non-header, non-whitespace characters."""
    total = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.startswith(">"):
                continue
            # remove whitespace and count remaining characters
            total += len("".join(line.split()))
    return total

def species_total_bases(species):
    """Sum bases across all matching PacBio FASTA.gz files for one species."""
    if species in _SPECIES_TOTAL_CACHE:
        return _SPECIES_TOTAL_CACHE[species]

    pattern = os.path.join(
        BASE_DIR, species, "genomic_data", "g*", "pacbio", "fasta", "*fasta.gz"
    )
    files = glob.glob(pattern)
    total = 0
    for fp in files:
        try:
            total += count_bases_in_fasta_gz(fp)
        except Exception as e:
            print(f"[warn] Skipping {fp}: {e}", file=sys.stderr)

    _SPECIES_TOTAL_CACHE[species] = total
    return total

def filter_table(infile: Path):
    """Read CSV, add total_bases per species, write <filename>_bp.csv."""
    # Read all rows
    with infile.open(newline="") as f:
        rdr = csv.reader(f)
        rows = list(rdr)

    if not rows:
        print(f"[warn] {infile.name} is empty; skipping.", file=sys.stderr)
        return

    header = rows[0]
    data = rows[1:]

    # Find 'species' column (fallback to first column)
    try:
        species_idx = header.index("species")
    except ValueError:
        species_idx = 0  # as per your example

    # Prepare output
    out_header = header + ["total_bases"]
    outfile = infile.with_name(infile.stem + "_bp.csv")

    # Compute per-species totals once per file (cache persists across files)
    species_set = {r[species_idx] for r in data if r and len(r) > species_idx}
    for sp in sorted(species_set):
        tb = species_total_bases(sp)
        print(f"[info] {sp}: {tb} bases", file=sys.stderr)

    with outfile.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(out_header)
        for r in data:
            sp = r[species_idx]
            w.writerow(r + [ _SPECIES_TOTAL_CACHE.get(sp, 0) ])

    print(f"Wrote {outfile}", file=sys.stderr)

# ----- Driver (your format) -----
# Input directory (optional argument)
indir = Path(sys.argv[1])

# List of combined files
files = [
    "domain_all_combined_filtered.csv",
    "kingdom_all_combined_filtered.csv",
    "phylum_all_combined_filtered.csv",
    "order_all_combined_filtered.csv",
    "family_all_combined_filtered.csv",
]

if __name__ == "__main__":
    for fname in files:
        infile = indir / fname
        if infile.exists():
            filter_table(infile)
        else:
            print(f"Skipping {fname} — file not found.")
