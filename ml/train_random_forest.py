import pandas as pd

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

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("Loading dataset...")

df = pd.read_csv(TRAINING_FILE)


# =========================================================
# FEATURES AND TARGET
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


print("\n========== DATA ==========")

print("X shape:", X.shape)
print("y shape:", y.shape)

print("\nCategorical features:")
print(categorical_features)

print("\nNumerical features:", len(numerical_features))


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


print("\n========== SPLIT ==========")

print("Training samples  :", len(X_train))
print("Validation samples:", len(X_valid))


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
# RANDOM FOREST
# =========================================================

model = RandomForestClassifier(
    n_estimators=150,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# =========================================================
# PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# =========================================================
# TRAIN
# =========================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# PREDICTION
# =========================================================

print("\nGenerating predictions...")

y_pred = pipeline.predict(X_valid)


# =========================================================
# EVALUATION
# =========================================================

accuracy = accuracy_score(
    y_valid,
    y_pred
)

precision = precision_score(
    y_valid,
    y_pred
)

recall = recall_score(
    y_valid,
    y_pred
)

f1 = f1_score(
    y_valid,
    y_pred
)


print("\n========== RANDOM FOREST PERFORMANCE ==========")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-score : {f1:.4f}")


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_valid,
        y_pred,
        target_names=["Normal", "Attack"]
    )
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

print("\n========== CONFUSION MATRIX ==========")

print(
    confusion_matrix(
        y_valid,
        y_pred
    )
)