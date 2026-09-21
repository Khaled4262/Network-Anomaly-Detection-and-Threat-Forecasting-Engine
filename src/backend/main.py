import os
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.backend.schemas import NetworkLogRecord, PredictionResponse
from src.ml.feature_engineering import apply_encoding, CATEGORICAL_COLUMNS

# Paths are relative to wherever the process is launched from -- same
# convention the src/ml scripts use for "data/...". Run uvicorn from the
# repo root: python -m uvicorn src.backend.main:app
MODEL_PATH = os.path.join("models", "rf_baseline.joblib")
ENCODER_PATH = os.path.join("models", "onehot_encoder.joblib")

# Populated at startup by load_artifacts(); left as None until then so
# /health can report readiness instead of crashing on import.
model = None
encoder = None
model_columns = None


def load_artifacts() -> None:
    """Loads the trained model and fitted encoder once, at process startup.

    Both come from train.py's output -- the model was fit on the encoder's
    exact column layout, so they're only ever valid loaded together.
    """
    global model, encoder, model_columns
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        # RandomForestClassifier remembers the column names/order it was
        # trained on when fit on a DataFrame -- use that as the source of
        # truth for aligning every live request to the expected feature
        # layout, rather than trusting encoding to always line up.
        model_columns = list(model.feature_names_in_)
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Could not load model/encoder artifacts ({e}). "
            "Run `python -m src.ml.train` first to generate "
            "models/rf_baseline.joblib and models/onehot_encoder.joblib."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifacts()
    yield


app = FastAPI(
    title="NADTFE Inference API",
    description="Scores a single network connection record as normal or attack traffic.",
    version="0.1.0",
    lifespan=lifespan,
)

# Permissive for local dev so the React frontend (running on a different
# port) can call this freely. Tighten allow_origins before any real deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Basic liveness/readiness check -- useful for Docker/EC2 health checks later."""
    return {
        "status": "ok" if model is not None else "not_ready",
        "model_loaded": model is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(record: NetworkLogRecord):
    """Scores one network connection record as normal or attack traffic."""
    if model is None or encoder is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    raw_df = pd.DataFrame([record.model_dump()])

    try:
        encoded_df = apply_encoding(raw_df, encoder, CATEGORICAL_COLUMNS)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to encode record: {e}")

    # Defensive alignment to the model's exact training-time column layout --
    # same guarantee the train/test assertion in train.py checks, just
    # enforced here instead of only asserted.
    for col in model_columns:
        if col not in encoded_df.columns:
            encoded_df[col] = 0
    encoded_df = encoded_df[model_columns]

    # One forest pass: RandomForest.predict() is just argmax over
    # predict_proba(), so derive the label from the probabilities.
    probabilities = model.predict_proba(encoded_df)[0]
    prediction = int(model.classes_[probabilities.argmax()])
    probability_attack = float(probabilities[list(model.classes_).index(1)])

    return PredictionResponse(
        classification="attack" if prediction == 1 else "normal",
        label=prediction,
        risk_score=probability_attack,
    )
