import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


# =========================================================
# CONFIGURATION
# =========================================================

TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"

RANDOM_STATE = 42


# =========================================================
# LOAD DATA
# =========================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAINING_FILE)
test_df = pd.read_csv(TESTING_FILE)


# =========================================================
# PREPARE FEATURES
# =========================================================

X_train_full = train_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_train_full = train_df["label"]

X_test = test_df.drop(
    columns=["id", "attack_cat", "label"]
)

y_test = test_df["label"]


# =========================================================
# FEATURE TYPES
# =========================================================

categorical_features = X_train_full.select_dtypes(
    include=["str"]
).columns.tolist()

numerical_features = X_train_full.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


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

print()
print("Training Random Forest...")

pipeline.fit(X_train, y_train)

print("Training completed.")


# =========================================================
# PREDICTIONS
# =========================================================

print()
print("Generating predictions...")

y_pred = pipeline.predict(X_test)


# =========================================================
# CREATE FUZZER DATA
# =========================================================

fuzzer_df = test_df[
    test_df["attack_cat"] == "Fuzzers"
].copy()

fuzzer_predictions = y_pred[
    test_df["attack_cat"].values == "Fuzzers"
]


fuzzer_df["prediction"] = fuzzer_predictions


# =========================================================
# SEPARATE DETECTED / MISSED
# =========================================================

detected_fuzzers = fuzzer_df[
    fuzzer_df["prediction"] == 1
].copy()

missed_fuzzers = fuzzer_df[
    fuzzer_df["prediction"] == 0
].copy()


print()
print("================================================")
print("           FUZZER ERROR SUMMARY")
print("================================================")

print("Total Fuzzers       :", len(fuzzer_df))
print("Detected Fuzzers    :", len(detected_fuzzers))
print("Missed Fuzzers      :", len(missed_fuzzers))


# =========================================================
# NUMERICAL FEATURE ANALYSIS
# =========================================================

exclude_columns = [
    "id",
    "attack_cat",
    "label",
    "prediction"
]

numerical_features = [
    col for col in fuzzer_df.select_dtypes(
        include=["int64", "float64"]
    ).columns
    if col not in exclude_columns
]


# =========================================================
# COMPARE DETECTED VS MISSED
# =========================================================

comparison = pd.DataFrame(index=numerical_features)

comparison["detected_mean"] = (
    detected_fuzzers[numerical_features].mean()
)

comparison["missed_mean"] = (
    missed_fuzzers[numerical_features].mean()
)

comparison["absolute_difference"] = (
    comparison["missed_mean"]
    - comparison["detected_mean"]
).abs()


# =========================================================
# SORT FEATURES
# =========================================================

comparison = comparison.sort_values(
    by="absolute_difference",
    ascending=False
)


# =========================================================
# DISPLAY TOP FEATURES
# =========================================================

print()
print("================================================")
print("     DETECTED VS MISSED FUZZER FEATURES")
print("================================================")

print(
    comparison.head(20).to_string()
)


# =========================================================
# CATEGORICAL FEATURE ANALYSIS
# =========================================================

print()
print("================================================")
print("        FUZZER CATEGORICAL FEATURES")
print("================================================")


for feature in categorical_features:

    print()
    print("Feature:", feature)

    detected_distribution = (
        detected_fuzzers[feature]
        .value_counts(normalize=True)
        .head(15)
        * 100
    )

    missed_distribution = (
        missed_fuzzers[feature]
        .value_counts(normalize=True)
        .head(15)
        * 100
    )

    print()
    print("Detected Fuzzers (%):")
    print(detected_distribution.to_string())

    print()
    print("Missed Fuzzers (%):")
    print(missed_distribution.to_string())


# =========================================================
# SAVE RESULTS
# =========================================================

comparison.to_csv(
    "data/fuzzer_error_feature_analysis.csv"
)

missed_fuzzers.to_csv(
    "data/missed_fuzzers.csv",
    index=False
)


print()
print("================================================")
print("Analysis files saved:")
print("data/fuzzer_error_feature_analysis.csv")
print("data/missed_fuzzers.csv")
print("================================================")

print()
print("Fuzzer error analysis completed.")