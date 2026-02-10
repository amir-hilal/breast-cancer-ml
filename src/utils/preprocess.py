"""
Data preprocessing functionality
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from utils.config import TARGET_COLUMN, CLASS_LABELS, TEST_SIZE, RANDOM_STATE


def encode_target(df):
    """
    Encode the target variable from M/B to 1/0

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: Dataframe with encoded target
    """
    print("\n" + "=" * 60)
    print("ENCODING TARGET VARIABLE")
    print("=" * 60)

    print(f"Original values: M (Malignant), B (Benign)")
    print(f"Encoded values: M -> {CLASS_LABELS['M']}, B -> {CLASS_LABELS['B']}")

    df[TARGET_COLUMN] = df[TARGET_COLUMN].map(CLASS_LABELS)

    print("\nEncoding complete!")
    return df


def split_features_target(df):
    """
    Split dataframe into features (X) and target (y)

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        tuple: (X, y) - Features and target
    """
    print("\n" + "=" * 60)
    print("SPLITTING FEATURES AND TARGET")
    print("=" * 60)

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    print(f"Features (X) shape: {X.shape}")
    print(f"Target (y) shape: {y.shape}")
    print(f"\nFeature columns ({len(X.columns)}):")
    for idx, col in enumerate(X.columns, 1):
        print(f"  {idx:2d}. {col}")

    return X, y


def split_train_test(X, y):
    """
    Split data into training and testing sets

    Args:
        X: Features
        y: Target

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    print("\n" + "=" * 60)
    print("SPLITTING INTO TRAIN AND TEST SETS")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y  # Maintain class distribution
    )

    print(f"Test size: {TEST_SIZE * 100}%")
    print(f"Random state: {RANDOM_STATE}")
    print(f"\nTraining set: {X_train.shape[0]} samples")
    print(f"Testing set: {X_test.shape[0]} samples")

    print(f"\nTraining set class distribution:")
    print(y_train.value_counts())
    print(f"\nTesting set class distribution:")
    print(y_test.value_counts())

    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    """
    Scale features using StandardScaler

    Args:
        X_train: Training features
        X_test: Testing features

    Returns:
        tuple: (X_train_scaled, X_test_scaled, scaler)
    """
    print("\n" + "=" * 60)
    print("SCALING FEATURES")
    print("=" * 60)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Features scaled using StandardScaler (mean=0, std=1)")
    print("Scaler fitted on training data only")

    return X_train_scaled, X_test_scaled, scaler
