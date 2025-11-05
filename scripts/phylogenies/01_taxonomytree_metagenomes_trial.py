import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from ete3 import NCBITaxa, TreeStyle, CircleFace, faces, NodeStyle, Tree
import pandas as pd

# --- Inputs ---
TAXDB = "/data/tol/resources/taxonomy/latest/taxa.sqlite"
TAXIDS_CSV = "lichens_taxid.csv"          # columns: taxon (NCBI taxid)
BINS_CSV   = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/bins_filtered.csv"
OUT_PNG    = "lichens_tree_bins.png"
OUT_PDF    = "lichens_tree_bins.pdf"

# --- Load data ---
ncbi = NCBITaxa(TAXDB)
df_bins = pd.read_csv(BINS_CSV)

# Keep only bins with >=10% completeness
df_bins["completeness"] = pd.to_numeric(df_bins["completeness"], errors="coerce")
before = len(df_bins)
df_bins = df_bins[df_bins["completeness"] >= 10].copy()
removed = before - len(df_bins)
if removed:
    print(f"[info] Excluded {removed} bins with <10% completeness")

# Normalize species naming to match your bins table
# (bins use underscores; NCBI returns 'Genus species')
taxids = pd.read_csv(TAXIDS_CSV)["taxon"].astype(int).tolist()
tree = ncbi.get_topology(taxids, intermediate_nodes=False)  # <-- no parent ranks injected

# Translate taxids -> scientific names, then -> underscore form to match df
translator = ncbi.get_taxid_translator([int(n.name) for n in tree.traverse()])
for n in tree.traverse():
    sci = translator.get(int(n.name), str(n.name))
    n.add_features(sci_name=sci, df_key=sci.replace(" ", "_"))  # df_key matches df_bins["species"]

# Optional sanity check: which tree tips aren’t in your table?
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

# --- Colors for phyla ---
colors = {
    "cyanobacteriota": "#F1C40F",  
    "ascomycota":      "#B39DDB",  
    "chlorophyta":     "#66BB6A",  
    "basidiomycota":   "#ea97e3",  
}

# --- Layout: show only species names at tips + one circle per BIN (keeps multiplicity) ---
def layout(node):
    if node.is_leaf():
        # species label at tip
        faces.add_face_to_node(faces.TextFace(node.sci_name, fsize=12), node, column=0, position="branch-right")

        # all bins for this species
        bins = df_bins[df_bins["species"] == node.df_key]
        # draw each bin as a colored circle (color=phylum, size=by completeness)
        col = 1
        for _, row in bins.iterrows():
            ph = str(row["phylum"]).lower()
            comp = float(row["completeness"])
            color = colors.get(ph, "gray")
            size = 4 + (comp / 10.0)     # scale completeness -> radius (tweak to taste)
            cf = CircleFace(radius=size, color=color, style="circle")
            cf.opacity = 0.8
            node.add_face(cf, column=col, position="aligned")
            col += 1

# --- TreeStyle: no auto-names, no supports/scale ---
ts = TreeStyle()
ts.layout_fn = layout
ts.show_leaf_name = False
ts.show_branch_length = False
ts.show_branch_support = False
ts.show_scale = False
ts.mode = "r"  # "r" rectangular; use "c" for circular

# Sort taxa in a fixed way
tree.ladderize(direction=1)  

# --- Render ---
tree.render(OUT_PNG, tree_style=ts, w=2400)
tree.render(OUT_PDF, tree_style=ts, w=2400)


print(f"Exported: {OUT_PNG}, {OUT_PDF}")
