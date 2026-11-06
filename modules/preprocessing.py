"""
Data Preprocessing Module for SocialShield AI
Validates, cleans, and standardizes account datasets while guarding against target leakage.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
from modules.feature_extraction import FEATURE_COLUMNS, extract_features_df

# Known label column names in academic and public bot datasets
TARGET_COLUMNS = [
    "is_bot",
    "bot",
    "label",
    "target",
    "is_fake",
    "fake",
    "account_type",
    "class",
]

# Common aliases mapping to standardized raw fields
COLUMN_ALIASES = {
    "username": ["username", "screen_name", "user_name", "handle", "account_name"],
    "created_at": ["created_at", "account_created_at", "creation_date", "registered_at", "timestamp"],
    "followers_count": ["followers_count", "followers", "user_followers", "follower_count", "#followers"],
    "following_count": ["following_count", "following", "friends_count", "user_friends", "user_following", "#follows"],
    "total_posts": ["total_posts", "statuses_count", "posts", "media_count", "tweet_count", "tweets", "#posts"],
    "description": ["description", "bio", "profile_description", "user_description", "about"],
    "has_profile_picture": ["has_profile_picture", "has_profile_pic", "profile_image_url", "default_profile_image", "profile pic"],
    "is_verified": ["is_verified", "verified", "user_verified", "is_blue_verified"],
    "platform": ["platform", "social_network", "source_platform"],
}


def detect_column_mapping(df_columns: list) -> Dict[str, Optional[str]]:
    """Finds best matching column in dataframe for each standard field."""
    mapping = {}
    cols_lower = {col.lower().strip(): col for col in df_columns}
    for standard_field, aliases in COLUMN_ALIASES.items():
        matched = None
        for alias in aliases:
            if alias.lower() in cols_lower:
                matched = cols_lower[alias.lower()]
                break
        mapping[standard_field] = matched
    return mapping


def detect_target_column(df_columns: list) -> Optional[str]:
    """Identifies the target label column without user ambiguity."""
    cols_lower = {col.lower().strip(): col for col in df_columns}
    for t in TARGET_COLUMNS:
        if t in cols_lower:
            return cols_lower[t]
    return None


def clean_and_prepare_dataset(
    df: pd.DataFrame,
    target_col: Optional[str] = None
) -> Tuple[pd.DataFrame, Optional[pd.Series], Dict[str, Any]]:
    """
    Cleans raw account DataFrame, maps fields, prevents data leakage,
    and returns standardized feature DataFrame X and binary series y (if target exists).
    
    Target encoding:
    1 = Bot / Fake / Suspicious
    0 = Genuine / Human
    """
    df_clean = df.copy()

    # Detect target if not explicitly passed
    if not target_col:
        target_col = detect_target_column(df_clean.columns.tolist())

    y = None
    if target_col and target_col in df_clean.columns:
        # Extract target and drop immediately to prevent data leakage
        raw_y = df_clean[target_col]
        # Standardize labels
        if raw_y.dtype == object or isinstance(raw_y.iloc[0], str):
            y_mapped = raw_y.astype(str).str.strip().str.lower().map({
                "bot": 1, "fake": 1, "1": 1, "true": 1, "spam": 1, "spambot": 1,
                "human": 0, "genuine": 0, "0": 0, "false": 0, "real": 0, "legit": 0
            })
            y = y_mapped.fillna(0).astype(int)
        else:
            y = (raw_y.astype(float) > 0.5).astype(int)
        df_clean = df_clean.drop(columns=[target_col])

    # Extract features using feature extraction pipeline
    X = extract_features_df(df_clean)

    # Impute any residual inf or NaN
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)

    summary = {
        "total_records": len(df_clean),
        "features_extracted": len(FEATURE_COLUMNS),
        "target_detected": target_col is not None,
        "target_col_name": target_col,
        "class_balance": y.value_counts().to_dict() if y is not None else None,
    }

    return X, y, summary

