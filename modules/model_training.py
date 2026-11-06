"""
Model Training & Evaluation Module for SocialShield AI
Trains, evaluates, and serializes a Scikit-Learn Random Forest Classifier
with complete metrics (Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix).
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
)

from modules.feature_extraction import FEATURE_COLUMNS
from modules.preprocessing import clean_and_prepare_dataset

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, "random_forest.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")


def train_and_save_model(
    df: pd.DataFrame,
    target_col: Optional[str] = None,
    dataset_name: str = "Synthetic Benchmark Sample",
    model_path: str = DEFAULT_MODEL_PATH,
    n_estimators: int = 120,
    max_depth: Optional[int] = 12,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Cleans raw DataFrame, splits stratified train/test, trains Random Forest,
    computes evaluation metrics, and serializes the model and metadata.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    # 1. Clean and extract features
    X, y, prep_summary = clean_and_prepare_dataset(df, target_col=target_col)

    if y is None or len(y) < 10 or y.nunique() < 2:
        raise ValueError("Dataset must contain at least 10 rows and binary target labels (0 and 1).")

    # 2. Stratified Train / Test Split
    test_size = 0.25 if len(X) >= 50 else 0.2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # 3. Model Architecture
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # 4. Evaluation
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))

    try:
        auc = float(roc_auc_score(y_test, y_prob))
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
        roc_data = {
            "fpr": [round(float(v), 4) for v in fpr],
            "tpr": [round(float(v), 4) for v in tpr],
        }
    except Exception:
        auc = 0.5
        roc_data = {"fpr": [0.0, 1.0], "tpr": [0.0, 1.0]}

    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature importances
    importances = model.feature_importances_
    feat_importance_dict = {
        feat: round(float(imp), 4)
        for feat, imp in sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: x[1], reverse=True)
    }

    # Cross-validation score (5-fold)
    cv_scores = cross_val_score(model, X, y, cv=min(5, len(y) // 5), scoring="f1")
    cv_mean = float(np.mean(cv_scores))

    # Metadata payload
    metadata = {
        "dataset_name": dataset_name,
        "is_synthetic": "synthetic" in dataset_name.lower() or "demo" in dataset_name.lower(),
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "cv_f1_mean": round(cv_mean, 4),
        },
        "confusion_matrix": cm,
        "roc_curve": roc_data,
        "feature_importances": feat_importance_dict,
        "feature_columns": FEATURE_COLUMNS,
        "parameters": {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "class_weight": "balanced",
            "random_state": random_state,
        },
    }

    # Save model artifact and metadata
    joblib.dump(model, model_path)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def get_model_metadata() -> Optional[Dict[str, Any]]:
    """Loads existing model metadata if available."""
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

