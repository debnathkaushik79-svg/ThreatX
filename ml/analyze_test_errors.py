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
# PREDICT OFFICIAL TEST DATA
# =========================================================

print()
print("Generating test predictions...")

y_pred = pipeline.predict(X_test)


# =========================================================
# CREATE ANALYSIS DATAFRAME
# =========================================================

analysis_df = test_df[
    ["attack_cat", "label"]
].copy()

analysis_df["prediction"] = y_pred


# =========================================================
# DEFINE RESULT
# =========================================================

analysis_df["result"] = "Correct"

analysis_df.loc[
    (analysis_df["label"] == 1) &
    (analysis_df["prediction"] == 0),
    "result"
] = "Missed Attack"

analysis_df.loc[
    (analysis_df["label"] == 0) &
    (analysis_df["prediction"] == 1),
    "result"
] = "False Alarm"


# =========================================================
# ATTACK CATEGORY ANALYSIS
# =========================================================

print()
print("================================================")
print("       ATTACK CATEGORY ANALYSIS")
print("================================================")


attack_df = analysis_df[
    analysis_df["label"] == 1
].copy()


category_analysis = attack_df.groupby(
    "attack_cat"
).agg(
    total_attacks=("label", "count"),
    detected_attacks=("prediction", "sum")
)


category_analysis["missed_attacks"] = (
    category_analysis["total_attacks"]
    - category_analysis["detected_attacks"]
)


category_analysis["detection_rate"] = (
    category_analysis["detected_attacks"]
    / category_analysis["total_attacks"]
    * 100
)


category_analysis = category_analysis.sort_values(
    by="missed_attacks",
    ascending=False
)


print(category_analysis.to_string())


# =========================================================
# FALSE ALARM ANALYSIS
# =========================================================

print()
print("================================================")
print("          FALSE ALARM ANALYSIS")
print("================================================")

false_alarms = analysis_df[
    (analysis_df["label"] == 0) &
    (analysis_df["prediction"] == 1)
]

print(
    "Normal flows incorrectly detected as attacks:",
    len(false_alarms)
)


# =========================================================
# MISSED ATTACK ANALYSIS
# =========================================================

print()
print("================================================")
print("          MISSED ATTACK ANALYSIS")
print("================================================")

missed_attacks = analysis_df[
    (analysis_df["label"] == 1) &
    (analysis_df["prediction"] == 0)
]

print(
    "Total missed attacks:",
    len(missed_attacks)
)


# =========================================================
# TOP MISSED ATTACK CATEGORIES
# =========================================================

print()
print("Top attack categories with missed detections:")

top_missed = (
    missed_attacks["attack_cat"]
    .value_counts()
    .sort_values(ascending=False)
)


print(top_missed.to_string())


# =========================================================
# OVERALL CATEGORY DISTRIBUTION
# =========================================================

print()
print("================================================")
print("       TEST ATTACK DISTRIBUTION")
print("================================================")

print(
    attack_df["attack_cat"]
    .value_counts()
    .to_string()
)


# =========================================================
# SAVE RESULTS
# =========================================================

category_analysis.to_csv(
    "data/attack_category_analysis.csv"
)

print()
print("Analysis saved to:")
print("data/attack_category_analysis.csv")


print()
print("Test error analysis completed.")