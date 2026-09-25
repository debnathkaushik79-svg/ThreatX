import pandas as pd
import numpy as np


TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"


print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)


# =========================================================
# NUMERICAL COLUMNS
# =========================================================

numeric_columns = train_df.select_dtypes(
    include=["int64", "float64"]
).columns


print("\n========== NUMERICAL COLUMNS ==========")

print("Number of numerical columns:", len(numeric_columns))

print(numeric_columns.tolist())


# =========================================================
# INFINITE VALUES
# =========================================================

print("\n========== INFINITE VALUES ==========")

train_inf = np.isinf(
    train_df[numeric_columns]
).sum().sum()

test_inf = np.isinf(
    test_df[numeric_columns]
).sum().sum()

print("Training infinite values:", train_inf)
print("Testing infinite values :", test_inf)


# =========================================================
# MISSING VALUES
# =========================================================

print("\n========== MISSING VALUES ==========")

print(
    "Training:",
    train_df.isnull().sum().sum()
)

print(
    "Testing :",
    test_df.isnull().sum().sum()
)


# =========================================================
# DUPLICATES
# =========================================================

print("\n========== DUPLICATES ==========")

print(
    "Training duplicates:",
    train_df.duplicated().sum()
)

print(
    "Testing duplicates:",
    test_df.duplicated().sum()
)


# =========================================================
# UNIQUE VALUES
# =========================================================

print("\n========== UNIQUE VALUES ==========")

for column in ["proto", "service", "state"]:

    print(
        f"{column}: "
        f"training={train_df[column].nunique()}, "
        f"testing={test_df[column].nunique()}"
    )


# =========================================================
# NUMERICAL SUMMARY
# =========================================================

print("\n========== NUMERICAL SUMMARY ==========")

print(
    train_df[numeric_columns].describe().T
)