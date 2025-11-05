#!/usr/bin/env python3
import os
import re
import csv
import argparse
from collections import defaultdict

# Standard bins (metabat2/dastool etc.), allowing dot OR underscore between method and bin id
MAIN_PATTERN = re.compile(
    r'^'
    r'(?P<species>.+?)'
    r'_meta[a-z]*_'
    r'(?P<method>[A-Za-z0-9]+)'
    r'[._]'
    r'(?P<binid>\d+)'
    r'_(?:c|comp)(?P<comp>[\d.]+)'
    r'(?:_co[\d.]+)?'
    r'_(?P<rest>.+?)'
    r'\.fa(?:\.gz)?'
    r'$'
)

# Special eukcc "merged" bins: merged.<binid>_cXX[_coYY]_Taxon.fa
MERGED_PATTERN = re.compile(
    r'^'
    r'merged\.(?P<binid>\d+)'
    r'_c(?P<comp>[\d.]+)'
    r'(?:_co[\d.]+)?'
    r'_(?P<rest>.+?)'
    r'\.fa'
    r'$'
)

def parse_filename(fname, species_from_dir=None):
    # Try normal pattern
    m = MAIN_PATTERN.match(fname)
    if m:
        species = m.group('species') or species_from_dir
        method = m.group('method')
        binid = m.group('binid')
        comp = m.group('comp')
        rest = m.group('rest')
        taxonomy = rest.split('_')[-1]
        return {
            "species": species or species_from_dir,
            "binning_method": method,
            "bin_id": binid,
            "completeness": comp,
            "taxonomy": taxonomy
        }

    # Try merged/eukcc pattern
    m2 = MERGED_PATTERN.match(fname)
    if m2:
        binid = m2.group('binid')
        comp = m2.group('comp')
        rest = m2.group('rest')
        taxonomy = rest.split('_')[-1]
        return {
            "species": species_from_dir,      # not present in filename
            "binning_method": "eukcc",        # per your rule
            "bin_id": binid,
            "completeness": comp,
            "taxonomy": taxonomy
        }

    return None

def main():
    ap = argparse.ArgumentParser(description="Extract metagenome bin info into a tidy table.")
    ap.add_argument("--root", required=True,
        help="Path to /lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome")
    ap.add_argument("--out", required=True, help="Output table path (e.g., bins.csv or bins.tsv)")
    ap.add_argument("--sep", default=None, help="Column separator (.csv=',' .tsv='\\t' by default)")
    ap.add_argument("--warn", action="store_true", help="List files that do not match any pattern")
    args = ap.parse_args()

    sep = args.sep if args.sep is not None else ("\t" if args.out.lower().endswith(".tsv") else ",")

    rows = []
    unmatched = []

    # Iterate species
    if os.path.isdir(args.root):
        for species_dirname in sorted(os.listdir(args.root)):
            sp_dir = os.path.join(args.root, species_dirname)
            if not os.path.isdir(sp_dir):
                continue

            bin_sel = os.path.join(sp_dir, "bin_selection")
            if not os.path.isdir(bin_sel):
                continue

            for phylum in sorted(os.listdir(bin_sel)):
                phylum_dir = os.path.join(bin_sel, phylum)
                if not os.path.isdir(phylum_dir):
                    continue

                # Normalize typo
                phylum_norm = "chlorophyta" if phylum.lower() == "chrolophyta" else phylum

                for fname in sorted(os.listdir(phylum_dir)):
                    if not (fname.endswith(".fa") or fname.endswith(".fa.gz")):
                        continue

                    parsed = parse_filename(fname, species_from_dir=species_dirname)
                    if not parsed:
                        unmatched.append(os.path.join(phylum_dir, fname))
                        continue

                    rows.append({
                        "species": parsed["species"],
                        "binning_method": parsed["binning_method"],
                        "bin_id": parsed["bin_id"],
                        "phylum": phylum_norm,
                        "taxonomy": parsed["taxonomy"],
                        "completeness": parsed["completeness"],
                    })

    fieldnames = ["species", "binning_method", "bin_id", "phylum", "taxonomy", "completeness"]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=sep)
        writer.writeheader()
        writer.writerows(rows)

    counts = defaultdict(int)
    for r in rows:
        counts[r["phylum"]] += 1

    print(f"Wrote {len(rows)} rows to {args.out}")
    if counts:
        print("Counts by phylum:")
        for k in sorted(counts):
            print(f"  {k}: {counts[k]}")

    if args.warn and unmatched:
        print("\nUnmatched files:")
        for p in unmatched:
            print("  ", p)

if __name__ == "__main__":
    main()
