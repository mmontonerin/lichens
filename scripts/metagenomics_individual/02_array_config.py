import os
import glob

# Folder with the yaml files
yaml_files = sorted(glob.glob("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_individual/yamls/*.yaml"))

config_file = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics_individual/02_array_config.txt"

# Create config file with the following format:
# 1 /path/to/yaml1
# 2 /path/to/yaml2
# ...
with open(config_file, 'w') as f:
    for job_number, yaml in enumerate(yaml_files, start=1):
        f.write(f"{job_number} {yaml}\n")