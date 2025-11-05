import pandas as pd
import sys
from pathlib import Path

# Input directory (optional argument)
indir = Path(sys.argv[1])

# List of combined files
files = [
    "domain_all_combined.csv",
    "kingdom_all_combined.csv",
    "phylum_all_combined.csv",
    "order_all_combined.csv",
    "family_all_combined.csv",
]

def filter_table(infile: Path):
    print(f"Processing {infile.name}...")

    # Read table
    df = pd.read_csv(infile)

    # Ensure numeric
    df["percent"] = pd.to_numeric(df["percent"], errors="coerce")

    # Case-insensitive exact match for "Unclassified" (after trimming)
    name_ci = df["name"].astype(str).str.strip().str.casefold()
    is_unclassified = name_ci == "unclassified"

    # Keep rows that are Unclassified OR percent >= 1
    filtered = df[ is_unclassified | (df["percent"] >= 1) ].copy()

    # Save new file
    outfile = infile.with_name(infile.stem + "_filtered.csv")
    filtered.to_csv(outfile, index=False)
    print(f"  → Saved {outfile.name} ({len(filtered)} rows kept)\n")

if __name__ == "__main__":
    for fname in files:
        infile = indir / fname
        if infile.exists():
            filter_table(infile)
        else:
            print(f"Skipping {fname} — file not found.")
