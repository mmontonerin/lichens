import os
import pandas as pd
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from ete3 import NCBITaxa, TreeStyle, TextFace, AttrFace, faces, NodeStyle, RectFace
from PIL import Image, ImageDraw
import tempfile, os

# Initialize and load NCBI taxonomy database
ncbi = NCBITaxa("/data/tol/resources/taxonomy/latest/taxa.sqlite")

# Tables taxid and kraken2 result table
df = pd.read_csv("lichens_taxid.csv")
taxids = df["taxon"].astype(int).tolist()
domain = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports/domain_all_combined_filtered.csv")
kingdom = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/kraken2/00_csv-rank_reports_includeparents/kingdom_all_combined_filtered.csv") 

taxids = df["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=True)

# Add sci_name attribute for all nodes (we’ll only display it on leaves)
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    n.add_features(sci_name=translator.get(int(n.name), str(n.name)))

# build percent maps
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

# Tree styling
nstyle = NodeStyle()
nstyle["size"] = 0
nstyle["vt_line_width"] = 2
nstyle["hz_line_width"] = 2
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"
for n in tree.traverse():
    n.set_style(nstyle)

# Draw bars entirely in memory
BAR_W, BAR_H = 140, 12
GREY   = (221, 221, 221)
_bar_cache = {}
_tmp_files = []   # track temp files to delete afterwards

COL_DOMAIN = {"Bacteria": (241, 196, 15), "Eukaryota": (108, 92, 231)}
COL_EUK    = {"Fungi": (179, 157, 219), "Metazoa": (129, 212, 250), "Viridiplantae": (102, 187, 106)}

_bar_cache = {}

def make_bar_face(segments, width=BAR_W, height=BAR_H):
    key = tuple((tuple(c), round(float(p), 2)) for c, p in segments)
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
    img.save(tf.name)
    tf.close()
    _tmp_files.append(tf.name)

    face = faces.ImgFace(tf.name)
    face.margin_left = face.margin_right = face.margin_top = face.margin_bottom = 0
    _bar_cache[key] = face
    return face

# Layout: name + domain bar + eukaryote bar
def layout(node):
    if not node.is_leaf():
        return

    sci = node.sci_name
    # Tip name
    faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")

    # Domain bar (Bacteria / Eukaryota + grey remainder)
    dvals = domain_map.get(sci, (0.0, 0.0))
    d_segments = [
        (COL_DOMAIN["Bacteria"],  dvals[0]),
        (COL_DOMAIN["Eukaryota"], dvals[1]),
    ]
    faces.add_face_to_node(make_bar_face(d_segments), node, column=1, position="aligned")

    # Spacer (white gap between the two bars)
    spacer = faces.RectFace(10, BAR_H, fgcolor=None, bgcolor="white")
    spacer.margin_left = spacer.margin_right = 5  
    faces.add_face_to_node(spacer, node, column=2, position="aligned")

    # Eukaryote bar (Fungi / Metazoa / Viridiplantae + grey remainder)
    evals = kingdom_map.get(sci, (0.0, 0.0, 0.0))
    e_segments = [
        (COL_EUK["Fungi"],         evals[0]),
        (COL_EUK["Metazoa"],       evals[1]),
        (COL_EUK["Viridiplantae"], evals[2]),
    ]
    faces.add_face_to_node(make_bar_face(e_segments), node, column=3, position="aligned")

# TreeStyle and render
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"

# Legend
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

# Fixed tree topology
tree.ladderize(direction=1)  

# render tree
tree.render("lichens_taxonomy_domain+euk.png", tree_style=ts, w=2400)
tree.render("lichens_taxonomy_domain+euk.pdf", tree_style=ts, w=2400)

# Remove temp bar images
for p in _tmp_files:
    try:
        os.remove(p)
    except OSError:
        pass
