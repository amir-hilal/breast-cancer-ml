"""
Decision Tree model training
"""
from sklearn.tree import DecisionTreeClassifier
from utils.config import DECISION_TREE_PARAMS


def create_decision_tree_pipeline():
    """
    Create a Decision Tree classifier (no scaling needed - DTs are scale-invariant)

    Returns:
        DecisionTreeClassifier: Scikit-learn classifier
    """
    print("\n" + "=" * 60)
    print("CREATING DECISION TREE MODEL")
    print("=" * 60)

    model = DecisionTreeClassifier(**DECISION_TREE_PARAMS)

    print("Decision Tree classifier created")
    print("Note: No feature scaling needed (DTs are scale-invariant)")
    print(f"\nDecision Tree parameters:")
    for param, value in DECISION_TREE_PARAMS.items():
        print(f"  - {param}: {value}")

    return model


def train_decision_tree(model, X_train, y_train):
    """
    Train the Decision Tree model

    Args:
        model: Decision Tree classifier
        X_train: Training features
        y_train: Training target

    Returns:
        DecisionTreeClassifier: Trained model
    """
    print("\n" + "=" * 60)
    print("TRAINING DECISION TREE MODEL")
    print("=" * 60)

    print("Training in progress...")
    model.fit(X_train, y_train)
    print("✓ Training complete!")

    return model
