import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


# =========================================================
# CONFIGURATION
# =========================================================

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)

print("Training shape :", train_df.shape)
print("Testing shape  :", test_df.shape)


# =========================================================
# PREPARE FEATURES
# =========================================================

X_train_full = train_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_train_full = train_df["label"]

X_test = test_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_test = test_df["label"]


# =========================================================
# FEATURE TYPES
# =========================================================

categorical_features = X_train_full.select_dtypes(
    include=["object", "str"]
).columns.tolist()

numerical_features = X_train_full.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_train_full
)


# =========================================================
# PREPROCESSOR
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# =========================================================
# RANDOM FOREST
# =========================================================

model = RandomForestClassifier(
    n_estimators=150,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# =========================================================
# PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# =========================================================
# TRAIN
# =========================================================

print()
print("Training Random Forest...")

pipeline.fit(X_train, y_train)

print("Training completed.")


# =========================================================
# PREDICT TEST DATA
# =========================================================

print()
print("Generating predictions...")

y_pred = pipeline.predict(X_test)


# =========================================================
# ADD PREDICTION
# =========================================================

test_analysis = test_df.copy()

test_analysis["prediction"] = y_pred


# =========================================================
# CREATE GROUPS
# =========================================================

missed_fuzzers = test_analysis[
    (test_analysis["attack_cat"] == "Fuzzers") &
    (test_analysis["prediction"] == 0)
].copy()

detected_fuzzers = test_analysis[
    (test_analysis["attack_cat"] == "Fuzzers") &
    (test_analysis["prediction"] == 1)
].copy()

normal_samples = test_analysis[
    test_analysis["attack_cat"] == "Normal"
].copy()


print()
print("================================================")
print("                 GROUP SIZES")
print("================================================")

print("Detected Fuzzers :", len(detected_fuzzers))
print("Missed Fuzzers   :", len(missed_fuzzers))
print("Normal samples   :", len(normal_samples))


# =========================================================
# NUMERICAL FEATURES
# =========================================================

analysis_features = [
    col for col in numerical_features
    if col not in ["id", "label"]
]


# =========================================================
# FUNCTION: STANDARDIZED DIFFERENCE
# =========================================================

def standardized_difference(group_a, group_b):

    mean_a = group_a.mean()
    mean_b = group_b.mean()

    std_a = group_a.std()
    std_b = group_b.std()

    pooled_std = np.sqrt(
        (std_a ** 2 + std_b ** 2) / 2
    )

    result = (mean_a - mean_b) / pooled_std.replace(
        0,
        np.nan
    )

    return result.abs()


# =========================================================
# MISSED VS DETECTED
# =========================================================

print()
print("================================================")
print("      MISSED VS DETECTED FUZZER ANALYSIS")
print("================================================")

comparison_fd = pd.DataFrame(
    index=analysis_features
)

comparison_fd["detected_mean"] = (
    detected_fuzzers[analysis_features].mean()
)

comparison_fd["missed_mean"] = (
    missed_fuzzers[analysis_features].mean()
)

comparison_fd["detected_median"] = (
    detected_fuzzers[analysis_features].median()
)

comparison_fd["missed_median"] = (
    missed_fuzzers[analysis_features].median()
)

comparison_fd["standardized_difference"] = (
    standardized_difference(
        detected_fuzzers[analysis_features],
        missed_fuzzers[analysis_features]
    )
)

comparison_fd = comparison_fd.sort_values(
    by="standardized_difference",
    ascending=False
)


print()
print(
    comparison_fd.head(20).to_string()
)


# =========================================================
# MISSED FUZZERS VS NORMAL
# =========================================================

print()
print("================================================")
print("        MISSED FUZZERS VS NORMAL")
print("================================================")

comparison_fn = pd.DataFrame(
    index=analysis_features
)

comparison_fn["missed_fuzzer_mean"] = (
    missed_fuzzers[analysis_features].mean()
)

comparison_fn["normal_mean"] = (
    normal_samples[analysis_features].mean()
)

comparison_fn["missed_fuzzer_median"] = (
    missed_fuzzers[analysis_features].median()
)

comparison_fn["normal_median"] = (
    normal_samples[analysis_features].median()
)

comparison_fn["standardized_difference"] = (
    standardized_difference(
        missed_fuzzers[analysis_features],
        normal_samples[analysis_features]
    )
)

comparison_fn = comparison_fn.sort_values(
    by="standardized_difference",
    ascending=False
)


print()
print(
    comparison_fn.head(20).to_string()
)


# =========================================================
# CATEGORICAL ANALYSIS
# =========================================================

print()
print("================================================")
print("           CATEGORICAL COMPARISON")
print("================================================")


for feature in categorical_features:

    print()
    print("------------------------------------------------")
    print("Feature:", feature)
    print("------------------------------------------------")

    missed_distribution = (
        missed_fuzzers[feature]
        .value_counts(normalize=True)
        .head(10)
        * 100
    )

    detected_distribution = (
        detected_fuzzers[feature]
        .value_counts(normalize=True)
        .head(10)
        * 100
    )

    normal_distribution = (
        normal_samples[feature]
        .value_counts(normalize=True)
        .head(10)
        * 100
    )

    print()
    print("Missed Fuzzers (%):")
    print(missed_distribution.to_string())

    print()
    print("Detected Fuzzers (%):")
    print(detected_distribution.to_string())

    print()
    print("Normal (%):")
    print(normal_distribution.to_string())


# =========================================================
# SAVE RESULTS
# =========================================================

comparison_fd.to_csv(
    "data/fuzzer_detected_vs_missed_similarity.csv"
)

comparison_fn.to_csv(
    "data/fuzzer_missed_vs_normal_similarity.csv"
)


print()
print("================================================")
print("Analysis files saved:")
print()
print("data/fuzzer_detected_vs_missed_similarity.csv")
print("data/fuzzer_missed_vs_normal_similarity.csv")
print("================================================")

print()
print("Fuzzer similarity analysis completed.")