import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


# =========================================================
# FILE PATHS
# =========================================================

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"


# =========================================================
# LOAD DATA
# =========================================================

print("Loading training dataset...")

df = pd.read_csv(TRAINING_FILE)


# =========================================================
# SEPARATE FEATURES AND TARGET
# =========================================================

X = df.drop(
    columns=["id", "attack_cat", "label"]
)

y = df["label"]


# =========================================================
# IDENTIFY FEATURE TYPES
# =========================================================

categorical_features = X.select_dtypes(
    include=["str"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


print("\n========== FEATURES ==========")

print("Total features:", X.shape[1])

print("\nCategorical features:")
print(categorical_features)

print("\nNumber of numerical features:")
print(len(numerical_features))


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
# FIT TRANSFORMER
# =========================================================

print("\nFitting preprocessor...")

X_processed = preprocessor.fit_transform(X)


# =========================================================
# RESULT
# =========================================================

print("\n========== PREPROCESSING RESULT ==========")

print("Original feature count :", X.shape[1])

print("Processed feature shape:", X_processed.shape)

print("\nTarget shape:", y.shape)

print("\nPreprocessing completed successfully.")