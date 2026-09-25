import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
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

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"

RANDOM_STATE = 42


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def create_features(df):

    df = df.copy()

    eps = 1e-6

    # Bytes per packet
    df["sbytes_per_packet"] = (
        df["sbytes"] / (df["spkts"] + eps)
    )

    df["dbytes_per_packet"] = (
        df["dbytes"] / (df["dpkts"] + eps)
    )

    # Packet rate
    df["source_packet_rate"] = (
        df["spkts"] / (df["dur"] + eps)
    )

    df["destination_packet_rate"] = (
        df["dpkts"] / (df["dur"] + eps)
    )

    # Total traffic
    df["total_bytes"] = (
        df["sbytes"] + df["dbytes"]
    )

    df["total_packets"] = (
        df["spkts"] + df["dpkts"]
    )

    # Traffic balance
    df["byte_ratio"] = (
        df["sbytes"] / (df["dbytes"] + eps)
    )

    df["packet_ratio"] = (
        df["spkts"] / (df["dpkts"] + eps)
    )

    # Load relationship
    df["load_ratio"] = (
        df["sload"] / (df["dload"] + eps)
    )

    df["load_difference"] = (
        df["sload"] - df["dload"]
    )

    # Packet loss
    df["total_loss"] = (
        df["sloss"] + df["dloss"]
    )

    df["loss_ratio"] = (
        df["sloss"] / (df["dloss"] + eps)
    )

    # Timing
    df["packet_interval_ratio"] = (
        df["sinpkt"] / (df["dinpkt"] + eps)
    )

    df["jitter_ratio"] = (
        df["sjit"] / (df["djit"] + eps)
    )

    # Mean packet relationship
    df["mean_packet_difference"] = (
        df["smean"] - df["dmean"]
    )

    df["mean_packet_ratio"] = (
        df["smean"] / (df["dmean"] + eps)
    )

    # TCP timing
    df["tcp_handshake_time"] = (
        df["synack"] + df["ackdat"]
    )

    return df


# =========================================================
# LOAD DATA
# =========================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)

print("Training shape :", train_df.shape)
print("Testing shape  :", test_df.shape)


# =========================================================
# CREATE FEATURES
# =========================================================

print()
print("Creating behavioral features...")

train_df = create_features(train_df)
test_df = create_features(test_df)

print(
    "Training shape after feature engineering :",
    train_df.shape
)

print(
    "Testing shape after feature engineering  :",
    test_df.shape
)


# =========================================================
# PREPARE DATA
# =========================================================

X = train_df.drop(
    columns=["id", "attack_cat", "label"]
)

y = train_df["label"]

X_test = test_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_test = test_df["label"]


# =========================================================
# FEATURE TYPES
# =========================================================

categorical_features = X.select_dtypes(
    include=["object", "str"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


print()
print("Categorical features :", len(categorical_features))
print("Numerical features   :", len(numerical_features))
print("Total raw features   :", len(X.columns))


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_valid, y_train, y_valid = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)


# =========================================================
# PREPROCESSOR
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
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
# BALANCED RANDOM FOREST
# =========================================================

model = RandomForestClassifier(
    n_estimators=150,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    class_weight="balanced"
)


# =========================================================
# PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# =========================================================
# TRAIN
# =========================================================

print()
print("Training balanced Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# VALIDATION
# =========================================================

print()
print("Evaluating validation set...")

y_valid_pred = pipeline.predict(
    X_valid
)

validation_accuracy = accuracy_score(
    y_valid,
    y_valid_pred
)

validation_precision = precision_score(
    y_valid,
    y_valid_pred
)

validation_recall = recall_score(
    y_valid,
    y_valid_pred
)

validation_f1 = f1_score(
    y_valid,
    y_valid_pred
)


print()
print("================================================")
print("       VALIDATION PERFORMANCE")
print("================================================")

print(
    f"Accuracy  : {validation_accuracy:.4f}"
)

print(
    f"Precision : {validation_precision:.4f}"
)

print(
    f"Recall    : {validation_recall:.4f}"
)

print(
    f"F1 Score  : {validation_f1:.4f}"
)


# =========================================================
# OFFICIAL TEST
# =========================================================

print()
print("Evaluating official test set...")

y_test_pred = pipeline.predict(
    X_test
)


test_accuracy = accuracy_score(
    y_test,
    y_test_pred
)

test_precision = precision_score(
    y_test,
    y_test_pred
)

test_recall = recall_score(
    y_test,
    y_test_pred
)

test_f1 = f1_score(
    y_test,
    y_test_pred
)


print()
print("================================================")
print("        OFFICIAL TEST PERFORMANCE")
print("================================================")

print(
    f"Accuracy  : {test_accuracy:.4f}"
)

print(
    f"Precision : {test_precision:.4f}"
)

print(
    f"Recall    : {test_recall:.4f}"
)

print(
    f"F1 Score  : {test_f1:.4f}"
)


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print()
print("================================================")
print("          CLASSIFICATION REPORT")
print("================================================")

print(
    classification_report(
        y_test,
        y_test_pred,
        target_names=[
            "Normal",
            "Attack"
        ]
    )
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

print()
print("================================================")
print("            CONFUSION MATRIX")
print("================================================")

print(
    confusion_matrix(
        y_test,
        y_test_pred
    )
)


# =========================================================
# FUZZER PERFORMANCE
# =========================================================

fuzzer_mask = (
    test_df["attack_cat"] == "Fuzzers"
)

fuzzer_actual = y_test[
    fuzzer_mask
]

fuzzer_predictions = y_test_pred[
    fuzzer_mask
]

fuzzer_detected = (
    fuzzer_predictions == 1
).sum()

fuzzer_total = len(
    fuzzer_actual
)

fuzzer_recall = (
    fuzzer_detected /
    fuzzer_total
)


print()
print("================================================")
print("            FUZZER PERFORMANCE")
print("================================================")

print(
    "Total Fuzzers    :",
    fuzzer_total
)

print(
    "Detected Fuzzers :",
    fuzzer_detected
)

print(
    "Missed Fuzzers   :",
    fuzzer_total - fuzzer_detected
)

print(
    f"Fuzzer Recall    : {fuzzer_recall:.4f}"
)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

feature_names = (
    pipeline
    .named_steps["preprocessor"]
    .get_feature_names_out()
)

rf_model = (
    pipeline
    .named_steps["model"]
)

importance = rf_model.feature_importances_

feature_importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
})

feature_importance_df = (
    feature_importance_df
    .sort_values(
        by="importance",
        ascending=False
    )
)

feature_importance_df.to_csv(
    "data/balanced_rf_feature_importance.csv",
    index=False
)


print()
print(
    "Feature importance saved:"
)

print(
    "data/balanced_rf_feature_importance.csv"
)


print()
print("Balanced Random Forest experiment completed.")