"""
Feature Extraction Module for SocialShield AI
Extracts consistent numerical and behavioral indicators from account records across platforms.
"""

from datetime import datetime, date
import re
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "account_age_days",
    "followers_count",
    "following_count",
    "follower_following_ratio",
    "reputation_ratio",
    "total_posts",
    "posts_per_day",
    "has_profile_description",
    "description_length",
    "has_profile_picture",
    "username_length",
    "username_digits_count",
    "username_digit_ratio",
    "is_verified",
]


def parse_date(date_val) -> int:
    """Calculates account age in days from various date formats."""
    if date_val is None or pd.isna(date_val) or str(date_val).strip() == "":
        return 365  # Default baseline age if completely missing

    now = datetime.now()
    if isinstance(date_val, (datetime, date)):
        target_dt = datetime.combine(date_val, datetime.min.time()) if isinstance(date_val, date) and not isinstance(date_val, datetime) else date_val
    else:
        s = str(date_val).strip()
        parsed = None
        # Try common datetime formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%a %b %d %H:%M:%S +0000 %Y",  # Twitter API format
            "%a %b %d %H:%M:%S %z %Y",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
        ]
        for fmt in formats:
            try:
                parsed = datetime.strptime(s, fmt)
                break
            except (ValueError, TypeError):
                continue

        if parsed is None:
            # Fallback to dateutil if available
            try:
                from dateutil import parser
                parsed = parser.parse(s)
            except Exception:
                return 365
        target_dt = parsed

    # Remove timezone info for simple delta calculation
    if target_dt.tzinfo is not None:
        target_dt = target_dt.replace(tzinfo=None)

    delta = (now - target_dt).days
    return max(0, min(delta, 10000))  # Bound between 0 and ~27 years


def extract_username_features(username: str) -> dict:
    """Extracts lexical signals from the username."""
    u = str(username or "").strip()
    length = len(u)
    if length == 0:
        return {
            "username_length": 0,
            "username_digits_count": 0,
            "username_digit_ratio": 0.0,
        }

    digits = len(re.findall(r"\d", u))
    digit_ratio = round(digits / length, 4)
    return {
        "username_length": length,
        "username_digits_count": digits,
        "username_digit_ratio": digit_ratio,
    }


def extract_features_from_dict(raw: dict) -> dict:
    """
    Transforms a single account dictionary (manual input or API response)
    into a standardized numeric feature dictionary.
    """
    # 1. Date & Age
    created_at = raw.get("created_at") or raw.get("account_created_at") or raw.get("creation_date")
    # If age in days is provided directly
    if "account_age_days" in raw and not pd.isna(raw["account_age_days"]):
        try:
            account_age_days = max(0, int(float(raw["account_age_days"])))
        except (ValueError, TypeError):
            account_age_days = parse_date(created_at)
    else:
        account_age_days = parse_date(created_at)

    # 2. Followers & Following
    def safe_int(val, default=0):
        if val is None or pd.isna(val):
            return default
        try:
            return max(0, int(float(val)))
        except (ValueError, TypeError):
            return default

    followers = safe_int(
        raw.get("followers_count") or raw.get("followers") or raw.get("user_followers") or raw.get("#followers")
    )
    following = safe_int(
        raw.get("following_count") or raw.get("following") or raw.get("friends_count") or raw.get("user_following") or raw.get("#follows")
    )

    # Ratios (safe division)
    follower_following_ratio = round(followers / (following + 1), 4)
    reputation_ratio = round(followers / (followers + following + 1), 4)

    # 3. Posts & Activity
    total_posts = safe_int(
        raw.get("total_posts") or raw.get("statuses_count") or raw.get("media_count") or raw.get("posts_count") or raw.get("#posts")
    )
    # Posts per day
    if "posts_per_day" in raw and not pd.isna(raw["posts_per_day"]):
        try:
            posts_per_day = max(0.0, float(raw["posts_per_day"]))
        except (ValueError, TypeError):
            posts_per_day = round(total_posts / (account_age_days + 1), 4)
    else:
        posts_per_day = round(total_posts / (account_age_days + 1), 4)

    # 4. Profile Description / Bio
    if "description length" in raw and not pd.isna(raw["description length"]):
        description_length = safe_int(raw["description length"])
        has_profile_description = 1 if description_length > 0 else 0
    else:
        description = str(raw.get("description") or raw.get("profile_description") or raw.get("bio") or "").strip()
        has_profile_description = 1 if len(description) > 0 and description.lower() != "none" and description.lower() != "nan" else 0
        description_length = len(description) if has_profile_description else 0

    # 5. Profile Picture
    has_pic = raw.get("has_profile_picture") or raw.get("has_profile_pic") or raw.get("default_profile_image") or raw.get("profile pic")
    if isinstance(has_pic, bool):
        has_profile_picture = 1 if has_pic else 0
    elif isinstance(has_pic, (int, float)):
        has_profile_picture = 1 if int(has_pic) == 1 else 0
    elif isinstance(has_pic, str):
        # Note: In Twitter API, default_profile_image=True means they DO NOT have custom picture
        s = has_pic.strip().lower()
        if "default" in s:
            has_profile_picture = 0 if "true" in s or s == "1" else 1
        else:
            has_profile_picture = 1 if s in ["yes", "true", "1", "available", "y"] else 0
    else:
        has_profile_picture = 1  # Standard default assumption if unstated

    # 6. Username metrics
    username = str(raw.get("username") or raw.get("screen_name") or "")
    u_feat = extract_username_features(username)
    if "nums/length username" in raw and not pd.isna(raw["nums/length username"]):
        try:
            u_feat["username_digit_ratio"] = round(float(raw["nums/length username"]), 4)
        except (ValueError, TypeError):
            pass

    # 7. Verification
    is_ver = raw.get("is_verified") or raw.get("verified")
    if isinstance(is_ver, bool):
        is_verified = 1 if is_ver else 0
    elif isinstance(is_ver, (int, float)):
        is_verified = 1 if int(is_ver) == 1 else 0
    elif isinstance(is_ver, str):
        is_verified = 1 if is_ver.strip().lower() in ["yes", "true", "1"] else 0
    else:
        is_verified = 0

    features = {
        "account_age_days": account_age_days,
        "followers_count": followers,
        "following_count": following,
        "follower_following_ratio": follower_following_ratio,
        "reputation_ratio": reputation_ratio,
        "total_posts": total_posts,
        "posts_per_day": posts_per_day,
        "has_profile_description": has_profile_description,
        "description_length": description_length,
        "has_profile_picture": has_profile_picture,
        "username_length": u_feat["username_length"],
        "username_digits_count": u_feat["username_digits_count"],
        "username_digit_ratio": u_feat["username_digit_ratio"],
        "is_verified": is_verified,
    }
    return features


def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts standardized features DataFrame from any tabular account data."""
    extracted_rows = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        extracted_rows.append(extract_features_from_dict(row_dict))
    return pd.DataFrame(extracted_rows, columns=FEATURE_COLUMNS)

