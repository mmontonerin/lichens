import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
import sys
import types
sys.modules["cgi"] = types.ModuleType("cgi")
from ete3 import faces, AttrFace, RectFace, NodeStyle, NCBITaxa, TreeStyle
from ete3 import faces as ete_faces
import pandas as pd
from PIL import Image, ImageDraw
import tempfile, math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io

# --- Inputs ---
TAXDB = "/data/tol/resources/taxonomy/latest/taxa.sqlite"
TAXIDS_CSV = "lichens_taxid.csv"
CSV   = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered_bp.csv"
BINS_CSV        = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered.csv"
BINS_EUKBIN_CSV = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome_tables/bins_filtered_eukbin.csv"
OUT_DIR = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/phylogenies/figures"
OUT_PNG = f"{OUT_DIR}/lichens_tree_reads-bases_bins_kraken.png"
OUT_PDF = f"{OUT_DIR}/lichens_tree_reads-bases_bins_kraken.pdf"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Load data ---
ncbi = NCBITaxa(TAXDB)
df_reads = pd.read_csv(CSV)
df_std = pd.read_csv(BINS_CSV)
df_euk = pd.read_csv(BINS_EUKBIN_CSV)
df_euk = df_euk[df_euk["phylum"] != "cyanobacteriota"].copy()
# Kraken data
domain  = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered.csv")
kingdom = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/kingdom_all_combined_filtered.csv")
# Colors
COL_DOMAIN = {"Bacteria": (241, 196, 15), "Eukaryota": (108, 92, 231)}
COL_EUK    = {"Fungi": (179, 157, 219), "Metazoa": (129, 212, 250), "Viridiplantae": (102, 187, 106)}
COL_BACTERIA = (241, 196, 15)   # yellow for the "other" slot

for df in [df_std, df_euk]:
    df.drop(df[df["completeness"] < 10].index, inplace=True)

# --- Prepare reads/bases table ---
df_reads = (df_reads
            .drop_duplicates(subset=["species"])
            .loc[:, ["species", "total_reads", "total_bases"]]
           )
df_reads["reads_M"]   = df_reads["total_reads"] / 1e6
df_reads["bases_Gbp"] = df_reads["total_bases"] / 1e9
metrics = df_reads.set_index("species")[["reads_M", "bases_Gbp"]].to_dict(orient="index")

# --- Axis helpers ---
def _nice_max(x):
    if x <= 0: return 1.0
    exp = math.floor(math.log10(x))
    base = 10 ** exp
    for m in (1, 2, 5, 10):
        if m * base >= x:
            return m * base
    return 10 * base

def _ticks(maxv, target=5):
    if maxv <= 0: return [0, 1]
    raw = maxv / target
    exp = math.floor(math.log10(raw))
    base = 10 ** exp
    step = min([1, 2, 5, 10], key=lambda m: abs(raw - m*base)) * base
    xs = [0]; t = step
    while t < maxv + 1e-9:
        xs.append(t); t += step
    if xs[-1] != maxv:
        xs.append(maxv)
    return xs

READS_MAX  = 30.0
READ_TICKS = list(range(0, 31, 10))
BASES_MAX  = _nice_max(df_reads["bases_Gbp"].max() if len(df_reads) else 1.0)
BASE_TICKS = _ticks(BASES_MAX)

BAR_W             = 40
BAR_H             = 30
LEFT_GAP_PX       = 20
BETWEEN_COL_GAP_PX = 8

GRID_CLR = (229, 229, 229)
BAR_CLR  = (100, 100, 100)
BG_CLR   = (255, 255, 255)

