import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from ete3 import faces, AttrFace, RectFace, NodeStyle, NCBITaxa, TreeStyle
from ete3 import faces as ete_faces
import pandas as pd
from PIL import Image, ImageDraw
import tempfile, math

# --- Inputs ---
TAXDB = "/data/tol/resources/taxonomy/latest/taxa.sqlite"
TAXIDS_CSV = "lichens_taxid.csv"  # columns: taxon (NCBI taxid)
CSV   = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered_bp.csv"
OUT_PNG    = "lichens_tree_reads-bases.png"
OUT_PDF    = "lichens_tree_reads-bases.pdf"

# --- Load data ---
ncbi = NCBITaxa(TAXDB)
df_bins = pd.read_csv(CSV)

# -------------------------------- Prepare the table
df_bins = (df_bins
           .drop_duplicates(subset=["species"])
           .loc[:, ["species", "total_reads", "total_bases"]]
          )

# Units: reads in M; bases in Gbp
df_bins["reads_M"]   = df_bins["total_reads"] / 1e6
df_bins["bases_Gbp"] = df_bins["total_bases"] / 1e9

metrics = df_bins.set_index("species")[["reads_M", "bases_Gbp"]].to_dict(orient="index")

# Axis helpers
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

# ---- FIXED scale for READS: cap at 30 M ----
READS_MAX  = 30.0
READ_TICKS = list(range(0, 31, 10))   # 0..30 by 10

# ---- AUTO scale for BASES (Gbp) ----
BASES_MAX  = _nice_max(df_bins["bases_Gbp"].max() if len(df_bins) else 1.0)
BASE_TICKS = _ticks(BASES_MAX)

# Visual tuning for bar columns (images)
BAR_W      = 100   
BAR_H      = 20    
LEFT_GAP_PX = 24   # whitespace between labels and first column
BETWEEN_COL_GAP_PX = 12  # gap between the two numeric columns

GRID_CLR   = (229, 229, 229)  # faint grey grid (ticks)
BAR_CLR    = (100, 100, 100)  # bar fill color
BG_CLR     = (255, 255, 255)

# --------------------------------------------------------- Build the taxonomy tree
taxids = pd.read_csv(TAXIDS_CSV)["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=False)

translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    sci = translator.get(int(n.name), str(n.name))
    n.add_features(sci_name=sci, df_key=sci.replace(" ", "_"))

# Optional sanity check
tree_tips = {n.df_key for n in tree.iter_leaves()}
table_species = set(df_bins["species"].unique())
missing_in_table = sorted(tree_tips - table_species)
missing_in_tree  = sorted(table_species - tree_tips)
if missing_in_table:
    print("[warn] Tips not in bins table:", ", ".join(missing_in_table))
if missing_in_tree:
    print("[warn] Table species not in tree:", ", ".join(missing_in_tree))

# --- Styling (no node dots, thicker lines) ---
nstyle = NodeStyle()
nstyle["size"] = 0
nstyle["vt_line_width"] = 2
nstyle["hz_line_width"] = 2
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"
for n in tree.traverse():
    n.set_style(nstyle)

# ---------------------------------------------------------------- Bar images with shared ticks
_bar_cache = {}
_tmp_files = []

def _bar_img_face(value, vmax, ticks, w=BAR_W, h=BAR_H):
    """
    Draw one horizontal bar with faint vertical grid lines at `ticks`
    and a solid bar from 0 to `value`. Returns an ete3 faces.ImgFace.
    """
    key = (round(float(value), 6), round(float(vmax), 6),
           tuple(round(float(t), 6) for t in ticks), w, h)
    if key in _bar_cache:
        return _bar_cache[key]

    img = Image.new("RGB", (w, h), BG_CLR)
    draw = ImageDraw.Draw(img)

    # grid lines
    denom = vmax if vmax > 0 else 1.0
    for tk in ticks:
        x = int(round(w * (tk / denom)))
        draw.line([(x, 0), (x, h)], fill=GRID_CLR, width=1)

    # bar fill (clip at max)
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

# ---------------------------------------------------------------- Layout: name + left gap + Reads(M) + gap + Bases(Gbp)
def layout(node):
    if not node.is_leaf():
        return

    # left label
    faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")

    key = getattr(node, "df_key", None)
    vals = metrics.get(key)
    if not vals:
        return

    reads_M = float(vals["reads_M"])
    bases_G = float(vals["bases_Gbp"])

    # whitespace between label and first bar column
    faces.add_face_to_node(RectFace(LEFT_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=1, position="aligned")

    # Reads column (aligned)
    faces.add_face_to_node(_bar_img_face(reads_M, READS_MAX, READ_TICKS, w=BAR_W, h=BAR_H),
                           node, column=2, position="aligned")

    # gap between columns
    faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=3, position="aligned")

    # Bases column (aligned)
    faces.add_face_to_node(_bar_img_face(bases_G, BASES_MAX, BASE_TICKS, w=BAR_W, h=BAR_H),
                           node, column=4, position="aligned")

# --- TreeStyle (no legend at all) ---
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

# --- Render base PNG ---
tree.render(OUT_PNG, tree_style=ts, w=2400)

# ====== Post-process: add numbers once at the bottom, aligned to each column ======
GRID_RGB = GRID_CLR
AXIS_RGB = (0, 0, 0)
PAD_H    = 50    # bottom strip height

def _find_column_left_edges(img, search_top_frac=0.05, search_bottom_frac=0.95):
    """Detect the x of the leftmost grid line for each column (tick=0)."""
    w, h = img.size
    y0 = int(h * search_top_frac)
    y1 = int(h * search_bottom_frac)

    counts = [0]*w
    px = img.load()
    for x in range(w):
        c = 0
        for y in range(y0, y1):
            if px[x, y][:3] == GRID_RGB:
                c += 1
        counts[x] = c

    # strong vertical grid lines → spikes
    m = max(counts) if counts else 0
    thresh = m * 0.6 if m else 0
    spikes = [i for i, v in enumerate(counts) if v >= thresh]

    # group to peaks; take left edge of each
    edges = []
    if spikes:
        start = spikes[0]; prev = spikes[0]
        for x in spikes[1:]:
            if x == prev + 1:
                prev = x
            else:
                edges.append(start)
                start = prev = x
        edges.append(start)

    # keep the first two (reads, bases)
    edges = sorted(edges)[:2]
    return edges

# Load the rendered PNG
img = Image.open(OUT_PNG).convert("RGB")
W, H = img.size

# New canvas with bottom strip
canvas = Image.new("RGB", (W, H + PAD_H), (255, 255, 255))
canvas.paste(img, (0, 0))
draw = ImageDraw.Draw(canvas)

# Detect left edges of both numeric columns
edges = _find_column_left_edges(img)
if len(edges) == 2:
    x_reads, x_bases = edges[0], edges[1]
else:
    # Fallback: use a reasonable guess based on layout
    x_reads = edges[0] if edges else int(W * 0.55)
    x_bases = x_reads + BAR_W + BETWEEN_COL_GAP_PX + 1

# Save composited PNG + a PDF twin
canvas.save(OUT_PNG)
canvas.convert("RGB").save(OUT_PDF)

print(f"Exported: {OUT_PNG}, {OUT_PDF}")

# --- Cleanup temp files ---
for p in _tmp_files:
    try:
        os.remove(p)
    except OSError:
        pass
