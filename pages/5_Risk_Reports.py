"""
Page 5: Risk Reports & Moderator Review Queue
Human-in-the-loop audit console, review status management, and audit log CSV export.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from modules.session_state import init_session_state, update_moderator_status
from modules.report_generator import generate_audit_export_csv

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">Risk Reports & Moderator Review Console</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Human-in-the-loop moderation interface for adjudicating suspicious accounts and exporting compliance audit briefs.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="review-notice">
    <b>⚖️ Operational Safety Mandate:</b> Detection algorithms never perform autonomous punitive actions. Every flagged account resides in an advisory holding state until reviewed by an authorized human analyst.
</div>
""", unsafe_allow_html=True)

history = st.session_state.audit_history

if not history:
    st.info("No accounts currently in the audit queue. Run an analysis in the 'Account Analyzer' or 'Batch Analysis' first.")
    st.stop()

# Queue KPI counters
total_cases = len(history)
pending_cases = sum(1 for r in history if r.get("review_status") == "Pending Review")
escalated_cases = sum(1 for r in history if r.get("review_status") == "Escalated")
cleared_cases = sum(1 for r in history if r.get("review_status") == "Cleared")
reviewed_cases = sum(1 for r in history if r.get("review_status") == "Reviewed")

q1, q2, q3, q4 = st.columns(4)
with q1:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #F59E0B;">
        <div class="metric-label">Pending Review</div>
        <div class="metric-value" style="color:#D97706;">{pending_cases}</div>
        <div class="metric-sub">Awaiting moderator triage</div>
    </div>
    """, unsafe_allow_html=True)

with q2:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #DC2626;">
        <div class="metric-label">Escalated Cases</div>
        <div class="metric-value" style="color:#DC2626;">{escalated_cases}</div>
        <div class="metric-sub">Sent for identity challenge</div>
    </div>
    """, unsafe_allow_html=True)

with q3:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #10B981;">
        <div class="metric-label">Cleared / Genuine</div>
        <div class="metric-value" style="color:#059669;">{cleared_cases}</div>
        <div class="metric-sub">False positives dismissed</div>
    </div>
    """, unsafe_allow_html=True)

with q4:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #1E3A8A;">
        <div class="metric-label">Reviewed Total</div>
        <div class="metric-value" style="color:#1E3A8A;">{reviewed_cases + cleared_cases + escalated_cases}</div>
        <div class="metric-sub">Out of {total_cases} total records</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Filtering options
col_f_status, col_f_plat, col_exp_btn = st.columns([1, 1, 2])
with col_f_status:
    filter_status = st.selectbox("Filter Status", ["All Statuses", "Pending Review", "Escalated", "Cleared", "Reviewed"])
with col_f_plat:
    filter_plat = st.selectbox("Filter Platform", ["All Platforms", "X (Twitter)", "Instagram", "Facebook", "Other"])
with col_exp_btn:
    st.markdown("<p style='font-size:12px; margin-bottom:4px; color:#64748B;'>Audit Trail Export</p>", unsafe_allow_html=True)
    export_csv_data = generate_audit_export_csv(history)
    st.download_button(
        label="📥 Download Moderator Audit Report (CSV)",
        data=export_csv_data,
        file_name=f"socialshield_moderator_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("---")

# Filtered list of accounts
filtered_history = [
    r for r in history
    if (filter_status == "All Statuses" or r.get("review_status") == filter_status)
    and (filter_plat == "All Platforms" or r.get("raw_input", {}).get("platform") == filter_plat)
]

if not filtered_history:
    st.info("No records match the current filter selection.")
else:
    st.markdown(f"<b>Displaying {len(filtered_history)} account audit dossiers:</b>", unsafe_allow_html=True)

    for idx, item in enumerate(filtered_history):
        raw = item.get("raw_input", {})
        risk = item.get("risk", {})
        pred = item.get("prediction", {})
        exp = item.get("explanation", {})
        current_status = item.get("review_status", "Pending Review")

        status_badge_bg = {
            "Pending Review": "#FEF3C7",
            "Escalated": "#FEE2E2",
            "Cleared": "#DCFCE7",
            "Reviewed": "#EFF6FF",
        }.get(current_status, "#F1F5F9")

        status_badge_color = {
            "Pending Review": "#92400E",
            "Escalated": "#991B1B",
            "Cleared": "#166534",
            "Reviewed": "#1E40AF",
        }.get(current_status, "#334155")

        with st.expander(f"👤 @{raw.get('username')}  |  Risk: {risk.get('risk_score', 'N/A')}/100 ({risk.get('risk_category')})  |  Status: {current_status}", expanded=(idx == 0)):
            c_left, c_right = st.columns([3, 2])

            with c_left:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:14px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <div>
                            <span style="font-size:16px; font-weight:800; color:#0F2942;">@{raw.get('username')}</span>
                            <span style="font-size:12px; color:#64748B;">({raw.get('platform')})</span>
                        </div>
                        <div>
                            <span class="source-pill">Source: {raw.get('data_source', 'Manual')}</span>
                        </div>
                    </div>
                    <div style="font-size:13px; color:#334155; margin-bottom:10px;">
                        <b>Biography:</b> <i>"{raw.get('description') or 'No description provided.'}"</i>
                    </div>
                    <div style="display:flex; gap:16px; font-size:12px; color:#475569; border-top:1px solid #F1F5F9; padding-top:8px;">
                        <span><b>Followers:</b> {raw.get('followers_count', 0):,}</span>
                        <span><b>Following:</b> {raw.get('following_count', 0):,}</span>
                        <span><b>Total Posts:</b> {raw.get('total_posts', 0):,}</span>
                        <span><b>Account Age:</b> {raw.get('account_age_days', 'N/A')} days</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<b>Flagged Threat Indicators:</b>", unsafe_allow_html=True)
                if exp.get("suspicious_indicators"):
                    for si in exp["suspicious_indicators"]:
                        st.markdown(f"- ⚠️ **{si['title']}:** {si['detail']}")
                else:
                    st.markdown("*(No major suspicious indicators)*")

                st.markdown(f"**Recommended Action:** {risk.get('recommended_action')}")

            with c_right:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:14px;">
                    <div style="font-size:12px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:6px;">Current Adjudication</div>
                    <div style="margin-bottom:12px;">
                        <span style="background:{status_badge_bg}; color:{status_badge_color}; font-weight:700; padding:4px 12px; border-radius:9999px; font-size:12px;">
                            {current_status}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Inline Status Update Form
                with st.form(f"mod_form_{idx}"):
                    new_st = st.selectbox(
                        "Change Status",
                        ["Pending Review", "Reviewed", "Escalated", "Cleared"],
                        index=["Pending Review", "Reviewed", "Escalated", "Cleared"].index(current_status),
                        key=f"status_select_{idx}"
                    )
                    notes = st.text_input("Reviewer Notes", value=item.get("moderator_notes", ""), key=f"notes_input_{idx}")
                    save_btn = st.form_submit_button("Update Status")
                    if save_btn:
                        update_moderator_status(raw.get("username"), new_st, notes)
                        st.success(f"Updated @{raw.get('username')} to '{new_st}'!")
                        st.rerun()

