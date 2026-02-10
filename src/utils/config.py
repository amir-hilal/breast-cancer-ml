"""
Configuration file for breast cancer detection project
"""

# Dataset path
DATASET_PATH = r'C:\Users\user123\.cache\kagglehub\datasets\yasserh\breast-cancer-dataset\versions\1\breast-cancer.csv'

# Target column
TARGET_COLUMN = 'diagnosis'

# Columns to drop
COLUMNS_TO_DROP = ['id']

# Class labels
CLASS_LABELS = {
    'M': 1,  # Malignant (cancerous)
    'B': 0   # Benign (non-cancerous)
}

# Train-test split parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Model parameters
DECISION_TREE_PARAMS = {
    'random_state': RANDOM_STATE,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2
}

LOGISTIC_REGRESSION_PARAMS = {
    'random_state': RANDOM_STATE,
    'max_iter': 1000,
    'solver': 'lbfgs'
}
