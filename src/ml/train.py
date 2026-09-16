import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from src.ml.data_loader import load_dataset, prepare_targets
from src.ml.feature_engineering import encode_categoricals


def split_features_and_target(df: pd.DataFrame, target_col: str = "label"):
    """Splits an encoded DataFrame into a feature matrix X and target vector y."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return X, y


def train_baseline_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Trains a baseline RandomForest classifier.

    Tree-based models are scale-invariant, so no numeric feature scaling is
    applied here. 
    """
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    """Evaluates the model with precision/recall/F1/confusion matrix.

    Accuracy alone is misleading given class imbalance in NSL-KDD, so it's
    printed for reference only, not as the headline metric.
    """
    y_pred = model.predict(X_test)

    print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\n--- Classification Report (precision / recall / F1) ---")
    print(classification_report(y_test, y_pred, target_names=["normal", "attack"]))

    print("--- Confusion Matrix ---")
    print("             predicted normal  predicted attack")
    cm = confusion_matrix(y_test, y_pred)
    print(f"actual normal      {cm[0][0]:>6}           {cm[0][1]:>6}")
    print(f"actual attack      {cm[1][0]:>6}           {cm[1][1]:>6}")


if __name__ == "__main__":
    train_path = os.path.join("data", "KDDTrain+.txt")
    test_path = os.path.join("data", "KDDTest+.txt")

    try:
        # Load raw data
        train_df = load_dataset(train_path)
        test_df = load_dataset(test_path)

        # Binary target prep (adds 'label', drops 'target'/'difficulty_level')
        train_df = prepare_targets(train_df)
        test_df = prepare_targets(test_df)

        # Fit encoder on train only, apply to both (see feature_engineering.py)
        train_encoded, test_encoded, encoder = encode_categoricals(train_df, test_df)

        # Sanity check: same guarantee feature_engineering.py's __main__ checks,
        # re-asserted here since train.py calls encode_categoricals() directly.
        assert list(train_encoded.columns) == list(test_encoded.columns), \
            "Column mismatch between train and test after encoding!"

        X_train, y_train = split_features_and_target(train_encoded)
        X_test, y_test = split_features_and_target(test_encoded)

        print(f"Training on {X_train.shape[0]} rows, {X_train.shape[1]} features")
        model = train_baseline_model(X_train, y_train)

        evaluate_model(model, X_test, y_test)

        # Persist both the model and the encoder together -- the FastAPI
        # service will need both to score new, unseen traffic later.
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, os.path.join("models", "rf_baseline.joblib"))
        joblib.dump(encoder, os.path.join("models", "onehot_encoder.joblib"))
        print("\nSaved model to models/rf_baseline.joblib")
        print("Saved encoder to models/onehot_encoder.joblib")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")