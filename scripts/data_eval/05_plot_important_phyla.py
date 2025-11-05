import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Input and output paths ===
input_csv = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/phylum_all_combined_filtered.csv"
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/plots"
os.makedirs(output_dir, exist_ok=True)

# === Load data ===
df = pd.read_csv(input_csv)

target_names = [
    "Cyanobacteriota",
    "Ascomycota",
    "Chlorophyta",
    "Basidiomycota",
]

color_map = {
    "Cyanobacteriota": "#F1C40F",  
    "Ascomycota":      "#B39DDB",  
    "Chlorophyta":     "#66BB6A",  
    "Basidiomycota":   "#ea97e3",  
}

# === Filter for selected phyla only ===
phy = df[df["name"].isin(target_names)].copy()

# === Keep relevant columns ===
phy = phy[["species", "name", "percent"]]

# === Remove duplicates (one species-order pair) ===
phy = phy.drop_duplicates(subset=["species", "name"])

# === Count unique species per name (for n= annotation) ===
name_counts = phy.groupby("name")["species"].nunique().reset_index(name="n")

# === x-axis order ===
x_order = name_counts.sort_values("n", ascending=False)["name"].tolist()

# === Palette aligned to x_order using your fixed colors ===
palette = [color_map[n] for n in x_order]

# === Plot ===
plt.figure(figsize=(7, 7))

sns.boxplot(
    data=phy,
    x="name",
    y="percent",
    order=x_order,
    palette=palette,
    showmeans=False,
    meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"},
)

sns.despine(top=True, right=True)

# === Annotate with n ===
for i, nm in enumerate(x_order):
    n = int(name_counts.loc[name_counts["name"] == nm, "n"].values[0])
    y_max = phy[phy["name"] == nm]["percent"].max()
    plt.text(i, y_max + 1, f"n={n}", ha="center", va="bottom", fontsize=15)

#plt.title("Percentage of reads for relevant phyla", fontsize=14)
plt.xlabel("Phylum", fontsize=15)
plt.ylabel("Percent Reads", fontsize=15)
plt.xticks(fontsize=13)
plt.yticks(fontsize=13)
plt.tight_layout()

# === Export ===
png_path = os.path.join(output_dir, "phylum_boxplot.png")
pdf_path = os.path.join(output_dir, "phylum_boxplot.pdf")

plt.savefig(png_path, dpi=800, bbox_inches="tight")
plt.savefig(pdf_path, dpi=800, bbox_inches="tight")
plt.close()

print(f"Plots saved to:\n  - {png_path}\n  - {pdf_path}")
