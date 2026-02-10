"""
MLflow-Integrated Training Pipeline for Breast Cancer Detection
Logs all experiments, metrics, artifacts, and data versions
"""
import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
import warnings
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mlflow
import mlflow.sklearn
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# Import project utilities
from utils.load_data import load_data, drop_unnecessary_columns
from utils.preprocess import encode_target, split_features_target, split_train_test
from utils.evaluate import perform_cross_validation
from training_models.train_logistic_regression import create_logistic_regression_model
from utils.config import (
    RANDOM_STATE, TEST_SIZE, LOGISTIC_REGRESSION_PARAMS,
    DATASET_PATH, MODEL_PROMOTION_THRESHOLDS, MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI, LATEST_MODEL_DIR, PROJECT_ROOT
)

warnings.filterwarnings('ignore')


def compute_data_hash(file_path):
    """
    Compute SHA256 hash of dataset file for data versioning

    Args:
        file_path: Path to dataset file

    Returns:
        str: Hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_confusion_matrix(y_true, y_pred, output_path):
    """
    Generate and save confusion matrix plot

    Args:
        y_true: True labels
        y_pred: Predicted labels
        output_path: Path to save figure
    """
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Benign', 'Malignant'],
                yticklabels=['Benign', 'Malignant'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Confusion matrix saved to {output_path}")


def save_classification_report(y_true, y_pred, output_path):
    """
    Generate and save classification report as text file

    Args:
        y_true: True labels
        y_pred: Predicted labels
        output_path: Path to save report
    """
    report = classification_report(
        y_true, y_pred,
        target_names=['Benign (0)', 'Malignant (1)'],
        digits=4
    )

    with open(output_path, 'w') as f:
        f.write("Classification Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(report)

    print(f"Classification report saved to {output_path}")


def save_run_summary(metrics, cv_scores, params, output_path):
    """
    Save JSON summary of the run for CI/CD integration

    Args:
        metrics: Dictionary of test metrics
        cv_scores: Dictionary of cross-validation scores
        params: Dictionary of parameters
        output_path: Path to save JSON
    """
    summary = {
        'timestamp': datetime.now().isoformat(),
        'parameters': params,
        'cv_metrics': cv_scores,
        'test_metrics': metrics,
        'meets_promotion_criteria': check_promotion_criteria(cv_scores)
    }

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Run summary saved to {output_path}")


def check_promotion_criteria(cv_scores):
    """
    Check if model meets promotion thresholds

    Args:
        cv_scores: Dictionary containing CV results

    Returns:
        bool: True if meets all criteria
    """
    recall_mean = float(cv_scores.get('recall_mean', 0))
    recall_std = float(cv_scores.get('recall_std', 1))

    thresholds = MODEL_PROMOTION_THRESHOLDS

    meets_recall = recall_mean >= thresholds['min_recall']
    meets_stability = recall_std <= thresholds['max_recall_std']

    print("\n" + "=" * 60)
    print("MODEL PROMOTION CRITERIA")
    print("=" * 60)
    print(f"Recall Mean:     {recall_mean:.4f} (threshold: {thresholds['min_recall']:.2f}) {'✓' if meets_recall else '✗'}")
    print(f"Recall Std Dev:  {recall_std:.4f} (threshold: {thresholds['max_recall_std']:.2f}) {'✓' if meets_stability else '✗'}")
    print(f"\nPromotion Status: {'APPROVED' if (meets_recall and meets_stability) else 'REJECTED'}")
    print("=" * 60)

    # Convert to native Python bool for JSON serialization
    return bool(meets_recall and meets_stability)


def promote_model(run_id, artifacts_dir):
    """
    Promote model to 'latest' directory if it meets criteria

    Args:
        run_id: MLflow run ID
        artifacts_dir: Path to local artifacts directory (for reports/images)
    """
    print("\n" + "=" * 60)
    print("PROMOTING MODEL TO PRODUCTION")
    print("=" * 60)

    # Use absolute path from config
    latest_dir = Path(LATEST_MODEL_DIR)
    latest_dir.mkdir(parents=True, exist_ok=True)

    # Download model from MLflow artifact storage
    try:
        client = mlflow.tracking.MlflowClient()
        model_uri = f"runs:/{run_id}/model"
        target_path = latest_dir / "model"

        # Remove existing model if present
        if target_path.exists():
            shutil.rmtree(target_path)

        # Download model artifacts from MLflow
        mlflow.artifacts.download_artifacts(artifact_uri=model_uri, dst_path=str(latest_dir))
        print(f"✓ Model downloaded from MLflow to {target_path}")
    except Exception as e:
        print(f"✗ Failed to download model: {str(e)}")
        raise

    # Copy other artifacts
    for artifact in ['confusion_matrix.png', 'classification_report.txt', 'run_summary.json']:
        src = Path(artifacts_dir) / artifact
        if src.exists():
            shutil.copy(src, latest_dir / artifact)
            print(f"✓ {artifact} copied")

    # Save promotion metadata
    metadata = {
        'promoted_at': datetime.now().isoformat(),
        'mlflow_run_id': run_id,
        'artifacts_source': str(artifacts_dir)
    }

    with open(latest_dir / 'promotion_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Model promoted successfully!")
    print(f"Location: {latest_dir.absolute()}")
    print("=" * 60)


def train_pipeline(k_folds=10, smoke_test=False):
    """
    Complete training pipeline with MLflow logging

    Args:
        k_folds: Number of folds for cross-validation
        smoke_test: If True, use subset of data for quick testing
    """
    print("\n" + "=" * 80)
    print("MLFLOW-INTEGRATED TRAINING PIPELINE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Set MLflow tracking URI and experiment
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"\nMLflow Tracking URI: {MLFLOW_TRACKING_URI}")

    # Set experiment
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    # Start MLflow run
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"MLflow Run ID: {run_id}")

        # Step 1: Load and prepare data
        print("\n" + "=" * 60)
        print("STEP 1: DATA LOADING & PREPROCESSING")
        print("=" * 60)

        df, dataset_path = load_data()
        df = drop_unnecessary_columns(df)

        # Compute data version hash
        data_hash = compute_data_hash(dataset_path)
        print(f"\nData Version (SHA256): {data_hash[:16]}...")
        mlflow.log_param("data_version", data_hash[:16])
        mlflow.log_param("data_hash_full", data_hash)
        mlflow.log_param("dataset_path", str(dataset_path))

        # Encode target and split
        df = encode_target(df)
        X, y = split_features_target(df)

        # Smoke test mode: use subset
        if smoke_test:
            print("\n⚠️  SMOKE TEST MODE: Using 20% of data")
            from sklearn.model_selection import train_test_split
            X, _, y, _ = train_test_split(X, y, train_size=0.2, random_state=RANDOM_STATE, stratify=y)
            mlflow.log_param("smoke_test", True)
        else:
            mlflow.log_param("smoke_test", False)

        X_train, X_test, y_train, y_test = split_train_test(X, y)

        print(f"\nDataset split:")
        print(f"  Training:   {X_train.shape[0]} samples")
        print(f"  Test:       {X_test.shape[0]} samples")
        print(f"  Features:   {X_train.shape[1]}")

        # Log dataset info
        mlflow.log_param("n_samples_total", len(X))
        mlflow.log_param("n_features", X_train.shape[1])
        mlflow.log_param("n_samples_train", len(X_train))
        mlflow.log_param("n_samples_test", len(X_test))
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("random_state", RANDOM_STATE)

        # Step 2: Create model
        print("\n" + "=" * 60)
        print("STEP 2: MODEL CREATION")
        print("=" * 60)

        model = create_logistic_regression_model()

        # Log model parameters
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("k_folds", k_folds)
        for param, value in LOGISTIC_REGRESSION_PARAMS.items():
            mlflow.log_param(f"lr_{param}", value)

        # Step 3: Cross-validation
        print("\n" + "=" * 60)
        print("STEP 3: K-FOLD CROSS-VALIDATION")
        print("=" * 60)

        cv_results = perform_cross_validation(model, X_train, y_train, "Logistic Regression", cv=k_folds)

        # Log CV metrics
        mlflow.log_metric("cv_accuracy_mean", cv_results['accuracy_mean'])
        mlflow.log_metric("cv_accuracy_std", cv_results['accuracy_std'])
        mlflow.log_metric("cv_precision_mean", cv_results['precision_mean'])
        mlflow.log_metric("cv_precision_std", cv_results['precision_std'])
        mlflow.log_metric("cv_recall_mean", cv_results['recall_mean'])
        mlflow.log_metric("cv_recall_std", cv_results['recall_std'])
        mlflow.log_metric("cv_f1_mean", cv_results['f1_mean'])
        mlflow.log_metric("cv_f1_std", cv_results['f1_std'])

        # Step 4: Train final model on full training set
        print("\n" + "=" * 60)
        print("STEP 4: TRAINING FINAL MODEL")
        print("=" * 60)

        print("Training on full training set...")
        model.fit(X_train, y_train)
        print("✓ Training complete!")

        # Step 5: Evaluate on test set
        print("\n" + "=" * 60)
        print("STEP 5: TEST SET EVALUATION")
        print("=" * 60)

        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        test_accuracy = accuracy_score(y_test, y_pred)
        test_precision = precision_score(y_test, y_pred)
        test_recall = recall_score(y_test, y_pred)
        test_f1 = f1_score(y_test, y_pred)
        test_roc_auc = roc_auc_score(y_test, y_pred_proba)

        print(f"\nTest Set Metrics:")
        print(f"  Accuracy:  {test_accuracy:.4f}")
        print(f"  Precision: {test_precision:.4f}")
        print(f"  Recall:    {test_recall:.4f}")
        print(f"  F1-Score:  {test_f1:.4f}")
        print(f"  ROC-AUC:   {test_roc_auc:.4f}")

        # Log test metrics
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("test_precision", test_precision)
        mlflow.log_metric("test_recall", test_recall)
        mlflow.log_metric("test_f1", test_f1)
        mlflow.log_metric("test_roc_auc", test_roc_auc)

        test_metrics = {
            'accuracy': test_accuracy,
            'precision': test_precision,
            'recall': test_recall,
            'f1': test_f1,
            'roc_auc': test_roc_auc
        }

        # Step 6: Generate and log artifacts
        print("\n" + "=" * 60)
        print("STEP 6: GENERATING ARTIFACTS")
        print("=" * 60)

        # Create temporary artifacts directory
        artifacts_dir = Path("temp_artifacts")
        artifacts_dir.mkdir(exist_ok=True)

        # Confusion matrix
        cm_path = artifacts_dir / "confusion_matrix.png"
        save_confusion_matrix(y_test, y_pred, cm_path)
        mlflow.log_artifact(cm_path)

        # Classification report
        report_path = artifacts_dir / "classification_report.txt"
        save_classification_report(y_test, y_pred, report_path)
        mlflow.log_artifact(report_path)

        # Run summary JSON
        summary_path = artifacts_dir / "run_summary.json"
        save_run_summary(test_metrics, cv_results,
                        {**LOGISTIC_REGRESSION_PARAMS, 'k_folds': k_folds},
                        summary_path)
        mlflow.log_artifact(summary_path)

        # Step 7: Save model
        print("\n" + "=" * 60)
        print("STEP 7: SAVING MODEL")
        print("=" * 60)

        mlflow.sklearn.log_model(model, "model")
        print(f"✓ Model logged to MLflow")
        print(f"   Artifact URI: {mlflow.get_artifact_uri()}")

        # Step 8: Check promotion criteria
        print("\n" + "=" * 60)
        print("STEP 8: MODEL PROMOTION CHECK")
        print("=" * 60)

        should_promote = check_promotion_criteria(cv_results)
        mlflow.log_metric("promoted", 1 if should_promote else 0)

        if should_promote:
            promote_model(run_id, artifacts_dir)
        else:
            print("\n✗ Model does not meet promotion criteria")
            print("  Will not be promoted to models/latest/")

        # Cleanup temp artifacts
        # shutil.rmtree(artifacts_dir)  # Keep for now, MLflow has copies

        # Final summary
        print("\n" + "=" * 80)
        print("TRAINING PIPELINE COMPLETE")
        print("=" * 80)
        print(f"MLflow Run ID: {run_id}")
        print(f"Experiment: {MLFLOW_EXPERIMENT_NAME}")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nView results: mlflow ui")
        print("=" * 80)

        return run_id, should_promote


def main():
    """
    Main entry point with CLI arguments
    """
    parser = argparse.ArgumentParser(description='Train breast cancer detection model with MLflow')
    parser.add_argument('--k-folds', type=int, default=10,
                       help='Number of cross-validation folds (default: 10)')
    parser.add_argument('--smoke', action='store_true',
                       help='Run smoke test with subset of data')

    args = parser.parse_args()

    try:
        run_id, promoted = train_pipeline(k_folds=args.k_folds, smoke_test=args.smoke)

        # Exit with appropriate code for CI/CD
        if promoted:
            sys.exit(0)  # Success + promoted
        else:
            sys.exit(0)  # Success but not promoted (still consider it success)

    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
