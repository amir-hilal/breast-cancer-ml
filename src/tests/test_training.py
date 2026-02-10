"""
Unit tests for training pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from training_models.train_logistic_regression import create_logistic_regression_model  # noqa: E402
from utils.load_data import drop_unnecessary_columns, load_data  # noqa: E402
from utils.preprocess import encode_target, split_features_target  # noqa: E402


@pytest.fixture
def sample_data():
    """Create sample breast cancer dataset for testing"""
    np.random.seed(42)
    n_samples = 100

    # Create sample features
    data = {
        "id": range(1, n_samples + 1),
        "diagnosis": np.random.choice(["M", "B"], n_samples),
    }

    # Add 30 feature columns (matching breast cancer dataset structure)
    feature_names = [
        "radius_mean",
        "texture_mean",
        "perimeter_mean",
        "area_mean",
        "smoothness_mean",
        "compactness_mean",
        "concavity_mean",
        "concave points_mean",
        "symmetry_mean",
        "fractal_dimension_mean",
        "radius_se",
        "texture_se",
        "perimeter_se",
        "area_se",
        "smoothness_se",
        "compactness_se",
        "concavity_se",
        "concave points_se",
        "symmetry_se",
        "fractal_dimension_se",
        "radius_worst",
        "texture_worst",
        "perimeter_worst",
        "area_worst",
        "smoothness_worst",
        "compactness_worst",
        "concavity_worst",
        "concave points_worst",
        "symmetry_worst",
        "fractal_dimension_worst",
    ]

    for feature in feature_names:
        data[feature] = np.random.randn(n_samples)

    df = pd.DataFrame(data)
    return df


@pytest.fixture
def real_data_available():
    """Check if real dataset is available"""
    try:
        df, _ = load_data()
        return True
    except Exception:
        return False


def test_load_data(real_data_available):
    """Test data loading - skip if dataset not available"""
    if not real_data_available:
        pytest.skip("Dataset not available in CI environment")

    df, _ = load_data()
    assert df is not None
    assert len(df) > 0
    assert "diagnosis" in df.columns


def test_drop_unnecessary_columns(sample_data):
    """Test column dropping"""
    df_clean = drop_unnecessary_columns(sample_data)
    assert "id" not in df_clean.columns
    assert "diagnosis" in df_clean.columns


def test_encode_target(sample_data):
    """Test target encoding"""
    df_clean = drop_unnecessary_columns(sample_data)
    df_encoded = encode_target(df_clean)

    # Check that diagnosis values are now 0 or 1
    assert df_encoded["diagnosis"].isin([0, 1]).all()


def test_split_features_target(sample_data):
    """Test feature-target split"""
    df_clean = drop_unnecessary_columns(sample_data)
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


def test_model_training_smoke(sample_data):
    """Smoke test for model training"""
    from sklearn.model_selection import train_test_split

    from utils.config import RANDOM_STATE

    # Prepare data
    df = drop_unnecessary_columns(sample_data)
    df = encode_target(df)
    X, y = split_features_target(df)

    # Use small subset for fast testing
    X_small, _, y_small, _ = train_test_split(X, y, train_size=0.8, random_state=RANDOM_STATE, stratify=y)

    # Create and train model
    model = create_logistic_regression_model()
    model.fit(X_small, y_small)

    # Make predictions
    predictions = model.predict(X_small)

    assert len(predictions) == len(y_small)
    assert all(p in [0, 1] for p in predictions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
