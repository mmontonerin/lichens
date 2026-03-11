import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Load data ────────────────────────────────────────────────────────────────

df1 = pd.read_csv(
    "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered.csv"
)
df2 = pd.read_csv(
    "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered_eukbin.csv"
)

output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/plots/figures"
os.makedirs(output_dir, exist_ok=True)

# Drop cyanobacteriota from eukbin table (same as bins_filtered)
df2 = df2[df2["phylum"] != "cyanobacteriota"]

# Drop dastool rows from eukbin table — identical data already present in bins_filtered
df2 = df2[df2["binning_method"] != "dastool"]

# ── Normalise method labels ──────────────────────────────────────────────────
# bins_filtered uses: metabat2, eukcc (metabat2+eukcc), dastool (metabat2+dastool)
# bins_filtered_eukbin uses: eukbin, eukcc (eukbin+eukcc), dastool


# eukcc bins are merged into their parent method (metabat2 or eukbin)
df1["method_label"] = df1["binning_method"].map(
    {"metabat2": "metabat2", "eukcc": "metabat2", "dastool": "dastool"}
)
df2["method_label"] = df2["binning_method"].map(
    {"eukbin": "eukbin", "eukcc": "eukbin", "dastool": "dastool"}
)

df = pd.concat([df1, df2], ignore_index=True)

# ── Colors ───────────────────────────────────────────────────────────────────

phylum_colors = {
    "cyanobacteriota": "#F1C40F",
    "ascomycota":      "#B39DDB",
    "chlorophyta":     "#66BB6A",
    "basidiomycota":   "#ea97e3",
}

method_order = ["metabat2", "eukbin", "dastool"]
phylum_order = ["ascomycota", "chlorophyta", "basidiomycota", "cyanobacteriota"]

# ── Poster style ─────────────────────────────────────────────────────────────

plt.rcParams.update({
    "font.size":        24,
    "axes.titlesize":   28,
    "axes.labelsize":   24,
    "xtick.labelsize":  24,
    "ytick.labelsize":  24,
    "axes.linewidth":   2.5,
    "xtick.major.width": 2.5,
    "ytick.major.width": 2.5,
    "xtick.major.size":  8,
    "ytick.major.size":  8,
    "lines.linewidth":   2.5,
})

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 1 — Completeness distribution per method, coloured by phylum
# ═══════════════════════════════════════════════════════════════════════════

fig1, axes1 = plt.subplots(
    1, len(phylum_order),
    figsize=(7 * len(phylum_order), 10),
    sharey=True,
)
fig1.suptitle("Bin completeness by binning method and phylum", fontweight="bold", y=1.01)

for ax, phylum in zip(axes1, phylum_order):
    sub = df[df["phylum"] == phylum]
    color = phylum_colors.get(phylum, "#aaaaaa")

    methods_present = [m for m in method_order if m in sub["method_label"].values]
    data_by_method  = [sub[sub["method_label"] == m]["completeness"].dropna().values
                       for m in methods_present]

    # Only draw violin when ≥2 data points; otherwise strip plot
    violin_data   = [(d if len(d) >= 2 else np.array([])) for d in data_by_method]
    strip_indices = [i for i, d in enumerate(data_by_method) if len(d) < 2]

    if any(len(d) >= 2 for d in violin_data):
        parts = ax.violinplot(
            [d for d in violin_data if len(d) >= 2],
            positions=[i + 1 for i, d in enumerate(violin_data) if len(d) >= 2],
            showmedians=True,
            showextrema=True,
        )
        for pc in parts["bodies"]:
            pc.set_facecolor(color)
            pc.set_alpha(0.75)
            pc.set_linewidth(2.5)
        for key in ("cmedians", "cmins", "cmaxes", "cbars"):
            parts[key].set_linewidth(2.5)
            parts[key].set_color("black")

    # Overlay individual points
    for i, d in enumerate(data_by_method):
        if len(d) > 0:
            ax.scatter(
                np.full(len(d), i + 1) + np.random.uniform(-0.08, 0.08, len(d)),
                d,
                color=color, edgecolors="black", linewidths=1.5,
                s=80, zorder=3, alpha=0.9,
            )

    ax.set_title(phylum, fontweight="bold", color=color,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=2))
    ax.set_xticks(range(1, len(methods_present) + 1))
    ax.set_xticklabels(methods_present, rotation=35, ha="right")
    ax.set_ylim(-5, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.5, linewidth=1.5)
    for spine in ax.spines.values():
        spine.set_linewidth(2.5)

