"""
Page 7: System Settings & Platform Credentials
Risk threshold calibration, API token credentials, and runtime diagnostics.
"""

import sys
import streamlit as st
import sklearn
import pandas as pd

from modules.session_state import init_session_state
from modules.data_loader import generate_benchmark_dataset
from modules.model_training import train_and_save_model

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">System Settings & Governance</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Calibrate organizational risk thresholds, configure optional API integrations, and manage audit storage.
    </p>
</div>
""", unsafe_allow_html=True)

# Section 1: Risk Score Threshold Calibration
st.markdown("<h4 style='color:#0F2942;'>1. Risk Threshold Calibration</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size:13px; color:#64748B;'>Adjust organizational risk boundaries according to risk tolerance and triage capacity.</p>", unsafe_allow_html=True)

current_th = st.session_state.thresholds

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    low_val = st.slider("Low Risk Max (Safe ceiling)", 10, 40, int(current_th.get("low_max", 29)))
with col_t2:
    mod_val = st.slider("Moderate Risk Max (Caution ceiling)", low_val + 5, 75, int(current_th.get("moderate_max", 59)))
with col_t3:
    high_val = st.slider("High Risk Max (Suspicious ceiling)", mod_val + 5, 95, int(current_th.get("high_max", 79)))

if st.button("💾 Apply Updated Thresholds", type="primary"):
    st.session_state.thresholds = {
        "low_max": low_val,
        "moderate_max": mod_val,
        "high_max": high_val,
    }
    st.success("Risk boundaries updated across all assessment engines.")

st.markdown("---")

# Section 2: Optional API Integration Credentials
st.markdown("<h4 style='color:#0F2942;'>2. Platform API Credentials (Optional)</h4>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:13px; color:#64748B;'>
    SocialShield AI functions fully offline without external APIs. Supplying bearer tokens allows optional live telemetry extraction directly from official platform endpoints.
</p>
""", unsafe_allow_html=True)

with st.form("api_settings_form"):
    x_token = st.text_input(
        "X (Twitter) API v2 Bearer Token",
        value=st.session_state.api_keys.get("x_bearer_token", ""),
        type="password",
        help="Obtained from the official X Developer Portal."
    )
    ig_token = st.text_input(
        "Instagram Graph API User Access Token",
        value=st.session_state.api_keys.get("instagram_token", ""),
        type="password",
        help="Requires Meta Developer App with instagram_basic scope."
    )
    fb_token = st.text_input(
        "Facebook Graph API Page Access Token",
        value=st.session_state.api_keys.get("facebook_token", ""),
        type="password",
        help="Requires Meta Developer App with pages_read_engagement scope."
    )
    
    save_api_btn = st.form_submit_button("Save API Credentials")
    if save_api_btn:
        st.session_state.api_keys = {
            "x_bearer_token": x_token.strip(),
            "instagram_token": ig_token.strip(),
            "facebook_token": fb_token.strip(),
        }
        st.success("API credentials updated in session memory.")

st.markdown("---")

# Section 3: Data Management & Cache Reset
st.markdown("<h4 style='color:#0F2942;'>3. Demonstration Data & Queue Management</h4>", unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.markdown("<b style='font-size:13px; color:#334155;'>Reset Demonstration Benchmark:</b>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#64748B;'>Regenerates synthetic Cresci benchmark dataset and re-fits baseline model.</p>", unsafe_allow_html=True)
    if st.button("🔄 Regenerate Demo Data & Re-train Baseline"):
        with st.spinner("Regenerating benchmark dataset..."):
            df = generate_benchmark_dataset(350, save=True)
            train_and_save_model(df, target_col="is_bot", dataset_name="Synthetic Cresci-2017 Benchmark")
            st.success("Demo dataset and baseline model re-generated successfully!")
            st.rerun()

with col_d2:
    st.markdown("<b style='font-size:13px; color:#334155;'>Purge Session Audit History:</b>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#64748B;'>Empties active moderator queue and recent analysis records.</p>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Audit Queue"):
        st.session_state.audit_history = []
        if "last_analysis" in st.session_state:
            del st.session_state["last_analysis"]
        st.success("Audit queue cleared.")
        st.rerun()

st.markdown("---")

# Section 4: System Runtime Diagnostics
st.markdown("<h4 style='color:#0F2942;'>4. Runtime Diagnostics</h4>", unsafe_allow_html=True)

diag_data = {
    "Component": [
        "Python Runtime",
        "Streamlit Engine",
        "Scikit-Learn ML",
        "Pandas Data Processor",
        "NetworkX Graph Core",
        "Plotly Visualization",
        "Active Platform Mode",
    ],
    "Version / Status": [
        f"v{sys.version.split()[0]}",
        f"v{st.__version__}",
        f"v{sklearn.__version__}",
        f"v{pd.__version__}",
        "Active (Network Intelligence Enabled)",
        "Active (Interactive 2D Rendering)",
        "Offline-First / Hybrid API-Ready",
    ],
}
st.dataframe(pd.DataFrame(diag_data), use_container_width=True, hide_index=True)

