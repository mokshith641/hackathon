"""
Report Generator Module for SocialShield AI
Generates structured CSV and markdown intelligence briefs for analyzed accounts and moderator audits.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List


def generate_single_account_report_df(analysis_result: Dict[str, Any]) -> pd.DataFrame:
    """Creates a flattened 1-row DataFrame ready for instant CSV export."""
    raw = analysis_result.get("raw_input", {})
    risk = analysis_result.get("risk", {})
    pred = analysis_result.get("prediction", {})
    exp = analysis_result.get("explanation", {})

    record = {
        "analysis_timestamp": risk.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "username": raw.get("username", "Unknown"),
        "platform": raw.get("platform", "Unknown"),
        "data_source": raw.get("data_source", "Manual Input"),
        "risk_score": risk.get("risk_score", "N/A"),
        "risk_category": risk.get("risk_category", "Unknown"),
        "bot_probability": pred.get("bot_probability", "N/A"),
        "model_prediction": "Bot / Suspicious" if pred.get("predicted_class") == 1 else "Organic / Human",
        "confidence_level": risk.get("confidence_level", "Standard"),
        "moderator_recommendation": risk.get("recommended_action", ""),
        "explanation_summary": exp.get("summary", ""),
        "suspicious_factors_count": len(exp.get("suspicious_indicators", [])),
        "mitigating_factors_count": len(exp.get("mitigating_indicators", [])),
        "followers_count": raw.get("followers_count", 0),
        "following_count": raw.get("following_count", 0),
        "total_posts": raw.get("total_posts", 0),
        "account_age_days": raw.get("account_age_days", 0),
        "has_profile_picture": raw.get("has_profile_picture", 1),
        "is_verified": raw.get("is_verified", 0),
        "review_status": analysis_result.get("review_status", "Pending Review"),
        "moderator_notes": analysis_result.get("moderator_notes", ""),
    }

    return pd.DataFrame([record])


def generate_audit_export_csv(audit_records: List[Dict[str, Any]]) -> str:
    """Exports a list of reviewed accounts to CSV string."""
    rows = []
    for item in audit_records:
        df_single = generate_single_account_report_df(item)
        rows.append(df_single)
    if rows:
        combined = pd.concat(rows, ignore_index=True)
        return combined.to_csv(index=False)
    return pd.DataFrame().to_csv(index=False)

