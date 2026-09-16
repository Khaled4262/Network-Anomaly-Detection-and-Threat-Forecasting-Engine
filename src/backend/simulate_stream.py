import argparse
import os
import time

import numpy as np
import pandas as pd
import requests

from src.ml.data_loader import load_dataset


def row_to_payload(row: pd.Series, feature_cols: list) -> dict:
    """Converts a pandas row into plain Python types requests can JSON-encode.

    pandas/numpy scalar types (np.int64, np.float64, ...) aren't always
    JSON-serializable as-is, so this normalizes each value to a plain
    int/float/str before it gets sent.
    """
    payload = {}
    for col in feature_cols:
        val = row[col]
        if isinstance(val, np.integer):
            payload[col] = int(val)
        elif isinstance(val, np.floating):
            payload[col] = float(val)
        else:
            payload[col] = val
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Live-stream simulator: posts mock traffic from the NSL-KDD "
        "test set to a running NADTFE /predict endpoint, one record at a time."
    )
    parser.add_argument("--url", default="http://127.0.0.1:8000/predict")
    parser.add_argument("--n", type=int, default=20, help="number of records to stream")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible sampling")
    args = parser.parse_args()

    test_path = os.path.join("data", "KDDTest+.txt")
    df = load_dataset(test_path)

    # Everything except the ground-truth columns -- these are exactly the
    # fields NetworkLogRecord expects the API to receive.
    feature_cols = [c for c in df.columns if c not in ("target", "difficulty_level")]

    sample_size = min(args.n, len(df))
    sample = df.sample(n=sample_size, random_state=args.seed).reset_index(drop=True)

    correct = 0
    sent = 0
    for i, row in sample.iterrows():
        payload = row_to_payload(row, feature_cols)
        actual = "normal" if row["target"] == "normal" else "attack"

        try:
            response = requests.post(args.url, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            print(f"[{i}] request failed: {e}")
            continue

        sent += 1
        match = result["classification"] == actual
        correct += int(match)
        marker = "match" if match else "MISS"
        print(
            f"[{i}] actual={actual:7s} predicted={result['classification']:7s} "
            f"risk={result['risk_score']:.3f}  {marker}"
        )

        time.sleep(args.delay)

    if sent:
        print(f"\n{correct}/{sent} predictions matched the actual label")
    else:
        print("\nNo requests succeeded -- is the API running? (uvicorn src.backend.main:app)")


if __name__ == "__main__":
    main()
