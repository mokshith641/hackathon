"""
Explainable AI (XAI) Module for SocialShield AI
Generates human-interpretable feature contribution attributions and natural language explanations.
"""

from typing import Dict, Any, List


def explain_account_risk(features: dict, raw_account: dict, bot_prob: float) -> Dict[str, Any]:
    """
    Deconstructs account indicators to show:
    1. Suspicious risk indicators pushing score higher
    2. Mitigating organic indicators lowering score
    3. Missing or unverified evidence
    4. Quantitative feature impact scores for waterfall / attribution visualization
    """
    suspicious_indicators = []
    mitigating_indicators = []
    neutral_or_missing = []
    impact_scores = {}

    age_days = features.get("account_age_days", 365)
    followers = features.get("followers_count", 0)
    following = features.get("following_count", 0)
    ratio = features.get("follower_following_ratio", 1.0)
    posts_per_day = features.get("posts_per_day", 1.0)
    has_bio = features.get("has_profile_description", 1)
    has_pic = features.get("has_profile_picture", 1)
    digit_ratio = features.get("username_digit_ratio", 0.0)
    is_verified = features.get("is_verified", 0)

    # 1. Follower-to-Following Dynamic
    if following > 500 and followers < 50:
        suspicious_indicators.append({
            "title": "Severe Follower Asymmetry",
            "detail": f"Account follows {following:,} accounts but has only {followers:,} followers (ratio: {ratio:.3f}). Classic follow-farming signature.",
            "severity": "High",
            "weight": +25,
        })
        impact_scores["Follower/Following Disparity"] = +25
    elif following > 2000 and followers < 250:
        suspicious_indicators.append({
            "title": "Aggressive Mass Following",
            "detail": f"Unusually high outbound following ({following:,}) relative to audience engagement.",
            "severity": "Medium",
            "weight": +18,
        })
        impact_scores["Mass Following Pattern"] = +18
    elif followers > 200 and following > 50 and ratio >= 0.7:
        mitigating_indicators.append({
            "title": "Balanced Social Graph",
            "detail": f"Healthy follower-to-following balance ({followers:,} / {following:,}).",
            "benefit": "Strong",
            "weight": -15,
        })
        impact_scores["Balanced Social Graph"] = -15

    # 2. Account Age & Velocity
    if age_days < 14:
        suspicious_indicators.append({
            "title": "Brand New Account (< 14 days)",
            "detail": f"Account created just {age_days} days ago. High vulnerability window for disposable automation.",
            "severity": "High",
            "weight": +22,
        })
        impact_scores["Account Recency (< 14d)"] = +22
    elif age_days < 60:
        suspicious_indicators.append({
            "title": "Recently Created Account",
            "detail": f"Account age is {age_days} days. Immature history.",
            "severity": "Low",
            "weight": +10,
        })
        impact_scores["Account Recency (< 60d)"] = +10
    elif age_days > 730:
        mitigating_indicators.append({
            "title": "Established Tenure (> 2 years)",
            "detail": f"Account has existed stably for {age_days} days ({round(age_days/365, 1)} years).",
            "benefit": "Strong",
            "weight": -18,
        })
        impact_scores["Established Longevity"] = -18

    # 3. Post Frequency / Burstiness
    if posts_per_day > 60:
        suspicious_indicators.append({
            "title": "Inhuman Posting Velocity",
            "detail": f"Averaging {posts_per_day:.1f} posts/day. Exceeds typical manual human publishing rates.",
            "severity": "High",
            "weight": +20,
        })
        impact_scores["Posting Velocity (>60/day)"] = +20
    elif posts_per_day > 25:
        suspicious_indicators.append({
            "title": "Elevated Post Velocity",
            "detail": f"Publishing {posts_per_day:.1f} posts/day continuously.",
            "severity": "Medium",
            "weight": +12,
        })
        impact_scores["Elevated Post Velocity"] = +12
    elif 0.1 <= posts_per_day <= 5.0:
        mitigating_indicators.append({
            "title": "Natural Human Posting Cadence",
            "detail": f"Sustainable posting rate of {posts_per_day:.2f} posts/day.",
            "benefit": "Moderate",
            "weight": -10,
        })
        impact_scores["Natural Post Cadence"] = -10

    # 4. Username Lexical Pattern
    if digit_ratio >= 0.40:
        suspicious_indicators.append({
            "title": "High Username Digit Concentration",
            "detail": f"{round(digit_ratio * 100)}% of the username consists of random numeric digits. Typical of automated batch registration.",
            "severity": "Medium",
            "weight": +15,
        })
        impact_scores["Automated Username Syntax"] = +15
    elif digit_ratio == 0:
        mitigating_indicators.append({
            "title": "Organic Human Username",
            "detail": "Username consists entirely of alphabetic characters without trailing generation numbers.",
            "benefit": "Low",
            "weight": -6,
        })
        impact_scores["Clean Username Syntax"] = -6

    # 5. Profile Completeness
    if has_pic == 0:
        suspicious_indicators.append({
            "title": "Default Avatar / Missing Profile Picture",
            "detail": "Account has not uploaded a customized profile avatar.",
            "severity": "Medium",
            "weight": +14,
        })
        impact_scores["Default Avatar"] = +14
    else:
        mitigating_indicators.append({
            "title": "Custom Profile Picture Set",
            "detail": "Account maintains a customized personal/brand avatar.",
            "benefit": "Low",
            "weight": -5,
        })
        impact_scores["Profile Picture Active"] = -5

    if has_bio == 0:
        suspicious_indicators.append({
            "title": "Empty Profile Description",
            "detail": "No biographical context provided in profile description.",
            "severity": "Low",
            "weight": +8,
        })
        impact_scores["Empty Bio"] = +8
    else:
        bio_text = str(raw_account.get("description", "")).lower()
        if any(w in bio_text for w in ["crypto", "airdrop", "f4f", "follow back", "free followers", "giveaway", "100x"]):
            suspicious_indicators.append({
                "title": "Spam / Promotion Keyword Triggers in Bio",
                "detail": "Profile description contains commercial spam or botnet recruitment terms.",
                "severity": "High",
                "weight": +18,
            })
            impact_scores["Spam Bio Keywords"] = +18
        else:
            mitigating_indicators.append({
                "title": "Coherent Profile Biography",
                "detail": "Profile includes a descriptive personal or professional statement.",
                "benefit": "Low",
                "weight": -5,
            })
            impact_scores["Descriptive Biography"] = -5

    # 6. Verification Status
    if is_verified == 1:
        mitigating_indicators.append({
            "title": "Platform Verified Identity",
            "detail": "Account holds verified status on this platform.",
            "benefit": "Strong",
            "weight": -25,
        })
        impact_scores["Platform Verified"] = -25

    # Check for missing platform telemetry
    if raw_account.get("created_at") is None and raw_account.get("account_age_days") is None:
        neutral_or_missing.append("Exact account creation timestamp not available.")
    if raw_account.get("has_profile_picture") is None:
        neutral_or_missing.append("Profile picture metadata was inferred by default.")

    # Natural Language Executive Summary
    if bot_prob >= 0.60:
        nl_summary = (
            f"This account is flagged with high risk ({round(bot_prob*100, 1)}%) primarily driven by "
            + (f"'{suspicious_indicators[0]['title']}'" if suspicious_indicators else "pattern anomalies")
            + (f" and '{suspicious_indicators[1]['title']}'." if len(suspicious_indicators) > 1 else ".")
            + " Human moderator review is recommended to inspect content originality before taking action."
        )
    elif bot_prob >= 0.30:
        nl_summary = (
            f"This account exhibits moderate caution indicators ({round(bot_prob*100, 1)}%). While exhibiting some suspicious traits, "
            + (f"counterbalanced by '{mitigating_indicators[0]['title']}'." if mitigating_indicators else "it does not present conclusive automation patterns.")
            + " Standard behavioral monitoring is advised."
        )
    else:
        nl_summary = (
            f"This account exhibits authentic human social behavior ({round(bot_prob*100, 1)}% risk). "
            + (f"Key organic signals include '{mitigating_indicators[0]['title']}'." if mitigating_indicators else "Metrics fall well within normal user distributions.")
        )

    return {
        "summary": nl_summary,
        "suspicious_indicators": suspicious_indicators,
        "mitigating_indicators": mitigating_indicators,
        "neutral_or_missing": neutral_or_missing,
        "impact_scores": impact_scores,
    }

