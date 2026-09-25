# =========================================================
# ThreatX — End-to-End Hierarchical System Evaluation
# =========================================================

import joblib
import numpy as np
import pandas as pd

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

TEST_PATH = "data/UNSW_NB15_testing-set.csv"

STAGE1_MODEL_PATH = (
    "models/targeted_feature_engineered_rf.pkl"
)

STAGE2_MODEL_PATH = (
    "models/hierarchical_attack_classifier.pkl"
)


# =========================================================
# LOAD MODELS
# =========================================================

print("=" * 70)
print("ThreatX — End-to-End Hierarchical Evaluation")
print("=" * 70)

print("\nLoading Stage 1 model...")

stage1 = joblib.load(
    STAGE1_MODEL_PATH
)

print("Stage 1 loaded.")

print("\nLoading Stage 2 model...")

stage2 = joblib.load(
    STAGE2_MODEL_PATH
)

print("Stage 2 loaded.")


# =========================================================
# LOAD TEST DATA
# =========================================================

print("\nLoading test dataset...")

df = pd.read_csv(
    TEST_PATH
)

print(
    "Test shape:",
    df.shape
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
    # Invalid values
    # -----------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df


# =========================================================
# APPLY FEATURES
# =========================================================

print("\nApplying feature engineering...")

df = add_features(df)


# =========================================================
# CREATE INPUT
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]

X = df.drop(
    columns=DROP_COLUMNS
)

y_binary = df["label"]

y_attack = df["attack_cat"]


# =========================================================
# STAGE 1
# =========================================================

print("\n")
print("=" * 70)
print("STAGE 1 — BINARY DETECTION")
print("=" * 70)

stage1_pred = stage1.predict(X)

print("\nStage 1 prediction completed.")


# =========================================================
# STAGE 1 METRICS
# =========================================================

print("\nStage 1 metrics:")

print(
    f"Accuracy : "
    f"{accuracy_score(y_binary, stage1_pred):.4f}"
)

print(
    f"Precision: "
    f"{precision_score(y_binary, stage1_pred, zero_division=0):.4f}"
)

print(
    f"Recall   : "
    f"{recall_score(y_binary, stage1_pred, zero_division=0):.4f}"
)

print(
    f"F1       : "
    f"{f1_score(y_binary, stage1_pred, zero_division=0):.4f}"
)


# =========================================================
# STAGE 2
# =========================================================

print("\n")
print("=" * 70)
print("STAGE 2 — ATTACK CLASSIFICATION")
print("=" * 70)

attack_mask = stage1_pred == 1

X_attacks = X.loc[attack_mask]

print(
    "\nTraffic classified as Attack by Stage 1:",
    len(X_attacks)
)

stage2_pred = stage2.predict(
    X_attacks
)

print(
    "Stage 2 prediction completed."
)


# =========================================================
# BUILD FINAL PREDICTIONS
# =========================================================

final_predictions = np.empty(
    len(df),
    dtype=object
)

# First assume everything is Normal
final_predictions[:] = "Normal"


# Replace Stage 1 attack predictions
final_predictions[attack_mask] = stage2_pred


# =========================================================
# END-TO-END BINARY METRICS
# =========================================================

# Convert final predictions back to binary
final_binary = (
    final_predictions != "Normal"
).astype(int)


print("\n")
print("=" * 70)
print("END-TO-END BINARY RESULTS")
print("=" * 70)

print(
    f"\nAccuracy : "
    f"{accuracy_score(y_binary, final_binary):.4f}"
)

print(
    f"Precision: "
    f"{precision_score(y_binary, final_binary, zero_division=0):.4f}"
)

print(
    f"Recall   : "
    f"{recall_score(y_binary, final_binary, zero_division=0):.4f}"
)

print(
    f"F1       : "
    f"{f1_score(y_binary, final_binary, zero_division=0):.4f}"
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_binary,
        final_binary
    )
)


# =========================================================
# END-TO-END ATTACK CLASSIFICATION
# =========================================================

# Only evaluate attack-category predictions
# for actual attack traffic.

actual_attack_mask = y_binary == 1

actual_attack_categories = (
    y_attack.loc[
        actual_attack_mask
    ]
)

predicted_attack_categories = (
    final_predictions[actual_attack_mask]
)


print("\n")
print("=" * 70)
print("END-TO-END ATTACK CATEGORY RESULTS")
print("=" * 70)


print(
    "\nAttack-category accuracy:"
)

print(
    accuracy_score(
        actual_attack_categories,
        predicted_attack_categories
    )
)


print("\nClassification Report:")

print(
    classification_report(
        actual_attack_categories,
        predicted_attack_categories,
        zero_division=0
    )
)


# =========================================================
# ATTACK CATEGORY CONFUSION MATRIX
# =========================================================

attack_labels = [
    "Analysis",
    "Backdoor",
    "DoS",
    "Exploits",
    "Fuzzers",
    "Generic",
    "Reconnaissance",
    "Shellcode",
    "Worms"
]


print("\nAttack Category Confusion Matrix:")

print(
    confusion_matrix(
        actual_attack_categories,
        predicted_attack_categories,
        labels=attack_labels
    )
)


# =========================================================
# PER-CLASS DETECTION
# =========================================================

print("\n")
print("=" * 70)
print("PER-ATTACK DETECTION")
print("=" * 70)

results = []

for attack_type in attack_labels:

    actual = (
        y_attack == attack_type
    )

    detected = (
        final_predictions == attack_type
    )

    total = actual.sum()

    correct = (
        actual & detected
    ).sum()

    detection_rate = (
        correct / total
        if total > 0
        else 0
    )

    results.append({
        "attack_type": attack_type,
        "total": total,
        "correct": correct,
        "detection_rate": detection_rate
    })


results_df = pd.DataFrame(
    results
)

results_df["detection_rate"] = (
    results_df["detection_rate"] * 100
)

print(
    results_df.to_string(
        index=False
    )
)


# =========================================================
# SAVE RESULTS
# =========================================================

results_df.to_csv(
    "data/hierarchical_attack_detection.csv",
    index=False
)

print(
    "\nSaved to:"
)

print(
    "data/hierarchical_attack_detection.csv"
)


print("\n")
print("=" * 70)
print("END-TO-END EVALUATION COMPLETED")
print("=" * 70)