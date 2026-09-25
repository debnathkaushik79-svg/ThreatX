# =========================================================
# ThreatX — Stage 2 Hierarchical Attack Classifier
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


# =========================================================
# CONFIGURATION
# =========================================================

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"

MODEL_PATH = "models/hierarchical_attack_classifier.pkl"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("=" * 70)
print("ThreatX — Stage 2 Hierarchical Attack Classifier")
print("=" * 70)

print("\nLoading training data...")

df = pd.read_csv(TRAIN_PATH)

print("Original shape:", df.shape)


# =========================================================
# KEEP ONLY ATTACK TRAFFIC
# =========================================================

df = df[df["label"] == 1].copy()

print("\nAttack-only shape:", df.shape)

print("\nAttack distribution:")

print(
    df["attack_cat"]
    .value_counts()
)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def add_features(df):

    df = df.copy()

    # -----------------------------------------------------
    # Existing 17 engineered features
    # -----------------------------------------------------

    df["sbytes_per_packet"] = (
        df["sbytes"] / (df["spkts"] + 1)
    )

    df["dbytes_per_packet"] = (
        df["dbytes"] / (df["dpkts"] + 1)
    )

    df["source_packet_rate"] = (
        df["spkts"] / (df["dur"] + 1e-6)
    )

    df["destination_packet_rate"] = (
        df["dpkts"] / (df["dur"] + 1e-6)
    )

    df["total_bytes"] = (
        df["sbytes"] + df["dbytes"]
    )

    df["total_packets"] = (
        df["spkts"] + df["dpkts"]
    )

    df["byte_ratio"] = (
        df["sbytes"] / (df["dbytes"] + 1)
    )

    df["packet_ratio"] = (
        df["spkts"] / (df["dpkts"] + 1)
    )

    df["load_ratio"] = (
        df["sload"] / (df["dload"] + 1)
    )

    df["load_difference"] = (
        df["sload"] - df["dload"]
    )

    df["total_loss"] = (
        df["sloss"] + df["dloss"]
    )

    df["loss_ratio"] = (
        df["sloss"] / (df["dloss"] + 1)
    )

    df["packet_interval_ratio"] = (
        df["sinpkt"] / (df["dinpkt"] + 1e-6)
    )

    df["jitter_ratio"] = (
        df["sjit"] / (df["djit"] + 1e-6)
    )

    df["mean_packet_difference"] = (
        df["smean"] - df["dmean"]
    )

    df["mean_packet_ratio"] = (
        df["smean"] / (df["dmean"] + 1)
    )

    df["tcp_handshake_time"] = (
        df["synack"] + df["ackdat"]
    )


    # -----------------------------------------------------
    # Targeted features
    # -----------------------------------------------------

    df["ttl_difference"] = (
        df["sttl"] - df["dttl"]
    )

    df["ttl_ratio"] = (
        df["sttl"] / (df["dttl"] + 1)
    )

    df["tcp_window_difference"] = (
        df["swin"] - df["dwin"]
    )

    df["tcp_window_ratio"] = (
        df["swin"] / (df["dwin"] + 1)
    )

    df["handshake_total"] = (
        df["synack"]
        + df["ackdat"]
        + df["tcprtt"]
    )


    # -----------------------------------------------------
    # Handle invalid numerical values
    # -----------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df


# =========================================================
# APPLY FEATURE ENGINEERING
# =========================================================

print("\nApplying feature engineering...")

df = add_features(df)

print("New shape:", df.shape)


# =========================================================
# TARGET
# =========================================================

TARGET = "attack_cat"

y = df[TARGET]


# =========================================================
# REMOVE COLUMNS THAT SHOULD NOT BE FEATURES
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]

X = df.drop(
    columns=DROP_COLUMNS
)


# =========================================================
# FEATURE TYPES
# =========================================================

categorical_columns = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_columns = X.select_dtypes(
    include=np.number
).columns.tolist()


print("\nFeature information:")

print(
    "Numeric features     :",
    len(numeric_columns)
)

print(
    "Categorical features :",
    len(categorical_columns)
)

print(
    "Total raw features   :",
    len(X.columns)
)


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)


print("\nDataset split:")

print(
    "Training   :",
    X_train.shape
)

print(
    "Validation :",
    X_val.shape
)


# =========================================================
# PREPROCESSING
# =========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
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

classifier = RandomForestClassifier(
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
            classifier
        )
    ]
)


# =========================================================
# TRAIN
# =========================================================

print("\nTraining Stage 2 Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# VALIDATION PREDICTION
# =========================================================

print("\n")
print("=" * 70)
print("STAGE 2 VALIDATION RESULTS")
print("=" * 70)

y_pred = model.predict(X_val)


# =========================================================
# METRICS
# =========================================================

accuracy = accuracy_score(
    y_val,
    y_pred
)

precision = precision_score(
    y_val,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_val,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_val,
    y_pred,
    average="weighted",
    zero_division=0
)


print(
    f"\nAccuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print("\nClassification Report:")

print(
    classification_report(
        y_val,
        y_pred,
        zero_division=0
    )
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

labels = sorted(
    y.unique()
)

cm = confusion_matrix(
    y_val,
    y_pred,
    labels=labels
)

print("\nClass order:")

print(labels)

print("\nConfusion Matrix:")

print(cm)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

print("\n")
print("=" * 70)
print("TOP FEATURE IMPORTANCE")
print("=" * 70)

try:

    feature_names = (
        model
        .named_steps["preprocessor"]
        .get_feature_names_out()
    )

    importances = (
        model
        .named_steps["classifier"]
        .feature_importances_
    )

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    })

    importance_df = (
        importance_df
        .sort_values(
            by="importance",
            ascending=False
        )
    )

    print(
        importance_df
        .head(25)
        .to_string(index=False)
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    importance_df.to_csv(
        "data/hierarchical_attack_feature_importance.csv",
        index=False
    )

    print(
        "\nFeature importance saved to:"
    )

    print(
        "data/hierarchical_attack_feature_importance.csv"
    )

except Exception as e:

    print(
        "\nCould not calculate feature importance:"
    )

    print(e)


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

print(
    f"\nSaved to: {MODEL_PATH}"
)

print("\nAnalysis completed.")