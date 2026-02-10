"""
Unit tests for API endpoints
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_status" in data


def test_predict_invalid_features_count():
    """Test prediction with wrong number of features"""
    response = client.post("/predict", json={"features": [1.0, 2.0, 3.0]})  # Only 3 features instead of 30
    assert response.status_code == 422  # Validation error


@pytest.mark.skipif(not Path("models/latest/model").exists(), reason="Model not trained yet")
def test_predict_valid():
    """Test prediction with valid input (requires trained model)"""
    # Example features (30 values)
    features = [
        17.99,
        10.38,
        122.8,
        1001.0,
        0.1184,
        0.2776,
        0.3001,
        0.1471,
        0.2419,
        0.07871,
        1.095,
        0.9053,
        8.589,
        153.4,
        0.006399,
        0.04904,
        0.05373,
        0.01587,
        0.03003,
        0.006193,
        25.38,
        17.33,
        184.6,
        2019.0,
        0.1622,
        0.6656,
        0.7119,
        0.2654,
        0.4601,
        0.1189,
    ]

    response = client.post("/predict", json={"features": features})

    if response.status_code == 503:
        pytest.skip("Model not loaded")

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "prediction_label" in data
    assert "probability" in data
    assert "confidence" in data

    assert data["prediction"] in [0, 1]
    assert data["prediction_label"] in ["Benign", "Malignant"]
    assert 0 <= data["probability"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
