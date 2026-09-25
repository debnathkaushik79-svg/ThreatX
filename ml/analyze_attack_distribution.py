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
# ATTACK CATEGORY COUNTS
# =========================================================

train_counts = (
    train_df["attack_cat"]
    .value_counts()
)

test_counts = (
    test_df["attack_cat"]
    .value_counts()
)


# =========================================================
# CREATE COMPARISON TABLE
# =========================================================

comparison = pd.DataFrame({
    "training_count": train_counts,
    "testing_count": test_counts
})

comparison = comparison.fillna(0)


# =========================================================
# PERCENTAGES
# =========================================================

comparison["training_percentage"] = (
    comparison["training_count"]
    / len(train_df)
    * 100
)

comparison["testing_percentage"] = (
    comparison["testing_count"]
    / len(test_df)
    * 100
)


# =========================================================
# RATIO
# =========================================================

comparison["test_to_train_ratio"] = (
    comparison["testing_count"]
    / comparison["training_count"]
)


# =========================================================
# SORT
# =========================================================

comparison = comparison.sort_values(
    by="testing_count",
    ascending=False
)


# =========================================================
# DISPLAY
# =========================================================

print()
print("================================================")
print("        ATTACK CATEGORY DISTRIBUTION")
print("================================================")

print(
    comparison.to_string()
)


# =========================================================
# LABEL DISTRIBUTION
# =========================================================

print()
print("================================================")
print("             BINARY LABEL DISTRIBUTION")
print("================================================")

print()
print("Training:")

print(
    train_df["label"]
    .value_counts()
    .sort_index()
    .to_string()
)

print()
print("Testing:")

print(
    test_df["label"]
    .value_counts()
    .sort_index()
    .to_string()
)


# =========================================================
# ATTACK-ONLY DISTRIBUTION
# =========================================================

train_attacks = train_df[
    train_df["label"] == 1
]

test_attacks = test_df[
    test_df["label"] == 1
]


train_attack_distribution = (
    train_attacks["attack_cat"]
    .value_counts(normalize=True)
    * 100
)

test_attack_distribution = (
    test_attacks["attack_cat"]
    .value_counts(normalize=True)
    * 100
)


attack_comparison = pd.DataFrame({
    "training_attack_percentage":
        train_attack_distribution,

    "testing_attack_percentage":
        test_attack_distribution
})

attack_comparison = (
    attack_comparison
    .fillna(0)
)


attack_comparison["percentage_point_difference"] = (
    attack_comparison["testing_attack_percentage"]
    -
    attack_comparison["training_attack_percentage"]
)


attack_comparison = (
    attack_comparison
    .sort_values(
        by="testing_attack_percentage",
        ascending=False
    )
)


print()
print("================================================")
print("       ATTACK-ONLY DISTRIBUTION")
print("================================================")

print(
    attack_comparison.to_string()
)


# =========================================================
# SAVE
# =========================================================

comparison.to_csv(
    "data/attack_category_distribution.csv"
)

attack_comparison.to_csv(
    "data/attack_only_distribution.csv"
)


print()
print("================================================")
print("Analysis files saved:")
print()
print("data/attack_category_distribution.csv")
print("data/attack_only_distribution.csv")
print("================================================")

print()
print("Attack distribution analysis completed.")