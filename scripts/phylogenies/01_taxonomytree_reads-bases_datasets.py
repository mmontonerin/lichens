import os
import glob
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from ete3 import faces, AttrFace, RectFace, NodeStyle, NCBITaxa, TreeStyle, TextFace
from ete3 import faces as ete_faces
import pandas as pd
from PIL import Image, ImageDraw
import tempfile, math
import yaml

# --- Inputs ---
TAXDB = "/data/tol/resources/taxonomy/latest/taxa.sqlite"
TAXIDS_CSV = "lichens_taxid.csv"  # columns: taxon (NCBI taxid)
CSV   = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents_reads/domain_all_combined_filtered_bp.csv"
OUT_PNG    = "lichens_tree_reads-bases_dataset.png"
OUT_PDF    = "lichens_tree_reads-bases_dataset.pdf"
YAML_DIR = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/yamls"

PACBIO_ICON  = "●"   # one per PacBio fasta entry
HIC_ICON     = "★"   # one per Hi-C cram entry
PACBIO_COLOR = "#2C3E50"
HIC_COLOR    = "#E74C3C"

NAME_FSIZE   = 12
ICON_FSIZE   = 14

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
LEFT_GAP_PX = 40   # whitespace between labels and first column
BETWEEN_COL_GAP_PX = 12  # gap between the two numeric columns
BETWEEN_DATA_COL = 12 # gap between datsets and base/reads data

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


# Scan YAMLs to count PacBio/Hi-C per species ----------
def load_yaml_counts(yaml_dir):
    """
    Returns dict mapping 'Genus species' -> (pacbio_count, hic_count)
    from *.yaml files with structure:
      id: Caloplaca_littorea
      pacbio: { fasta: [ ... ] }
      hic:    { cram:  [ ... ] }
    """
    counts = {}
    for path in glob.glob(os.path.join(yaml_dir, "*.yaml")):
        try:
            with open(path, "r") as fh:
                y = yaml.safe_load(fh) or {}
        except Exception:
            continue

        sp_id = str(y.get("id", "")).strip()
        if not sp_id:
            sp_id = os.path.splitext(os.path.basename(path))[0]
        sci_space = sp_id.replace("_", " ")

        pacbio_count = 0
        hic_count = 0

        pacbio = y.get("pacbio", {})
        if isinstance(pacbio, dict):
            fasta_list = pacbio.get("fasta", []) or []
            if isinstance(fasta_list, list):
                pacbio_count = len(fasta_list)

        hic = y.get("hic", {})
        if isinstance(hic, dict):
            cram_list = hic.get("cram", []) or []
            if isinstance(cram_list, list):
                hic_count = len(cram_list)

        counts[sci_space] = (pacbio_count, hic_count)
    return counts

yaml_counts = load_yaml_counts(YAML_DIR)

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

    sci = node.sci_name  # "Genus species"
    pb_cnt, hic_cnt = yaml_counts.get(sci, (0, 0))

    # left label
    faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")

    key = getattr(node, "df_key", None)
    vals = metrics.get(key)
    if not vals:
        return

    reads_M = float(vals["reads_M"])
    bases_G = float(vals["bases_Gbp"])

    # Add gap
    spacer = RectFace(LEFT_GAP_PX, 1, fgcolor=None, bgcolor=None)
    faces.add_face_to_node(spacer, node, column=1, position="aligned")

    # PacBio icons (one ● per fasta)
    if pb_cnt > 0:
        pb_face = TextFace(PACBIO_ICON * pb_cnt, fsize=ICON_FSIZE, fgcolor=PACBIO_COLOR)
        pb_face.margin_left = 6
        faces.add_face_to_node(pb_face, node, column=2, position="aligned")

    # Hi-C icons (one ★ per cram)
    if hic_cnt > 0:
        hic_face = TextFace(HIC_ICON * hic_cnt, fsize=ICON_FSIZE, fgcolor=HIC_COLOR)
        hic_face.margin_left = 6
        faces.add_face_to_node(hic_face, node, column=3, position="aligned")

    # whitespace between label and first bar column
    faces.add_face_to_node(RectFace(BETWEEN_DATA_COL, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=4, position="aligned")

    # Reads column (aligned)
    faces.add_face_to_node(_bar_img_face(reads_M, READS_MAX, READ_TICKS, w=BAR_W, h=BAR_H),
                           node, column=5, position="aligned")

    # gap between columns
    faces.add_face_to_node(RectFace(BETWEEN_COL_GAP_PX, BAR_H, fgcolor=None, bgcolor=None),
                           node, column=6, position="aligned")

    # Bases column (aligned)
    faces.add_face_to_node(_bar_img_face(bases_G, BASES_MAX, BASE_TICKS, w=BAR_W, h=BAR_H),
                           node, column=7, position="aligned")

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

#Fixed tree topology
tree.ladderize(direction=1)  

# Legend (only dataset markers)
ts.legend.add_face(TextFace(" ●  PacBio", fsize=10, fgcolor=PACBIO_COLOR), column=0)
ts.legend.add_face(TextFace("   ★  Hi-C",  fsize=10, fgcolor=HIC_COLOR),   column=1)

# --- Render base PNG ---
tree.render(OUT_PNG, tree_style=ts, w=2400)

# --- Cleanup temp files ---
for p in _tmp_files:
    try:
        os.remove(p)
    except OSError:
        pass
