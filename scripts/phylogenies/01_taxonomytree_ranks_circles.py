import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from ete3 import NCBITaxa, TreeStyle, TextFace, AttrFace, faces, NodeStyle

# Initialize and load NCBI taxonomy database
ncbi = NCBITaxa("/data/tol/resources/taxonomy/latest/taxa.sqlite")

# Read taxids from CSV
import pandas as pd
df = pd.read_csv("lichens_taxid.csv")
taxids = df["taxon"].astype(int).tolist()

# Build taxonomy tree (adds intermediate nodes automatically)
tree = ncbi.get_topology(taxids, intermediate_nodes=True)

# Optional: print tree in ASCII
#print(tree.get_ascii(attributes=["sci_name"], show_internal=False))

# Add the 'sci_name' attribute to each node (like ASCII uses)
# Add the scientific name and rank to each node
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
rank_map = ncbi.get_rank([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    n.add_features(
        sci_name=translator.get(int(n.name), str(n.name)),
        rank=rank_map.get(int(n.name))
    )

# Define colors per rank
RANK_COLORS = {
    "family": "#fce5cd",  # light beige
    "order":  "#c79562",  # medium brown
    "phylum": "#634322",  # dark brown
}

# Style branches and apply - no dots, thicker lines
nstyle = NodeStyle()
nstyle["shape"] = "square"   # (doesn’t matter, since size=0 hides it)
nstyle["size"] = 0           # hides node dots
nstyle["vt_line_width"] = 2  # vertical branch thickness
nstyle["hz_line_width"] = 2  # horizontal branch thickness
nstyle["vt_line_color"] = "black"
nstyle["hz_line_color"] = "black"

for n in tree.traverse():
    n.set_style(nstyle)

# Layout: only add colored dots for nodes with rank family/order/phylum
def layout(node):
    rank = getattr(node, "rank", None)
    if rank in RANK_COLORS:
        dot = faces.CircleFace(radius=6, color=RANK_COLORS[rank])
        dot.opacity = 1.0
        faces.add_face_to_node(dot, node, column=0, position="branch-right")
    if node.is_leaf():
        faces.add_face_to_node(AttrFace("sci_name", fsize=12), node, column=0, position="branch-right")


# Style: do NOT auto-draw node names; no internal/support/scale
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False          # <- prevents auto drawing of node.name (TaxIDs)
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"  # or "c" for circular

# Sort taxa in a fixed way
tree.ladderize(direction=1)  

# Export PNG/PDF — only species names at tips, just like the ASCII view
tree.render("lichens_taxonomy_tree_ranks.png", tree_style=ts, w=2400)
tree.render("lichens_taxonomy_tree_ranks.pdf", tree_style=ts, w=2400)