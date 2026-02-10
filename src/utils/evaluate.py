"""
Model evaluation functionality
"""
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import cross_validate


def evaluate_model(pipeline, X_test, y_test, model_name):
    """
    Evaluate a trained model on test data

    Args:
        pipeline: Trained pipeline
        X_test: Test features
        y_test: Test target
        model_name: Name of the model for display

    Returns:
        dict: Dictionary containing evaluation metrics
    """
    print("\n" + "=" * 60)
    print(f"EVALUATING {model_name.upper()}")
    print("=" * 60)

    # Make predictions
    y_pred = pipeline.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Display metrics
    print(f"\n{model_name} Performance Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1-Score:  {f1:.4f} ({f1*100:.2f}%)")

    # Confusion Matrix
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives (TN):  {cm[0][0]}")
    print(f"  False Positives (FP): {cm[0][1]}")
    print(f"  False Negatives (FN): {cm[1][0]}")
    print(f"  True Positives (TP):  {cm[1][1]}")

    # Classification Report
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Benign (0)", "Malignant (1)"]))

    # Return metrics dictionary
    return {
        "model_name": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm,
    }


def compare_models(results_list):
    """
    Compare multiple models and display comparison table

    Args:
        results_list: List of dictionaries containing evaluation results
    """
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    print(f"\n{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 73)

    for result in results_list:
        print(
            f"{result['model_name']:<25} "
            f"{result['accuracy']:<12.4f} "
            f"{result['precision']:<12.4f} "
            f"{result['recall']:<12.4f} "
            f"{result['f1_score']:<12.4f}"
        )

    # Find best model for each metric
    print("\n" + "=" * 60)
    print("BEST PERFORMING MODEL PER METRIC")
    print("=" * 60)

    best_accuracy = max(results_list, key=lambda x: x["accuracy"])
    best_precision = max(results_list, key=lambda x: x["precision"])
    best_recall = max(results_list, key=lambda x: x["recall"])
    best_f1 = max(results_list, key=lambda x: x["f1_score"])

    print(f"Best Accuracy:  {best_accuracy['model_name']} ({best_accuracy['accuracy']:.4f})")
    print(f"Best Precision: {best_precision['model_name']} ({best_precision['precision']:.4f})")
    print(f"Best Recall:    {best_recall['model_name']} ({best_recall['recall']:.4f})")
    print(f"Best F1-Score:  {best_f1['model_name']} ({best_f1['f1_score']:.4f})")


def perform_cross_validation(model, X, y, model_name, cv=10):
    """
    Perform k-fold cross-validation on a model

    Args:
        model: Scikit-learn model
        X: Features
        y: Target
        model_name: Name of the model for display
        cv: Number of folds (default: 10)

    Returns:
        dict: Dictionary containing cross-validation scores
    """
    print("\n" + "=" * 60)
    print(f"{model_name.upper()} - 10-FOLD CROSS-VALIDATION")
    print("=" * 60)

    # Define scoring metrics
    scoring = {"accuracy": "accuracy", "precision": "precision", "recall": "recall", "f1": "f1"}

    print(f"Performing {cv}-fold cross-validation...")
    cv_results = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)

    # Calculate mean and std for each metric
    accuracy_mean = cv_results["test_accuracy"].mean()
    accuracy_std = cv_results["test_accuracy"].std()

    precision_mean = cv_results["test_precision"].mean()
    precision_std = cv_results["test_precision"].std()

    recall_mean = cv_results["test_recall"].mean()
    recall_std = cv_results["test_recall"].std()

    f1_mean = cv_results["test_f1"].mean()
    f1_std = cv_results["test_f1"].std()

    # Display results
    print(f"\nCross-Validation Results ({cv} folds):")
    print(f"  Accuracy:  {accuracy_mean:.4f} (+/- {accuracy_std:.4f})")
    print(f"  Precision: {precision_mean:.4f} (+/- {precision_std:.4f})")
    print(f"  Recall:    {recall_mean:.4f} (+/- {recall_std:.4f})")
    print(f"  F1-Score:  {f1_mean:.4f} (+/- {f1_std:.4f})")

    return {
        "model_name": model_name,
        "accuracy_mean": accuracy_mean,
        "accuracy_std": accuracy_std,
        "precision_mean": precision_mean,
        "precision_std": precision_std,
        "recall_mean": recall_mean,
        "recall_std": recall_std,
        "f1_mean": f1_mean,
        "f1_std": f1_std,
    }
