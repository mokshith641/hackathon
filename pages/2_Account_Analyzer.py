"""
Page 2: Multi-Platform Account Analyzer
Individual account risk assessment with explainable AI indicators and moderator review actions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

from modules.session_state import init_session_state, add_audit_record
from modules.feature_extraction import extract_features_from_dict
from modules.prediction import predict_single_account
from modules.risk_scoring import calculate_risk_score
from modules.explainability import explain_account_risk
from modules.platform_adapters import fetch_x_account, fetch_instagram_account, fetch_facebook_account

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">Multi-Platform Account Analyzer</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Inspect individual user accounts across X, Instagram, and Facebook using explainable ML indicators.
    </p>
</div>
""", unsafe_allow_html=True)

# Preset Demo Scenarios for instant hackathon testing
PRESETS = {
    "Select a preset scenario...": None,
    "1. Genuine Tech Journalist (Verified, organic history)": {
        "username": "elena_vance_press",
        "platform": "X (Twitter)",
        "creation_date": date.today() - timedelta(days=1840),
        "followers": 14200,
        "following": 680,
        "posts": 4120,
        "bio": "Investigative cyber reporter @ TechHerald. Stories on AI ethics, digital rights, and privacy. DMs open.",
        "has_pic": True,
        "verified": True,
    },
    "2. High-Frequency Follower Bot (Asymmetric following, young age)": {
        "username": "boost_fans_fast_9921",
        "platform": "X (Twitter)",
        "creation_date": date.today() - timedelta(days=12),
        "followers": 18,
        "following": 4850,
        "posts": 620,
        "bio": "FOLLOW ME FOR INSTANT FOLLOW BACK! Automated growth booster 24/7. Gain 1000 real followers fast!",
        "has_pic": False,
        "verified": False,
    },
    "3. Crypto Pump Scam Bot (Repetitive spam bio, default avatar)": {
        "username": "crypto_moon_gem_8472",
        "platform": "X (Twitter)",
        "creation_date": date.today() - timedelta(days=19),
        "followers": 42,
        "following": 3100,
        "posts": 490,
        "bio": "🚀 100x GEM CRYPTO ALERT! Free airdrop tokens claim now at t.me/free_crypto_drop 🔥 Don't miss out!",
        "has_pic": False,
        "verified": False,
    },
    "4. Organic Indie Creator (Healthy balanced ratio)": {
        "username": "lucas_indie_games",
        "platform": "Instagram",
        "creation_date": date.today() - timedelta(days=820),
        "followers": 3200,
        "following": 510,
        "posts": 184,
        "bio": "Solo game developer crafting cozy pixel art adventures. Sharing devlogs, mechanics, and coffee.",
        "has_pic": True,
        "verified": False,
    },
    "5. Dormant / Disposable Profile (Minimal metadata)": {
        "username": "user84920194821",
        "platform": "X (Twitter)",
        "creation_date": date.today() - timedelta(days=5),
        "followers": 0,
        "following": 85,
        "posts": 2,
        "bio": "",
        "has_pic": False,
        "verified": False,
    }
}

col_preset, col_mode = st.columns([3, 2])
with col_preset:
    chosen_preset = st.selectbox("⚡ Quick Demo Presets (1-Click Test Cases)", list(PRESETS.keys()))

with col_mode:
    input_mode = st.radio("Acquisition Mode", ["Manual Input", "Live API Lookup"], horizontal=True)

# Preset data filler
preset_data = PRESETS.get(chosen_preset) if chosen_preset != "Select a preset scenario..." else None

