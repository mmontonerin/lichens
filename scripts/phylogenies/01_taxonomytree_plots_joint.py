import os
import pandas as pd
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from ete3 import NCBITaxa, TreeStyle, TextFace, AttrFace, faces, NodeStyle, RectFace
from PIL import Image, ImageDraw
import tempfile, math

# Initialize and load NCBI taxonomy database
ncbi = NCBITaxa("/data/tol/resources/taxonomy/latest/taxa.sqlite")

# Tables taxid and kraken2 result table
df = pd.read_csv("lichens_taxid.csv")
taxids = df["taxon"].astype(int).tolist()
domain = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered.csv")
kingdom = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/kingdom_all_combined_filtered.csv")
bases   = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered_bp.csv")

tree = ncbi.get_topology(taxids, intermediate_nodes=True)

# Add sci_name attribute for all nodes
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    n.add_features(sci_name=translator.get(int(n.name), str(n.name)))

# ----------------------------------------------------
# BARS - TAXONOMY - build percent maps
def build_perc_map(table_df, categories, species_col="species", name_col="name", value_col="percent"):
    df2 = table_df[[species_col, name_col, value_col]].copy()
    df2[species_col] = df2[species_col].str.replace("_", " ", regex=False)
    df2 = df2[df2[name_col].isin(categories)]
    pv = df2.pivot_table(index=species_col, columns=name_col, values=value_col, aggfunc="max").fillna(0.0)
    for c in categories:
        if c not in pv.columns:
            pv[c] = 0.0
    pv = pv[categories]
    return {sp: tuple(float(pv.loc[sp, c]) for c in categories) for sp in pv.index}

domain_cats = ["Bacteria", "Eukaryota"]
domain_map  = build_perc_map(domain, domain_cats)

kingdom_cats = ["Fungi", "Metazoa", "Viridiplantae"]
kingdom_map  = build_perc_map(kingdom, kingdom_cats)

# ----------------------------------------------------
# Reads/Bases metrics (use 'bases' table, keep variable name as in base script)
# Expect columns: species, total_reads, total_bases
rb = (bases
      .drop_duplicates(subset=["species"])
      .loc[:, ["species", "total_reads", "total_bases"]]
      .copy())
rb["reads_M"]   = rb["total_reads"]  / 1e6
rb["bases_Gbp"] = rb["total_bases"]  / 1e9
metrics = rb.set_index("species")[["reads_M", "bases_Gbp"]].to_dict(orient="index")

# ----------------------------------------------------
# Tree styling ---
nstyle = NodeStyle()
nstyle["size"] = 0
nstyle["vt_line_width"] = 2
nstyle["hz_line_width"] = 2
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"
for n in tree.traverse():
    n.set_style(nstyle)

# ----------------------------------------------------
# Draw bars entirely in memory ---
# Taxonomy stacked bars
BAR_W_TAX, BAR_H_TAX = 150, 16
GREY   = (221, 221, 221)
_bar_cache = {}
_tmp_files = []   # track temp files to delete afterwards

COL_DOMAIN = {"Bacteria": (241, 196, 15), "Eukaryota": (108, 92, 231)}
COL_EUK    = {"Fungi": (179, 157, 219), "Metazoa": (129, 212, 250), "Viridiplantae": (102, 187, 106)}

def make_bar_face(segments, width=BAR_W_TAX, height=BAR_H_TAX):
    """
    segments = list of (rgb_tuple, percent_float).
    Creates ONE taxonomy bar image (gray background, colored segments).
    """
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

# Reads/Bases simple bars with grid lines
def _nice_max(x):
    if x <= 0: return 1.0
    exp = math.floor(math.log10(x)); base = 10 ** exp
    for m in (1, 2, 5, 10):
        if m * base >= x:
            return m * base
    return 10 * base

def _ticks(maxv, target=5):
    if maxv <= 0: return [0, 1]
    raw = maxv / target
    exp = math.floor(math.log10(raw)); base = 10 ** exp
    step = min([1, 2, 5, 10], key=lambda m: abs(raw - m*base)) * base
    xs = [0]; t = step
    while t < maxv + 1e-9:
        xs.append(t); t += step
    if xs[-1] != maxv:
        xs.append(maxv)
    return xs

# Fixed reads scale at 30 M (grid at 0,10,20,30)
READS_MAX  = 30.0
READ_TICKS = [0, 10, 20, 30]

# Auto bases scale in Gbp
BASES_MAX  = _nice_max(rb["bases_Gbp"].max() if len(rb) else 1.0)
BASE_TICKS = _ticks(BASES_MAX)

# Visual tuning for numeric bar columns (narrower; compact)
BAR_W_NUM  = 100
BAR_H_NUM  = 20
GRID_CLR   = (229, 229, 229)  # faint grey grid
BAR_CLR    = (100, 100, 100)
BG_CLR     = (255, 255, 255)

# Spacing
LEFT_GAP_PX        = 24   # whitespace between name and first (Reads) column
BETWEEN_NUM_GAP_PX = 12   # gap between Reads and Bases
BETWEEN_SETS_GAP_PX= 12   # gap between Bases and Domain bar
BETWEEN_TAX_GAP_PX = 10   # gap between Domain and Kingdom bars

