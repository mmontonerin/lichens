#!/usr/bin/env python3
import os
import sys
import math
from collections import Counter
import pandas as pd

input_path  = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
out_mito    = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/alpha_diversity_mitochondria.csv"
out_plastid = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/alpha_diversity_plastid.csv"

# We want at least phylum level — meaning the lineage must have more than
# just the top-level terms above
def parse_lineage(lineage_str):
    """
    Returns dict with keys: domain, phylum, class, order, family, genus, species
    Returns None if lineage is N/A or too shallow (only kingdom/domain level).
    """
    if not lineage_str or lineage_str.strip() in ("N/A", ""):
        return None

    parts = [p.strip() for p in lineage_str.split(";")]

    # Remove universal top terms
    filtered = [p for p in parts if p not in ("cellular organisms",)]

    if len(filtered) < 3:
        # Only domain + kingdom or less — skip
        return None

    # Assign positional ranks loosely:
    # filtered[0] = domain (Eukaryota / Bacteria)
    # filtered[1] = kingdom or phylum depending on domain
    # We just want phylum+ so require at least 3 meaningful terms
    # after stripping "cellular organisms"
    domain  = filtered[0] if len(filtered) > 0 else ""
    # For eukaryotes the lineage often has extra groupings before phylum
    # so we just take last few levels as genus/family/phylum heuristically
    species = filtered[-1] if len(filtered) >= 1 else ""
    genus   = filtered[-2] if len(filtered) >= 2 else ""
    family  = filtered[-3] if len(filtered) >= 3 else ""
    phylum  = filtered[-4] if len(filtered) >= 4 else filtered[1] if len(filtered) >= 2 else ""

    return {
        "domain":  domain,
        "phylum":  phylum,
        "family":  family,
        "genus":   genus,
        "species": species,
    }

def shannon(counts):
    total = sum(counts)
    if total == 0: return 0
    return -sum((c/total) * math.log(c/total) for c in counts if c > 0)

def simpson(counts):
    total = sum(counts)
    if total == 0: return 0
    return 1 - sum((c/total)**2 for c in counts)

def compute_stats(sp, rows):
    if not rows:
        return None
    df = pd.DataFrame(rows)

    phylum_counts = list(Counter(df["phylum"][df["phylum"] != ""]).values())
    family_counts = list(Counter(df["family"][df["family"] != ""]).values())
    genus_counts  = list(Counter(df["genus"] [df["genus"]  != ""]).values())

    return {
        "species":         sp,
        "n_contigs":       len(df),
        "phylum_richness": df["phylum"].nunique(),
        "family_richness": df[df["family"] != ""]["family"].nunique(),
        "genus_richness":  df[df["genus"]  != ""]["genus"].nunique(),
        "shannon_phylum":  round(shannon(phylum_counts), 4),
        "shannon_family":  round(shannon(family_counts), 4),
        "shannon_genus":   round(shannon(genus_counts),  4),
        "simpson_phylum":  round(simpson(phylum_counts), 4),
        "simpson_family":  round(simpson(family_counts), 4),
        "simpson_genus":   round(simpson(genus_counts),  4),
    }

def parse_diamond_file(filepath):
    """Parse a diamond organelle file, return list of parsed lineage dicts."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n\r")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue

            lineage_str = parts[3].strip()
            parsed = parse_lineage(lineage_str)
            if parsed is None:
                continue

            rows.append(parsed)
    return rows

# --- Walk species dirs ---
mito_results    = []
plastid_results = []

for sp in sorted(os.listdir(input_path)):
    sp_dir = os.path.join(input_path, sp)
    if not os.path.isdir(sp_dir):
        continue

    diamond_dir = os.path.join(sp_dir, "assembly", "diamond_organelle")
    if not os.path.isdir(diamond_dir):
        continue

    mito_file    = None
    plastid_file = None

    for fname in os.listdir(diamond_dir):
        if fname.startswith("mitochondrion_"):
            mito_file = os.path.join(diamond_dir, fname)
        elif fname.startswith("plastid_"):
            plastid_file = os.path.join(diamond_dir, fname)

    if mito_file:
        rows = parse_diamond_file(mito_file)
        stats = compute_stats(sp, rows)
        if stats:
            mito_results.append(stats)
            print(f"[mito]    {sp}: {stats['n_contigs']} classified contigs")
        else:
            print(f"[mito]    {sp}: no classified contigs")

    if plastid_file:
        rows = parse_diamond_file(plastid_file)
        stats = compute_stats(sp, rows)
        if stats:
            plastid_results.append(stats)
            print(f"[plastid] {sp}: {stats['n_contigs']} classified contigs")
        else:
            print(f"[plastid] {sp}: no classified contigs")

# --- Save ---
pd.DataFrame(mito_results).sort_values("species").to_csv(out_mito, index=False)
pd.DataFrame(plastid_results).sort_values("species").to_csv(out_plastid, index=False)
print(f"\nSaved: {out_mito}")
print(f"Saved: {out_plastid}")