# --- Build tree ---
taxids = pd.read_csv(TAXIDS_CSV)["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=False)
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    sci = translator.get(int(n.name), str(n.name))
    n.add_features(sci_name=sci, df_key=sci.replace(" ", "_"))

nstyle = NodeStyle()
nstyle["size"] = 0
nstyle["vt_line_width"] = 2
nstyle["hz_line_width"] = 2
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"
for n in tree.traverse():
    n.set_style(nstyle)

tree.ladderize(direction=1)
species_order = [n.df_key for n in tree.iter_leaves()]

# --- Bar image faces (reads/bases) ---
_bar_cache = {}
_tmp_files = []

def _bar_img_face(value, vmax, ticks, w=BAR_W, h=BAR_H):
    key = (round(float(value), 6), round(float(vmax), 6),
           tuple(round(float(t), 6) for t in ticks), w, h)
    if key in _bar_cache:
        return _bar_cache[key]

    img = Image.new("RGB", (w, h), BG_CLR)
    draw = ImageDraw.Draw(img)
    denom = vmax if vmax > 0 else 1.0
    for tk in ticks:
        x = int(round(w * (tk / denom)))
        draw.line([(x, 0), (x, h)], fill=GRID_CLR, width=1)
    bw = int(round(w * (max(0.0, min(float(value), vmax)) / denom)))
    if bw > 0:
        draw.rectangle([0, 0, max(bw-1, 0), h-1], fill=BAR_CLR)

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tf.name); tf.close()
    _tmp_files.append(tf.name)

    f = ete_faces.ImgFace(tf.name)
    f.margin_left = f.margin_right = f.margin_top = f.margin_bottom = 0
    _bar_cache[key] = f
    return f

# --- Kraken panel faces 
# Build maps
def build_perc_map(table_df, categories, species_col="species", name_col="name", value_col="percent"):
    df2 = table_df[[species_col, name_col, value_col]].copy()
    df2[species_col] = df2[species_col].str.replace("_", " ", regex=False)
    df2 = df2[df2[name_col].isin(categories)]
    pv = df2.pivot_table(index=species_col, columns=name_col, values=value_col, aggfunc="max").fillna(0.0)
    for c in categories:
        if c not in pv.columns:
            pv[c] = 0.0
    return {sp: tuple(float(pv.loc[sp, c]) for c in categories) for sp in pv.index}

kingdom_cats = ["Fungi", "Metazoa", "Viridiplantae"]
kingdom_map  = build_perc_map(kingdom, kingdom_cats)
domain_cats  = ["Bacteria"]
domain_map   = build_perc_map(domain, domain_cats)

BAR_W_TAX = 150
BAR_H_TAX = 20
GREY = (221, 221, 221)

def make_bar_face(segments, width=BAR_W_TAX, height=BAR_H_TAX):
    key = ("tax", width, height, tuple((tuple(c), round(float(p), 2)) for c, p in segments))
    if key in _bar_cache:
        return _bar_cache[key]
    img = Image.new("RGB", (width, height), GREY)
    draw = ImageDraw.Draw(img)
    x = 0
    for color, pct in segments:
        pct = max(0.0, min(100.0, float(pct)))
        w = int(round(width * pct / 100.0))
        if w > 0:
            draw.rectangle([x, 0, x + w - 1, height - 1], fill=color)
        x += w
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tf.name); tf.close()
    _tmp_files.append(tf.name)
    face = faces.ImgFace(tf.name)
    face.margin_left = face.margin_right = face.margin_top = face.margin_bottom = 0
    _bar_cache[key] = face
    return face

# --- Bins panel faces (matplotlib per-row images) ---
PHYLUMS = ["ascomycota", "chlorophyta", "cyanobacteriota", "basidiomycota"]
COLORS  = {
    "ascomycota":      "#9B7FD4",
    "chlorophyta":     "#66BB6A",
    "cyanobacteriota": "#F1C40F",
    "basidiomycota":   "#ea97e3",
}
MAX_BINS   = 15
BINS_W     = 800   # total pixel width of bins panel per row
BINS_H     = BAR_H

_bins_cache = {}

