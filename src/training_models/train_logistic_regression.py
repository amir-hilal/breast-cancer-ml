"""
Logistic Regression model training
"""

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from utils.config import LOGISTIC_REGRESSION_PARAMS


def create_logistic_regression_model():
    """
    Create a pipeline with StandardScaler and Logistic Regression classifier

    Returns:
        Pipeline: Scikit-learn pipeline (returned as model for consistency)
    """
    print("\n" + "=" * 60)
    print("CREATING LOGISTIC REGRESSION MODEL")
    print("=" * 60)

    model = Pipeline([("scaler", StandardScaler()), ("classifier", LogisticRegression(**LOGISTIC_REGRESSION_PARAMS))])

    print("Pipeline steps:")
    print("  1. StandardScaler - Feature scaling")
    print("  2. LogisticRegression")
    print("\nLogistic Regression parameters:")
    for param, value in LOGISTIC_REGRESSION_PARAMS.items():
        print(f"  - {param}: {value}")

    return model


def train_logistic_regression(model, X_train, y_train):
    """
    Train the Logistic Regression model

    Args:
        model: Scikit-learn pipeline (StandardScaler + LogisticRegression)
        X_train: Training features
        y_train: Training target

    Returns:
        Pipeline: Trained model
    """
    print("\n" + "=" * 60)
    print("TRAINING LOGISTIC REGRESSION MODEL")
    print("=" * 60)

    print("Training in progress...")
    model.fit(X_train, y_train)
    print("✓ Training complete!")

    return model
