import os
import matplotlib.pyplot as plt
import pandas as pd

input_report = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation/kraken2_db_report.txt"
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_report, 
    sep='\t',
    comment='#',          # db investigation report has headers
    header=None,
    names=['pct', 'clade_frags', 'direct_frags', 'rank', 'taxid', 'name']
)

# Lepidoptera taxid = 7088
total_kmers = df[df['taxid'] == 1]['clade_frags'].values[0]
lepi_kmers  = df[df['taxid'] == 7088]['clade_frags'].values[0]

print(f"Lepidoptera k-mer fraction: {lepi_kmers/total_kmers:.2%}")

# Filter to rank == 'O' (order)
orders = df[df['rank'] == 'O'].copy()
orders['pct'] = orders['clade_frags'] / total_kmers * 100
orders = orders.sort_values('clade_frags', ascending=False)

top_n = orders.head(20)
colors = ['#e63946' if 'Lepidoptera' in n else '#457b9d' 
          for n in top_n['name'].str.strip()]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(top_n['name'].str.strip(), top_n['pct'], color=colors)
ax.set_xlabel('% of total database k-mers')
ax.set_title('K-mer space occupancy by order in NCBI nt (k=35)\nRed = Lepidoptera')
plt.tight_layout()

png_path = os.path.join(output_dir, "kmerfraction_lepidoptera.png")
plt.savefig(png_path, dpi=800, bbox_inches="tight")
plt.close()