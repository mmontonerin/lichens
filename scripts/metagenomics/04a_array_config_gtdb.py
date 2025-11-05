import os
import glob

# Folder with the sp folders containing metagenome results
base_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"
config_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/04b_array_config_gtdb.txt"

# Create config file with the following format:
# 1 /path/to/spfolder
# 2 /path/to/spfolder
# ...

path = os.path.join(base_dir, "*")
sp_folders=sorted(glob.glob(path))

with open(config_file, 'w') as f:
    for job_number, sp in enumerate(sp_folders, start=1):
        folder_name = os.path.basename(os.path.normpath(sp))
        f.write(f"{job_number}\t{folder_name}\t{sp}\n")
