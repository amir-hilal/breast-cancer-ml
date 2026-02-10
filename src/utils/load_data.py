"""
Data loading functionality
"""
import pandas as pd
from utils.config import DATASET_PATH, COLUMNS_TO_DROP, TARGET_COLUMN

def load_data():
    """
    Load the breast cancer dataset from CSV file

    Returns:
        pd.DataFrame: Loaded dataset
    """
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded successfully!")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    return df

def drop_unnecessary_columns(df):
    """
    Drop columns that are not needed for training

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: Dataframe with unnecessary columns removed
    """
    print(f"\nDropping columns: {COLUMNS_TO_DROP}")
    df = df.drop(columns=COLUMNS_TO_DROP, errors='ignore')
    print(f"New shape: {df.shape[0]} rows, {df.shape[1]} columns")

    return df

def display_data_info(df):
    """
    Display basic information about the dataset

    Args:
        df (pd.DataFrame): Input dataframe
    """
    print("\n" + "=" * 60)
    print("DATA INFORMATION")
    print("=" * 60)

    print(f"\nTarget variable: {TARGET_COLUMN}")
    print(f"Class distribution:")
    print(df[TARGET_COLUMN].value_counts())
    print(f"\nPercentage:")
    print(df[TARGET_COLUMN].value_counts(normalize=True) * 100)

    print(f"\nFeature columns: {df.shape[1] - 1}")
    print(f"Missing values: {df.isnull().sum().sum()}")
