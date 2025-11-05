#!/usr/bin/env python3
import os
import sys

input_path = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
output_subdir = "bin_selection"  # to be created under each species folder

# To search on lineage section of the table
lineages = { "cyanobacteriota": "cyanobacteriota"}

def fix_spaces(s: str) -> str:
    # Some lineages/sp have spaces, which we do not want as filename
    return s.replace(" ", "_")


for sp in sorted(os.listdir(input_path)):
    sp_dir = os.path.join(input_path, sp)
    if not os.path.isdir(sp_dir):
        continue
    
    # Build paths
    tax_dir   = os.path.join(sp_dir, "bins", "taxonomy")
    table = os.path.join(tax_dir, f"gtdbtk.{sp}.bac120.summary.tsv")
    dastool  = os.path.join(sp_dir, "bins", "fasta", "dastool")
    out_base  = os.path.join(sp_dir, "bin_selection")

    if not os.path.isfile(table):
        # species without the table -> skip
        continue

    # Create output dirs
    out_dirs = {b: os.path.join(out_base, b) for b in lineages}
    for d in out_dirs.values():
        os.makedirs(d, exist_ok=True)

    with open(table, "r", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n\r")
        if not header:
            continue
        cols = header.split("\t")
        try:
            i_bin = cols.index("user_genome")
            i_comp = cols.index("msa_percent")
            i_lin = cols.index("classification")
        except ValueError:
            print(f"ERROR: Missing expected columns in {table}", file=sys.stderr)
            continue

        for line in fh:
            line = line.rstrip("\n\r")
            if not line:
                continue
            parts = line.split("\t")

            bin_name = parts[i_bin].strip()
            # only keep bins that include "dastool" in the name
            if "dastool" not in bin_name.lower():
                continue

            comp = parts[i_comp].strip()  # completeness (string keeps original precision)
            lineage = parts[i_lin].strip()

            # Parse ranks into dict like {'p': 'Cyanobacteriota', 'f': 'Chroococcidiopsidaceae', ...}
            ranks = {}
            for tok in lineage.split(";"):
                tok = tok.strip()
                if "__" in tok:
                    r, v = tok.split("__", 1)
                    ranks[r] = v

            # Values AFTER "__"
            tax  = fix_spaces(ranks.get("p", ""))  # phylum
            tax2 = fix_spaces(ranks.get("f", ""))  # family (may be "")

            if not tax:
                continue

            tax_l = tax.lower()
            if tax_l not in lineages:
                continue
            bucket = lineages[tax_l]

            # Build new filename
            base = bin_name[:-3] if bin_name.endswith(".fa") else bin_name
            name_parts = [base, f"comp{comp}", tax]
            if tax2:
                name_parts.append(tax2)
            new_name = "_".join(name_parts) + ".fa.gz"

            # Source path 
            src = os.path.join(dastool, bin_name + ".gz")
            if not os.path.isfile(src):
                continue

            dst = os.path.join(out_dirs[bucket], new_name)

            # Replace existing symlink or file if present (but don't nuke directories)
            if os.path.islink(dst) or (os.path.exists(dst) and not os.path.isdir(dst)):
                try:
                    os.remove(dst)
                except OSError:
                    pass
            try:
                os.symlink(src, dst)
                print(f"{sp}: {bucket}: {bin_name} -> {new_name}")
            except OSError as e:
                print(f"ERROR: symlink failed {dst}: {e}", file=sys.stderr)
