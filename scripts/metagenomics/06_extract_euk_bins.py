#!/usr/bin/env python3
import os
import sys

input_path = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
output_subdir = "bin_selection"  # to be created under each species folder

# To search on lineage section of the table
lineages = {
    "ascomycota": "ascomycota",
    "basidiomycota": "basidiomycota",
    "chlorophyta": "chlorophyta",
}

def fix_spaces(s: str) -> str:
    # Some lineages/sp have spaces, which we do not want as filename
    return s.replace(" ", "_")


#for sp in sorted(os.listdir(input_path)):
#    sp_dir = os.path.join(input_path, sp)
#    if not os.path.isdir(sp_dir):
#        continue

for sp in ["Xanthoria_parietina", "Cystocoleus_ebeneus"]:
    sp_dir = os.path.join(input_path, sp)
    if not os.path.isdir(sp_dir):
        continue
    
    # Build paths
    tax_dir   = os.path.join(sp_dir, "bins", "taxonomy_eukcc")
    table     = os.path.join(tax_dir, "eukcc_lineage_names.csv") # It is a tsv file despite name
    metabat2  = os.path.join(sp_dir, "bins", "fasta", "metabat2")
    merged    = os.path.join(tax_dir, "merged_bins")
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
            i_bin = cols.index("bin")
            i_comp = cols.index("completeness")
            i_cont = cols.index("contamination")
            i_lin = cols.index("lineage_names")
        except ValueError:
            print(f"ERROR: Missing expected columns in {table}", file=sys.stderr)
            continue

        for line in fh:
            line = line.rstrip("\n\r")
            if not line:
                continue
            parts = line.split("\t")

            bin_name = parts[i_bin].strip()
            comp = parts[i_comp].strip()
            cont = parts[i_cont].strip()
            lineage = parts[i_lin].strip()
            low = lineage.lower()

            bucket = None
            for b in lineages:
                # lineage is ';'-separated
                if f";{b};" in low or low.endswith(";" + b) or low.startswith(b + ";") or low == b:
                    bucket = b
                    break
            if bucket is None:
                continue

            # last lineage to add to file name
            last_tax = lineage.split(";")[-1]
            last_tax = fix_spaces(last_tax)

            # Build new filename
            base = bin_name[:-3] if bin_name.endswith(".fa") else bin_name
            new_base = f"{base}_c{comp}_co{cont}_{last_tax}"

            # Source path (merged.* vs metabat2/)
            if bin_name.startswith("merged."):
                src = os.path.join(merged, bin_name)
                ext = ".fa"
            else:
                src = os.path.join(metabat2, bin_name)  # files are now plain .fa
                ext = ".fa"

            if not os.path.isfile(src):
                continue

            new_name = f"{new_base}{ext}"
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
