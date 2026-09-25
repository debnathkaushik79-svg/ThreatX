import pandas as pd


TRAINING_FILE = "data/UNSW_NB15_training-set.csv"
TESTING_FILE = "data/UNSW_NB15_testing-set.csv"


print("Loading training dataset...")
train_df = pd.read_csv(TRAINING_FILE)

print("Loading testing dataset...")
test_df = pd.read_csv(TESTING_FILE)


print("\n========== TRAINING DATA ==========")

print("Shape:")
print(train_df.shape)

print("\nColumns:")
print(train_df.columns.tolist())

print("\nData Types:")
print(train_df.dtypes)

print("\nMissing Values:")
print(train_df.isnull().sum())

print("\nDuplicate Rows:")
print(train_df.duplicated().sum())


print("\n========== TESTING DATA ==========")

print("Shape:")
print(test_df.shape)

print("\nColumns:")
print(test_df.columns.tolist())