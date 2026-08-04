import os
import joblib
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

from data_loader import load_dataset, prepare_targets

# The three categorical (non-numeric) columns in NSL-KDD
CATEGORICAL_COLUMNS = ["protocol_type", "service", "flag"]


def fit_encoder(train_df: pd.DataFrame, columns: list = CATEGORICAL_COLUMNS) -> OneHotEncoder:
    """Fits OneHotEncoder on training data only; handle_unknown="ignore" encodes 
    unseen test categories as zeros to prevent ValueError."""
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoder.fit(train_df[columns])
    return encoder


def apply_encoding(df: pd.DataFrame, encoder: OneHotEncoder, columns: list = CATEGORICAL_COLUMNS) -> pd.DataFrame:
    """
    Transforms the given categorical columns using an already-fitted encoder
    and returns a new DataFrame with the originals dropped and the one-hot
    columns appended.
    """
    encoded_array = encoder.transform(df[columns])
    encoded_df = pd.DataFrame(
        encoded_array,
        columns=encoder.get_feature_names_out(columns),
        index=df.index,
    )

    remaining_df = df.drop(columns=columns).reset_index(drop=True)
    encoded_df = encoded_df.reset_index(drop=True)

    return pd.concat([remaining_df, encoded_df], axis=1)


def encode_categoricals(train_df: pd.DataFrame, test_df: pd.DataFrame, columns: list = CATEGORICAL_COLUMNS):
    """
    Fits the encoder on train_df and applies it to both train_df and test_df,
    guaranteeing both outputs end up with identical columns in identical order
    (a requirement for feeding both into the same model).
    """
    encoder = fit_encoder(train_df, columns)
    train_encoded = apply_encoding(train_df, encoder, columns)
    test_encoded = apply_encoding(test_df, encoder, columns)
    return train_encoded, test_encoded, encoder


if __name__ == "__main__":
    train_path = os.path.join("data", "KDDTrain+.txt")
    test_path = os.path.join("data", "KDDTest+.txt")

    try:
        # Load raw data
        train_df = load_dataset(train_path)
        test_df = load_dataset(test_path)

        # Convert target to binary numeric label (drops target/difficulty_level)
        train_df = prepare_targets(train_df)
        test_df = prepare_targets(test_df)

        print(f"Before encoding -> train: {train_df.shape}, test: {test_df.shape}")

        train_encoded, test_encoded, encoder = encode_categoricals(train_df, test_df)

        print(f"After encoding  -> train: {train_encoded.shape}, test: {test_encoded.shape}")
        print(f"New one-hot columns added: {len(encoder.get_feature_names_out(CATEGORICAL_COLUMNS))}")

        # Sanity check: train and test must have identical columns in identical order
        assert list(train_encoded.columns) == list(test_encoded.columns), \
            "Column mismatch between train and test after encoding!"
        print("Column alignment check passed: train and test have identical schemas.")

        # Persist the fitted encoder so the same transformation can be reused
        # later by the FastAPI service (Week 2) on live/incoming traffic.
        os.makedirs("models", exist_ok=True)
        joblib.dump(encoder, os.path.join("models", "onehot_encoder.joblib"))
        print("Saved fitted encoder to models/onehot_encoder.joblib")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")