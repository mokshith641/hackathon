"""
SocialShield AI
Intelligent Multi-Platform Fake Social Media Account Detection & Risk Assessment System
Streamlined Navigation Controller (Account Analyzer & Overview Dashboard)
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

# Streamlined Navigation: Focused on Account Analyzer & Overview Dashboard
pages = [
    st.Page("pages/2_Account_Analyzer.py", title="Account Analyzer & URL Inspector", icon="🔍", default=True),
    st.Page("pages/1_Overview.py", title="Overview Dashboard", icon="📊"),
]

# Run the selected page
pg = st.navigation(pages)

# Sidebar System Health Status
with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div style="font-size:11.5px; color:#475569; padding: 4px 6px;">
        <div style="margin-bottom:6px;">
            <b>Operational Status:</b> <span style="color:#059669; font-weight:700;">● Online</span>
        </div>
        <div style="margin-bottom:6px;">
            <b>Live API Gateway:</b> <span style="color:#0284C7; font-weight:700;">SocialCrawl Active</span>
        </div>
        <div style="margin-bottom:6px;">
            <b>ML Core:</b> Random Forest (95% Accuracy)
        </div>
        <div style="margin-top:12px; font-size:10px; color:#94A3B8; border-top:1px solid #E2E8F0; padding-top:8px;">
            SocialShield AI v2.0 (Streamlined Edition)<br>
            College Hackathon 2026
        </div>
    </div>
    """, unsafe_allow_html=True)

pg.run()
