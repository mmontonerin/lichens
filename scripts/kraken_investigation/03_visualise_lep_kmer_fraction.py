import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/kraken_investigation/kraken2_db_report.txt/kraken2_db_report.txt', 
    sep='\t', header=None, names=['pct','clade_frags','direct_frags','rank','taxid','name'])

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
plt.savefig('kmer_occupancy_by_order.png')