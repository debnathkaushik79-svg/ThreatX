import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"


# =========================================================
# LOAD DATA
# =========================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)


# =========================================================
# SELECT FUZZER DATA
# =========================================================

train_fuzzers = train_df[
    train_df["attack_cat"] == "Fuzzers"
].copy()

test_fuzzers = test_df[
    test_df["attack_cat"] == "Fuzzers"
].copy()

train_normal = train_df[
    train_df["label"] == 0
].copy()

test_normal = test_df[
    test_df["label"] == 0
].copy()


# =========================================================
# DATASET SIZES
# =========================================================

print()
print("========== DATASET SIZES ==========")

print("Training Fuzzers :", len(train_fuzzers))
print("Testing Fuzzers  :", len(test_fuzzers))

print("Training Normal  :", len(train_normal))
print("Testing Normal   :", len(test_normal))


# =========================================================
# NUMERICAL FEATURES
# =========================================================

exclude_columns = [
    "id",
    "attack_cat",
    "label"
]

numerical_features = train_df.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

numerical_features = [
    col for col in numerical_features
    if col not in exclude_columns
]


# =========================================================
# COMPARE FEATURE MEANS
# =========================================================

comparison = pd.DataFrame(
    index=numerical_features
)

comparison["train_fuzzer_mean"] = (
    train_fuzzers[numerical_features].mean()
)

comparison["test_fuzzer_mean"] = (
    test_fuzzers[numerical_features].mean()
)

comparison["train_normal_mean"] = (
    train_normal[numerical_features].mean()
)

comparison["test_normal_mean"] = (
    test_normal[numerical_features].mean()
)


# =========================================================
# CALCULATE FUZZER DISTRIBUTION DIFFERENCE
# =========================================================

comparison["absolute_difference"] = (
    comparison["test_fuzzer_mean"]
    - comparison["train_fuzzer_mean"]
).abs()


comparison["percentage_difference"] = (
    comparison["absolute_difference"]
    / comparison["train_fuzzer_mean"].abs().replace(0, pd.NA)
) * 100


# =========================================================
# SORT BY DIFFERENCE
# =========================================================

comparison = comparison.sort_values(
    by="percentage_difference",
    ascending=False
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print()
print("================================================")
print("       FUZZER FEATURE DISTRIBUTION")
print("================================================")

print(
    comparison.to_string()
)


# =========================================================
# TOP FEATURES
# =========================================================

print()
print("================================================")
print("       TOP 15 DISTRIBUTION DIFFERENCES")
print("================================================")

print(
    comparison.head(15).to_string()
)


# =========================================================
# SAVE RESULTS
# =========================================================

output_file = "data/fuzzer_distribution_analysis.csv"

comparison.to_csv(output_file)

print()
print("Analysis saved to:")
print(output_file)

print()
print("Fuzzer distribution analysis completed.")