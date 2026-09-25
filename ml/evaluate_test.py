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
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("Loading training dataset...")
train_df = pd.read_csv(TRAINING_FILE)

print("Loading testing dataset...")
test_df = pd.read_csv(TESTING_FILE)


# =========================================================
# PREPARE FEATURES AND TARGET
# =========================================================

# Remove:
# id         -> identifier
# attack_cat -> target-related information
# label      -> target variable

X_train_full = train_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_train_full = train_df["label"]

X_test = test_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_test = test_df["label"]


# =========================================================
# DATA INFORMATION
# =========================================================

print()
print("========== DATA ==========")

print("Training shape :", X_train_full.shape)
print("Testing shape  :", X_test.shape)


# =========================================================
# IDENTIFY FEATURE TYPES
# =========================================================

categorical_features = X_train_full.select_dtypes(
    include=["str"]
).columns.tolist()

numerical_features = X_train_full.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


print()
print("Categorical features:")
print(categorical_features)

print()
print("Number of numerical features:", len(numerical_features))


# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

X_train, X_valid, y_train, y_valid = train_test_split(
    X_train_full,
    y_train_full,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_train_full
)


print()
print("========== SPLIT ==========")

print("Training samples  :", len(X_train))
print("Validation samples:", len(X_valid))
print("Official test     :", len(X_test))


# =========================================================
# PREPROCESSING
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
# RANDOM FOREST MODEL
# =========================================================

model = RandomForestClassifier(
    n_estimators=150,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# =========================================================
# CREATE PIPELINE
# =========================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# =========================================================
# TRAIN MODEL
# =========================================================

print()
print("Training Random Forest...")

pipeline.fit(X_train, y_train)

print("Training completed.")


# =========================================================
# VALIDATION PREDICTION
# =========================================================

print()
print("Generating validation predictions...")

y_valid_pred = pipeline.predict(X_valid)


# =========================================================
# VALIDATION PERFORMANCE
# =========================================================

valid_accuracy = accuracy_score(
    y_valid,
    y_valid_pred
)

valid_precision = precision_score(
    y_valid,
    y_valid_pred
)

valid_recall = recall_score(
    y_valid,
    y_valid_pred
)

valid_f1 = f1_score(
    y_valid,
    y_valid_pred
)


print()
print("========== VALIDATION PERFORMANCE ==========")

print(f"Accuracy : {valid_accuracy:.4f}")
print(f"Precision: {valid_precision:.4f}")
print(f"Recall   : {valid_recall:.4f}")
print(f"F1-score : {valid_f1:.4f}")


# =========================================================
# OFFICIAL TEST PREDICTION
# =========================================================

print()
print("Generating official test predictions...")

y_test_pred = pipeline.predict(X_test)


# =========================================================
# OFFICIAL TEST PERFORMANCE
# =========================================================

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
print("       OFFICIAL TEST PERFORMANCE")
print("================================================")

print(f"Accuracy : {test_accuracy:.4f}")
print(f"Precision: {test_precision:.4f}")
print(f"Recall   : {test_recall:.4f}")
print(f"F1-score : {test_f1:.4f}")


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print()
print("========== OFFICIAL TEST CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test,
        y_test_pred,
        target_names=["Normal", "Attack"]
    )
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

print()
print("========== OFFICIAL TEST CONFUSION MATRIX ==========")

cm = confusion_matrix(
    y_test,
    y_test_pred
)

print(cm)


# =========================================================
# CONFUSION MATRIX BREAKDOWN
# =========================================================

tn, fp, fn, tp = cm.ravel()


print()
print("========== CONFUSION MATRIX BREAKDOWN ==========")

print("True Negatives (TN):", tn)
print("False Positives (FP):", fp)
print("False Negatives (FN):", fn)
print("True Positives (TP):", tp)


# =========================================================
# END
# =========================================================

print()
print("Official test evaluation completed.")