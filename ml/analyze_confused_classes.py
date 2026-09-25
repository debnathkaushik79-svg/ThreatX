# =========================================================
# ThreatX — Analysis of Highly Confused Attack Classes
# =========================================================

import pandas as pd
import numpy as np


# =========================================================
# CONFIGURATION
# =========================================================

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"

TARGET_CLASSES = [
    "DoS",
    "Exploits",
    "Fuzzers"
]


# =========================================================
# LOAD DATA
# =========================================================

print("Loading dataset...")

df = pd.read_csv(TRAIN_PATH)

print(
    "Original shape:",
    df.shape
)


# =========================================================
# SELECT TARGET CLASSES
# =========================================================

df = df[
    df["attack_cat"].isin(TARGET_CLASSES)
].copy()

print(
    "\nSelected classes:"
)

print(
    df["attack_cat"]
    .value_counts()
)


# =========================================================
# SELECT NUMERIC FEATURES
# =========================================================

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

# Remove identifiers / target columns
exclude_columns = [
    "id",
    "label"
]

numeric_columns = [
    col
    for col in numeric_columns
    if col not in exclude_columns
]


# =========================================================
# GROUP STATISTICS
# =========================================================

print("\n")
print("=" * 70)
print("MEAN FEATURE VALUES")
print("=" * 70)

means = (
    df.groupby("attack_cat")[numeric_columns]
    .mean()
    .T
)

print(
    means.to_string()
)


# =========================================================
# STANDARDIZED DIFFERENCE
# =========================================================

print("\n")
print("=" * 70)
print("FEATURE SEPARATION")
print("=" * 70)

results = []

for feature in numeric_columns:

    grouped = (
        df.groupby("attack_cat")[feature]
        .mean()
    )

    # Range of class means
    mean_range = (
        grouped.max() - grouped.min()
    )

    # Overall standard deviation
    overall_std = df[feature].std()

    if overall_std == 0 or pd.isna(overall_std):
        separation = 0
    else:
        separation = (
            mean_range / overall_std
        )

    results.append({
        "feature": feature,
        "mean_range": mean_range,
        "standardized_separation": separation
    })


separation_df = pd.DataFrame(
    results
)

separation_df = separation_df.sort_values(
    by="standardized_separation",
    ascending=False
)


# =========================================================
# DISPLAY TOP FEATURES
# =========================================================

print("\nTop 25 features separating")
print("DoS / Exploits / Fuzzers:\n")

print(
    separation_df
    .head(25)
    .to_string(index=False)
)


# =========================================================
# SAVE RESULTS
# =========================================================

output_path = (
    "data/confused_class_feature_analysis.csv"
)

separation_df.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved to: {output_path}"
)

print("\nAnalysis completed.")