import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Input and output paths ===
input_csv = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/order_all_combined_filtered.csv"
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/plots"
os.makedirs(output_dir, exist_ok=True)

# === Load data ===
df = pd.read_csv(input_csv)

# === Filter for Metazoa only ===
meta = df[df["kingdom_lineage"] == "Metazoa"].copy()

# === Keep relevant columns ===
meta = meta[["species", "name", "percent"]]

# === Remove duplicates (one species-order pair) ===
meta = meta.drop_duplicates(subset=["species", "name"])

# === Count number of unique species per order ===
order_counts = meta.groupby("name")["species"].nunique().reset_index(name="n")

# === Merge to add n info ===
meta = meta.merge(order_counts, on="name", how="left")

# === Sort by number of species (descending) ===
order_order = order_counts.sort_values("n", ascending=False)["name"]

# === Plot ===
plt.figure(figsize=(12, 6))
palette = sns.color_palette("Blues", n_colors=len(order_order))

sns.boxplot(
    data=meta,
    x="name",
    y="percent",
    order=order_order,
    palette=palette,
    showmeans=False,
    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"},
)

sns.despine(top=True, right=True)

# === Annotate with n ===
for i, order in enumerate(order_order):
    n = order_counts.loc[order_counts["name"] == order, "n"].values[0]
    plt.text(i, meta[meta["name"] == order]["percent"].max() + 1, f"n={n}",
             ha="center", va="bottom", fontsize=15)

#plt.title("Distribution of Metazoa Orders Across Species", fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel("Order (Metazoa)", fontsize=15)
plt.ylabel("Percent Reads", fontsize=15)
plt.tight_layout()

# === Export ===
png_path = os.path.join(output_dir, "metazoa_orders_boxplot.png")
pdf_path = os.path.join(output_dir, "metazoa_orders_boxplot.pdf")

plt.savefig(png_path, dpi=800, bbox_inches="tight")
plt.savefig(pdf_path, dpi=800, bbox_inches="tight")
plt.close()

print(f"Plots saved to:\n  - {png_path}\n  - {pdf_path}")
