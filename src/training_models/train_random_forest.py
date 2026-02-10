"""
Random Forest model training
"""
from sklearn.ensemble import RandomForestClassifier
from utils.config import RANDOM_STATE

# Random Forest parameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': RANDOM_STATE
}

def create_random_forest_model():
    """
    Create a Random Forest classifier (no scaling needed - tree-based model)

    Returns:
        RandomForestClassifier: Scikit-learn classifier
    """
    print("\n" + "=" * 60)
    print("CREATING RANDOM FOREST MODEL")
    print("=" * 60)

    model = RandomForestClassifier(**RANDOM_FOREST_PARAMS)

    print("Random Forest classifier created")
    print("Note: No feature scaling needed (tree-based model)")
    print(f"\nRandom Forest parameters:")
    for param, value in RANDOM_FOREST_PARAMS.items():
        print(f"  - {param}: {value}")

    return model

def train_random_forest(model, X_train, y_train):
    """
    Train the Random Forest model

    Args:
        model: Random Forest classifier
        X_train: Training features
        y_train: Training target

    Returns:
        RandomForestClassifier: Trained model
    """
    print("\n" + "=" * 60)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 60)

    print("Training in progress...")
    model.fit(X_train, y_train)
    print("✓ Training complete!")

    return model
