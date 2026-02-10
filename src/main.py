"""
Main entry point for Breast Cancer Detection ML Project

Available comparison scripts:
1. comparison/logistic-regression-and-dt-comparison.py
   - Compares Logistic Regression vs Decision Tree
   - Standard train/test split evaluation

2. comparison/logistic-regression-random-forest-comparison.py
   - Compares Logistic Regression vs Random Forest
   - Uses 10-fold cross-validation for robust evaluation
"""


def main():
    """
    Display available comparison scripts
    """
    print("\n" + "=" * 60)
    print("BREAST CANCER DETECTION - ML PROJECT")
    print("=" * 60)

    print("\nAvailable Comparison Scripts:")
    print("\n1. Logistic Regression vs Decision Tree")
    print("   Run: python comparison/logistic-regression-and-dt-comparison.py")
    print("   - Standard train/test split evaluation")
    print("   - Compares LR and DT performance")

    print("\n2. Logistic Regression vs Random Forest (with 10-fold CV)")
    print("   Run: python comparison/logistic-regression-random-forest-comparison.py")
    print("   - 10-fold cross-validation")
    print("   - More robust performance estimates")
    print("   - Compares LR and RF performance")

    print("\n" + "=" * 60)
    print("MODULAR PROJECT STRUCTURE")
    print("=" * 60)
    print("\nUtility Modules (utils/):")
    print("  - config.py: Configuration and parameters")
    print("  - load_data.py: Data loading functions")
    print("  - preprocess.py: Data preprocessing functions")
    print("  - evaluate.py: Model evaluation functions")

    print("\nModel Training Modules (training/):")
    print("  - train_decision_tree.py: Decision Tree model")
    print("  - train_logistic_regression.py: Logistic Regression model")
    print("  - train_random_forest.py: Random Forest model")

    print("\nComparison Scripts (comparison/):")


if __name__ == "__main__":
    main()
