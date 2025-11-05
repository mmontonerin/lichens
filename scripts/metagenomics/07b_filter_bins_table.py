import pandas as pd

df = pd.read_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/bins.csv")

# Rule:
# If a species+taxonomy combination has any eukcc bin,
# keep only the eukcc ones and drop metabat2 for that combination.

# Identify all (species, taxonomy) pairs that contain eukcc
pairs_with_eukcc = set(
    df.loc[df["binning_method"] == "eukcc", ["species", "taxonomy"]]
    .itertuples(index=False, name=None)
)

# Keep rows that:
# - are eukcc, or
# - are NOT part of a (species, taxonomy) pair that has eukcc
filtered = df[
    (df["binning_method"] == "eukcc")
    | (~df[["species", "taxonomy"]].apply(tuple, axis=1).isin(pairs_with_eukcc))
].copy()

# Save filtered table (optional)
filtered.to_csv("/lustre/scratch127/tol/teams/blaxter/users/mn16/lichens/results/metagenome/bins_filtered.csv", index=False)

print(f"Filtered: {len(df)} → {len(filtered)} rows kept")
print(
    f"Removed {len(df) - len(filtered)} metabat2 rows where eukcc existed for the same species+taxonomy"
)