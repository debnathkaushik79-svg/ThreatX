# =========================================================
# ThreatX — Targeted Feature-Engineered Random Forest
# =========================================================

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from ml.feature_engineering import add_features


# =========================================================
# CONFIGURATION
# =========================================================

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"
TEST_PATH = "data/UNSW_NB15_testing-set.csv"

MODEL_PATH = "models/targeted_feature_engineered_rf.pkl"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("=" * 70)
print("ThreatX — Targeted Feature-Engineered Random Forest")
print("=" * 70)

print("\nLoading training data...")
train_df = pd.read_csv(TRAIN_PATH)

print("Loading testing data...")
test_df = pd.read_csv(TEST_PATH)

print("\nTraining shape:", train_df.shape)
print("Testing shape :", test_df.shape)



# =========================================================
# APPLY FEATURE ENGINEERING
# =========================================================

print("\nApplying feature engineering...")

train_df = add_features(train_df)
test_df = add_features(test_df)

print("New training shape:", train_df.shape)
print("New testing shape :", test_df.shape)


# =========================================================
# TARGET
# =========================================================

TARGET = "label"

y_train_full = train_df[TARGET]
y_test = test_df[TARGET]


# =========================================================
# REMOVE TARGET-RELATED / ID COLUMNS
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]

X_train_full = train_df.drop(
    columns=DROP_COLUMNS
)

X_test = test_df.drop(
    columns=DROP_COLUMNS
)


# =========================================================
# IDENTIFY COLUMN TYPES
# =========================================================

categorical_columns = X_train_full.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_columns = X_train_full.select_dtypes(
    include=np.number
).columns.tolist()

print("\nFeature information:")
print("Numeric features     :", len(numeric_columns))
print("Categorical features :", len(categorical_columns))
print("Total raw features   :", len(X_train_full.columns))


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_val, y_train, y_val = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_train_full
)

print("\nDataset split:")
print("Training   :", X_train.shape)
print("Validation :", X_val.shape)
print("Test       :", X_test.shape)


# =========================================================
# PREPROCESSING
# =========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numeric_pipeline,
            numeric_columns
        ),
        (
            "cat",
            categorical_pipeline,
            categorical_columns
        )
    ]
)


# =========================================================
# RANDOM FOREST
# =========================================================

rf = RandomForestClassifier(
    n_estimators=300,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            rf
        )
    ]
)


# =========================================================
# TRAIN
# =========================================================

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# VALIDATION
# =========================================================

print("\n")
print("=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

y_val_pred = model.predict(X_val)


val_accuracy = accuracy_score(
    y_val,
    y_val_pred
)

val_precision = precision_score(
    y_val,
    y_val_pred,
    zero_division=0
)

val_recall = recall_score(
    y_val,
    y_val_pred,
    zero_division=0
)

val_f1 = f1_score(
    y_val,
    y_val_pred,
    zero_division=0
)


print(f"\nAccuracy  : {val_accuracy:.4f}")
print(f"Precision : {val_precision:.4f}")
print(f"Recall    : {val_recall:.4f}")
print(f"F1 Score  : {val_f1:.4f}")


print("\nClassification Report:")

print(
    classification_report(
        y_val,
        y_val_pred,
        target_names=[
            "Normal",
            "Attack"
        ],
        zero_division=0
    )
)


print("Confusion Matrix:")

print(
    confusion_matrix(
        y_val,
        y_val_pred
    )
)


# =========================================================
# OFFICIAL TEST SET
# =========================================================

print("\n")
print("=" * 70)
print("OFFICIAL TEST RESULTS")
print("=" * 70)

y_test_pred = model.predict(X_test)


test_accuracy = accuracy_score(
    y_test,
    y_test_pred
)

test_precision = precision_score(
    y_test,
    y_test_pred,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    y_test_pred,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    y_test_pred,
    zero_division=0
)


print(f"\nAccuracy  : {test_accuracy:.4f}")
print(f"Precision : {test_precision:.4f}")
print(f"Recall    : {test_recall:.4f}")
print(f"F1 Score  : {test_f1:.4f}")


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_test_pred,
        target_names=[
            "Normal",
            "Attack"
        ],
        zero_division=0
    )
)


print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_test_pred
    )
)


# =========================================================
# SAVE MODEL
# =========================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\n")
print("=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(f"\nSaved to: {MODEL_PATH}")

print("\nAnalysis completed.")