"""
Data loading functionality
"""
import os
import pandas as pd
from pathlib import Path
from utils.config import DATASET_PATH, COLUMNS_TO_DROP, TARGET_COLUMN, KAGGLE_DATASET, PROJECT_ROOT


def load_data():
    """
    Load the breast cancer dataset from CSV file
    Supports multiple sources:
    1. Local file path
    2. AWS S3 (s3://bucket/path/to/file.csv)
    3. Kaggle auto-download

    Returns:
        pd.DataFrame: Loaded dataset
    """
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    # Check for S3 URI (for CI/CD and production)
    s3_uri = os.environ.get('DATASET_S3_URI', '')
    if s3_uri.startswith('s3://'):
        return _load_from_s3(s3_uri)

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

        # Download dataset from Kaggle (correct API)
        download_path = kagglehub.dataset_download(KAGGLE_DATASET, force_download=False)
        print(f"✓ Dataset downloaded to: {download_path}")

        # Find CSV file in downloaded directory
        csv_files = list(Path(download_path).glob('**/*.csv'))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {download_path}")

        csv_path = csv_files[0]
        print(f"Using: {csv_path.name}")

        df = pd.read_csv(csv_path)
        print(f"Dataset loaded successfully!")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

        return df

    except ImportError:
        raise RuntimeError(
            "\n❌ Dataset not found and 'kagglehub' is not installed.\n"
            "   Install it with: pip install kagglehub\n"
            f"   Or set DATASET_S3_URI environment variable\n"
            f"   Or download manually from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}"
        )
    except AttributeError as e:
        # Fallback for older kagglehub versions
        raise RuntimeError(
            f"\n❌ kagglehub API error: {str(e)}\n"
            "   Solution: Set DATASET_S3_URI environment variable to S3 path\n"
            f"   Example: export DATASET_S3_URI=s3://your-bucket/breast-cancer.csv\n"
            f"   Or download manually from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}"
        )
    except Exception as e:
        raise RuntimeError(
            f"\n❌ Failed to download dataset: {str(e)}\n"
            "   Solution: Set DATASET_S3_URI environment variable\n"
            f"   Or download manually from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}"
        )


def _load_from_s3(s3_uri):
    """
    Load dataset from AWS S3

    Args:
        s3_uri: S3 URI (e.g., s3://bucket/path/to/file.csv)

    Returns:
        pd.DataFrame: Loaded dataset
    """
    print(f"Loading from S3: {s3_uri}")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        # Parse S3 URI
        parts = s3_uri.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''

        if not key:
            raise ValueError(f"Invalid S3 URI: {s3_uri}")

        # Download from S3
        s3_client = boto3.client('s3')

        # Create local data directory
        data_dir = PROJECT_ROOT / 'data'
        data_dir.mkdir(exist_ok=True)

        local_path = data_dir / Path(key).name

        print(f"Downloading from bucket '{bucket}', key '{key}'...")
        s3_client.download_file(bucket, key, str(local_path))
        print(f"✓ Downloaded to: {local_path}")

        # Load CSV
        df = pd.read_csv(local_path)
        print(f"Dataset loaded successfully!")
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

        return df

    except ImportError:
        raise RuntimeError(
            "\n❌ boto3 is not installed.\n"
            "   Install it with: pip install boto3"
        )
    except NoCredentialsError:
        raise RuntimeError(
            "\n❌ AWS credentials not found.\n"
            "   Configure AWS CLI or set environment variables:\n"
            "   - AWS_ACCESS_KEY_ID\n"
            "   - AWS_SECRET_ACCESS_KEY\n"
            "   - AWS_REGION"
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise RuntimeError(
                f"\n❌ Dataset not found in S3: {s3_uri}\n"
                "   Please verify the bucket and key are correct."
            )
        elif error_code == '403':
            raise RuntimeError(
                f"\n❌ Access denied to S3: {s3_uri}\n"
                "   Please check IAM permissions."
            )
        else:
            raise RuntimeError(f"\n❌ S3 error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"\n❌ Failed to load from S3: {str(e)}")


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
