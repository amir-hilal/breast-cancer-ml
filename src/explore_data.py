import os

import pandas as pd

# Path to the dataset
dataset_path = r"C:\Users\user123\.cache\kagglehub\datasets\yasserh\breast-cancer-dataset\versions\1"

# List files in the dataset directory
print("=" * 60)
print("FILES IN DATASET DIRECTORY")
print("=" * 60)
files = os.listdir(dataset_path)
for file in files:
    print(f"  - {file}")

# Find and load the CSV file
csv_file = [f for f in files if f.endswith(".csv")][0]
data_file_path = os.path.join(dataset_path, csv_file)

print(f"\nLoading data from: {csv_file}")
df = pd.read_csv(data_file_path)

# Display basic dataset information
print("\n" + "=" * 60)
print("DATASET SHAPE")
print("=" * 60)
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# Display column names
print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)
for idx, col in enumerate(df.columns, 1):
    print(f"{idx:2d}. {col}")

# Display first few rows
print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)
print(df.head())

# Display diagnosis column information (target variable)
print("\n" + "=" * 60)
print("DIAGNOSIS COLUMN ANALYSIS (Target Variable)")
print("=" * 60)
print(f"M = Malignant (cancerous)")
print(f"B = Benign (non-cancerous)")
print(f"\nValue counts:")
print(df["diagnosis"].value_counts())
print(f"\nPercentage distribution:")
print(df["diagnosis"].value_counts(normalize=True) * 100)

# Display data types
print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)
print(df.dtypes)

# Display missing values
print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)
missing = df.isnull().sum()
if missing.sum() == 0:
    print("No missing values found!")
else:
    print(missing[missing > 0])

# Display basic statistics
print("\n" + "=" * 60)
print("BASIC STATISTICS")
print("=" * 60)
print(df.describe())
