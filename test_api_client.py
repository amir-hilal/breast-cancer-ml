"""
Simple script to test the prediction API
Run this after starting the API server
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000"

# Sample features (30 values from actual dataset)
# This is a malignant tumor example
sample_features = [
    17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471,
    0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904,
    0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0,
    0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
]


def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)

    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()

        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_prediction():
    """Test prediction endpoint"""
    print("\n" + "=" * 60)
    print("Testing Prediction Endpoint")
    print("=" * 60)

    payload = {
        "features": sample_features
    }

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        result = response.json()

        print(f"✅ Status: {response.status_code}")
        print("\nPrediction Result:")
        print(f"  Prediction: {result['prediction']} ({result['prediction_label']})")
        print(f"  Probability: {result['probability']:.4f}")
        print(f"  Confidence: {result['confidence']}")

        # Interpretation
        if result['prediction'] == 1:
            print("\n⚠️  Model predicts: MALIGNANT (cancerous)")
        else:
            print("\n✅ Model predicts: BENIGN (non-cancerous)")

        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_model_info():
    """Test model info endpoint"""
    print("\n" + "=" * 60)
    print("Testing Model Info Endpoint")
    print("=" * 60)

    try:
        response = requests.get(f"{API_URL}/model/info")
        response.raise_for_status()

        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("API TEST SUITE")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print("\nMake sure the API is running:")
    print("  cd src")
    print("  uvicorn src.api.main:app --reload")

    # Test health
    health_ok = test_health()

    if not health_ok:
        print("\n❌ Health check failed. Is the API running?")
        print("\nTo start the API:")
        print("  cd src")
        print("  uvicorn src.api.main:app --reload")
        return

    # Test prediction
    prediction_ok = test_prediction()

    # Test model info
    info_ok = test_model_info()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Health Endpoint:     {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Prediction Endpoint: {'✅ PASS' if prediction_ok else '❌ FAIL'}")
    print(f"Model Info Endpoint: {'✅ PASS' if info_ok else '❌ FAIL'}")

    if health_ok and prediction_ok and info_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()
