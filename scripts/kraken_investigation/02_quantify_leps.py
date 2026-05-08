import pandas as pd

df = pd.read_csv('/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation/kraken2_db_report.txt/kraken2_db_report.txt', 
    sep='\t', header=None, names=['pct','clade_frags','direct_frags','rank','taxid','name'])

# Lepidoptera taxid = 7088
total_kmers = df[df['taxid'] == 1]['clade_frags'].values[0]
lepi_kmers  = df[df['taxid'] == 7088]['clade_frags'].values[0]

print(f"Lepidoptera k-mer fraction: {lepi_kmers/total_kmers:.2%}")