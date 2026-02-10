# Breast Cancer Detection - Machine Learning Pipeline

A modular machine learning project for breast cancer detection using the Wisconsin Breast Cancer Dataset. This project compares multiple classification algorithms with robust evaluation techniques including 10-fold cross-validation.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Dataset Information](#dataset-information)
- [Project Structure](#project-structure)
- [Model Comparisons](#model-comparisons)
- [Installation & Usage](#installation--usage)
- [Technologies Used](#technologies-used)
- [Learning Outcomes](#learning-outcomes)

> **📊 For detailed results, analysis, and model selection decisions, see [MODEL_SELECTION.md](MODEL_SELECTION.md)**

## 🎯 Project Overview

This project implements and compares three machine learning algorithms for breast cancer detection:
- **Logistic Regression** (with feature scaling)
- **Decision Tree** (scale-invariant)
- **Random Forest** (ensemble, scale-invariant)

The goal is to identify the most reliable model for distinguishing between malignant (M) and benign (B) breast tumors.

## 📊 Dataset Information

**Dataset**: Wisconsin Breast Cancer Dataset (Kaggle)
- **Total Samples**: 569
- **Features**: 30 numerical features (mean, SE, and worst values for 10 measurements)
- **Target Variable**: Diagnosis (M = Malignant, B = Benign)
- **Class Distribution**:
  - Benign (B): 357 samples (62.7%)
  - Malignant (M): 212 samples (37.3%)
- **Missing Values**: None

### Feature Categories
1. **Mean values**: radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension
2. **Standard Error (SE)**: Same measurements with SE suffix
3. **Worst values**: Same measurements with "worst" suffix

## 📁 Project Structure

```
breast-cancer-ml/
├── main.py                          # Project overview and entry point
├── import-dataset.py                # Dataset download script
├── explore_data.py                  # Data exploration script
├── README.md                        # Project documentation
├── MODEL_SELECTION.md               # Results analysis & model selection guide
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── config.py                    # Configuration and parameters
│   ├── load_data.py                 # Data loading functions
│   ├── preprocess.py                # Preprocessing functions
│   └── evaluate.py                  # Evaluation metrics
│
├── training/                        # Model training modules
│   ├── __init__.py
│   ├── train_decision_tree.py       # Decision Tree (no scaling)
│   ├── train_logistic_regression.py # Logistic Regression (with pipeline)
│   └── train_random_forest.py       # Random Forest (no scaling)
│
└── comparison/                      # Comparison scripts
    ├── __init__.py
    ├── logistic-regression-and-dt-comparison.py
    └── logistic-regression-random-forest-comparison.py
```

## 🔬 Model Comparisons

### Comparison 1: Logistic Regression vs Decision Tree

**Evaluation Method**: Standard train-test split (80/20)

**Purpose**: Compare a linear model with feature scaling against a tree-based model without scaling.

**Run**:
```bash
python comparison/logistic-regression-and-dt-comparison.py
```

---

### Comparison 2: Logistic Regression vs Random Forest (with 10-Fold CV)

**Evaluation Method**:
- 10-fold cross-validation on full dataset
- Train-test split evaluation (80/20)

**Purpose**: Compare linear model vs ensemble method with robust cross-validation to assess model stability.

**Run**:
```bash
python comparison/logistic-regression-random-forest-comparison.py
```

**📊 For detailed results and analysis, see [MODEL_SELECTION.md](MODEL_SELECTION.md)**

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- Virtual environment recommended

### Setup

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
