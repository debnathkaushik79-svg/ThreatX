# =========================================================
# ThreatX — Multiclass Error Analysis
# =========================================================

import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


# =========================================================
# CONFIGURATION
# =========================================================

TRAIN_PATH = "data/UNSW_NB15_training-set.csv"

RANDOM_STATE = 42


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def add_behavioral_features(df):

    df = df.copy()

    eps = 1e-9

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

    df["total_bytes"] = (
        df["sbytes"] + df["dbytes"]
    )

    df["total_packets"] = (
        df["spkts"] + df["dpkts"]
    )

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

    df["total_loss"] = (
        df["sloss"] + df["dloss"]
    )

    df["loss_ratio"] = (
        (df["sloss"] + df["dloss"])
        / (df["spkts"] + df["dpkts"] + eps)
    )

    df["packet_interval_ratio"] = (
        df["sinpkt"] / (df["dinpkt"] + eps)
    )

    df["jitter_ratio"] = (
        df["sjit"] / (df["djit"] + eps)
    )

    df["mean_packet_difference"] = (
        df["smean"] - df["dmean"]
    )

    df["mean_packet_ratio"] = (
        df["smean"] / (df["dmean"] + eps)
    )

    df["tcp_handshake_time"] = (
        df["synack"] + df["ackdat"]
    )

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

print("Loading training dataset...")

df = pd.read_csv(TRAIN_PATH)

print("Original shape:", df.shape)


# =========================================================
# ATTACKS ONLY
# =========================================================

df = df[
    df["label"] == 1
].copy()

print(
    "Attack-only shape:",
    df.shape
)


# =========================================================
# FEATURE ENGINEERING
# =========================================================

df = add_behavioral_features(df)


# =========================================================
# PREPARE X / y
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]

X = df.drop(
    columns=DROP_COLUMNS
)

y = df["attack_cat"]


# =========================================================
# FEATURE TYPES
# =========================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numeric_features = X.select_dtypes(
    exclude=["object"]
).columns.tolist()


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


X_processed = preprocessor.fit_transform(X)


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_val, y_train, y_val = train_test_split(
    X_processed,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y
)


# =========================================================
# TRAIN BASELINE MULTICLASS MODEL
# =========================================================

print("\nTraining model...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)


# =========================================================
# PREDICTIONS
# =========================================================

predictions = model.predict(X_val)


# =========================================================
# CONFUSION MATRIX
# =========================================================

labels = sorted(
    y_val.unique()
)

cm = confusion_matrix(
    y_val,
    predictions,
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
# FIND MAJOR CONFUSIONS
# =========================================================

confusions = []

for actual_index, actual_label in enumerate(labels):

    for predicted_index, predicted_label in enumerate(labels):

        if actual_index == predicted_index:
            continue

        count = cm[
            actual_index,
            predicted_index
        ]

        if count > 0:

            confusions.append({
                "actual": actual_label,
                "predicted": predicted_label,
                "count": int(count)
            })


confusions_df = pd.DataFrame(
    confusions
)

confusions_df = confusions_df.sort_values(
    by="count",
    ascending=False
)


# =========================================================
# TOP CONFUSIONS
# =========================================================

print("\n")
print("=" * 60)
print("TOP 20 MULTICLASS CONFUSIONS")
print("=" * 60)

print(
    confusions_df
    .head(20)
    .to_string(index=False)
)


# =========================================================
# SAVE RESULTS
# =========================================================

output_path = (
    "data/multiclass_confusion_analysis.csv"
)

confusions_df.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved to: {output_path}"
)

print("\nAnalysis completed.")