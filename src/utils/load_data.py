"""  
Data loading functionality
"""
import pandas as pd
from pathlib import Path
from utils.config import DATASET_PATH, COLUMNS_TO_DROP, TARGET_COLUMN, KAGGLE_DATASET

def load_data():
    """
    Load the breast cancer dataset from CSV file
    If local file doesn't exist, downloads from Kaggle automatically

    Returns:
        pd.DataFrame: Loaded dataset
    """
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    dataset_path = Path(DATASET_PATH)
    
    # Try to load from local path first
    if dataset_path.exists():
        print(f"Loading from: {dataset_path}")
        df = pd.read_csv(dataset_path)
        print(f"Dataset loaded successfully!")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    # Dataset not found - attempt to download from Kaggle
    print(f"⚠️  Dataset not found at {dataset_path}")
    print(f"Attempting to download from Kaggle: {KAGGLE_DATASET}")
    
    try:
        import kagglehub
        
        # Download dataset from Kaggle
        download_path = kagglehub.dataset_download(KAGGLE_DATASET)
        print(f"✓ Dataset downloaded to: {download_path}")
        
        # Find CSV file in downloaded directory
        csv_files = list(Path(download_path).glob('*.csv'))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {download_path}")
        
        csv_path = csv_files[0]
        print(f"Using: {csv_path.name}")
        
        df = pd.read_csv(csv_path)
        print(f"Dataset loaded successfully!")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Optional: Update config for future runs
        print(f"\n💡 Tip: Update DATASET_PATH in config.py to:")
        print(f"   {csv_path}")
        
        return df
        
    except ImportError:
        raise RuntimeError(
            "\n❌ Dataset not found and 'kagglehub' is not installed.\n"
            "   Install it with: pip install kagglehub\n"
            f"   Or download manually from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}"
        )
    except Exception as e:
        raise RuntimeError(
            f"\n❌ Failed to download dataset: {str(e)}\n"
            f"   Please download manually from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}\n"
            "   Then update DATASET_PATH in config.py with the correct path."
        )

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
