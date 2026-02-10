"""
Comparison between Logistic Regression and Decision Tree
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import model training functions
from training_models.train_decision_tree import create_decision_tree_pipeline, train_decision_tree  # noqa: E402
from training_models.train_logistic_regression import (  # noqa: E402
    create_logistic_regression_model,
    train_logistic_regression,
)

# Import evaluation functions
from utils.evaluate import compare_models, evaluate_model  # noqa: E402

# Import data loading functions
from utils.load_data import display_data_info, drop_unnecessary_columns, load_data  # noqa: E402

# Import preprocessing functions
from utils.preprocess import encode_target, split_features_target, split_train_test  # noqa: E402


def main():
    """
    Compare Logistic Regression vs Decision Tree models
    """
    print("\n" + "=" * 60)
    print("BREAST CANCER DETECTION - ML PIPELINE")
    print("=" * 60)
    print("Comparing Logistic Regression vs Decision Tree")

    # Step 1: Load data
    df, _ = load_data()
    df = drop_unnecessary_columns(df)
    display_data_info(df)

    # Step 2: Preprocess data
    df = encode_target(df)
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    # Step 3: Train Decision Tree model
    dt_model = create_decision_tree_pipeline()
    dt_model = train_decision_tree(dt_model, X_train, y_train)

    # Step 4: Train Logistic Regression model
    lr_model = create_logistic_regression_model()
    lr_model = train_logistic_regression(lr_model, X_train, y_train)

    # Step 5: Evaluate both models
    dt_results = evaluate_model(dt_model, X_test, y_test, "Decision Tree")
    lr_results = evaluate_model(lr_model, X_test, y_test, "Logistic Regression")

    # Step 6: Compare models
    compare_models([dt_results, lr_results])

    # Note: Based on typical results, Logistic Regression tends to have better metrics
    # for this dataset, showing higher accuracy, precision, recall, and F1-score
    # compared to Decision Tree, making it more reliable for breast cancer detection.

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)
    print("\nBoth models have been trained and evaluated successfully!")
    print("Check the comparison table above to see which model performs better.")


if __name__ == "__main__":
    main()
