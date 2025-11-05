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
print(tree.get_ascii(attributes=["sci_name"], show_internal=False))

# Add the 'sci_name' attribute to each node (like ASCII uses)
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    # keep node.name as-is (TaxID) so we can control rendering cleanly
    n.add_features(sci_name=translator.get(int(n.name), str(n.name)))

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

# Layout: draw exactly ONE label per leaf using the sci_name attribute
def layout(node):
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
tree.render("lichens_taxonomy_tree.png", tree_style=ts, w=2400)
tree.render("lichens_taxonomy_tree.pdf", tree_style=ts, w=2400)

# Newick with ONLY tip names (no internal labels):
tree_tips_only = tree.copy()
for n in tree_tips_only.traverse():
    if n.is_leaf():
        n.name = n.sci_name
    else:
        n.name = ""  # blank internal labels
tree_tips_only.write(outfile="lichens_taxonomy_tips_only.nwk", format=1)