"""
Risk Scoring Engine for SocialShield AI
Converts model probabilities and data completeness into transparent 0-100 risk assessments.
"""

from datetime import datetime
from typing import Dict, Any, Tuple


DEFAULT_RISK_THRESHOLDS = {
    "low_max": 29,
    "moderate_max": 59,
    "high_max": 79,
}


def check_data_completeness(account_data: dict) -> Tuple[bool, str]:
    """
    Checks if there is sufficient data to make a reliable assessment.
    Returns (is_sufficient, reason).
    """
    followers = account_data.get("followers_count") or account_data.get("followers")
    following = account_data.get("following_count") or account_data.get("following")
    created = account_data.get("created_at") or account_data.get("account_created_at") or account_data.get("account_age_days")
    username = account_data.get("username") or account_data.get("screen_name")

    missing = []
    if username is None or str(username).strip() == "":
        missing.append("Username")
    if followers is None and following is None:
        missing.append("Followers/Following metrics")
    if created is None:
        missing.append("Account creation timeline")

    if len(missing) >= 2:
        return False, f"Insufficient Data: Missing critical profile signals ({', '.join(missing)})."
    return True, "Data sufficiency verified."


def calculate_risk_score(
    bot_probability: float,
    account_data: dict,
    thresholds: dict = None
) -> Dict[str, Any]:
    """
    Computes the final risk score (0-100), categorization, and actionable recommendations.
    """
    th = thresholds or DEFAULT_RISK_THRESHOLDS

    is_sufficient, sufficiency_note = check_data_completeness(account_data)

    if not is_sufficient:
        return {
            "risk_score": None,
            "risk_category": "Insufficient Data",
            "badge_color": "#94A3B8",  # Slate
            "status_label": "Inconclusive",
            "bot_probability": None,
            "confidence_level": "Low (Missing signals)",
            "sufficiency_note": sufficiency_note,
            "recommended_action": "Request full profile audit or wait for API synchronization.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # Base formula: Risk Score = Probability * 100
    base_score = bot_probability * 100

    # Threat Intelligence Calibration: Adjust for extreme structural anomalies
    adjustment = 0.0
    followers = float(account_data.get("followers_count") or account_data.get("followers") or 0)
    following = float(account_data.get("following_count") or account_data.get("following") or 0)

    # 1. Follower Asymmetry (Mass outbound follow farm)
    if following > 2000 and followers < 100:
        adjustment += 22.0
    elif following > 800 and followers < 40:
        adjustment += 14.0

    # 2. Extreme follow count (> 20,000 following with minimal followers)
    if following > 20000 and followers < 500:
        adjustment += 25.0

    # 3. Verified authenticity mitigation
    is_ver = account_data.get("is_verified")
    if is_ver in [1, True, "1", "true", "True"]:
        adjustment -= 25.0

    # Combined calibrated score bounded between 0 and 100
    risk_score = round(max(0.0, min(100.0, base_score + adjustment * 0.7)), 1)

    if risk_score <= th.get("low_max", 29):
        category = "Low Risk"
        badge_color = "#10B981"  # Emerald green
        status_label = "Organic / Genuine"
        confidence = "High (Consistent human activity signals)"
        action = "No intervention necessary. Normal account activity."
    elif risk_score <= th.get("moderate_max", 59):
        category = "Moderate Risk"
        badge_color = "#F59E0B"  # Amber
        status_label = "Elevated Caution"
        confidence = "Moderate (Mixed behavioral indicators)"
        action = "Flag for routine periodic monitoring. No punitive action recommended."
    elif risk_score <= th.get("high_max", 79):
        category = "High Risk"
        badge_color = "#EA580C"  # Orange
        status_label = "Suspicious Activity"
        confidence = "High (Multiple automated patterns detected)"
        action = "Assign to human moderator queue for profile inspection and activity audit."
    else:
        category = "Very High Risk"
        badge_color = "#DC2626"  # Crimson red
        status_label = "High Probability Bot / Farm"
        confidence = "Very High (Dominant coordinated/bot indicators)"
        action = "Immediate priority moderator review. Verify phone/reCAPTCHA challenge."

    return {
        "risk_score": risk_score,
        "risk_category": category,
        "badge_color": badge_color,
        "status_label": status_label,
        "bot_probability": bot_probability,
        "confidence_level": confidence,
        "sufficiency_note": sufficiency_note,
        "recommended_action": action,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

