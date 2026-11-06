"""
Model Inference & Prediction Module for SocialShield AI
Loads the serialized Random Forest model and performs robust single and batch predictions.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Tuple, Optional

from modules.feature_extraction import extract_features_from_dict, extract_features_df, FEATURE_COLUMNS
from modules.data_loader import generate_benchmark_dataset
from modules.model_training import train_and_save_model, DEFAULT_MODEL_PATH, METADATA_PATH, get_model_metadata

_LOADED_MODEL = None


def get_model(force_reload: bool = False):
    """Loads and caches the Random Forest model; trains a benchmark model if none exists."""
    global _LOADED_MODEL
    if _LOADED_MODEL is not None and not force_reload:
        return _LOADED_MODEL

    if not os.path.exists(DEFAULT_MODEL_PATH):
        # Generate initial benchmark dataset and train initial model
        demo_df = generate_benchmark_dataset(num_records=300, save=True)
        train_and_save_model(demo_df, target_col="is_bot", dataset_name="Synthetic Cresci-2017 Benchmark")

    try:
        _LOADED_MODEL = joblib.load(DEFAULT_MODEL_PATH)
    except Exception:
        # Re-train if corrupt
        demo_df = generate_benchmark_dataset(num_records=300, save=True)
        train_and_save_model(demo_df, target_col="is_bot", dataset_name="Synthetic Cresci-2017 Benchmark")
        _LOADED_MODEL = joblib.load(DEFAULT_MODEL_PATH)

    return _LOADED_MODEL


def predict_single_account(account_data: dict) -> Dict[str, Any]:
    """
    Predicts bot probability for a single account dictionary.
    Returns probability, feature vector, and model inference context.
    """
    model = get_model()
    features = extract_features_from_dict(account_data)
    X = pd.DataFrame([features], columns=FEATURE_COLUMNS)

    # Impute safety
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

    probs = model.predict_proba(X)[0]
    bot_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    predicted_class = int(bot_prob >= 0.5)

    platform = str(account_data.get("platform", "X (Twitter)"))
    is_x_platform = "twitter" in platform.lower() or "x" in platform.lower()

    metadata = get_model_metadata() or {}
    dataset_name = metadata.get("dataset_name", "Synthetic Benchmark Sample")
    is_synthetic = metadata.get("is_synthetic", True)

    return {
        "bot_probability": round(bot_prob, 4),
        "predicted_class": predicted_class,
        "features": features,
        "platform": platform,
        "is_platform_native": is_x_platform,
        "dataset_lineage": dataset_name,
        "is_synthetic_model": is_synthetic,
    }


def predict_batch_accounts(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Predicts bot probabilities for a batch DataFrame of accounts.
    Returns (probabilities, predictions, feature_dataframe).
    """
    model = get_model()
    X = extract_features_df(df)
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= 0.5).astype(int)

    return probs, preds, X

