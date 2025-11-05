import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Input directory (optional arg)
indir = Path(sys.argv[1])

files = [
    "domain_all.csv",
    "kingdom_all.csv",
    "phylum_all.csv",
    "order_all.csv",
    "family_all.csv",
]

# Keys that define a unique call
BASE_KEYS = [
    "species","tolid","tolid_farm","from","link",
    "phylum","order","family","name","taxid"
]

# Potential lineage columns added by the new script
LINEAGE_CANDIDATES = ["domain_lineage", "kingdom_lineage", "phylum_lineage", "order_lineage"]

def safe_groupby(df: pd.DataFrame, keys, agg_spec):
    """
    Groupby that keeps NaN keys.
    Tries pandas >=1.1 'dropna=False', else falls back to filling NaNs with a sentinel per column.
    """
    try:
        # Preferred: keep NaNs as their own "blank" groups
        return df.groupby(keys, as_index=False, dropna=False).agg(**agg_spec)
    except TypeError:
        # Fallback for old pandas: temporarily fill NaNs with unique sentinels per column
        sentinels = {}
        df_tmp = df.copy()
        for k in keys:
            if df_tmp[k].dtype.kind in "fc":  # numeric sentinel
                s = -9.223372e18  # unlikely float sentinel
            else:
                s = "__NA__SENTINEL__"
            sentinels[k] = s
            df_tmp[k] = df_tmp[k].fillna(s)

        grouped = df_tmp.groupby(keys, as_index=False).agg(**agg_spec)

        # Restore sentinels back to NaN (so they show as blank in CSV)
        for k, s in sentinels.items():
            if grouped[k].dtype.kind in "fc":
                grouped[k] = grouped[k].replace(s, np.nan)
            else:
                grouped[k] = grouped[k].replace(s, np.nan)
        return grouped

def combine_csv(infile: Path):
    print(f"Processing {infile.name}...")
    df = pd.read_csv(infile)

    # Detect lineage columns present in this file
    extra_cols = [c for c in LINEAGE_CANDIDATES if c in df.columns]

    # Build group keys dynamically (base keys + lineage columns)
    key_cols = BASE_KEYS + extra_cols

    # Ensure numeric types
    df["reads"] = pd.to_numeric(df.get("reads"), errors="coerce")
    df["percent"] = pd.to_numeric(df.get("percent"), errors="coerce")


    has_total_reads = "total_reads" in df.columns
    if has_total_reads:
        df["total_reads"] = pd.to_numeric(df.get("total_reads"), errors="coerce")

    # Denominator only where percent > 0; else NaN (prevents 0-denom sums)
    df["denom"] = np.where(df["percent"] > 0, df["reads"] / (df["percent"] / 100.0), np.nan)

    agg_spec = {
        "reads": ("reads", "sum"),
        "total_denom": ("denom", lambda x: x.sum(min_count=1)),
    }

    grouped = safe_groupby(df, key_cols, agg_spec)

    # Safe percent: if denom > 0 compute, else 0.00 (or np.nan if you prefer)
    grouped["percent"] = np.where(
        (grouped["total_denom"].notna()) & (grouped["total_denom"] > 0),
        100.0 * grouped["reads"] / grouped["total_denom"],
        0.0
    ).round(2)

    if has_total_reads:
        # Keep only (species, total_reads) pairs, drop NaNs and duplicates,
        # then sum the remaining distinct totals per species.
        tr = df[["species", "total_reads"]].dropna()
        tr["total_reads"] = pd.to_numeric(tr["total_reads"], errors="coerce")
        tr = tr.dropna()
        tr_unique = tr.drop_duplicates()  # removes repeated same totals within a species
        species_total_reads = (
            tr_unique.groupby("species", dropna=False)["total_reads"]
                     .sum(min_count=1)   # sums distinct totals if multiple exist
                     .to_dict()
        )
        grouped["total_reads"] = grouped["species"].map(species_total_reads).astype("Int64")
    else:
        grouped["total_reads"] = pd.NA

    # Final columns: group keys + metrics
    outcols = key_cols + ["reads", "percent", "total_reads"]
    grouped = grouped[outcols]

    # Optional: stable sort for readability
    sort_cols = ["species","reads","total_reads","percent","name"]
    existing_sort_cols = [c for c in sort_cols if c in grouped.columns]
    grouped = grouped.sort_values(by=existing_sort_cols, ascending=[True, False, False, True, True][:len(existing_sort_cols)])

    outfile = infile.with_name(infile.stem + "_combined.csv")
    grouped.to_csv(outfile, index=False)
    print(f"  → Saved: {outfile.name}\n")

if __name__ == "__main__":
    for fname in files:
        p = indir / fname
        if p.exists():
            combine_csv(p)
        else:
            print(f"Skipping {fname} — not found.")