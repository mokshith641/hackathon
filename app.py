"""
SocialShield AI
Intelligent Multi-Platform Fake Social Media Account Detection & Risk Assessment System
Main Application Entry Point & Navigation Controller
"""

import os
import streamlit as st

# Configure wide layout and page metadata
st.set_page_config(
    page_title="SocialShield AI | Multi-Platform Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Custom Professional Light Theme CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Application Logo and Navigation Header in Sidebar
st.sidebar.markdown("""
<div class="shield-brand-header">
    <div class="shield-brand-logo">🛡️</div>
    <div>
        <div class="shield-title">SocialShield AI</div>
        <div class="shield-tagline">Intelligent Risk Assessment</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation via Streamlit st.navigation (modern multi-page architecture)
pages = [
    st.Page("pages/1_Overview.py", title="Overview Dashboard", icon="📊", default=True),
    st.Page("pages/2_Account_Analyzer.py", title="Account Analyzer", icon="🔍"),
    st.Page("pages/3_Batch_Analysis.py", title="Batch Analysis", icon="📁"),
    st.Page("pages/4_Network_Intelligence.py", title="Network Intelligence", icon="🕸️"),
    st.Page("pages/5_Risk_Reports.py", title="Risk Reports & Queue", icon="📑"),
    st.Page("pages/6_Dataset_Model_Info.py", title="Dataset & ML Model", icon="🧠"),
    st.Page("pages/7_Settings.py", title="Settings & Governance", icon="⚙️"),
]

# Run the selected page
pg = st.navigation(pages)

# Sidebar System Health Status
with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#64748B; padding: 4px 8px;">
        <div style="margin-bottom:6px;">
            <b>Operational Status:</b> <span style="color:#059669; font-weight:700;">● Online</span>
        </div>
        <div style="margin-bottom:6px;">
            <b>ML Engine:</b> Random Forest (120 Estimators)
        </div>
        <div style="margin-bottom:6px;">
            <b>Network Core:</b> NetworkX + Plotly
        </div>
        <div style="margin-top:12px; font-size:10px; color:#94A3B8; border-top:1px solid #E2E8F0; padding-top:8px;">
            SocialShield AI v1.0.0<br>
            College Hackathon Edition 2026
        </div>
    </div>
    """, unsafe_allow_html=True)

pg.run()

