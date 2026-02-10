"""
FastAPI application for breast cancer prediction
Loads the trained model pipeline and exposes REST API endpoints
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global model variable
model = None
model_metadata = {}
MODEL_PATH = Path("models/latest/model")

# Read API version from VERSION file
version_file = Path(__file__).parent.parent.parent / "VERSION"
if version_file.exists():
    with open(version_file, "r") as f:
        API_VERSION = f"v{f.read().strip()}"
else:
    API_VERSION = "development"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup: Load the model
    global model, model_metadata
    try:
        if MODEL_PATH.exists():
            model = mlflow.sklearn.load_model(MODEL_PATH)
            print(f"✓ Model loaded successfully from {MODEL_PATH}")

            # Load model metadata
            metadata_path = Path("models/latest/promotion_metadata.json")
            if metadata_path.exists():
                import json

                with open(metadata_path, "r") as f:
                    model_metadata = json.load(f)
                print(f"✓ Model metadata loaded: Run ID {model_metadata.get('mlflow_run_id', 'unknown')}")
        else:
            print(f"⚠️  Model not found at {MODEL_PATH}")
            print("   Run training pipeline first: python src/train.py")
    except Exception as e:
        print(f"✗ Error loading model: {str(e)}")
        model = None
        model_metadata = {}

    yield

    # Shutdown: cleanup if needed
    print("Shutting down...")


app = FastAPI(
    title="Breast Cancer Detection API",
    description="ML-powered API for breast cancer diagnosis prediction",
    version=API_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionInput(BaseModel):
    """Input schema for prediction requests"""

    features: List[float] = Field(
        ..., description="30 numerical features from breast cancer diagnostic test", min_items=30, max_items=30
    )

    class Config:
        json_schema_extra = {
            "example": {
                "features": [
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
            }
        }


class PredictionOutput(BaseModel):
    """Output schema for prediction responses"""

    prediction: int = Field(..., description="0 = Benign, 1 = Malignant")
    prediction_label: str = Field(..., description="Human-readable label")
    probability: float = Field(..., description="Probability of malignancy (0-1)")
    confidence: str = Field(..., description="Confidence level")
    api_version: str = Field(..., description="API version")
    model_version: str = Field(..., description="Model run ID")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Breast Cancer Detection API",
        "api_version": API_VERSION,
        "model_version": model_metadata.get("mlflow_run_id", "unknown"),
        "model_promoted_at": model_metadata.get("promoted_at", "unknown"),
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    model_status = "loaded" if model is not None else "not_loaded"

    return {
        "status": "healthy" if model is not None else "degraded",
        "model_status": model_status,
        "model_path": str(MODEL_PATH),
        "api_version": API_VERSION,
        "model_version": model_metadata.get("mlflow_run_id", "unknown"),
        "model_promoted_at": model_metadata.get("promoted_at", "unknown"),
    }


@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Make a prediction on breast cancer diagnosis

    Args:
        input_data: PredictionInput with 30 features

    Returns:
        PredictionOutput with prediction, label, probability, and confidence
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")

    try:
        # Convert features to DataFrame (model expects DataFrame)
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

        X = pd.DataFrame([input_data.features], columns=feature_names)

        # Make prediction
        prediction = int(model.predict(X)[0])
        prediction_proba = float(model.predict_proba(X)[0][1])  # Probability of malignancy

        # Determine confidence level
        if prediction_proba >= 0.8 or prediction_proba <= 0.2:
            confidence = "high"
        elif prediction_proba >= 0.6 or prediction_proba <= 0.4:
            confidence = "medium"
        else:
            confidence = "low"

        # Map prediction to label
        label = "Malignant" if prediction == 1 else "Benign"

        return PredictionOutput(
            prediction=prediction,
            prediction_label=label,
            probability=prediction_proba,
            confidence=confidence,
            api_version=API_VERSION,
            model_version=model_metadata.get("mlflow_run_id", "unknown"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        return {
            "api_version": API_VERSION,
            "model_type": str(type(model)),
            "model_path": str(MODEL_PATH),
            "model_version": model_metadata.get("mlflow_run_id", "unknown"),
            "promotion_metadata": model_metadata,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
