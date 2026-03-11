import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Global poster aesthetics ──────────────────────────────────────────────────
plt.rcParams.update({
    "font.size":         24,
    "axes.titlesize":    26,
    "axes.labelsize":    24,
    "xtick.labelsize":   24,
    "ytick.labelsize":   24,
    "legend.fontsize":   22,
    "lines.linewidth":   2.5,
    "axes.linewidth":    2.0,
    "xtick.major.width": 2.0,
    "ytick.major.width": 2.0,
})

# ── Input path ────────────────────────────────────────────────────────────────
input_path = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome"

# ── Collect counts per species ────────────────────────────────────────────────
records = []

for species_name in sorted(os.listdir(input_path)):
    species_dir  = os.path.join(input_path, species_name)
    assembly_dir = os.path.join(species_dir, "assembly")

    if not os.path.isdir(assembly_dir):
        continue

    # ── Tiara: mitochondria & plastids ────────────────────────────────────────
    tiara_path = os.path.join(assembly_dir, "tiara", "tiara_out.txt")
    n_mito = n_plastid = 0

    if os.path.isfile(tiara_path):
        tiara = pd.read_csv(tiara_path, sep="\t", low_memory=False)

        n_mito = int(
            ((tiara["class_fst_stage"] == "organelle") &
             (tiara["class_snd_stage"] == "mitochondrion")).sum()
        )
        n_plastid = int(
            ((tiara["class_fst_stage"] == "organelle") &
             (tiara["class_snd_stage"] == "plastid")).sum()
        )

    # ── QC: plasmids & viruses ────────────────────────────────────────────────
    qc_dir       = os.path.join(assembly_dir, "qc")
    plasmid_file = os.path.join(qc_dir, f"{species_name}_metamdbg.circles_plasmid_summary.tsv")
    virus_file   = os.path.join(qc_dir, f"{species_name}_metamdbg.circles_virus_summary.tsv")

    n_plasmid = 0
    if os.path.isfile(plasmid_file):
        n_plasmid = len(pd.read_csv(plasmid_file, sep="\t"))

    n_virus = 0
    if os.path.isfile(virus_file):
        n_virus = len(pd.read_csv(virus_file, sep="\t"))

    records.append({
        "species":      species_name,
        "Mitochondria": n_mito,
        "Plastids":     n_plastid,
        "Plasmids":     n_plasmid,
        "Viruses":      n_virus,
    })

df_counts = pd.DataFrame(records)
print(f"Loaded data for {len(df_counts)} species.")
print(df_counts.describe())

# ── Layout constants ──────────────────────────────────────────────────────────
categories = ["Mitochondria", "Plastids", "Plasmids", "Viruses"]
greyscales = ["#1a1a1a", "#595959", "#9e9e9e", "#d4d4d4"]
positions  = [1, 2, 3, 4]

BREAK_LO  = 1200   # top of the main (bottom) panel
BREAK_HI  = 1400   # bottom of the outlier (top) panel
UPPER_MAX = 3400   # ceiling of the top panel

# Upper panel is narrow (1 unit) vs main panel (4 units)
fig, (ax_top, ax_bot) = plt.subplots(
    2, 1,
    figsize=(14, 12),
    gridspec_kw={"height_ratios": [1, 4], "hspace": 0.05},
    sharex=True,
)
fig.patch.set_facecolor("white")


# ── Helper: draw violins + jitter on any axes ─────────────────────────────────
def plot_violins(ax):
    for pos, cat, colour in zip(positions, categories, greyscales):
        data = df_counts[cat].dropna().values

        if len(data) < 2 or np.std(data) == 0:
            ax.scatter(
                np.full(len(data), pos), data,
                color=colour, s=80, zorder=3, alpha=0.8
            )
            continue

        parts = ax.violinplot(
            data,
            positions=[pos],
            widths=0.6,
            showmeans=False,
            showmedians=True,
            showextrema=True,
        )

        for pc in parts["bodies"]:
            pc.set_facecolor(colour)
            pc.set_edgecolor("#333333")
            pc.set_linewidth(2.0)
            pc.set_alpha(0.85)

        for part_name in ("cmedians", "cmins", "cmaxes", "cbars"):
            if part_name in parts:
                parts[part_name].set_edgecolor("#111111")
                parts[part_name].set_linewidth(2.5)

        jitter = np.random.default_rng(seed=42).uniform(-0.08, 0.08, size=len(data))
        ax.scatter(
            np.full(len(data), pos) + jitter, data,
            color="#111111", s=60, zorder=3, alpha=0.55
        )


plot_violins(ax_bot)
plot_violins(ax_top)

# ── Y-axis limits ─────────────────────────────────────────────────────────────
ax_bot.set_ylim(0, BREAK_LO)
ax_top.set_ylim(BREAK_HI, UPPER_MAX)

# ── Shared styling ────────────────────────────────────────────────────────────
for ax in (ax_top, ax_bot):
    ax.set_facecolor("white")
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#aaaaaa")
    ax.spines["bottom"].set_color("#aaaaaa")
    ax.spines["top"].set_color("#aaaaaa")
    ax.yaxis.grid(True, color="#dddddd", linewidth=2, zorder=0)
    ax.set_axisbelow(True)

# Hide the spines at the break boundary
ax_bot.spines["top"].set_visible(False)
ax_top.spines["bottom"].set_visible(False)
ax_top.spines["top"].set_visible(False)
ax_top.tick_params(bottom=False)   # no tick marks on the cut edge

# ── Diagonal break marks ──────────────────────────────────────────────────────
# Draw small diagonal slashes on the left spine at the break point.
dx, dy = 0.018, 0.025

for ax, edge in ((ax_bot, "top"), (ax_top, "bottom")):
    y_ax = 1.0 if edge == "top" else 0.0
    slash = plt.Line2D(
        [0.0 - dx, 0.0 + dx],
        [y_ax - dy, y_ax + dy],
        color="#555555", linewidth=2.5,
        clip_on=False, transform=ax.transAxes
    )
    ax.add_line(slash)

# ── Axis labels & title ───────────────────────────────────────────────────────
ax_bot.set_xticks(positions)
ax_bot.set_xticklabels(categories)

# Single y-label spanning both panels
fig.text(0.04, 0.5, "Count per species",
         va="center", ha="center", rotation="vertical", fontsize=24)

fig.suptitle("Assembly element counts across lichen metagenome species",
             fontweight="bold", fontsize=26, y=0.99)

# Legend in the main panel
#legend_patches = [
#    mpatches.Patch(facecolor=c, edgecolor="#333333", label=cat)
#    for cat, c in zip(categories, greyscales)
#]
#ax_bot.legend(handles=legend_patches, loc="upper right", framealpha=0.6)

plt.tight_layout(rect=[0.06, 0, 1, 0.98])

# === Export ===
output_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/plots/figures"
os.makedirs(output_dir, exist_ok=True)

png_path = os.path.join(output_dir, "metagenome_violin_counts.png")
pdf_path = os.path.join(output_dir, "metagenome_violin_counts.pdf")

plt.savefig(png_path, dpi=800, bbox_inches="tight")
plt.savefig(pdf_path, dpi=800, bbox_inches="tight")
plt.close()
print(f"Saved: {png_path}")
print(f"Saved: {pdf_path}")