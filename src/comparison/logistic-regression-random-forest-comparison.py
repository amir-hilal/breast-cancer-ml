"""
Comparison between Logistic Regression and Random Forest with 10-fold Cross-Validation
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import model training functions
from training_models.train_logistic_regression import (  # noqa: E402
    create_logistic_regression_model,
    train_logistic_regression,
)
from training_models.train_random_forest import create_random_forest_model, train_random_forest  # noqa: E402

# Import evaluation functions
from utils.evaluate import compare_models, evaluate_model, perform_cross_validation  # noqa: E402

# Import data loading functions
from utils.load_data import display_data_info, drop_unnecessary_columns, load_data  # noqa: E402

# Import preprocessing functions
from utils.preprocess import encode_target, split_features_target, split_train_test  # noqa: E402


def compare_cv_results(results_list):
    """
    Compare cross-validation results from multiple models

    Args:
        results_list: List of dictionaries containing CV results
    """
    print("\n" + "=" * 60)
    print("CROSS-VALIDATION COMPARISON")
    print("=" * 60)

    print(f"\n{'Model':<25} {'Accuracy':<20} {'Precision':<20} {'Recall':<20} {'F1-Score':<20}")
    print("-" * 105)

    for result in results_list:
        print(
            f"{result['model_name']:<25} "
            f"{result['accuracy_mean']:.4f} ± {result['accuracy_std']:.4f}   "
            f"{result['precision_mean']:.4f} ± {result['precision_std']:.4f}   "
            f"{result['recall_mean']:.4f} ± {result['recall_std']:.4f}   "
            f"{result['f1_mean']:.4f} ± {result['f1_std']:.4f}"
        )

    # Find best model for each metric
    print("\n" + "=" * 60)
    print("BEST PERFORMING MODEL PER METRIC (Mean Score)")
    print("=" * 60)

    best_accuracy = max(results_list, key=lambda x: x["accuracy_mean"])
    best_precision = max(results_list, key=lambda x: x["precision_mean"])
    best_recall = max(results_list, key=lambda x: x["recall_mean"])
    best_f1 = max(results_list, key=lambda x: x["f1_mean"])

    print(
        f"Best Accuracy:  {best_accuracy['model_name']} "
        f"({best_accuracy['accuracy_mean']:.4f} ± {best_accuracy['accuracy_std']:.4f})"
    )
    print(
        f"Best Precision: {best_precision['model_name']} "
        f"({best_precision['precision_mean']:.4f} ± {best_precision['precision_std']:.4f})"
    )
    print(
        f"Best Recall:    {best_recall['model_name']} "
        f"({best_recall['recall_mean']:.4f} ± {best_recall['recall_std']:.4f})"
    )
    print(f"Best F1-Score:  {best_f1['model_name']} " f"({best_f1['f1_mean']:.4f} ± {best_f1['f1_std']:.4f})")


def main():
    """
    Compare Logistic Regression vs Random Forest with 10-fold Cross-Validation
    """
    print("\n" + "=" * 60)
    print("BREAST CANCER DETECTION - ML PIPELINE")
    print("=" * 60)
    print("Comparing Logistic Regression vs Random Forest")
    print("Using 10-Fold Cross-Validation")

    # Step 1: Load data
    df, _ = load_data()
    df = drop_unnecessary_columns(df)
    display_data_info(df)

    # Step 2: Preprocess data
    df = encode_target(df)
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    # Step 3: Create models
    lr_model = create_logistic_regression_model()
    rf_model = create_random_forest_model()

    # Step 4: Perform 10-fold cross-validation on entire dataset
    print("\n" + "=" * 60)
    print("PERFORMING CROSS-VALIDATION ON FULL DATASET")
    print("=" * 60)

    # Combine train and test back for cross-validation
    X_full = X
    y_full = y

    lr_cv_results = perform_cross_validation(lr_model, X_full, y_full, "Logistic Regression", cv=10)
    rf_cv_results = perform_cross_validation(rf_model, X_full, y_full, "Random Forest", cv=10)

    # Step 5: Compare cross-validation results
    compare_cv_results([lr_cv_results, rf_cv_results])

    # Step 6: Train models on full training set and evaluate on test set
    print("\n" + "=" * 60)
    print("TRAINING ON FULL TRAINING SET AND EVALUATING ON TEST SET")
    print("=" * 60)

    lr_model_trained = train_logistic_regression(lr_model, X_train, y_train)
    rf_model_trained = train_random_forest(rf_model, X_train, y_train)

    lr_results = evaluate_model(lr_model_trained, X_test, y_test, "Logistic Regression")
    rf_results = evaluate_model(rf_model_trained, X_test, y_test, "Random Forest")

    # Step 7: Compare models on test set
    compare_models([lr_results, rf_results])

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)
    print("\nBoth models have been trained and evaluated with 10-fold CV!")
    print("Cross-validation provides a more robust estimate of model performance.")
    print("Check the comparison tables above to see which model performs better.")


if __name__ == "__main__":
    main()
