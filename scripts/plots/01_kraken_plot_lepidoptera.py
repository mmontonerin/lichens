import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Input and output paths ===
input_csv = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/family_all_combined_filtered.csv"
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/plots/figures"
os.makedirs(output_dir, exist_ok=True)

# === Load data ===
df = pd.read_csv(input_csv)

# === Filter for Metazoa only ===
meta = df[df["order_lineage"] == "Lepidoptera"].copy()

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

# === Global matplotlib settings for poster ===
plt.rcParams.update({
    "lines.linewidth": 2.5,
    "patch.linewidth": 2.5,       # box outline thickness
    "axes.linewidth": 2.5,        # axis spine thickness
    "xtick.major.width": 2.5,
    "ytick.major.width": 2.5,
    "xtick.major.size": 8,
    "ytick.major.size": 8,
})

# === Plot ===
plt.figure(figsize=(14, 7))
palette = sns.color_palette("Blues", n_colors=len(order_order))

ax = sns.boxplot(
    data=meta,
    x="name",
    y="percent",
    order=order_order,
    palette=palette,
    showmeans=False,
    linewidth=2.5,                # whisker/box line thickness
    flierprops=dict(
        marker="o",
        markerfacecolor="gray",
        markeredgecolor="black",
        markersize=6,
        markeredgewidth=1.5,
    ),
    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"},
)

sns.despine(top=True, right=True)

# === Annotate with n ===
for i, order in enumerate(order_order):
    n = order_counts.loc[order_counts["name"] == order, "n"].values[0]
    plt.text(i, meta[meta["name"] == order]["percent"].max() + 1, f"n={n}",
             ha="center", va="bottom", fontsize=20, fontweight="bold")

plt.xlabel("Family (Lepidoptera)", fontsize=22, fontweight="bold", labelpad=12)
plt.ylabel("Percent Reads", fontsize=22, fontweight="bold", labelpad=12)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

# Thicken spines explicitly
for spine in ax.spines.values():
    spine.set_linewidth(2.5)

plt.tight_layout()

# === Export ===
png_path = os.path.join(output_dir, "lepidoptera_families_boxplot.png")
pdf_path = os.path.join(output_dir, "lepidoptera_families_boxplot.pdf")

plt.savefig(png_path, dpi=800, bbox_inches="tight")
plt.savefig(pdf_path, dpi=800, bbox_inches="tight")
plt.close()

print(f"Plots saved to:\n  - {png_path}\n  - {pdf_path}")
