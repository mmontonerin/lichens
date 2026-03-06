import sys
import types
sys.modules["cgi"] = types.ModuleType("cgi")

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from ete3 import NCBITaxa
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- Inputs ---
TAXDB = "/data/tol/resources/taxonomy/latest/taxa.sqlite"
TAXIDS_CSV = "lichens_taxid.csv"
BINS_CSV        = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered.csv"
BINS_EUKBIN_CSV = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered_eukbin.csv"

OUT_DIR = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/phylogenies/figures"
OUT_PNG = f"{OUT_DIR}/lichens_bins_poster.png"
OUT_PDF = f"{OUT_DIR}/lichens_bins_poster.pdf"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Load & filter data ---
df_std = pd.read_csv(BINS_CSV)
df_euk = pd.read_csv(BINS_EUKBIN_CSV)
df_euk = df_euk[df_euk["binning_method"] == "eukbin"].copy()

for df in [df_std, df_euk]:
    df.drop(df[df["completeness"] < 10].index, inplace=True)

# --- Build tree (topology only, no rendering) ---
ncbi = NCBITaxa(TAXDB)
taxids = pd.read_csv(TAXIDS_CSV)["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=True)
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    sci = translator.get(int(n.name), str(n.name))
    n.add_features(sci_name=sci, df_key=sci.replace(" ", "_"))

# Same as old code
tree.ladderize(direction=1)

species_order = [n.df_key for n in tree.iter_leaves()]
sci_names     = {n.df_key: n.sci_name for n in tree.iter_leaves()}
N = len(species_order)
sp_idx = {sp: i for i, sp in enumerate(species_order)}

# --- Figure layout ---
PHYLUMS = ["ascomycota", "chlorophyta", "cyanobacteriota", "basidiomycota"]
ABBREV  = {"ascomycota": "Asco.", "chlorophyta": "Chloro.",
           "cyanobacteriota": "Cyano.", "basidiomycota": "Basidio."}
COLORS  = {
    "ascomycota":      "#9B7FD4",
    "chlorophyta":     "#66BB6A",
    "cyanobacteriota": "#F1C40F",
    "basidiomycota":   "#ea97e3",
}

MAX_BINS  = 15
TREE_W    = 3.5
PANEL_W   = 4.0
ROW_H     = 0.28
FIG_H     = N * ROW_H + 1.5
DPI       = 200

fig = plt.figure(figsize=(TREE_W + PANEL_W, FIG_H), dpi=DPI)
fig.patch.set_facecolor("white")

ax_tree  = fig.add_axes([0, 0.05, TREE_W / (TREE_W + PANEL_W), 0.9])
ax_panel = fig.add_axes([TREE_W / (TREE_W + PANEL_W) + 0.01,
                          0.05, PANEL_W / (TREE_W + PANEL_W) - 0.01, 0.9])

for ax in [ax_tree, ax_panel]:
    ax.set_facecolor("white")
    ax.set_ylim(-0.5, N - 0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

# --- Draw tree in ax_tree ---
def get_node_depths(tree):
    depths = {}
    for n in tree.traverse():
        depths[n] = n.get_distance(tree, topology_only=True)
    return depths

node_depths = get_node_depths(tree)
max_depth   = max(node_depths.values())

def node_x(n):
    if n.is_leaf():
        return 1.0
    return node_depths[n] / max_depth

def node_y(n):
    leaves = n.get_leaves()
    ys = [sp_idx[l.df_key] for l in leaves if l.df_key in sp_idx]
    return np.mean(ys)

TREE_LINE_COLOR = "black"
TREE_LW = 1.2

for n in tree.traverse():
    if n.is_root():
        continue
    parent = n.up
    x0, y0 = node_x(parent), node_y(parent)
    x1, y1 = node_x(n),      node_y(n)
    ax_tree.plot([x0, x1], [y1, y1], color=TREE_LINE_COLOR, lw=TREE_LW, zorder=2)
    ax_tree.plot([x0, x0], [y0, y1], color=TREE_LINE_COLOR, lw=TREE_LW, zorder=2)

for sp, i in sp_idx.items():
    ax_tree.text(1.02, i, sci_names[sp],
                 va="center", ha="left", fontsize=6,
                 color="black", fontstyle="italic")

ax_tree.set_xlim(0, 1.8)

# --- Draw bar panel in ax_panel ---
cell_w    = 1.0
bar_gap   = 0.06
max_bar_w = (cell_w - bar_gap * 3) / 2

for i, sp in enumerate(species_order):
    ax_panel.axhspan(i - 0.5, i + 0.5,
                     color="#f5f5f5" if i % 2 == 0 else "white", zorder=0)

    for j, ph in enumerate(PHYLUMS):
        sub_std = df_std[(df_std["species"] == sp) & (df_std["phylum"] == ph)]
        sub_euk = df_euk[(df_euk["species"] == sp) & (df_euk["phylum"] == ph)]

        cell_left = j * cell_w

        for sub, x_anchor, is_euk in [
            (sub_std, cell_left + bar_gap,                False),
            (sub_euk, cell_left + max_bar_w + bar_gap*2,  True),
        ]:
            if len(sub) == 0:
                continue

            best  = sub["completeness"].max()
            count = len(sub)

            bar_h = best / 100
            bar_w = min(count, MAX_BINS) / MAX_BINS * max_bar_w

            ax_panel.add_patch(mpatches.Rectangle(
                (x_anchor, i - bar_h / 2),
                bar_w, bar_h,
                color=COLORS[ph],
                alpha=0.45 if not is_euk else 0.95,
                linewidth=0.8 if is_euk else 0,
                edgecolor="white" if is_euk else "none",
                zorder=3
            ))

            if best >= 50 and bar_h > 0.25:
                ax_panel.text(x_anchor + bar_w / 2, i,
                              f"{best:.0f}",
                              ha="center", va="center",
                              fontsize=3.5, color="white",
                              fontweight="bold", zorder=4)

            ax_panel.text(x_anchor + bar_w / 2, i + bar_h / 2 + 0.05,
                          str(count),
                          ha="center", va="bottom",
                          fontsize=3, color=COLORS[ph], alpha=0.85, zorder=4)

for j, ph in enumerate(PHYLUMS):
    ax_panel.text(j + 0.5, N - 0.5 + 0.3, ABBREV[ph],
                  ha="center", va="bottom", fontsize=7,
                  color=COLORS[ph], fontweight="bold", rotation=30)

for j in range(1, len(PHYLUMS)):
    ax_panel.axvline(j, color="#cccccc", lw=0.5, zorder=1)

ax_panel.set_xlim(0, len(PHYLUMS) * cell_w)

# --- Legend ---
legend_elements = [
    mpatches.Patch(color="gray", alpha=0.45, label="Standard binning"),
    mpatches.Patch(color="gray", alpha=0.95, label="Eukbin",
                   linewidth=0.8, edgecolor="#cccccc"),
    mpatches.Patch(color="none", label="Height = best completeness"),
    mpatches.Patch(color="none", label="Width = bin count"),
]
fig.legend(handles=legend_elements, loc="lower center", ncol=4,
           fontsize=5.5, facecolor="white", labelcolor="black",
           framealpha=0.9, edgecolor="#cccccc", bbox_to_anchor=(0.5, 0.0))

plt.savefig(OUT_PNG, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.savefig(OUT_PDF, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {OUT_PNG}, {OUT_PDF}")