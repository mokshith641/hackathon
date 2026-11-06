"""
Page 2: Social Media Profile URL & Account Risk Inspector
Paste any public social media link (X/Twitter, Instagram) to extract live telemetry
(followers, following, posts, bio) and detect whether the account is fake or genuine.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

from modules.session_state import init_session_state, add_audit_record
from modules.prediction import predict_single_account
from modules.risk_scoring import calculate_risk_score
from modules.explainability import explain_account_risk
from modules.platform_adapters import (
    parse_profile_url,
    fetch_by_url_or_handle,
    fetch_x_account,
    fetch_instagram_account,
)

init_session_state()

# Page Header
st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800; font-size:26px;">Social Media Profile & Fake Account Inspector</h2>
    <p style="color:#475569; margin:4px 0 0 0; font-size:14.5px;">
        Paste any public profile link to extract real-time audience metrics, biography, and assess fake/bot risk.
    </p>
</div>
""", unsafe_allow_html=True)

# Preset Demo Scenarios for instant offline testing
PRESETS = {
    "Select a quick demo account...": None,
    "🚀 Elon Musk (@elonmusk - Verified Human)": {
        "url": "https://x.com/elonmusk",
        "username": "elonmusk",
        "display_name": "Elon Musk",
        "platform": "X (Twitter)",
        "created_at": "2009-06-02",
        "followers_count": 241430000,
        "following_count": 1420,
        "total_posts": 111680,
        "description": "https://x.com",
        "has_profile_picture": 1,
        "is_verified": 1,
        "data_source": "Live API",
    },
    "🪐 NASA (@nasa - Verified Organization)": {
        "url": "https://www.instagram.com/nasa/",
        "username": "nasa",
        "display_name": "NASA",
        "platform": "Instagram",
        "created_at": "2013-08-01",
        "followers_count": 104446500,
        "following_count": 70,
        "total_posts": 4200,
        "description": "Exploring the secrets of the universe for the benefit of all. 🚀",
        "has_profile_picture": 1,
        "is_verified": 1,
        "data_source": "Live API",
    },
    "🤖 Follow-Train Spam Bot (Asymmetric Following)": {
        "url": "https://x.com/boost_fans_fast_9921",
        "username": "boost_fans_fast_9921",
        "display_name": "Fast Follower Booster 24/7",
        "platform": "X (Twitter)",
        "created_at": (date.today() - timedelta(days=12)).strftime("%Y-%m-%d"),
        "followers_count": 18,
        "following_count": 4850,
        "total_posts": 620,
        "description": "FOLLOW ME FOR INSTANT FOLLOW BACK! Automated growth booster 24/7. Gain 1000 real followers fast! #f4f",
        "has_profile_picture": 0,
        "is_verified": 0,
        "data_source": "Synthetic Demo Data",
    },
    "💎 Crypto Airdrop Scam Syndicate": {
        "url": "https://x.com/crypto_moon_gem_8472",
        "username": "crypto_moon_gem_8472",
        "display_name": "Crypto Airdrop Moon Alert",
        "platform": "X (Twitter)",
        "created_at": (date.today() - timedelta(days=19)).strftime("%Y-%m-%d"),
        "followers_count": 42,
        "following_count": 3100,
        "total_posts": 490,
        "description": "🚀 100x GEM CRYPTO ALERT! Free airdrop tokens claim now at t.me/free_crypto_drop 🔥 Don't miss out!",
        "has_profile_picture": 0,
        "is_verified": 0,
        "data_source": "Synthetic Demo Data",
    },
}

# Main Hero Search Container
with st.container(border=True):
    st.markdown("<p style='font-size:14px; font-weight:700; color:#0F2942; margin-bottom:8px;'>🔗 Enter Profile URL, Handle, or Choose Quick Demo:</p>", unsafe_allow_html=True)
    
    col_input, col_preset = st.columns([3, 2])
    with col_input:
        profile_url_input = st.text_input(
            "Social Media Profile Link",
            value="https://x.com/elonmusk",
            placeholder="e.g. https://x.com/elonmusk or https://www.instagram.com/nasa/ or @username",
            label_visibility="collapsed",
        )
    
    with col_preset:
        preset_choice = st.selectbox(
            "Demo Presets",
            list(PRESETS.keys()),
            label_visibility="collapsed",
        )

    # 1-Click Chip Buttons for quick interaction
    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
    with c_btn1:
        if st.button("🚀 Elon Musk (X)", use_container_width=True):
            profile_url_input = "https://x.com/elonmusk"
            st.session_state["active_profile_query"] = "https://x.com/elonmusk"
    with c_btn2:
        if st.button("🪐 NASA (Instagram)", use_container_width=True):
            profile_url_input = "https://www.instagram.com/nasa/"
            st.session_state["active_profile_query"] = "https://www.instagram.com/nasa/"
    with c_btn3:
        if st.button("🤖 Demo Spam Bot", use_container_width=True):
            st.session_state["active_profile_query"] = "demo_spam_bot"
    with c_btn4:
        if st.button("💎 Demo Crypto Scam", use_container_width=True):
            st.session_state["active_profile_query"] = "demo_crypto_scam"

    if preset_choice != "Select a quick demo account...":
        preset_data = PRESETS[preset_choice]
        profile_url_input = preset_data["url"]
        st.session_state["active_profile_query"] = profile_url_input

    # Prominent Action Button
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    analyze_url_btn = st.button("⚡ Inspect Profile URL & Detect Fake Status", type="primary", use_container_width=True)

