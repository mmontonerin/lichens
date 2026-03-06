#!/usr/bin/env python3
import os
import sys
import math
from collections import Counter
import pandas as pd

input_path = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
output_csv = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bacterial_alpha_diversity.csv"

# --- Alpha diversity functions ---
def shannon(counts):
    total = sum(counts)
    if total == 0: return 0
    return -sum((c/total) * math.log(c/total) for c in counts if c > 0)

def simpson(counts):
    total = sum(counts)
    if total == 0: return 0
    return 1 - sum((c/total)**2 for c in counts)

# --- Parse all species ---
results = []

for sp in sorted(os.listdir(input_path)):
    sp_dir = os.path.join(input_path, sp)
    if not os.path.isdir(sp_dir):
        continue

    tax_dir = os.path.join(sp_dir, "bins", "taxonomy")
    table   = os.path.join(tax_dir, f"gtdbtk.{sp}.bac120.summary.tsv")

    if not os.path.isfile(table):
        continue

    bins = []  # list of dicts per dastool bin

    with open(table, "r", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n\r")
        if not header:
            continue
        cols = header.split("\t")
        try:
            i_bin  = cols.index("user_genome")
            i_comp = cols.index("msa_percent")
            i_lin  = cols.index("classification")
        except ValueError:
            print(f"ERROR: Missing expected columns in {table}", file=sys.stderr)
            continue

        for line in fh:
            line = line.rstrip("\n\r")
            if not line:
                continue
            parts = line.split("\t")

            bin_name = parts[i_bin].strip()
            if "dastool" not in bin_name.lower():
                continue

            lineage = parts[i_lin].strip()

            # Parse ranks into dict
            ranks = {}
            for tok in lineage.split(";"):
                tok = tok.strip()
                if "__" in tok:
                    r, v = tok.split("__", 1)
                    ranks[r] = v

            phylum = ranks.get("p", "").strip()
            genus  = ranks.get("g", "").strip()
            family = ranks.get("f", "").strip()

            if not phylum:
                continue

            bins.append({
                "bin":    bin_name,
                "phylum": phylum,
                "family": family,
                "genus":  genus,
            })

    if not bins:
        continue

    df = pd.DataFrame(bins)

    # compute counts at each rank
    phylum_counts = list(Counter(df["phylum"]).values())
    family_counts = list(Counter(df["family"][df["family"] != ""]).values())
    genus_counts  = list(Counter(df["genus"][df["genus"]  != ""]).values())

    results.append({
        "species":          sp,
        "n_bins":           len(df),
        # richness
        "phylum_richness":  df["phylum"].nunique(),
        "family_richness":  df[df["family"] != ""]["family"].nunique(),
        "genus_richness":   df[df["genus"]  != ""]["genus"].nunique(),
        # shannon
        "shannon_phylum":   round(shannon(phylum_counts), 4),
        "shannon_family":   round(shannon(family_counts), 4),
        "shannon_genus":    round(shannon(genus_counts),  4),
        # simpson
        "simpson_phylum":   round(simpson(phylum_counts), 4),
        "simpson_family":   round(simpson(family_counts), 4),
        "simpson_genus":    round(simpson(genus_counts),  4),
    })

df_out = pd.DataFrame(results).sort_values("species")
df_out.to_csv(output_csv, index=False)
print(f"Saved: {output_csv}")
print(df_out.to_string(index=False))