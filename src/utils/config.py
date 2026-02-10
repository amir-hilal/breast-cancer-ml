"""
Configuration file for breast cancer detection project
"""

# Dataset path
import os
from pathlib import Path

# Allow override via environment variable
DATASET_PATH = os.environ.get(
    "DATASET_PATH",
    r"C:\Users\user123\.cache\kagglehub\datasets\yasserh\breast-cancer-dataset\versions\1\breast-cancer.csv",
)

# Kaggle dataset identifier for automatic download
KAGGLE_DATASET = "yasserh/breast-cancer-dataset"

# Target column
TARGET_COLUMN = "diagnosis"

# Columns to drop
COLUMNS_TO_DROP = ["id"]

# Class labels
CLASS_LABELS = {"M": 1, "B": 0}  # Malignant (cancerous)  # Benign (non-cancerous)

# Train-test split parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Model parameters
DECISION_TREE_PARAMS = {"random_state": RANDOM_STATE, "max_depth": 10, "min_samples_split": 5, "min_samples_leaf": 2}

LOGISTIC_REGRESSION_PARAMS = {"random_state": RANDOM_STATE, "max_iter": 1000, "solver": "lbfgs"}

RANDOM_FOREST_PARAMS = {
    "random_state": RANDOM_STATE,
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
}

# Get project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
MLRUNS_PATH = PROJECT_ROOT / "mlruns"

MLFLOW_EXPERIMENT_NAME = "breast-cancer-detection"
MLFLOW_TRACKING_URI = f"file:///{MLRUNS_PATH.as_posix()}"  # Local tracking at project root

# Model Promotion Thresholds
MODEL_PROMOTION_THRESHOLDS = {
    "min_recall": 0.95,  # Minimum recall (sensitivity) for medical diagnosis
    "max_recall_std": 0.07,  # Maximum standard deviation for stability
    "min_f1": 0.90,  # Minimum F1-score (optional, not enforced by default)
}

# Model Registry Settings
MODELS_DIR = PROJECT_ROOT / "models"
LATEST_MODEL_DIR = PROJECT_ROOT / "models" / "latest"

# CI/CD Settings
SMOKE_TEST_SAMPLE_SIZE = 0.2  # Use 20% of data for smoke tests
