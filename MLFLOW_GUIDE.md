# MLflow Training Pipeline & Deployment Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train Model with MLflow
```bash
cd src
python train.py --k-folds 10
```

### 3. View MLflow UI
```bash
mlflow ui
# Open http://localhost:5000
```

### 4. Run API Locally
```bash
cd src
uvicorn src.api.main:app --reload
# Open http://localhost:8000/docs
```

---

## 📊 What Does train.py Do?

The `train.py` script is a production-ready MLflow-integrated training pipeline that:

### ✅ Training Steps

1. **Load Data**: Loads and preprocesses the breast cancer dataset
2. **Build Model**: Creates Logistic Regression pipeline with StandardScaler
3. **K-Fold Cross-Validation**: Validates model stability across data splits
4. **Train Final Model**: Trains on full training set
5. **Evaluate on Test Set**: Comprehensive metrics on held-out test data
6. **Save Model Artifacts**: Saves model as MLflow artifact
7. **Log Everything to MLflow**: All parameters, metrics, and artifacts

### 📝 What Gets Logged to MLflow

#### Parameters
- `model_type`: "LogisticRegression"
- `k_folds`: Number of CV folds (default: 10)
- `lr_*`: Logistic regression hyperparameters
- `random_state`: Random seed for reproducibility
- `data_version`: SHA256 hash of dataset file
- `n_samples_train`, `n_samples_test`, `n_features`: Dataset info

#### Metrics
**Cross-Validation (mean ± std):**
- `cv_accuracy_mean`, `cv_accuracy_std`
- `cv_precision_mean`, `cv_precision_std`
- `cv_recall_mean`, `cv_recall_std`
- `cv_f1_mean`, `cv_f1_std`

**Test Set:**
- `test_accuracy`
- `test_precision`
- `test_recall`
- `test_f1`
- `test_roc_auc`

**Promotion:**
- `promoted`: 1 if promoted, 0 if not

