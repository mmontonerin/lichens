import os
import glob
import yaml
import pandas as pd
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from ete3 import NCBITaxa, TreeStyle, TextFace, AttrFace, faces, NodeStyle, RectFace

# ---------- 0) Config ----------
YAML_DIR = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/scripts/metagenomics/yamls"
NCBI_DB  = "/data/tol/resources/taxonomy/latest/taxa.sqlite"

PACBIO_ICON  = "●"   # one per PacBio fasta entry
HIC_ICON     = "★"   # one per Hi-C cram entry
PACBIO_COLOR = "#2C3E50"
HIC_COLOR    = "#E74C3C"

NAME_FSIZE   = 12
ICON_FSIZE   = 14

# ---------- 1) Load taxonomy ----------
ncbi = NCBITaxa(NCBI_DB)
df = pd.read_csv("lichens_taxid.csv")
taxids = df["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=True)

translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    n.add_features(sci_name=translator.get(int(n.name), str(n.name)))

# ---------- 2) Scan YAMLs to count PacBio/Hi-C per species ----------
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

# ---------- 3) Basic tree styling ----------
nstyle = NodeStyle()
nstyle["size"] = 0
nstyle["vt_line_width"] = 2
nstyle["hz_line_width"] = 2
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"
for n in tree.traverse():
    n.set_style(nstyle)

LEFT_GAP_PX = 40

# ---------- 4) Layout: name + PacBio/Hi-C icons ----------
def layout(node):
    if not node.is_leaf():
        return

    sci = node.sci_name  # "Genus species"
    pb_cnt, hic_cnt = yaml_counts.get(sci, (0, 0))

    # Tip name
    faces.add_face_to_node(AttrFace("sci_name", fsize=NAME_FSIZE), node, column=0, position="branch-right")

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

# ---------- 5) TreeStyle + legend ----------
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"

#Fixed tree topology
tree.ladderize(direction=1)  

# Legend (only dataset markers)
ts.legend.add_face(TextFace(" ●  PacBio", fsize=10, fgcolor=PACBIO_COLOR), column=0)
ts.legend.add_face(TextFace("   ★  Hi-C",  fsize=10, fgcolor=HIC_COLOR),   column=1)

# ---------- 6) Render ----------
tree.render("lichens_taxonomy_datasets-hicpacbio.png", tree_style=ts, w=2400)
tree.render("lichens_taxonomy_datasets-hicpacbio.pdf", tree_style=ts, w=2400)
