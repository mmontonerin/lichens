#!/usr/bin/env python3
import argparse
import os
import sys
import glob
import pandas as pd

# Columns in Kraken2 report
COLS = ["percent", "reads", "taxon_reads", "rank_code", "taxid", "name"]

# Exact ranks we export
VALID_RANKS = {
    "D": "domain",
    "K": "kingdom",
    "P": "phylum",
    "O": "order",
    "F": "family",
}

# Lineage columns derived from the report itself
LINEAGE_COLS = ["domain_lineage", "kingdom_lineage", "phylum_lineage", "order_lineage"]

def load_report(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", header=None, names=COLS, dtype=str, engine="python")

    df["name"] = df["name"].astype(str).str.strip()
    for col in ("percent", "reads", "taxon_reads", "taxid"):
        if col == "percent":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")
    df["rank_code"] = df["rank_code"].astype(str)

    for c in LINEAGE_COLS:
        df[c] = None

    current = {c: None for c in LINEAGE_COLS}
    for i, row in df.iterrows():
        rk = row["rank_code"]
        name = row["name"]
        if rk == "D":
            current["domain_lineage"] = name
            current["kingdom_lineage"] = None
            current["phylum_lineage"] = None
            current["order_lineage"] = None
        elif rk == "K":
            current["kingdom_lineage"] = name
            current["phylum_lineage"] = None
            current["order_lineage"] = None
        elif rk == "P":
            current["phylum_lineage"] = name
            current["order_lineage"] = None
        elif rk == "O":
            current["order_lineage"] = name
        for c in LINEAGE_COLS:
            df.at[i, c] = current[c]
    return df

def filter_exact_rank(df: pd.DataFrame, rank_letter: str) -> pd.DataFrame:
    base_cols = ["name", "reads", "percent", "taxid"]
    if rank_letter == "D":
        extras = []
    elif rank_letter == "K":
        extras = ["domain_lineage"]
    elif rank_letter == "P":
        extras = ["domain_lineage", "kingdom_lineage"]
    elif rank_letter == "O":
        extras = ["domain_lineage", "kingdom_lineage", "phylum_lineage"]
    elif rank_letter == "F":
        extras = ["domain_lineage", "kingdom_lineage", "phylum_lineage", "order_lineage"]
    else:
        extras = []
    cols = base_cols + extras
    sub = df.loc[df["rank_code"] == rank_letter, cols].copy()
    if not sub.empty:
        sub = sub.sort_values(by=["reads", "percent", "name"], ascending=[False, False, True])
    return sub

def compute_total_reads(df: pd.DataFrame) -> tuple[int, int, int]:
    root_reads = df.loc[(df["rank_code"] == "R") & (df["taxid"] == 1), "reads"]
    root_reads = int(root_reads.max()) if not root_reads.empty else 0
    unclassified_reads = int(df.loc[df["rank_code"] == "U", "reads"].sum() or 0)
    total_reads = root_reads + unclassified_reads
    return total_reads, root_reads, unclassified_reads

def infer_tolid_farm(filename_base: str) -> str:
    if "_" in filename_base:
        return filename_base.split("_", 1)[0]
    return filename_base

def _placeholder_row(meta_row: dict, tolid_farm: str, extras_cols: list[str], total_reads: int) -> pd.DataFrame:
    """
    Create a single-row dataframe with reads=0/percent=0 for samples that have no classified rows at a rank.
    """
    base = {
        "species":     meta_row.get("species"),
        "tolid":       meta_row.get("tolid"),
        "tolid_farm":  tolid_farm,
        "from":        meta_row.get("from"),
        "link":        meta_row.get("link"),
        "phylum":      meta_row.get("phylum"),
        "order":       meta_row.get("order"),
        "family":      meta_row.get("family"),
        "name":        "Unclassified",
        "reads":       0,
        "total_reads": total_reads,
        "percent":     0.0,
        "taxid":       0,
    }
    # add lineage extras as blank (NaN)
    for c in extras_cols:
        base[c] = pd.NA
    return pd.DataFrame([base])

def main():
    ap = argparse.ArgumentParser(
        description="Merge Kraken reports with lichens metadata and build rank-wide CSVs (D/K/P/O/F) with lineage columns."
    )
    ap.add_argument("-d", "--dir", required=True, help="Directory containing *.nt_report.out files.")
    ap.add_argument("-m", "--metadata", required=True, help="Path to lichens.csv metadata file.")
    ap.add_argument("-o", "--outdir", default=None, help="Output directory for the combined CSVs (default: same as --dir).")
    args = ap.parse_args()

    in_dir = os.path.abspath(args.dir)
    out_dir = os.path.abspath(args.outdir or in_dir)

    # Metadata
    try:
        meta = pd.read_csv(args.metadata, dtype=str)
    except Exception as e:
        print(f"[ERROR] Failed to read metadata: {e}", file=sys.stderr)
        sys.exit(1)

    rank_tables = {rk: [] for rk in VALID_RANKS.keys()}

    report_glob = os.path.join(in_dir, "*.nt_report.out")
    report_paths = sorted(glob.glob(report_glob))
    if not report_paths:
        print(f"[WARN] No files matched: {report_glob}", file=sys.stderr)

    for rpt in report_paths:
        base = os.path.basename(rpt)
        base_noext = base[:-len(".nt_report.out")] if base.endswith(".nt_report.out") else os.path.splitext(base)[0]

        # Metadata row matched by tolid in filename
        candidates = meta[meta["tolid"].apply(lambda t: isinstance(t, str) and t in base)]
        if candidates.empty:
            print(f"[WARN] No metadata row found for file: {base}", file=sys.stderr)
            continue
        row = candidates.iloc[0].to_dict()
        tolid_farm = infer_tolid_farm(base_noext)

        # Read report + totals
        try:
            df = load_report(rpt)
        except Exception as e:
            print(f"[WARN] Skipping {base} due to read/parse error: {e}", file=sys.stderr)
            continue

        total_reads, root_reads, unclassified_reads = compute_total_reads(df)

        # Build each rank table, injecting placeholder rows if needed
        for rk, label in VALID_RANKS.items():
            sub = filter_exact_rank(df, rk)

            # figure out lineage extras for this rank (must match final_cols order)
            if rk == "D":
                extras = []
            elif rk == "K":
                extras = ["domain_lineage"]
            elif rk == "P":
                extras = ["domain_lineage", "kingdom_lineage"]
            elif rk == "O":
                extras = ["domain_lineage", "kingdom_lineage", "phylum_lineage"]
            else:  # F
                extras = ["domain_lineage", "kingdom_lineage", "phylum_lineage", "order_lineage"]

            if sub.empty:
                # make a single placeholder row so the sample still appears
                sub = _placeholder_row(row, tolid_farm, extras, total_reads)
            else:
                # attach metadata to each classified row
                sub.insert(0, "family", row.get("family"))
                sub.insert(0, "order", row.get("order"))
                sub.insert(0, "phylum", row.get("phylum"))
                sub.insert(0, "link", row.get("link"))
                sub.insert(0, "from", row.get("from"))
                sub.insert(0, "tolid_farm", tolid_farm)
                sub.insert(0, "tolid", row.get("tolid"))
                sub.insert(0, "species", row.get("species"))
                sub["total_reads"] = total_reads  # add totals to real rows too

            final_cols = ["species","tolid","tolid_farm","from","link","phylum","order","family",
                          "name","reads","total_reads","percent","taxid"] + extras
            sub = sub.reindex(columns=final_cols)

            rank_tables[rk].append(sub)

    os.makedirs(out_dir, exist_ok=True)
    for rk, label in VALID_RANKS.items():
        parts = rank_tables.get(rk, [])
        if parts:
            combined = pd.concat(parts, ignore_index=True)
            if not combined.empty:
                combined = combined.sort_values(
                    by=["species","reads","percent","name"],
                    ascending=[True, False, False, True]
                )
                out_path = os.path.join(out_dir, f"{label}_all.csv")
                combined.to_csv(out_path, index=False)
                print(f"[OK] Wrote {out_path} ({len(combined)} rows)")
                continue
        print(f"[INFO] No rows for rank {label}; nothing written.", file=sys.stderr)

if __name__ == "__main__":
    main()
