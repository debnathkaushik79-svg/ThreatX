import pandas as pd

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"


print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)


# =========================================================
# BASIC INFORMATION
# =========================================================

print("\n========== DATASET INFORMATION ==========")

print("Training shape:", train_df.shape)
print("Testing shape :", test_df.shape)


# =========================================================
# BINARY TARGET
# =========================================================

print("\n========== LABEL DISTRIBUTION ==========")

print(train_df["label"].value_counts())

print("\nLabel percentage:")
print(train_df["label"].value_counts(normalize=True) * 100)


# =========================================================
# ATTACK CATEGORY
# =========================================================

print("\n========== ATTACK CATEGORY DISTRIBUTION ==========")

print(train_df["attack_cat"].value_counts())


# =========================================================
# UNIQUE VALUES OF CATEGORICAL FEATURES
# =========================================================

print("\n========== CATEGORICAL FEATURES ==========")

for column in ["proto", "service", "state"]:
    print(f"\n{column}:")
    print(train_df[column].nunique(), "unique values")
    print(train_df[column].unique()[:20])


# =========================================================
# TARGET CROSS-CHECK
# =========================================================

print("\n========== LABEL vs ATTACK CATEGORY ==========")

print(
    pd.crosstab(
        train_df["attack_cat"],
        train_df["label"]
    )
)