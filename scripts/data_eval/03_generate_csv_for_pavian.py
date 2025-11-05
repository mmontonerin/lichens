#!/usr/bin/env python3
import os
import sys
import pandas as pd
import glob


# Directories
input_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2"
out_csv = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/data_eval/pavian.csv"

# Find kraken reports
def find_kraken_reports(sp_dir):
    k_reports = []
    subdirs = [
        os.path.join(sp_dir, d)
        for d in os.listdir(sp_dir)
        if os.path.isdir(os.path.join(sp_dir, d))
    ]
    for dir in subdirs:
        print(dir)
        if os.path.isdir(dir):
            files = glob.glob(os.path.join(dir, "*_nt_report.out"))
            k_reports.extend([os.path.basename(f) for f in files])
    return k_reports

# Get sp names from the results directory
# Find all Kraken2 nt_report files
# Put it in a csv file as sp_name, reportfile
def main(input_dir):
    sp_names = [
        d for d in os.listdir(input_dir)
        if os.path.isdir(os.path.join(input_dir, d))
    ]
    first_write = True
    for sp_name in sorted(sp_names):
        sp_dir = os.path.join(input_dir, sp_name)
        print(sp_dir)
        # Use kraken report find function and skip if no report found
        k_reports = find_kraken_reports(sp_dir)
        if not k_reports:
            print(f"[SKIP] {sp_name}: no kraken report found", file=sys.stderr)
            continue
        print(k_reports)

        # Write CSV file
        data = {'Species_name': sp_name, 'report': k_reports}
        df = pd.DataFrame(data)
        df.to_csv(
            out_csv,
            index = False, 
            mode = "w" if first_write else "a", 
            header=first_write)
        first_write = False

if __name__ == "__main__":
    main(input_dir)