# Form Fields
with st.container():
    st.markdown("<div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        default_username = preset_data["username"] if preset_data else "alex_rivers"
        username_input = st.text_input("Username / Handle", value=default_username, placeholder="e.g. johndoe")
    
    with col2:
        default_platform_idx = ["X (Twitter)", "Instagram", "Facebook", "Other"].index(preset_data["platform"]) if preset_data else 0
        platform_input = st.selectbox("Platform", ["X (Twitter)", "Instagram", "Facebook", "Other"], index=default_platform_idx)
    
    with col3:
        default_date = preset_data["creation_date"] if preset_data else date.today() - timedelta(days=730)
        creation_date_input = st.date_input("Account Creation Date", value=default_date)

    # Check session state for fetched live data
    if "fetched_live_data" not in st.session_state:
        st.session_state.fetched_live_data = None
        st.session_state.fetched_source_label = "Manual Input"

    if input_mode == "Live API Lookup":
        st.info("ℹ️ Live API mode utilizes the SocialCrawl multi-platform intelligence gateway (active) and official platform APIs.")
        col_api_btn, col_api_status = st.columns([1, 2])
        with col_api_btn:
            if st.button("🌐 Fetch Live Profile Telemetry", type="primary"):
                with st.spinner(f"Connecting to {platform_input} API for @{username_input}..."):
                    if platform_input == "X (Twitter)":
                        data_fetched, source_lbl, msg = fetch_x_account(username_input)
                    elif platform_input == "Instagram":
                        data_fetched, source_lbl, msg = fetch_instagram_account(username_input)
                    elif platform_input == "Facebook":
                        data_fetched, source_lbl, msg = fetch_facebook_account(username_input)
                    else:
                        data_fetched, source_lbl, msg = None, "Manual Input", "No live API endpoint configured for this platform."

                    if data_fetched:
                        st.session_state.fetched_live_data = data_fetched
                        st.session_state.fetched_source_label = source_lbl
                        st.success(msg)
                    else:
                        st.session_state.fetched_live_data = None
                        st.session_state.fetched_source_label = "Manual Input"
                        st.warning(msg)
    else:
        st.session_state.fetched_live_data = None
        st.session_state.fetched_source_label = "Manual Input"

    live_data = st.session_state.fetched_live_data
    data_source_label = st.session_state.fetched_source_label

    # Metrics inputs
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        def_followers = live_data.get("followers_count") if live_data else (preset_data["followers"] if preset_data else 850)
        followers_input = st.number_input("Followers Count", min_value=0, max_value=1000000000, value=int(def_followers), step=10)

    with col_m2:
        def_following = live_data.get("following_count") if live_data else (preset_data["following"] if preset_data else 320)
        following_input = st.number_input("Following Count", min_value=0, max_value=50000000, value=int(def_following), step=10)

    with col_m3:
        def_posts = live_data.get("total_posts") if live_data else (preset_data["posts"] if preset_data else 450)
        total_posts_input = st.number_input("Total Posts / Tweets", min_value=0, max_value=5000000, value=int(def_posts), step=10)

    col_b1, col_b2, col_b3 = st.columns([3, 1, 1])
    with col_b1:
        def_bio = live_data.get("description") if live_data else (preset_data["bio"] if preset_data else "Building things with code, coffee, and AI.")
        bio_input = st.text_area("Profile Biography / Description", value=def_bio, height=68)

    with col_b2:
        def_pic = bool(live_data.get("has_profile_picture", 1)) if live_data else (preset_data["has_pic"] if preset_data else True)
        has_pic_input = st.checkbox("Has Custom Avatar", value=def_pic)

    with col_b3:
        def_ver = bool(live_data.get("is_verified", 0)) if live_data else (preset_data["verified"] if preset_data else False)
        is_verified_input = st.checkbox("Verified Badge", value=def_ver)

    st.markdown("</div>", unsafe_allow_html=True)

# Analyze Button
analyze_pressed = st.button("🛡️ Run SocialShield Risk Assessment", type="primary", use_container_width=True)

if analyze_pressed or "last_analysis" in st.session_state:
    if analyze_pressed:
        # Build account dictionary
        account_data = {
            "username": username_input.strip(),
            "platform": platform_input,
            "created_at": creation_date_input.strftime("%Y-%m-%d"),
            "followers_count": followers_input,
            "following_count": following_input,
            "total_posts": total_posts_input,
            "description": bio_input,
            "has_profile_picture": 1 if has_pic_input else 0,
            "is_verified": 1 if is_verified_input else 0,
            "data_source": data_source_label,
        }

        # Predict with ML Engine
        with st.spinner("Extracting behavioral features and scoring risk..."):
            pred_result = predict_single_account(account_data)
            risk_result = calculate_risk_score(pred_result["bot_probability"], account_data, st.session_state.thresholds)
            explanation_result = explain_account_risk(pred_result["features"], account_data, pred_result["bot_probability"])

            analysis_record = {
                "raw_input": account_data,
                "prediction": pred_result,
                "risk": risk_result,
                "explanation": explanation_result,
                "review_status": "Pending Review",
                "moderator_notes": "",
            }

            # Cache and persist in audit history
            st.session_state.last_analysis = analysis_record
            add_audit_record(analysis_record)

    record = st.session_state.last_analysis
    raw = record["raw_input"]
    risk = record["risk"]
    pred = record["prediction"]
    exp = record["explanation"]

    st.markdown("---")
    st.markdown("<h3 style='color:#0F2942;'>Assessment Results</h3>", unsafe_allow_html=True)

    # Top Status Bar with Data Source and Verification Badge
    source_bg = "#ECFDF5" if raw["data_source"] == "Live API" else ("#EFF6FF" if raw["data_source"] == "Manual Input" else "#FEF3C7")
    source_border = "#A7F3D0" if raw["data_source"] == "Live API" else ("#BFDBFE" if raw["data_source"] == "Manual Input" else "#FDE68A")
    source_color = "#065F46" if raw["data_source"] == "Live API" else ("#1E40AF" if raw["data_source"] == "Manual Input" else "#92400E")

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px 18px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:20px; font-weight:800; color:#0F2942;">@{raw['username']}</span>
            <span style="font-size:12px; color:#64748B;">({raw['platform']})</span>
            <span class="source-pill" style="background:{source_bg}; border-color:{source_border}; color:{source_color};">
                Data Source: {raw['data_source']}
            </span>
        </div>
        <div>
            <span style="background:{risk['badge_color']}; color:#FFFFFF; padding:5px 14px; border-radius:9999px; font-weight:700; font-size:13px;">
                {risk['risk_category']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cross-platform transparency callout
    if not pred.get("is_platform_native", True):
        st.markdown("""
        <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:8px 12px; border-radius:0 6px 6px 0; font-size:12px; color:#78350F; margin-bottom:14px;">
            ⚠️ <b>Cross-Platform Evaluation Notice:</b> The ML core was trained on Twitter/X academic behavioral patterns. Assessment for Instagram/Facebook applies common behavioral heuristics and is experimental.
        </div>
        """, unsafe_allow_html=True)

    # 3 Summary Score Cards
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div class="shield-metric-card" style="border-top:4px solid {risk['badge_color']};">
            <div class="metric-label">Calculated Risk Score</div>
            <div class="metric-value" style="color:{risk['badge_color']};">{risk['risk_score']} <span style="font-size:15px; color:#94A3B8;">/ 100</span></div>
            <div class="metric-sub">{risk['status_label']}</div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div class="shield-metric-card" style="border-top:4px solid #0284C7;">
            <div class="metric-label">Model Bot Probability</div>
            <div class="metric-value">{round(pred['bot_probability'] * 100, 1)}%</div>
            <div class="metric-sub">{risk['confidence_level']}</div>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div class="shield-metric-card" style="border-top:4px solid #475569;">
            <div class="metric-label">Moderator Recommendation</div>
            <div style="font-size:13px; font-weight:700; color:#1E293B; margin-top:6px; line-height:1.3;">
                {risk['recommended_action']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Explainability Section: "Why was this account flagged?"
    st.markdown("<h4 style='color:#0F2942; margin-bottom:10px;'>Why was this account flagged?</h4>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 16px; margin-bottom:16px; font-size:13px; color:#334155; line-height:1.4;">
        <b>Executive Finding:</b> {exp['summary']}
    </div>
    """, unsafe_allow_html=True)

    col_exp_left, col_exp_right = st.columns([3, 2])

    with col_exp_left:
        st.markdown("<b style='color:#DC2626; font-size:13px;'>Contributing Suspicious Indicators (+ Risk)</b>", unsafe_allow_html=True)
        if exp["suspicious_indicators"]:
            for ind in exp["suspicious_indicators"]:
                sev_color = "#DC2626" if ind.get("severity") == "High" else "#EA580C"
                st.markdown(f"""
                <div class="explain-card" style="border-left:3px solid {sev_color};">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="indicator-title">{ind['title']}</span>
                        <span style="font-size:11px; font-weight:700; color:{sev_color};">Severity: {ind.get('severity', 'Medium')}</span>
                    </div>
                    <div class="indicator-detail">{ind['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No abnormal suspicious automated anomalies detected for this account.")

        st.markdown("<b style='color:#059669; font-size:13px; margin-top:12px; display:inline-block;'>Mitigating Organic Indicators (- Risk)</b>", unsafe_allow_html=True)
        if exp["mitigating_indicators"]:
            for ind in exp["mitigating_indicators"]:
                st.markdown(f"""
                <div class="explain-card" style="border-left:3px solid #10B981;">
                    <div class="indicator-title" style="color:#065F46;">{ind['title']}</div>
                    <div class="indicator-detail">{ind['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strong mitigating authentic credibility signals present.")

    with col_exp_right:
        st.markdown("<b style='color:#0F2942; font-size:13px;'>Feature Attribution Waterfall</b>", unsafe_allow_html=True)
        if exp.get("impact_scores"):
            impact_df = pd.DataFrame([
                {"Feature": k, "Impact": v, "Color": "#DC2626" if v > 0 else "#10B981"}
                for k, v in exp["impact_scores"].items()
            ]).sort_values("Impact", ascending=True)

            fig_imp = px.bar(
                impact_df,
                x="Impact",
                y="Feature",
                orientation="h",
                color="Color",
                color_discrete_map={"#DC2626": "#DC2626", "#10B981": "#10B981"},
            )
            fig_imp.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=10, r=10, t=10, b=20),
                height=260,
                showlegend=False,
                xaxis=dict(title="Attribution Weight", zeroline=True, zerolinecolor="#64748B"),
                yaxis=dict(title=""),
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.caption("No significant feature attribution variances.")

    # Moderator Action Card
    st.markdown("---")
    st.markdown("<h4 style='color:#0F2942;'>Moderator Decision Console</h4>", unsafe_allow_html=True)

    with st.form("moderator_action_form"):
        col_act1, col_act2 = st.columns([1, 2])
        with col_act1:
            current_status = record.get("review_status", "Pending Review")
            status_options = ["Pending Review", "Reviewed", "Escalated", "Cleared"]
            status_idx = status_options.index(current_status) if current_status in status_options else 0
            new_status = st.selectbox("Update Review Status", status_options, index=status_idx)
        with col_act2:
            mod_notes = st.text_input("Moderator Audit Notes", value=record.get("moderator_notes", ""), placeholder="e.g. Identity verified via secondary channel; no malicious intent.")

        submitted = st.form_submit_button("Save Moderator Audit Decision", type="primary")
        if submitted:
            record["review_status"] = new_status
            record["moderator_notes"] = mod_notes
            st.session_state.last_analysis = record
            add_audit_record(record)
            st.success(f"Audit decision saved: @{raw['username']} status set to '{new_status}'.")