#### Artifacts
- **confusion_matrix.png**: Visual confusion matrix
- **classification_report.txt**: Detailed classification metrics
- **run_summary.json**: JSON summary for CI/CD
- **model/**: Serialized model pipeline

---

## 🏆 Model Promotion Logic

Models are **automatically promoted** to `models/latest/` if they meet:

### Promotion Thresholds (configurable in `utils/config.py`)
```python
MODEL_PROMOTION_THRESHOLDS = {
    'min_recall': 0.95,        # ≥ 95% recall (critical for medical diagnosis)
    'max_recall_std': 0.05,    # ≤ 5% std (stability requirement)
}
```

### What Happens on Promotion?
1. Model artifacts copied to `models/latest/`
2. Includes: model, confusion matrix, report, summary
3. `promotion_metadata.json` created with timestamp and run ID
4. Ready for deployment!

### What If Model Doesn't Meet Criteria?
- Run still logged to MLflow
- Model **not promoted** to `latest/`
- CI/CD deployment blocked (prevents bad models reaching production)

---

## 🔧 CLI Options

```bash
# Normal training (10-fold CV)
python train.py

# Custom number of folds
python train.py --k-folds 5

# Smoke test (20% of data, 3 folds, fast)
python train.py --smoke --k-folds 3
```

---

## 🐳 Docker & Deployment

### Build Docker Image
```bash
docker build -t breast-cancer-api -f deployment/Dockerfile .
```

### Run Container Locally
```bash
docker run -p 8000:8000 breast-cancer-api
```

### Test API
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001, 0.1471,
                 0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4, 0.006399, 0.04904,
                 0.05373, 0.01587, 0.03003, 0.006193, 25.38, 17.33, 184.6, 2019.0,
                 0.1622, 0.6656, 0.7119, 0.2654, 0.4601, 0.1189]
  }'
```

---

## 🔄 CI/CD Pipelines

### CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:** PR, push to main/develop

**Steps:**
1. ✅ Install dependencies
2. ✅ Code quality checks (black, isort, flake8)
3. ✅ Run unit tests with coverage
4. ✅ Smoke test training (`--smoke --k-folds 3`)
5. ✅ Validate artifacts produced
6. ✅ Upload artifacts to GitHub

### CD Pipeline (`.github/workflows/cd.yml`)

**Triggers:** Git tags (`v*.*.*`), manual dispatch

**Steps:**
1. ✅ Full training pipeline
2. ✅ Check promotion status
3. ✅ Build Docker image (if promoted)
4. ✅ Push to AWS ECR (if promoted)
5. ✅ Deploy to ECS/Beanstalk (optional, controlled by flag)
6. ✅ Create GitHub release with artifacts

**Key Feature:** CD only deploys if model meets promotion criteria!

---

## ☁️ AWS Deployment Options

### Option 1: Elastic Beanstalk (Simplest)
✅ Easiest to set up
✅ Auto-scaling built-in
✅ Health monitoring
✅ Best for small-medium workloads

### Option 2: ECS Fargate (Recommended)
✅ More control
✅ Better for production
✅ Container orchestration
✅ Integrates with ALB, CloudWatch

### Option 3: Lambda (Advanced)
⚠️ More complex packaging
✅ Serverless, pay-per-request
✅ Good for sporadic traffic

**See [DEPLOYMENT.md](deployment/DEPLOYMENT.md) for detailed AWS setup instructions.**

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_training.py -v
```

---

## 📂 Project Structure

```
breast-cancer-ml/
├── src/
│   ├── train.py                    # 🎯 Main training pipeline
│   ├── api/
│   │   └── main.py                 # FastAPI application
│   ├── utils/
│   │   ├── config.py               # Configuration & thresholds
│   │   ├── load_data.py
│   │   ├── preprocess.py
│   │   └── evaluate.py             # Includes perform_cross_validation
│   ├── training_models/
│   │   ├── train_logistic_regression.py
│   │   ├── train_decision_tree.py
│   │   └── train_random_forest.py
│   └── comparison/
│       └── *.py                    # Model comparison scripts
├── tests/
│   ├── test_training.py
│   └── test_api.py
├── deployment/
│   ├── Dockerfile
│   ├── Dockerrun.aws.json
│   └── DEPLOYMENT.md
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── models/
│   └── latest/                     # Promoted models go here
├── mlruns/                         # MLflow tracking data
├── requirements.txt
├── pyproject.toml                  # pytest, black, isort config
├── README.md
└── MODEL_SELECTION.md
```

---

## 📈 MLflow Workflow

```
1. Run Training
   └─> python train.py

2. Logs Everything
   ├─> Parameters (hyperparams, data version, etc.)
   ├─> Metrics (CV + test scores)
   └─> Artifacts (model, plots, reports)

3. Check Promotion Criteria
   ├─> Recall ≥ 0.95? ✓
   └─> Std ≤ 0.05? ✓

4. If Promoted:
   ├─> Copy to models/latest/
   └─> Ready for deployment

5. View in MLflow UI
   └─> mlflow ui (http://localhost:5000)
```

---

## 🎯 Key Features

✅ **Data Versioning**: SHA256 hash logged for every run
✅ **Reproducibility**: Random seeds, full parameter logging
✅ **Robust Evaluation**: K-fold CV + test set
✅ **Automated Promotion**: Only good models reach production
✅ **CI/CD Integration**: GitHub Actions with smoke tests
✅ **Production-Ready API**: FastAPI with health checks
✅ **Docker Support**: Multi-stage builds for efficiency
✅ **AWS Deployment**: ECR + ECS/Beanstalk ready

---

## 🔍 Troubleshooting

### Model Not Loading in API
```bash
# Check if model exists
ls models/latest/model

# If not, train first
cd src
python train.py
```

### MLflow UI Not Showing Runs
```bash
# Check tracking directory
ls mlruns/

# Make sure you're in project root
mlflow ui --backend-store-uri file:./src/mlruns
```

### CI Tests Failing
```bash
# Run locally first
pytest tests/ -v

# Check code quality
black --check src/
flake8 src/
```

---

## 📚 Learning Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is for educational purposes.

---

**Author**: ML Pipeline Project
**Dataset**: Wisconsin Breast Cancer Dataset (Kaggle)
