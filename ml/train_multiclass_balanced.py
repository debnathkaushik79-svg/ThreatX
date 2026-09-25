# =========================================================
# ThreatX — Multiclass Attack Classification
# Stage 2 of Hierarchical Threat Detection
# =========================================================

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
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
TEST_PATH = "data/UNSW_NB15_testing-set.csv"

MODEL_DIR = "models"
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "multiclass_attack_classifier.pkl"
)

RANDOM_STATE = 42


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def add_behavioral_features(df):

    df = df.copy()

    # -----------------------------------------------------
    # Avoid division by zero
    # -----------------------------------------------------

    eps = 1e-9

    # -----------------------------------------------------
    # Packet / byte relationships
    # -----------------------------------------------------

    df["sbytes_per_packet"] = (
        df["sbytes"] / (df["spkts"] + eps)
    )

    df["dbytes_per_packet"] = (
        df["dbytes"] / (df["dpkts"] + eps)
    )

    df["source_packet_rate"] = (
        df["spkts"] / (df["dur"] + eps)
    )

    df["destination_packet_rate"] = (
        df["dpkts"] / (df["dur"] + eps)
    )

    # -----------------------------------------------------
    # Total traffic
    # -----------------------------------------------------

    df["total_bytes"] = (
        df["sbytes"] + df["dbytes"]
    )

    df["total_packets"] = (
        df["spkts"] + df["dpkts"]
    )

    # -----------------------------------------------------
    # Ratios
    # -----------------------------------------------------

    df["byte_ratio"] = (
        df["sbytes"] / (df["dbytes"] + eps)
    )

    df["packet_ratio"] = (
        df["spkts"] / (df["dpkts"] + eps)
    )

    df["load_ratio"] = (
        df["sload"] / (df["dload"] + eps)
    )

    df["load_difference"] = (
        df["sload"] - df["dload"]
    )

    # -----------------------------------------------------
    # Packet loss
    # -----------------------------------------------------

    df["total_loss"] = (
        df["sloss"] + df["dloss"]
    )

    df["loss_ratio"] = (
        (df["sloss"] + df["dloss"])
        / (df["spkts"] + df["dpkts"] + eps)
    )

    # -----------------------------------------------------
    # Timing relationships
    # -----------------------------------------------------

    df["packet_interval_ratio"] = (
        df["sinpkt"] / (df["dinpkt"] + eps)
    )

    df["jitter_ratio"] = (
        df["sjit"] / (df["djit"] + eps)
    )

    # -----------------------------------------------------
    # Mean packet relationships
    # -----------------------------------------------------

    df["mean_packet_difference"] = (
        df["smean"] - df["dmean"]
    )

    df["mean_packet_ratio"] = (
        df["smean"] / (df["dmean"] + eps)
    )

    # -----------------------------------------------------
    # TCP handshake
    # -----------------------------------------------------

    df["tcp_handshake_time"] = (
        df["synack"] + df["ackdat"]
    )

    # -----------------------------------------------------
    # Replace invalid values
    # -----------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    df.fillna(0, inplace=True)

    return df


# =========================================================
# LOAD DATA
# =========================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

print("Training shape:", train_df.shape)
print("Testing shape :", test_df.shape)


# =========================================================
# KEEP ATTACK SAMPLES ONLY
# =========================================================

train_attack = train_df[
    train_df["label"] == 1
].copy()

test_attack = test_df[
    test_df["label"] == 1
].copy()

print("\nAttack samples:")
print("Training:", len(train_attack))
print("Testing :", len(test_attack))


# =========================================================
# TARGET DISTRIBUTION
# =========================================================

print("\nTraining attack categories:")
print(
    train_attack["attack_cat"]
    .value_counts()
)

print("\nTesting attack categories:")
print(
    test_attack["attack_cat"]
    .value_counts()
)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

print("\nApplying behavioral feature engineering...")

train_attack = add_behavioral_features(
    train_attack
)

test_attack = add_behavioral_features(
    test_attack
)


# =========================================================
# REMOVE TARGET / IDENTIFIER COLUMNS
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]