def make_num_bar_face(value, vmax, ticks, width=BAR_W_NUM, height=BAR_H_NUM):
    """
    Horizontal bar with faint vertical grid lines at `ticks` and solid fill up to `value`.
    """
    key = ("num", width, height, round(float(value),6), round(float(vmax),6),
           tuple(round(float(t),6) for t in ticks))
    if key in _bar_cache:
        return _bar_cache[key]

    img = Image.new("RGB", (width, height), BG_CLR)
    draw = ImageDraw.Draw(img)

    denom = vmax if vmax > 0 else 1.0
    for tk in ticks:
        x = int(round(width * (tk / denom)))
        draw.line([(x, 0), (x, height)], fill=GRID_CLR, width=1)

    bw = int(round(width * (max(0.0, min(float(value), vmax)) / denom)))
    if bw > 0:
        draw.rectangle([0, 0, max(bw-1, 0), height-1], fill=BAR_CLR)

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tf.name); tf.close()
    _tmp_files.append(tf.name)

    face = faces.ImgFace(tf.name)
    face.margin_left = face.margin_right = face.margin_top = face.margin_bottom = 0
    _bar_cache[key] = face
    return face

# --- Layout: name + gap + Reads + gap + Bases + gap + Domain + gap + Kingdom ---
def layout(node):
    if not node.is_leaf():
        return

    sci = node.sci_name
    faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")

    # whitespace before first numeric column
    faces.add_face_to_node(RectFace(LEFT_GAP_PX, BAR_H_NUM, fgcolor=None, bgcolor=None),
                           node, column=1, position="aligned")

    # Reads / Bases values
    sp_key = sci.replace(" ", "_")
    vals = metrics.get(sp_key)
    reads_M = float(vals["reads_M"])   if vals else 0.0
    bases_G = float(vals["bases_Gbp"]) if vals else 0.0

    # Reads
    faces.add_face_to_node(
        make_num_bar_face(reads_M, READS_MAX, READ_TICKS, width=BAR_W_NUM, height=BAR_H_NUM),
        node, column=2, position="aligned"
    )

    # gap between numeric columns
    faces.add_face_to_node(RectFace(BETWEEN_NUM_GAP_PX, BAR_H_NUM, fgcolor=None, bgcolor=None),
                           node, column=3, position="aligned")

    # Bases
    faces.add_face_to_node(
        make_num_bar_face(bases_G, BASES_MAX, BASE_TICKS, width=BAR_W_NUM, height=BAR_H_NUM),
        node, column=4, position="aligned"
    )

    # gap between numeric set and taxonomy bars
    faces.add_face_to_node(RectFace(BETWEEN_SETS_GAP_PX, BAR_H_NUM, fgcolor=None, bgcolor=None),
                           node, column=5, position="aligned")

    # Domain bar (Bacteria / Eukaryota)
    dvals = domain_map.get(sci, (0.0, 0.0))
    d_segments = [
        (COL_DOMAIN["Bacteria"],  dvals[0]),
        (COL_DOMAIN["Eukaryota"], dvals[1]),
    ]
    faces.add_face_to_node(make_bar_face(d_segments, width=BAR_W_TAX, height=BAR_H_TAX),
                           node, column=6, position="aligned")

    # gap between Domain and Kingdom
    faces.add_face_to_node(RectFace(BETWEEN_TAX_GAP_PX, BAR_H_TAX, fgcolor=None, bgcolor=None),
                           node, column=7, position="aligned")

    # Kingdom bar (Fungi / Metazoa / Viridiplantae)
    evals = kingdom_map.get(sci, (0.0, 0.0, 0.0))
    e_segments = [
        (COL_EUK["Fungi"],         evals[0]),
        (COL_EUK["Metazoa"],       evals[1]),
        (COL_EUK["Viridiplantae"], evals[2]),
    ]
    faces.add_face_to_node(make_bar_face(e_segments, width=BAR_W_TAX, height=BAR_H_TAX),
                           node, column=8, position="aligned")

# --- TreeStyle and render (NO legend) ---
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"

# Legend (colors for the taxonomy bars only)
legend = [
    ("#F1C40F", "Bacteria"),
    ("#6C5CE7", "Eukaryota"),
    ("#B39DDB", "Fungi"),
    ("#81D4FA", "Metazoa"),
    ("#66BB6A", "Viridiplantae"),
    ("#DDDDDD", "Other"),
]
for i, (col, label) in enumerate(legend):
    ts.legend.add_face(RectFace(10, 10, fgcolor=None, bgcolor=col), column=2*i)
    ts.legend.add_face(TextFace(f" {label}", fsize=10), column=2*i + 1)

# optional margins
ts.margin_left = 20
ts.margin_right = 30
ts.margin_top = 10
ts.margin_bottom = 30

#Fixed tree topology
tree.ladderize(direction=1)  

# render tree
tree.render("lichens_taxonomy_allplots.png", tree_style=ts, w=2400)
tree.render("lichens_taxonomy_allplots.pdf", tree_style=ts, w=2400)

# --- remove temp bar images ---
for p in _tmp_files:
    try:
        os.remove(p)
    except OSError:
        pass
