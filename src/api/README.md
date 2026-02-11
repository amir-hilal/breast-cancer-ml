# Breast Cancer Detection API

FastAPI application that exposes REST API endpoints for breast cancer diagnosis predictions using a trained ML model pipeline.

## Overview

The API loads a trained model from MLflow and provides endpoints for making predictions, health checks, and retrieving model information.

---

## Endpoints

### 1. Root Endpoint

**URL:** `/`
**Method:** `GET`

#### Request
- **Parameters:** None

#### Response (200 OK)
```json
{
  "message": "Breast Cancer Detection API",
  "api_version": "v{version}",
  "model_version": "{mlflow_run_id}",
  "model_promoted_at": "{timestamp}",
  "docs": "/docs",
  "health": "/health"
}
```

#### Possible Errors
- None (always returns successfully)

---

### 2. Health Check Endpoint

**URL:** `/health`
**Method:** `GET`

#### Request
- **Parameters:** None

#### Response (200 OK)
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "model_path": "models/latest/model",
  "api_version": "v{version}",
  "model_version": "{mlflow_run_id}",
  "model_promoted_at": "{timestamp}"
}
```

#### Degraded Status (200 OK - with model not loaded)
```json
{
  "status": "degraded",
  "model_status": "not_loaded",
  "model_path": "models/latest/model",
  "api_version": "v{version}",
  "model_version": "unknown",
  "model_promoted_at": "unknown"
}
```

#### Possible Errors
- None (always returns successfully, but status varies based on model availability)

---

### 3. Prediction Endpoint

**URL:** `/predict`
**Method:** `POST`

#### Request

**Content-Type:** `application/json`

**Body:**
```json
{
  "features": [
    17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871,
    1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193,
    25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189
  ]
}
```

**Feature Names (in order):**
1. radius_mean
2. texture_mean
3. perimeter_mean
4. area_mean
5. smoothness_mean
6. compactness_mean
7. concavity_mean
8. concave points_mean
9. symmetry_mean
10. fractal_dimension_mean
11. radius_se
12. texture_se
13. perimeter_se
14. area_se
15. smoothness_se
16. compactness_se
17. concavity_se
18. concave points_se
19. symmetry_se
20. fractal_dimension_se
21. radius_worst
22. texture_worst
23. perimeter_worst
24. area_worst
25. smoothness_worst
26. compactness_worst
27. concavity_worst
28. concave points_worst
29. symmetry_worst
30. fractal_dimension_worst

**Constraints:**
- Exactly 30 features required
- All features must be numerical (float)

#### Response (200 OK)
```json
{
  "prediction": 1,
  "prediction_label": "Malignant",
  "probability": 0.92,
  "confidence": "high",
  "api_version": "v{version}",
  "model_version": "{mlflow_run_id}"
}
```

**Field Descriptions:**
- `prediction`: Integer (0 = Benign, 1 = Malignant)
- `prediction_label`: Human-readable label ("Benign" or "Malignant")
- `probability`: Float between 0 and 1, representing the probability of malignancy
- `confidence`: One of three levels:
  - `"high"`: probability >= 0.8 or probability <= 0.2
  - `"medium"`: probability >= 0.6 or probability <= 0.4
  - `"low"`: probability between 0.4 and 0.6

#### Possible Errors

**503 Service Unavailable - Model Not Loaded**
```json
{
  "detail": "Model not loaded. Please train the model first."
}
```
- **Cause:** The trained model file is not available at `models/latest/model` or failed to load during startup
- **Resolution:** Run the training pipeline first: `python src/train.py`

**422 Unprocessable Entity - Invalid Input**
```json
{
  "detail": [
    {
      "loc": ["body", "features"],
      "msg": "ensure this value has at least 30 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```
- **Causes:**
  - Wrong number of features (must be exactly 30)
  - Features are not numerical
  - Features array is missing or malformed
- **Resolution:** Verify the input has exactly 30 numerical features

**500 Internal Server Error - Prediction Error**
```json
{
  "detail": "Prediction error: {error_message}"
}
```
- **Cause:** An unexpected error occurred during prediction (e.g., model processing error, feature transformation error)
- **Resolution:** Check the API logs for detailed error information; ensure features are in the correct format

---

### 4. Model Information Endpoint

**URL:** `/model/info`
**Method:** `GET`

#### Request
- **Parameters:** None

#### Response (200 OK)
```json
{
  "api_version": "v{version}",
  "model_type": "<class 'sklearn.pipeline.Pipeline'>",
  "model_path": "models/latest/model",
  "model_version": "{mlflow_run_id}",
  "promotion_metadata": {
    "mlflow_run_id": "{run_id}",
    "promoted_at": "{timestamp}",
    "additional_metadata": "..."
  }
}
```

**Field Descriptions:**
- `api_version`: Current API version
- `model_type`: The Python class type of the loaded model
- `model_path`: File system path where the model is stored
- `model_version`: MLflow run ID of the promoted model
- `promotion_metadata`: Complete metadata from `models/latest/promotion_metadata.json`

#### Possible Errors

**503 Service Unavailable - Model Not Loaded**
```json
{
  "detail": "Model not loaded"
}
```
- **Cause:** The trained model file is not available or failed to load
- **Resolution:** Run the training pipeline: `python src/train.py`

**500 Internal Server Error**
```json
{
  "detail": "{error_message}"
}
```
- **Cause:** An unexpected error occurred while retrieving model information
- **Resolution:** Check the API logs for detailed error information

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI (OpenAPI):** `http://localhost:8000/docs`
- **ReDoc (Alternative UI):** `http://localhost:8000/redoc`
- **OpenAPI JSON Schema:** `http://localhost:8000/openapi.json`

---

## Starting the API

```bash
# From the project root directory
python src/api/main.py
```

The API will start on `http://0.0.0.0:8000`

---

## CORS Configuration

The API is configured with CORS middleware that allows:
- **Origins:** All (`*`)
- **Credentials:** Enabled
- **Methods:** All
- **Headers:** All

⚠️ **Note:** This configuration is suitable for development but should be restricted for production use.

---

## Model Loading

The model is automatically loaded during API startup via the lifespan event handler:
- Location: `models/latest/model`
- Metadata: `models/latest/promotion_metadata.json`
- If loading fails, the API will start in degraded mode (health check will show status: degraded)

---

## Error Handling Summary

| Scenario | Endpoint | Status Code | Response |
|----------|----------|-------------|----------|
| Model not loaded | `/predict` | 503 | `{"detail": "Model not loaded..."}` |
| Invalid feature count | `/predict` | 422 | Validation error with details |
| Invalid feature type | `/predict` | 422 | Validation error with details |
| Prediction error | `/predict` | 500 | `{"detail": "Prediction error: ..."}` |
| Model not loaded | `/model/info` | 503 | `{"detail": "Model not loaded"}` |
| Model info retrieval error | `/model/info` | 500 | `{"detail": "{error_message}"}` |
| All GET endpoints | Any | 200 | Success response |

---

## Example Usage

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get model info
curl http://localhost:8000/model/info

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189]
  }'
```

### Using Python

```python
import requests

# Make a prediction
response = requests.post(
    'http://localhost:8000/predict',
    json={
        'features': [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471, 0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189]
    }
)
print(response.json())
```

---

## Dependencies

- **FastAPI:** Web framework
- **Uvicorn:** ASGI server
- **MLflow:** Model management
- **Pandas:** Data processing
- **Scikit-learn:** ML library (model inference)
- **Pydantic:** Data validation

See `requirements.txt` for full list of dependencies.
