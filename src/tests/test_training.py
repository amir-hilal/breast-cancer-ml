"""
Unit tests for training pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest  # noqa: E402

from training_models.train_logistic_regression import create_logistic_regression_model  # noqa: E402
from utils.load_data import drop_unnecessary_columns, load_data  # noqa: E402
from utils.preprocess import encode_target, split_features_target  # noqa: E402


def test_load_data():
    """Test data loading"""
    df, _ = load_data()
    assert df is not None
    assert len(df) > 0
    assert "diagnosis" in df.columns


def test_drop_unnecessary_columns():
    """Test column dropping"""
    df, _ = load_data()
    df_clean = drop_unnecessary_columns(df)
    assert "id" not in df_clean.columns


def test_encode_target():
    """Test target encoding"""
    df, _ = load_data()
    df_clean = drop_unnecessary_columns(df)
    df_encoded = encode_target(df_clean)

    # Check that diagnosis values are now 0 or 1
    assert df_encoded["diagnosis"].isin([0, 1]).all()


def test_split_features_target():
    """Test feature-target split"""
    df, _ = load_data()
    df_clean = drop_unnecessary_columns(df)
    df_encoded = encode_target(df_clean)

    X, y = split_features_target(df_encoded)

    assert len(X) == len(y)
    assert "diagnosis" not in X.columns
    assert len(X.columns) == 30  # 30 features


def test_create_model():
    """Test model creation"""
    model = create_logistic_regression_model()

    assert model is not None
    assert hasattr(model, "fit")
    assert hasattr(model, "predict")


def test_model_training_smoke():
    """Smoke test for model training"""
    from sklearn.model_selection import train_test_split

    from utils.config import RANDOM_STATE

    # Load and prepare data
    df, _ = load_data()
    df = drop_unnecessary_columns(df)
    df = encode_target(df)
    X, y = split_features_target(df)

    # Use small subset for fast testing
    X_small, _, y_small, _ = train_test_split(X, y, train_size=0.2, random_state=RANDOM_STATE, stratify=y)

    # Create and train model
    model = create_logistic_regression_model()
    model.fit(X_small, y_small)

    # Make predictions
    predictions = model.predict(X_small)

    assert len(predictions) == len(y_small)
    assert all(p in [0, 1] for p in predictions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