def _bins_img_face(sp, w=BINS_W, h=BINS_H):
    if sp in _bins_cache:
        return _bins_cache[sp]

    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=100)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    cell_w    = 2
    bar_gap   = 0.18
    max_bar_w = (cell_w - bar_gap * 3) / 2

    ax.set_xlim(0, len(PHYLUMS) * cell_w)
    ax.set_ylim(0, 1)
    ax.axis("off")


    for j, ph in enumerate(PHYLUMS):
        sub_std = df_std[(df_std["species"] == sp) & (df_std["phylum"] == ph)]
        sub_euk = df_euk[(df_euk["species"] == sp) & (df_euk["phylum"] == ph)]

        cell_left = j * cell_w

        for sub, x_anchor, is_euk in [
            (sub_std, cell_left + bar_gap,                False),
            (sub_euk, cell_left + max_bar_w + bar_gap*4,  True),
        ]:
            if len(sub) == 0:
                continue
            best  = sub["completeness"].max()
            count = len(sub)
            bar_h = best / 100
            bar_w = min(count, MAX_BINS) / MAX_BINS * max_bar_w

            ax.add_patch(mpatches.Rectangle(
                (x_anchor, (1 - bar_h) / 2),
                bar_w, bar_h,
                color=COLORS[ph],
                alpha=0.45 if not is_euk else 0.95,
                linewidth=1.5 if is_euk else 0,
                edgecolor="white" if is_euk else "none",
                transform=ax.transData, zorder=3
            ))

            # label to the right of the bar: count/completeness
            ax.text(x_anchor + bar_w + 0.02, 0.5,
                    f"{count}/{best:.0f}",
                    ha="left", va="center",
                    fontsize=12, color=COLORS[ph],
                    transform=ax.transData, zorder=4)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                pad_inches=0, facecolor="white", dpi=100)
    plt.close(fig)
    buf.seek(0)

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    Image.open(buf).save(tf.name)
    tf.close()
    _tmp_files.append(tf.name)

    f = ete_faces.ImgFace(tf.name)
    f.margin_left = f.margin_right = f.margin_top = f.margin_bottom = 0
    _bins_cache[sp] = f
    return f

# --- Layout ---
def layout(node):
    if not node.is_leaf():
        return

    faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")

    key  = getattr(node, "df_key", None)
    sci  = getattr(node, "sci_name", "")
    vals = metrics.get(key)

    # gap before bars
    faces.add_face_to_node(RectFace(LEFT_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=1, position="aligned")

    # col 2: reads
    if vals:
        reads_M = float(vals["reads_M"])
        bases_G = float(vals["bases_Gbp"])
        faces.add_face_to_node(_bar_img_face(reads_M, READS_MAX, READ_TICKS),
                               node, column=2, position="aligned")
        faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                               node, column=3, position="aligned")
        faces.add_face_to_node(_bar_img_face(bases_G, BASES_MAX, BASE_TICKS),
                               node, column=4, position="aligned")
    else:
        faces.add_face_to_node(RectFace(BAR_W, BAR_H, fgcolor=None, bgcolor=None),
                               node, column=2, position="aligned")
        faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                               node, column=3, position="aligned")
        faces.add_face_to_node(RectFace(BAR_W, BAR_H, fgcolor=None, bgcolor=None),
                               node, column=4, position="aligned")

    # gap before taxonomy bar
    faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H_TAX, fgcolor=None, bgcolor=None),
                           node, column=5, position="aligned")

    # col 6: kingdom bar — Fungi / Metazoa / Viridiplantae / Bacteria (as "other")
    evals   = kingdom_map.get(sci, (0.0, 0.0, 0.0))
    bval    = domain_map.get(sci, (0.0,))[0]
    e_segments = [
        (COL_EUK["Fungi"],         evals[0]),
        (COL_EUK["Metazoa"],       evals[1]),
        (COL_EUK["Viridiplantae"], evals[2]),
        (COL_BACTERIA,             bval),      # Bacteria in yellow as last segment
    ]
    faces.add_face_to_node(make_bar_face(e_segments), node, column=6, position="aligned")

    # gap before bins panel
    faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=7, position="aligned")

    # col 8: bins panel
    if key:
        faces.add_face_to_node(_bins_img_face(key), node, column=8, position="aligned")


# --- TreeStyle ---
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"
ts.margin_left = 20
ts.margin_right = 30
ts.margin_top = 10
ts.margin_bottom = 30

tree.render(OUT_PNG, tree_style=ts, w=2400)
tree.render(OUT_PDF, tree_style=ts, w=2400)
print(f"Exported: {OUT_PNG}, {OUT_PDF}")

for p in _tmp_files:
    try:
        os.remove(p)
    except OSError:
        pass