X = train_attack.drop(
    columns=DROP_COLUMNS
)

y = train_attack["attack_cat"]

X_test = test_attack.drop(
    columns=DROP_COLUMNS
)

y_test = test_attack["attack_cat"]


# =========================================================
# IDENTIFY FEATURE TYPES
# =========================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numeric_features = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

print("\nFeature information:")
print("Numeric features    :", len(numeric_features))
print("Categorical features:", len(categorical_features))
print("Total raw features  :", len(X.columns))


# =========================================================
# PREPROCESSING
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            "passthrough",
            numeric_features
        ),
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ]
)


# =========================================================
# TRANSFORM DATA
# =========================================================

print("\nFitting preprocessing pipeline...")

X_processed = preprocessor.fit_transform(X)

X_test_processed = preprocessor.transform(
    X_test
)

print(
    "Processed training shape:",
    X_processed.shape
)

print(
    "Processed testing shape :",
    X_test_processed.shape
)


# =========================================================
# DEVELOPMENT VALIDATION SPLIT
# =========================================================

X_train, X_val, y_train, y_val = train_test_split(
    X_processed,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nDevelopment split:")
print("Training:", X_train.shape)
print("Validation:", X_val.shape)


# =========================================================
# TRAIN BALANCED MULTICLASS RANDOM FOREST
# =========================================================

print("\nTraining balanced multiclass Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("Training completed.")

# =========================================================
# FEATURE IMPORTANCE
# =========================================================

print("\nCalculating feature importance...")

feature_names = preprocessor.get_feature_names_out()

importance = model.feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

importance_path = (
    "data/multiclass_feature_importance.csv"
)

importance_df.to_csv(
    importance_path,
    index=False
)

print("\nTop 20 important features:")

print(
    importance_df.head(20).to_string(
        index=False
    )
)

print(
    f"\nFeature importance saved to: "
    f"{importance_path}"
)
print("Training completed.")


# =========================================================
# VALIDATION EVALUATION
# =========================================================

print("\n")
print("=" * 60)
print("       VALIDATION PERFORMANCE")
print("=" * 60)

val_predictions = model.predict(X_val)

val_accuracy = accuracy_score(
    y_val,
    val_predictions
)

val_precision = precision_score(
    y_val,
    val_predictions,
    average="weighted",
    zero_division=0
)

val_recall = recall_score(
    y_val,
    val_predictions,
    average="weighted",
    zero_division=0
)

val_f1 = f1_score(
    y_val,
    val_predictions,
    average="weighted",
    zero_division=0
)

print(
    f"Accuracy : {val_accuracy:.4f}"
)

print(
    f"Precision: {val_precision:.4f}"
)

print(
    f"Recall   : {val_recall:.4f}"
)

print(
    f"F1 Score : {val_f1:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_val,
        val_predictions,
        zero_division=0
    )
)


# =========================================================
# OFFICIAL TEST EVALUATION
# =========================================================

print("\n")
print("=" * 60)
print("          OFFICIAL TEST PERFORMANCE")
print("=" * 60)

test_predictions = model.predict(
    X_test_processed
)

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    average="weighted",
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    average="weighted",
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    average="weighted",
    zero_division=0
)

print(
    f"Accuracy : {test_accuracy:.4f}"
)

print(
    f"Precision: {test_precision:.4f}"
)

print(
    f"Recall   : {test_recall:.4f}"
)

print(
    f"F1 Score : {test_f1:.4f}"
)


# =========================================================
# DETAILED TEST REPORT
# =========================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        zero_division=0
    )
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

labels = sorted(
    y_test.unique()
)

cm = confusion_matrix(
    y_test,
    test_predictions,
    labels=labels
)

cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels
)

print("\nConfusion Matrix:")
print(cm_df)


# =========================================================
# SAVE MODEL
# =========================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    {
        "model": model,
        "preprocessor": preprocessor,
        "features": X.columns.tolist(),
        "classes": model.classes_.tolist()
    },
    MODEL_PATH
)

print("\n")
print("=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(
    f"Path: {MODEL_PATH}"
)

print("\nMulticlass classification completed.")