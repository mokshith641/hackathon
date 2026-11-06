"""
Session State Management for SocialShield AI
Maintains synchronized audit history, moderator statuses, and configuration across all Streamlit pages.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from modules.data_loader import generate_benchmark_dataset


def init_session_state():
    """Initializes shared session state variables if not already set."""
    if "audit_history" not in st.session_state:
        # Pre-populate with a few realistic demonstration audit records
        st.session_state.audit_history = [
            {
                "raw_input": {
                    "username": "cryptopump_daily99",
                    "platform": "X (Twitter)",
                    "data_source": "Synthetic Demo Data",
                    "followers_count": 34,
                    "following_count": 3200,
                    "total_posts": 620,
                    "account_age_days": 14,
                    "description": "🚀 100x GEM CRYPTO ALERT! Free airdrop links in bio 🔥 DM for promotion",
                    "has_profile_picture": 0,
                    "is_verified": 0,
                },
                "risk": {
                    "risk_score": 91.2,
                    "risk_category": "Very High Risk",
                    "badge_color": "#DC2626",
                    "status_label": "High Probability Bot / Farm",
                    "confidence_level": "Very High (Dominant coordinated/bot indicators)",
                    "recommended_action": "Immediate priority moderator review. Verify phone/reCAPTCHA challenge.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "prediction": {
                    "bot_probability": 0.912,
                    "predicted_class": 1,
                    "platform": "X (Twitter)",
                    "is_platform_native": True,
                },
                "explanation": {
                    "summary": "This account is flagged with very high risk (91.2%) primarily driven by severe follower asymmetry and aggressive post velocity.",
                    "suspicious_indicators": [
                        {"title": "Severe Follower Asymmetry", "detail": "Following 3,200 accounts with only 34 followers.", "severity": "High"},
                        {"title": "Brand New Account (< 14 days)", "detail": "Account created 14 days ago.", "severity": "High"},
                        {"title": "Automated Username Syntax", "detail": "Contains 4 random suffix digits.", "severity": "Medium"},
                        {"title": "Default Avatar", "detail": "No custom avatar uploaded.", "severity": "Medium"}
                    ],
                    "mitigating_indicators": [],
                },
                "review_status": "Pending Review",
                "moderator_notes": "",
            },
            {
                "raw_input": {
                    "username": "sophia_tech_lead",
                    "platform": "X (Twitter)",
                    "data_source": "Synthetic Demo Data",
                    "followers_count": 2840,
                    "following_count": 520,
                    "total_posts": 3410,
                    "account_age_days": 1420,
                    "description": "Staff Engineer @ FinTech. Distributed systems, open source, and hiking.",
                    "has_profile_picture": 1,
                    "is_verified": 1,
                },
                "risk": {
                    "risk_score": 6.4,
                    "risk_category": "Low Risk",
                    "badge_color": "#10B981",
                    "status_label": "Organic / Genuine",
                    "confidence_level": "High (Consistent human activity signals)",
                    "recommended_action": "No intervention necessary. Normal account activity.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "prediction": {
                    "bot_probability": 0.064,
                    "predicted_class": 0,
                    "platform": "X (Twitter)",
                    "is_platform_native": True,
                },
                "explanation": {
                    "summary": "This account exhibits authentic human social behavior (6.4% risk).",
                    "suspicious_indicators": [],
                    "mitigating_indicators": [
                        {"title": "Established Tenure (> 2 years)", "detail": "Account active for 1,420 days.", "benefit": "Strong"},
                        {"title": "Platform Verified Identity", "detail": "Account is verified on platform.", "benefit": "Strong"},
                        {"title": "Balanced Social Graph", "detail": "2,840 followers / 520 following.", "benefit": "Strong"},
                    ],
                },
                "review_status": "Cleared",
                "moderator_notes": "Verified authentic creator profile.",
            },
            {
                "raw_input": {
                    "username": "insta_growth_hub22",
                    "platform": "Instagram",
                    "data_source": "Synthetic Demo Data",
                    "followers_count": 890,
                    "following_count": 4200,
                    "total_posts": 98,
                    "account_age_days": 65,
                    "description": "Follow for follow back! Grow fast with us 24/7 engagement #f4f",
                    "has_profile_picture": 1,
                    "is_verified": 0,
                },
                "risk": {
                    "risk_score": 72.8,
                    "risk_category": "High Risk",
                    "badge_color": "#EA580C",
                    "status_label": "Suspicious Activity",
                    "confidence_level": "High (Multiple automated patterns detected)",
                    "recommended_action": "Assign to human moderator queue for profile inspection.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                "prediction": {
                    "bot_probability": 0.728,
                    "predicted_class": 1,
                    "platform": "Instagram",
                    "is_platform_native": False,
                },
                "explanation": {
                    "summary": "This account exhibits high risk (72.8%) due to mass follow-farming patterns and engagement spam keywords.",
                    "suspicious_indicators": [
                        {"title": "Aggressive Mass Following", "detail": "Following 4,200 accounts with 890 followers.", "severity": "Medium"},
                        {"title": "Spam Bio Keywords", "detail": "Contains follow-for-follow recruitment tags.", "severity": "High"},
                    ],
                    "mitigating_indicators": [],
                },
                "review_status": "Escalated",
                "moderator_notes": "Suspected engagement ring node.",
            }
        ]

    if "thresholds" not in st.session_state:
        st.session_state.thresholds = {
            "low_max": 29,
            "moderate_max": 59,
            "high_max": 79,
        }

    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {
            "x_bearer_token": "",
            "instagram_token": "",
            "facebook_token": "",
        }


def add_audit_record(record: dict):
    """Appends an analyzed account to audit history, deduplicating by username."""
    history = st.session_state.audit_history
    username = record.get("raw_input", {}).get("username")
    # Remove older entry if same username exists
    st.session_state.audit_history = [
        r for r in history if r.get("raw_input", {}).get("username") != username
    ]
    st.session_state.audit_history.insert(0, record)


def update_moderator_status(username: str, status: str, notes: str = ""):
    """Updates review status for an account."""
    for r in st.session_state.audit_history:
        if r.get("raw_input", {}).get("username") == username:
            r["review_status"] = status
            if notes:
                r["moderator_notes"] = notes
            break

