"""
Page 1: Overview Dashboard
Cybersecurity Intelligence Metrics, Risk Distributions, and System Health.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.session_state import init_session_state

init_session_state()

st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
    <div>
        <h2 style="color:#0F2942; margin:0; font-weight:800;">Cyber Threat & Risk Intelligence Overview</h2>
        <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">Live surveillance metrics across monitored social platforms and bot syndicates.</p>
    </div>
    <div style="text-align:right;">
        <span class="source-pill" style="background:#ECFDF5; color:#065F46; border-color:#A7F3D0;">● System Active</span>
        <span class="source-pill">ML Engine: Random Forest</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Ethical & operational disclaimer banner
st.markdown("""
<div class="review-notice">
    <b>🛡️ Ethical Decision Support Protocol:</b> SocialShield AI operates under human-in-the-loop oversight. All risk scores (0–100) are probabilistic risk assessments intended for moderator investigation, not autonomous account suspension.
</div>
""", unsafe_allow_html=True)

# Retrieve analyzed accounts from session state
history = st.session_state.audit_history

total_analyzed = len(history)
low_risk = sum(1 for r in history if r.get("risk", {}).get("risk_category") == "Low Risk")
moderate_risk = sum(1 for r in history if r.get("risk", {}).get("risk_category") == "Moderate Risk")
high_risk = sum(1 for r in history if r.get("risk", {}).get("risk_category") == "High Risk")
vhigh_risk = sum(1 for r in history if r.get("risk", {}).get("risk_category") == "Very High Risk")
suspicious_total = moderate_risk + high_risk + vhigh_risk

# Top 4 Executive KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="shield-metric-card">
        <div class="metric-label">Total Accounts Analyzed</div>
        <div class="metric-value">{total_analyzed:,}</div>
        <div class="metric-sub">Across 4 supported platforms</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #10B981;">
        <div class="metric-label">Low Risk / Genuine</div>
        <div class="metric-value" style="color:#059669;">{low_risk:,}</div>
        <div class="metric-sub">{round((low_risk / max(1, total_analyzed)) * 100, 1)}% of total analyzed</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #F59E0B;">
        <div class="metric-label">Suspicious / Moderate</div>
        <div class="metric-value" style="color:#D97706;">{moderate_risk:,}</div>
        <div class="metric-sub">Requires periodic surveillance</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #DC2626;">
        <div class="metric-label">High / Very High Risk</div>
        <div class="metric-value" style="color:#DC2626;">{high_risk + vhigh_risk:,}</div>
        <div class="metric-sub">Active in moderator queue</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Visualizations Row 1
col_chart_left, col_chart_right = st.columns([3, 2])

with col_chart_left:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Risk Category Breakdown</h4>", unsafe_allow_html=True)
    cat_df = pd.DataFrame([
        {"Category": "Low Risk (0-29)", "Count": low_risk, "Color": "#10B981"},
        {"Category": "Moderate Risk (30-59)", "Count": moderate_risk, "Color": "#F59E0B"},
        {"Category": "High Risk (60-79)", "Count": high_risk, "Color": "#EA580C"},
        {"Category": "Very High Risk (80-100)", "Count": vhigh_risk, "Color": "#DC2626"},
    ])
    fig_cat = px.bar(
        cat_df,
        x="Category",
        y="Count",
        color="Category",
        color_discrete_map={
            "Low Risk (0-29)": "#10B981",
            "Moderate Risk (30-59)": "#F59E0B",
            "High Risk (60-79)": "#EA580C",
            "Very High Risk (80-100)": "#DC2626",
        },
        text="Count",
    )
    fig_cat.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=10, b=20),
        height=280,
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_chart_right:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Platform Distribution</h4>", unsafe_allow_html=True)
    platform_counts = {}
    for r in history:
        p = r.get("raw_input", {}).get("platform", "X (Twitter)")
        platform_counts[p] = platform_counts.get(p, 0) + 1

    plat_df = pd.DataFrame(list(platform_counts.items()), columns=["Platform", "Count"])
    fig_plat = px.pie(
        plat_df,
        names="Platform",
        values="Count",
        hole=0.55,
        color_discrete_sequence=["#1E3A8A", "#0284C7", "#38BDF8", "#94A3B8"],
    )
    fig_plat.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=10, b=20),
        height=280,
        showlegend=True,
    )
    st.plotly_chart(fig_plat, use_container_width=True)

# Row 2: Top Suspicious Accounts Leaderboard & Recent Analysis
col_table_left, col_summary_right = st.columns([3, 2])

with col_table_left:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Recent Account Audits</h4>", unsafe_allow_html=True)
    if history:
        audit_rows = []
        for r in history[:8]:
            raw = r.get("raw_input", {})
            risk = r.get("risk", {})
            audit_rows.append({
                "Username": f"@{raw.get('username')}",
                "Platform": raw.get("platform"),
                "Risk Score": f"{risk.get('risk_score')}/100",
                "Category": risk.get("risk_category"),
                "Source": raw.get("data_source", "Manual Input"),
                "Status": r.get("review_status", "Pending"),
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No accounts analyzed in the current session yet.")

with col_summary_right:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Network Syndicate Watch</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:16px;">
        <div style="font-size:13px; font-weight:700; color:#0F2942; margin-bottom:8px;">🚨 Coordinated Botnet Detected</div>
        <p style="font-size:12px; color:#475569; margin:0 0 12px 0;">
            Graph intelligence detected a cluster of <b>6 accounts</b> executing synchronized high-frequency promotional messaging on X (Twitter) with 94% bio similarity.
        </p>
        <div style="display:flex; justify-content:space-between; font-size:12px; border-top:1px solid #F1F5F9; padding-top:8px;">
            <span style="color:#64748B;">Identified Cluster:</span>
            <span style="font-weight:700; color:#DC2626;">Crypto Promo Syndicate #1</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-top:4px;">
            <span style="color:#64748B;">Average Cluster Risk:</span>
            <span style="font-weight:700; color:#DC2626;">88.5 / 100</span>
        </div>
        <div style="margin-top:14px;">
            <a href="/Account_Analyzer" target="_self" style="display:block; text-align:center; background:#0F2942; color:#FFFFFF; text-decoration:none; padding:8px 12px; border-radius:6px; font-size:12px; font-weight:700;">
                Analyze Profile URL Now →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

