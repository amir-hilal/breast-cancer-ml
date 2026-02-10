# Breast Cancer Detection - Production ML Pipeline

A **production-ready** machine learning project for breast cancer detection with MLflow experiment tracking, automated CI/CD, REST API, and AWS deployment capabilities.

## ✨ Key Features

🎯 **ML Training Pipeline** - Logistic Regression with K-Fold Cross-Validation
📊 **MLflow Integration** - Full experiment tracking, metrics, and artifacts
🚀 **FastAPI REST API** - Production-ready prediction endpoint
🐳 **Docker Support** - Containerized deployment
⚙️ **CI/CD Pipelines** - GitHub Actions for testing and deployment
☁️ **AWS Ready** - Deploy to ECS, Elastic Beanstalk, or Lambda
🏆 **Model Promotion** - Automated promotion based on performance thresholds
🔒 **Data Versioning** - SHA256 hash tracking for reproducibility

## 📋 Table of Contents
- [Quick Start](#-quick-start)
- [Project Overview](#-project-overview)
- [What's New](#-whats-new-production-features)
- [Documentation](#-documentation)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Note**: The dataset will download automatically on first run - no manual download needed!

### 2. Train Model with MLflow (Recommended)
```powershell
cd src
python train.py --k-folds 10
```

### 3. View MLflow Dashboard
```powershell
mlflow ui
# Open http://localhost:5000
# Run from project root to see all experiments
```

### 4. Run API Locally
```powershell
cd src
uvicorn src.api.main:app --reload
# Open http://localhost:8000/docs
```

### 5. Or Use Quick Start Script
```powershell
# Train model
python run.py train

# Start API
python run.py api

# Run tests
python run.py test

# Full pipeline
python run.py all
```

---

## 🎯 Project Overview

This project implements a **production-grade ML pipeline** for breast cancer detection using the Wisconsin Breast Cancer Dataset. Features include:

### Machine Learning Models
- **Logistic Regression** (Primary - 98% CV accuracy)
- **Random Forest** (Comparison)
- **Decision Tree** (Baseline)

### Production Capabilities
- ✅ MLflow experiment tracking
- ✅ Automated model promotion (Recall ≥ 95%, Std ≤ 5%)
- ✅ REST API with FastAPI
- ✅ Docker containerization
- ✅ CI/CD with GitHub Actions
- ✅ AWS deployment support

---

## 🆕 What's New: Production Features

### 1. MLflow Integration (`src/train.py`)
Complete experiment tracking with:
- **Parameters**: Model type, hyperparameters, data version
- **Metrics**: CV scores (mean ± std), test metrics, ROC-AUC
- **Artifacts**: Confusion matrix, classification report, model file
- **Data Versioning**: SHA256 hash of dataset

```powershell
cd src
python train.py --k-folds 10
mlflow ui  # View results at localhost:5000
```

**Note**: MLflow tracking data is stored in `mlruns/` at the project root. Always run `mlflow ui` from the project root directory.

### 2. Model Promotion Logic
Automatically promotes models to `models/latest/` if they meet:
- **Recall ≥ 95%** (critical for medical diagnosis)
- **Recall Std ≤ 7%** (stability requirement)

Only promoted models are deployed to production!

### 3. FastAPI REST API (`src/api/main.py`)
```powershell
# Start API
cd src
uvicorn src.api.main:app --reload
```

**Endpoints:**
- `GET /` - API info
- `GET /health` - Health check
- `POST /predict` - Make prediction
- `GET /model/info` - Model metadata

**Test prediction:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [17.99, 10.38, ..., 0.1189]}'
```

### 4. CI/CD Pipelines

**CI Pipeline** (`.github/workflows/ci.yml`) - On PR/Push:
- ✅ Code quality (black, flake8, isort)
- ✅ Unit tests with coverage
- ✅ Smoke test training (`--smoke`)
- ✅ Artifact validation

**CD Pipeline** (`.github/workflows/cd.yml`) - On Release Tag:
- ✅ Full training pipeline
- ✅ Promotion check
- ✅ Docker build & push to ECR
- ✅ Deploy to AWS ECS/Beanstalk
- ✅ GitHub release with artifacts

### 5. Docker Support
```powershell
# Build image
docker build -t breast-cancer-api -f deployment/Dockerfile .

# Run locally
docker run -p 8000:8000 breast-cancer-api

# Or use Docker Compose
docker-compose up -d
```

### 6. AWS Deployment Options
- **Elastic Beanstalk** (Simplest - $35-50/month)
- **ECS Fargate** (Production - $50-70/month)
- **Lambda** (Serverless - $5-20/month)

See [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md) for full guide.

---

## 📚 Documentation

- **[S3_DATASET_SETUP.md](S3_DATASET_SETUP.md)** - 🆕 AWS S3 dataset storage for CI/CD
- **[DATASET_CONFIG.md](DATASET_CONFIG.md)** - Dataset setup & auto-download
- **[MLFLOW_GUIDE.md](MLFLOW_GUIDE.md)** - MLflow training pipeline guide
- **[MODEL_SELECTION.md](MODEL_SELECTION.md)** - Model comparison analysis
- **[AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)** - ⭐ Complete AWS setup for CI/CD
- **[PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - AWS deployment options
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (after starting API)

---

## � Project Structure

```
breast-cancer-ml/
├── src/                             # Source code
│   ├── train.py                     # 🎯 MLflow training pipeline
│   ├── api/
│   │   └── main.py                  # FastAPI application
│   ├── utils/
│   │   ├── config.py                # Configuration & thresholds
│   │   ├── load_data.py
│   │   ├── preprocess.py
│   │   └── evaluate.py              # Includes perform_cross_validation
│   ├── training_models/
│   │   ├── train_logistic_regression.py
│   │   ├── train_decision_tree.py
│   │   └── train_random_forest.py
│   └── comparison/
│       └── *.py                     # Model comparison scripts
│
├── tests/                           # Unit tests
│   ├── test_training.py
│   └── test_api.py
│
├── deployment/                      # Deployment configs
│   ├── Dockerfile
│   ├── Dockerrun.aws.json
│   └── DEPLOYMENT.md                # AWS deployment guide
│
├── .github/workflows/               # CI/CD pipelines
│   ├── ci.yml                       # Continuous Integration
│   └── cd.yml                       # Continuous Deployment
│
├── models/
│   └── latest/                      # Promoted models
│
├── mlruns/                          # MLflow tracking data
│
├── run.py                           # Quick start script
├── docker-compose.yml               # Local development setup
├── requirements.txt
├── pyproject.toml                   # Tool configuration
├── MLFLOW_GUIDE.md                  # MLflow documentation
├── MODEL_SELECTION.md               # Model analysis
└── README.md
```

---

## 📊 Dataset Information

**Dataset**: Wisconsin Breast Cancer Dataset (Kaggle)
- **Total Samples**: 569
- **Features**: 30 numerical features (mean, SE, and worst values)
- **Target Variable**: Diagnosis (M = Malignant, B = Benign)
- **Class Distribution**: 62.7% Benign, 37.3% Malignant
- **Missing Values**: None

---

## 💻 Usage Examples

### Training

```powershell
# Normal training (10-fold CV)
cd src
python train.py

# Custom folds
python train.py --k-folds 5

# Smoke test (fast)
python train.py --smoke --k-folds 3

# View MLflow UI (run from project root)
cd ..
mlflow ui
# Open http://localhost:5000
```

### API Usage

```powershell
# Start API server
cd src
uvicorn src.api.main:app --reload
```

**Python client:**
```python
import requests

features = [17.99, 10.38, 122.8, 1001.0, ...]  # 30 features

response = requests.post(
    "http://localhost:8000/predict",
    json={"features": features}
)

print(response.json())
# {
#   "prediction": 1,
#   "prediction_label": "Malignant",
#   "probability": 0.92,
#   "confidence": "high"
# }
```

### Testing

```powershell
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

### Docker

```powershell
# Build and run
docker build -t breast-cancer-api -f deployment/Dockerfile .
docker run -p 8000:8000 breast-cancer-api

# Docker Compose (includes MLflow)
docker-compose up -d
docker-compose down
```

---

## 📚 Technologies Used

### Machine Learning
- **Python 3.11**
- **scikit-learn** - ML models and pipelines
- **NumPy** - Numerical operations
- **Pandas** - Data manipulation

### Experiment Tracking
- **MLflow** - Experiment tracking, model registry

### API & Deployment
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Docker** - Containerization
- **Pydantic** - Data validation

### DevOps & CI/CD
- **GitHub Actions** - CI/CD pipelines
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Linting
- **isort** - Import sorting

### Cloud & Infrastructure
- **AWS ECR** - Container registry
- **AWS ECS/Fargate** - Container orchestration
- **AWS Elastic Beanstalk** - PaaS deployment
- **AWS Lambda** - Serverless option

---

## 🎯 Learning Outcomes

This project demonstrates:

### Machine Learning Best Practices
✅ Modular ML pipeline design
✅ K-fold cross-validation for robust evaluation
✅ Proper train-test splitting with stratification
✅ Bias-variance tradeoff understanding
✅ Data-driven model selection

### MLOps & Production Readiness
✅ Experiment tracking with MLflow
✅ Data versioning (SHA256 hashing)
✅ Automated model promotion logic
✅ Comprehensive artifact logging
✅ Reproducible experiments

### Software Engineering
✅ RESTful API design with FastAPI
✅ Docker containerization
✅ CI/CD pipeline implementation
✅ Unit testing and code quality
✅ Infrastructure as Code (IaC)

### Cloud Deployment
✅ AWS deployment strategies
✅ Container orchestration with ECS
✅ Auto-scaling configuration
✅ Monitoring and observability

---

## 🔧 Configuration

Edit `src/utils/config.py` to customize:

```python
# Model promotion thresholds
MODEL_PROMOTION_THRESHOLDS = {
    'min_recall': 0.95,        # Adjust for your use case
    'max_recall_std': 0.05,    # Stability requirement
}

# MLflow settings
MLFLOW_EXPERIMENT_NAME = "breast-cancer-detection"
MLFLOW_TRACKING_URI = "file:./mlruns"  # Or remote server

# Model parameters
LOGISTIC_REGRESSION_PARAMS = {
    'random_state': 42,
    'max_iter': 1000,
    'solver': 'lbfgs'
}
```

---

## 🔍 Model Performance

**Logistic Regression** (Primary Model):
- **CV Accuracy**: 98.07% ± 1.46%
- **CV Recall**: 96.21% ± 3.56%
- **Test Accuracy**: 96.49%
- **Test ROC-AUC**: 99.2%

See [MODEL_SELECTION.md](MODEL_SELECTION.md) for detailed analysis.

---

## 🚦 CI/CD Status

**GitHub Actions Badges** (add after pushing to GitHub):
```markdown
![CI](https://github.com/username/breast-cancer-ml/workflows/CI/badge.svg)
![CD](https://github.com/username/breast-cancer-ml/workflows/CD/badge.svg)
![Coverage](https://codecov.io/gh/username/breast-cancer-ml/branch/main/graph/badge.svg)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Before submitting:**
```powershell
# Format code
black src/ tests/
isort src/ tests/

# Run tests
pytest tests/ -v

# Check lint
flake8 src/ tests/
```

---

## 📝 Next Steps

### For Learning
- [ ] Experiment with hyperparameter tuning
- [ ] Try different models (XGBoost, SVM)
- [ ] Add SHAP for model interpretability
- [ ] Implement feature selection

### For Production
- [ ] Set up remote MLflow tracking server
- [ ] Add model A/B testing capability
- [ ] Implement data drift monitoring
- [ ] Add Prometheus metrics
- [ ] Set up centralized logging (ELK stack)

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **Dataset**: [Wisconsin Breast Cancer Dataset](https://www.kaggle.com/datasets/yasserh/breast-cancer-dataset) (Kaggle)
- **Inspiration**: Real-world MLOps practices

---

## 📬 Contact

For questions or suggestions, please open an issue on GitHub.

---

**⭐ If you found this project helpful, please give it a star!**

1. **Clone or download the project**

2. **Create virtual environment**:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn kagglehub
```

4. **Download dataset**:
```bash
python import-dataset.py
```

### Running Comparisons

**View project overview**:
```bash
python main.py
```

**Run LR vs DT comparison**:
```bash
python comparison/logistic-regression-and-dt-comparison.py
```

**Run LR vs RF with 10-fold CV** (recommended):
```bash
python comparison/logistic-regression-random-forest-comparison.py
```

---

## 📚 Technologies Used

- **Python 3.12**
- **scikit-learn**: Model training and evaluation
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **kagglehub**: Dataset download

## 🎯 Learning Outcomes

This project demonstrates:
- Building modular ML pipelines
- Proper train-test splitting with stratification
- Cross-validation for robust model evaluation
- Understanding bias-variance tradeoff
- Making data-driven model selection decisions
- Recognizing when simpler models outperform complex ones

---

## 📊 Results & Model Selection

For detailed analysis, evaluation metrics, and model selection decisions, see:

### **[📈 MODEL_SELECTION.md](MODEL_SELECTION.md)**

Includes:
- Complete cross-validation results
- Test set performance comparison
- Variance analysis
- Why Logistic Regression is the recommended model
- Interview-ready conclusions

---

**Author**: Machine Learning Pipeline Project
**Dataset**: Wisconsin Breast Cancer Dataset (Kaggle)