# Processing Logic
trigger_analysis = analyze_url_btn or "last_analysis" in st.session_state

if analyze_url_btn:
    active_query = st.session_state.get("active_profile_query", profile_url_input)
    if not active_query or not active_query.strip():
        active_query = profile_url_input

    account_data = None
    data_src = "Manual Input"
    status_msg = ""

    # Check if a preset demo bot was clicked
    if active_query == "demo_spam_bot":
        account_data = PRESETS["🤖 Follow-Train Spam Bot (Asymmetric Following)"].copy()
        data_src = "Synthetic Demo Data"
        status_msg = "Loaded demonstration spam bot profile."
    elif active_query == "demo_crypto_scam":
        account_data = PRESETS["💎 Crypto Airdrop Scam Syndicate"].copy()
        data_src = "Synthetic Demo Data"
        status_msg = "Loaded demonstration crypto syndicate bot."
    else:
        # Live Profile Fetch via SocialCrawl API Gateway
        with st.spinner(f"Extracting live telemetry from {active_query}..."):
            platform_detected, clean_handle = parse_profile_url(active_query)
            account_data, data_src, status_msg = fetch_by_url_or_handle(active_query)

            if not account_data:
                # Graceful fallback: construct profile with handle
                account_data = {
                    "username": clean_handle or "unknown_user",
                    "display_name": clean_handle or "Unknown Profile",
                    "platform": platform_detected,
                    "created_at": (date.today() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    "followers_count": 150,
                    "following_count": 220,
                    "total_posts": 45,
                    "description": "Public profile telemetry unavailable via API. Using baseline parameters.",
                    "has_profile_picture": 1,
                    "is_verified": 0,
                    "data_source": "Manual Input",
                }
                st.warning(f"{status_msg} Analyzed with standard baseline telemetry.")
            else:
                st.success(f"✅ {status_msg}")

    # Run ML and Risk Analysis
    with st.spinner("Analyzing behavioral signals with Random Forest core..."):
        account_data["data_source"] = data_src
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
        st.session_state.last_analysis = analysis_record
        add_audit_record(analysis_record)

# Render Inspection Results
if "last_analysis" in st.session_state:
    record = st.session_state.last_analysis
    raw = record["raw_input"]
    risk = record["risk"]
    pred = record["prediction"]
    exp = record["explanation"]

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # 1. Big Executive Verdict Banner (Fake or Not)
    risk_score = risk["risk_score"] or 0.0
    if risk_score <= 35:
        verdict_title = "VERDICT: GENUINE / HUMAN PROFILE"
        verdict_badge = "🟢 GENUINE / AUTHENTIC"
        verdict_color = "#10B981"
        verdict_bg = "#ECFDF5"
        verdict_border = "#A7F3D0"
        verdict_sub = "Strong indicators of authentic human behavior and organic social engagement."
    elif risk_score <= 65:
        verdict_title = "VERDICT: SUSPICIOUS / ELEVATED CAUTION"
        verdict_badge = "🟡 SUSPICIOUS ACTIVITY"
        verdict_color = "#D97706"
        verdict_bg = "#FFFBEB"
        verdict_border = "#FDE68A"
        verdict_sub = "Noticeable behavioral anomalies detected. Account exhibits mixed automation patterns."
    else:
        verdict_title = "VERDICT: HIGH PROBABILITY FAKE / BOT PROFILE"
        verdict_badge = "🔴 FAKE / AUTOMATED BOT"
        verdict_color = "#DC2626"
        verdict_bg = "#FEF2F2"
        verdict_border = "#FECACA"
        verdict_sub = "Dominant automation signatures detected (severe follower asymmetry, mass posting, or automated naming)."

    st.markdown(f"""
    <div style="background:{verdict_bg}; border:2px solid {verdict_border}; border-left:8px solid {verdict_color}; border-radius:12px; padding:18px 24px; margin-bottom:18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:{verdict_color};">
                    SocialShield AI Assessment
                </span>
                <h2 style="color:{verdict_color}; margin:4px 0 2px 0; font-size:22px; font-weight:800;">
                    {verdict_title}
                </h2>
                <div style="font-size:13px; color:#334155; font-weight:500;">
                    {verdict_sub}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:32px; font-weight:900; color:{verdict_color}; line-height:1;">
                    {risk['risk_score']} <span style="font-size:16px; color:#64748B; font-weight:600;">/ 100</span>
                </div>
                <div style="font-size:12px; font-weight:700; color:#64748B; margin-top:2px;">
                    Risk Index
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Profile Details & Telemetry Card
    with st.container(border=True):
        col_prof_head, col_prof_meta = st.columns([3, 2])
        with col_prof_head:
            avatar_html = ""
            if raw.get("avatar_url"):
                avatar_html = f"<img src='{raw['avatar_url']}' style='width:52px; height:52px; border-radius:50%; object-fit:cover; border:2px solid #E2E8F0; margin-right:14px;'>"
            else:
                avatar_html = "<div style='width:52px; height:52px; border-radius:50%; background:#0F2942; color:#38BDF8; display:flex; align-items:center; justify-content:center; font-size:22px; margin-right:14px;'>👤</div>"

            verified_badge = " <span style='color:#0284C7; font-size:16px;'>✓</span>" if raw.get("is_verified") else ""
            display_name = raw.get("display_name") or raw.get("username")

            st.markdown(f"""
            <div style="display:flex; align-items:center;">
                {avatar_html}
                <div>
                    <div style="font-size:18px; font-weight:800; color:#0F2942; line-height:1.2;">
                        {display_name}{verified_badge}
                    </div>
                    <div style="font-size:13px; color:#64748B; font-weight:600;">
                        @{raw.get('username')} • <span style="color:#0284C7;">{raw.get('platform')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_prof_meta:
            source_badge_color = "#065F46" if "Live" in raw.get("data_source", "") else "#1E40AF"
            source_badge_bg = "#ECFDF5" if "Live" in raw.get("data_source", "") else "#EFF6FF"
            st.markdown(f"""
            <div style="text-align:right;">
                <span class="source-pill" style="background:{source_badge_bg}; color:{source_badge_color};">
                    📡 {raw.get('data_source', 'Manual')}
                </span>
                <div style="font-size:12px; color:#64748B; margin-top:6px;">
                    Assessed: {risk.get('timestamp', datetime.now().strftime('%H:%M:%S'))}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='margin:14px 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # 4 Key Signals KPI Cards (Followers, Following, Posts, Bio)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="shield-metric-card" style="border-top:3px solid #1E3A8A;">
                <div class="metric-label">Audience: Followers</div>
                <div class="metric-value" style="font-size:24px;">{raw.get('followers_count', 0):,}</div>
                <div class="metric-sub">Inbound audience</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="shield-metric-card" style="border-top:3px solid #0284C7;">
                <div class="metric-label">Outbound: Following</div>
                <div class="metric-value" style="font-size:24px;">{raw.get('following_count', 0):,}</div>
                <div class="metric-sub">Accounts followed</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="shield-metric-card" style="border-top:3px solid #10B981;">
                <div class="metric-label">Activity: Posts</div>
                <div class="metric-value" style="font-size:24px;">{raw.get('total_posts', 0):,}</div>
                <div class="metric-sub">Total published</div>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            ratio = raw.get('followers_count', 0) / (raw.get('following_count', 0) + 1)
            ratio_color = "#10B981" if ratio >= 0.5 else "#DC2626"
            st.markdown(f"""
            <div class="shield-metric-card" style="border-top:3px solid {ratio_color};">
                <div class="metric-label">Follower Ratio</div>
                <div class="metric-value" style="font-size:24px; color:{ratio_color};">{ratio:.2f}</div>
                <div class="metric-sub">Followers per Following</div>
            </div>
            """, unsafe_allow_html=True)

        # Profile Biography Box
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        bio_content = raw.get('description') or "No profile description or bio available."
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 16px;">
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#64748B; margin-bottom:4px;">
                💬 Profile Biography / Bio
            </div>
            <div style="font-size:14px; color:#0F172A; font-style:italic; line-height:1.4;">
                "{bio_content}"
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Explainable AI: "Why was this account flagged?"
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Why was this account evaluated this way?</h4>", unsafe_allow_html=True)

    col_exp_left, col_exp_right = st.columns([3, 2])

    with col_exp_left:
        st.markdown("<b style='color:#DC2626; font-size:13px;'>Contributing Risk Factors (+ Risk)</b>", unsafe_allow_html=True)
        if exp.get("suspicious_indicators"):
            for ind in exp["suspicious_indicators"]:
                sev_color = "#DC2626" if ind.get("severity") == "High" else "#EA580C"
                st.markdown(f"""
                <div class="explain-card" style="border-left:4px solid {sev_color};">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="indicator-title">{ind['title']}</span>
                        <span style="font-size:11px; font-weight:700; color:{sev_color};">Severity: {ind.get('severity', 'Medium')}</span>
                    </div>
                    <div class="indicator-detail">{ind['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No abnormal suspicious automated anomalies detected for this account.")

        st.markdown("<b style='color:#059669; font-size:13px; margin-top:12px; display:inline-block;'>Mitigating Authentic Factors (- Risk)</b>", unsafe_allow_html=True)
        if exp.get("mitigating_indicators"):
            for ind in exp["mitigating_indicators"]:
                st.markdown(f"""
                <div class="explain-card" style="border-left:4px solid #10B981;">
                    <div class="indicator-title" style="color:#065F46;">{ind['title']}</div>
                    <div class="indicator-detail">{ind['detail']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strong authentic mitigating credibility signals present.")

    with col_exp_right:
        st.markdown("<b style='color:#0F2942; font-size:13px;'>Feature Attribution Impact</b>", unsafe_allow_html=True)
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
                height=240,
                showlegend=False,
                xaxis=dict(title="Impact Weight", zeroline=True, zerolinecolor="#64748B"),
                yaxis=dict(title=""),
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.caption("No significant attribution variances.")

# 4. Optional Advanced / Manual Inspector Expander
with st.expander("🛠️ Advanced Manual Telemetry Override & Parameter Tuning", expanded=False):
    st.markdown("<p style='font-size:13px; color:#64748B;'>Manually adjust account metrics to simulate hypothetical or borderline accounts.</p>", unsafe_allow_html=True)
    
    col_m_u, col_m_p, col_m_d = st.columns(3)
    with col_m_u:
        man_username = st.text_input("Handle Override", value=raw.get("username", "custom_user") if "last_analysis" in st.session_state else "custom_user")
    with col_m_p:
        man_platform = st.selectbox("Platform Override", ["X (Twitter)", "Instagram", "Facebook", "Other"])
    with col_m_d:
        man_date = st.date_input("Registration Date", value=date.today() - timedelta(days=500))

    col_m_f1, col_m_f2, col_m_f3 = st.columns(3)
    with col_m_f1:
        man_followers = st.number_input("Followers Override", min_value=0, max_value=1000000000, value=int(raw.get("followers_count", 1000) if "last_analysis" in st.session_state else 1000))
    with col_m_f2:
        man_following = st.number_input("Following Override", min_value=0, max_value=50000000, value=int(raw.get("following_count", 300) if "last_analysis" in st.session_state else 300))
    with col_m_f3:
        man_posts = st.number_input("Posts Override", min_value=0, max_value=5000000, value=int(raw.get("total_posts", 250) if "last_analysis" in st.session_state else 250))

    man_bio = st.text_area("Bio Override", value=raw.get("description", "") if "last_analysis" in st.session_state else "Custom profile description")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        man_pic = st.checkbox("Profile Picture Set", value=True)
    with col_c2:
        man_ver = st.checkbox("Verified Identity", value=False)

    if st.button("Re-evaluate with Manual Overrides"):
        custom_account = {
            "username": man_username,
            "display_name": man_username,
            "platform": man_platform,
            "created_at": man_date.strftime("%Y-%m-%d"),
            "followers_count": man_followers,
            "following_count": man_following,
            "total_posts": man_posts,
            "description": man_bio,
            "has_profile_picture": 1 if man_pic else 0,
            "is_verified": 1 if man_ver else 0,
            "data_source": "Manual Input",
        }
        pred_res = predict_single_account(custom_account)
        risk_res = calculate_risk_score(pred_res["bot_probability"], custom_account, st.session_state.thresholds)
        exp_res = explain_account_risk(pred_res["features"], custom_account, pred_res["bot_probability"])

        st.session_state.last_analysis = {
            "raw_input": custom_account,
            "prediction": pred_res,
            "risk": risk_res,
            "explanation": exp_res,
            "review_status": "Pending Review",
            "moderator_notes": "Manual override test",
        }
        add_audit_record(st.session_state.last_analysis)
        st.success("Re-evaluated with manual parameters!")
        st.rerun()
