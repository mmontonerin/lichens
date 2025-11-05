import os
import glob

# Folder with the sp folders containing metagenome results
sp_folders = glob.glob("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/*")

config_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/03c_array_config.txt"

# Create config file with the following format:
# 1 /path/to/spfolder
# 2 /path/to/spfolder
# ...

with open(config_file, 'w') as f:
    for job_number, sp in enumerate(sp_folders, start=1):
        f.write(f"{job_number} {sp}\n")
