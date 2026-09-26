# =========================================================
# ThreatX — ML Model Service
# =========================================================

import os
import joblib
import pandas as pd

from ml.feature_engineering import add_features


# =========================================================
# MODEL PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

STAGE_1_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "targeted_feature_engineered_rf.pkl"
)

STAGE_2_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "hierarchical_attack_classifier.pkl"
)


# =========================================================
# LOAD MODELS
# =========================================================

print("Loading ThreatX ML models...")

if not os.path.exists(STAGE_1_MODEL_PATH):
    raise FileNotFoundError(
        f"Stage 1 model not found: {STAGE_1_MODEL_PATH}"
    )

if not os.path.exists(STAGE_2_MODEL_PATH):
    raise FileNotFoundError(
        f"Stage 2 model not found: {STAGE_2_MODEL_PATH}"
    )


stage_1_model = joblib.load(
    STAGE_1_MODEL_PATH
)

stage_2_model = joblib.load(
    STAGE_2_MODEL_PATH
)

print("Stage 1 model loaded.")
print("Stage 2 model loaded.")
print("ThreatX ML models ready.")


# =========================================================
# INPUT PREPARATION
# =========================================================

DROP_COLUMNS = [
    "id",
    "label",
    "attack_cat"
]


def prepare_features(data: dict) -> pd.DataFrame:
    """
    Convert raw network traffic data into the exact
    feature representation expected by the trained models.
    """

    df = pd.DataFrame([data])

    # Apply the same 22 feature engineering operations
    # used during model training.
    df = add_features(df)

    # Remove columns that were not used by the models.
    columns_to_drop = [
        column
        for column in DROP_COLUMNS
        if column in df.columns
    ]

    df = df.drop(
        columns=columns_to_drop
    )

    return df


# =========================================================
# PREDICTION
# =========================================================

def predict_threat(data: dict) -> dict:
    """
    Run the ThreatX hierarchical ML prediction.

    Stage 1:
        Normal vs Attack

    Stage 2:
        Attack category classification
    """

    # -----------------------------------------------------
    # Prepare input
    # -----------------------------------------------------

    features = prepare_features(data)

    # -----------------------------------------------------
    # Stage 1 — Binary classification
    # -----------------------------------------------------

    stage_1_prediction = stage_1_model.predict(
        features
    )[0]

    stage_1_probabilities = (
        stage_1_model.predict_proba(features)[0]
    )

    stage_1_classes = (
        stage_1_model.classes_
    )

    stage_1_probability_map = dict(
        zip(
            stage_1_classes,
            stage_1_probabilities
        )
    )

    # Probability of the predicted class
    stage_1_confidence = float(
        stage_1_probability_map[
            stage_1_prediction
        ]
    )

    # -----------------------------------------------------
    # Normal traffic
    # -----------------------------------------------------

    if stage_1_prediction == 0:

        return {
            "prediction": "Normal",
            "attack_category": None,
            "confidence": stage_1_confidence,
            "stage_1": {
                "prediction": "Normal",
                "confidence": stage_1_confidence
            },
            "stage_2": None
        }

    # -----------------------------------------------------
    # Stage 2 — Attack classification
    # -----------------------------------------------------

    stage_2_prediction = stage_2_model.predict(
        features
    )[0]

    stage_2_probabilities = (
        stage_2_model.predict_proba(features)[0]
    )

    stage_2_classes = (
        stage_2_model.classes_
    )

    stage_2_probability_map = dict(
        zip(
            stage_2_classes,
            stage_2_probabilities
        )
    )

    stage_2_confidence = float(
        stage_2_probability_map[
            stage_2_prediction
        ]
    )

    return {
        "prediction": "Attack",
        "attack_category": str(
            stage_2_prediction
        ),
        "confidence": stage_2_confidence,
        "stage_1": {
            "prediction": "Attack",
            "confidence": stage_1_confidence
        },
        "stage_2": {
            "prediction": str(
                stage_2_prediction
            ),
            "confidence": stage_2_confidence
        }
    }