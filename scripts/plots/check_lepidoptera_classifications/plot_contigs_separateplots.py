import os
import gzip
import pandas as pd
import matplotlib.pyplot as plt

# -------- PATHS --------
base_dir = "/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results"
meta_dir = os.path.join(base_dir, "metagenome")
kraken_dir = os.path.join(base_dir, "kraken2/01_kraken_translated_btk")
output_dir = os.path.join(base_dir, "kraken2/plots_gc_log-depth_length_separated")

os.makedirs(output_dir, exist_ok=True)

# -------- FUNCTIONS --------
def compute_gc(seq):
    seq = seq.upper()
    gc = seq.count("G") + seq.count("C")
    return gc / len(seq) if len(seq) > 0 else 0


def parse_fasta_gc(fasta_path):
    gc_dict = {}

    with gzip.open(fasta_path, "rt") as f:
        contig = None
        seq_chunks = []

        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if contig:
                    seq = "".join(seq_chunks)
                    gc_dict[contig] = compute_gc(seq)
                contig = line[1:].split()[0]
                seq_chunks = []
            else:
                seq_chunks.append(line)

        # last contig
        if contig:
            seq = "".join(seq_chunks)
            gc_dict[contig] = compute_gc(seq)

    return gc_dict

def plot_pairwise(df, output_prefix, title):
    import matplotlib.pyplot as plt

    # Remove zero depth (log scale issue)
    df = df[df["totalAvgDepth"] > 0]

    lep = df[df["is_lep"]]
    other = df[~df["is_lep"]]

    # ---- 1. GC vs Depth ----
    plt.figure(figsize=(6, 5))

    plt.scatter(other["GC"], other["totalAvgDepth"], alpha=0.4, label="Other contigs")
    plt.scatter(lep["GC"], lep["totalAvgDepth"], alpha=0.9, label="Lepidoptera contigs")

    plt.yscale("log")
    plt.xlabel("GC content")
    plt.ylabel("Average depth (log)")
    plt.title(f"{title} - GC vs Depth")
    plt.legend()

    plt.savefig(f"{output_prefix}_GC_vs_Depth.png", dpi=300)
    plt.close()

    # ---- 2. GC vs Length ----
    plt.figure(figsize=(6, 5))

    plt.scatter(other["GC"], other["contigLen"], alpha=0.4, label="Other contigs")
    plt.scatter(lep["GC"], lep["contigLen"], alpha=0.9, label="Lepidoptera contigs")

    plt.xlabel("GC content")
    plt.ylabel("Contig length")
    plt.title(f"{title} - GC vs Length")
    plt.legend()

    plt.savefig(f"{output_prefix}_GC_vs_Length.png", dpi=300)
    plt.close()

    # ---- 3. Depth vs Length ----
    plt.figure(figsize=(6, 5))

    plt.scatter(other["totalAvgDepth"], other["contigLen"], alpha=0.4, label="Other contigs")
    plt.scatter(lep["totalAvgDepth"], lep["contigLen"], alpha=0.9, label="Lepidoptera contigs")

    plt.xscale("log")
    plt.xlabel("Average depth (log)")
    plt.ylabel("Contig length")
    plt.title(f"{title} - Depth vs Length")
    plt.legend()

    plt.savefig(f"{output_prefix}_Depth_vs_Length.png", dpi=300)
    plt.close()

# -------- MAIN --------
all_data = []

for sp in os.listdir(meta_dir):
    sp_dir = os.path.join(meta_dir, sp)

    fasta_path = os.path.join(
        sp_dir, "assembly/fasta", f"{sp}_metamdbg.contigs.fasta.gz"
    )
    kraken_path = os.path.join(
        kraken_dir, f"{sp}_metamdbg.contigs_kraken_nt.out_lineage.tsv"
    )
    depth_path = os.path.join(
        sp_dir, "assembly/depth", f"{sp}_metamdbg_depth.tsv"
    )

    if not (os.path.exists(fasta_path) and os.path.exists(kraken_path) and os.path.exists(depth_path)):
        continue

    print(f"Processing {sp}...")

    # GC content
    gc_dict = parse_fasta_gc(fasta_path)
    gc_df = pd.DataFrame(list(gc_dict.items()), columns=["contig_id", "GC"])

    # Kraken
    kraken_df = pd.read_csv(kraken_path, sep="\t", usecols=["contig_id", "order"])
    kraken_df["is_lep"] = kraken_df["order"] == "Lepidoptera"

    # Depth
    depth_df = pd.read_csv(depth_path, sep="\t")
    depth_df = depth_df.rename(columns={"contigName": "contig_id"})

    # Merge
    df = gc_df.merge(kraken_df, on="contig_id", how="inner")
    df = df.merge(depth_df[["contig_id", "contigLen", "totalAvgDepth"]], on="contig_id", how="inner")

    df["species"] = sp

    # Save per-species plot

    output_prefix = os.path.join(output_dir, sp)
    plot_pairwise(df, output_prefix, sp)

    all_data.append(df)

# -------- COMBINED PLOT --------
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)

    output_prefix = os.path.join(output_dir, "ALL_species")
    plot_pairwise(combined_df, output_prefix, "All species combined")