axes1[0].set_ylabel("Completeness (%)", fontweight="bold")
fig1.tight_layout()
# === Export ===
png_path1 = os.path.join(output_dir, "plot1_completeness_violin_methods.png")
pdf_path1 = os.path.join(output_dir, "plot1_completeness_violin_methods.pdf")

fig1.savefig(pdf_path1, bbox_inches="tight", dpi=800)
fig1.savefig(png_path1, bbox_inches="tight", dpi=800)
print("Saved plot1_completeness_violin_methods.pdf / .png")


# ═══════════════════════════════════════════════════════════════════════════
# PLOT 2 — Number of bins per species, per method, coloured by phylum
# ═══════════════════════════════════════════════════════════════════════════

bin_counts = (
    df.groupby(["species", "method_label", "phylum"])
      .size()
      .reset_index(name="n_bins")
)

# One subplot per phylum
fig2, axes2 = plt.subplots(
    1, len(phylum_order),
    figsize=(7 * len(phylum_order), 11),
    sharey=False,
)
fig2.suptitle("Number of bins per species, method and phylum", fontweight="bold", y=1.01)

for ax, phylum in zip(axes2, phylum_order):
    sub = bin_counts[bin_counts["phylum"] == phylum]
    color = phylum_colors.get(phylum, "#aaaaaa")

    if sub.empty:
        ax.set_visible(False)
        continue

    methods_present = [m for m in method_order if m in sub["method_label"].values]
    species_list    = sorted(sub["species"].unique())

    violin_input = [sub[sub["method_label"] == m]["n_bins"].values for m in methods_present]

    if any(len(d) >= 2 for d in violin_input):
        parts = ax.violinplot(
            [d for d in violin_input if len(d) >= 2],
            positions=[i + 1 for i, d in enumerate(violin_input) if len(d) >= 2],
            showmedians=True,
            showextrema=True,
        )
        for pc in parts["bodies"]:
            pc.set_facecolor(color)
            pc.set_alpha(0.75)
            pc.set_linewidth(2.5)
        for key in ("cmedians", "cmins", "cmaxes", "cbars"):
            parts[key].set_linewidth(2.5)
            parts[key].set_color("black")

    # Scatter per species
    for i, m in enumerate(methods_present):
        vals = sub[sub["method_label"] == m]["n_bins"].values
        if len(vals) > 0:
            ax.scatter(
                np.full(len(vals), i + 1) + np.random.uniform(-0.08, 0.08, len(vals)),
                vals,
                color=color, edgecolors="black", linewidths=1.5,
                s=100, zorder=3, alpha=0.9,
            )

    ax.set_title(phylum, fontweight="bold", color=color,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=2))
    ax.set_xticks(range(1, len(methods_present) + 1))
    ax.set_xticklabels(methods_present, rotation=35, ha="right")
    ax.set_ylabel("Number of bins", fontweight="bold")
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(axis="y", linestyle="--", alpha=0.5, linewidth=1.5)
    for spine in ax.spines.values():
        spine.set_linewidth(2.5)

fig2.tight_layout()
# === Export ===
png_path2 = os.path.join(output_dir, "plot2_nbins_violin_methods.png")
pdf_path2 = os.path.join(output_dir, "plot2_nbins_violin_methods.pdf")

fig2.savefig(pdf_path2, bbox_inches="tight", dpi=800)
fig2.savefig(png_path2, bbox_inches="tight", dpi=800)
print("Saved plot2_nbins_violin_methods.pdf / .png")

plt.show()