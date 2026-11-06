"""
Page 3: Batch Account Analysis
Upload and evaluate multi-account CSV files with schema validation, filtering, and export.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.session_state import init_session_state, add_audit_record
from modules.preprocessing import clean_and_prepare_dataset, detect_column_mapping
from modules.prediction import predict_batch_accounts
from modules.risk_scoring import calculate_risk_score
from modules.explainability import explain_account_risk

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">Batch Account Risk Analysis</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Upload CSV portfolios of social media accounts for high-throughput automated risk profiling.
    </p>
</div>
""", unsafe_allow_html=True)

col_up, col_sample = st.columns([3, 2])
with col_up:
    uploaded_file = st.file_uploader("Upload Accounts CSV", type=["csv"])

with col_sample:
    st.markdown("<p style='font-size:13px; font-weight:600; color:#334155; margin-bottom:8px;'>Or use preloaded benchmark:</p>", unsafe_allow_html=True)
    load_sample_btn = st.button("📁 Load Sample Batch (35 Test Accounts)", use_container_width=True)

df_to_analyze = None
batch_source_name = "Uploaded CSV"

if load_sample_btn:
    sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "batch_test_accounts.csv")
    if os.path.exists(sample_path):
        df_to_analyze = pd.read_csv(sample_path)
        batch_source_name = "Synthetic Demonstration Batch"
        st.session_state.batch_df = df_to_analyze
        st.session_state.batch_source = batch_source_name
elif uploaded_file is not None:
    try:
        df_to_analyze = pd.read_csv(uploaded_file)
        batch_source_name = f"Uploaded ({uploaded_file.name})"
        st.session_state.batch_df = df_to_analyze
        st.session_state.batch_source = batch_source_name
    except Exception as e:
        st.error(f"Error parsing CSV file: {e}")
elif "batch_df" in st.session_state:
    df_to_analyze = st.session_state.batch_df
    batch_source_name = st.session_state.get("batch_source", "Cached Batch")

if df_to_analyze is not None:
    st.markdown(f"<b>Batch Dataset:</b> <code>{batch_source_name}</code> ({len(df_to_analyze)} accounts)", unsafe_allow_html=True)

    # Schema inspection accordion
    with st.expander("🔍 Inspect Schema & Column Mapping", expanded=False):
        mapping = detect_column_mapping(df_to_analyze.columns.tolist())
        map_df = pd.DataFrame([
            {"Standard Field": k, "Matched Column in File": v if v else "⚠️ Not Found (Defaults applied)"}
            for k, v in mapping.items()
        ])
        st.dataframe(map_df, use_container_width=True, hide_index=True)
        st.dataframe(df_to_analyze.head(4), use_container_width=True)

    # Run Analysis Button
    run_batch = st.button("🚀 Process & Assess Entire Batch", type="primary", use_container_width=True)

    if run_batch or "batch_results_df" in st.session_state:
        if run_batch:
            with st.spinner(f"Extracting features and scoring {len(df_to_analyze)} accounts..."):
                probs, preds, X = predict_batch_accounts(df_to_analyze)

                results = []
                for idx, row in df_to_analyze.iterrows():
                    row_dict = row.to_dict()
                    p = float(probs[idx])
                    risk_info = calculate_risk_score(p, row_dict, st.session_state.thresholds)

                    features_dict = X.iloc[idx].to_dict()
                    exp_info = explain_account_risk(features_dict, row_dict, p)

                    username = str(row_dict.get("username", f"user_{idx}"))
                    platform = str(row_dict.get("platform", "X (Twitter)"))

                    results.append({
                        "username": username,
                        "platform": platform,
                        "risk_score": risk_info["risk_score"],
                        "risk_category": risk_info["risk_category"],
                        "bot_probability": round(p, 4),
                        "followers_count": int(features_dict.get("followers_count", 0)),
                        "following_count": int(features_dict.get("following_count", 0)),
                        "account_age_days": int(features_dict.get("account_age_days", 0)),
                        "primary_flag": exp_info["suspicious_indicators"][0]["title"] if exp_info["suspicious_indicators"] else "Clean",
                        "recommended_action": risk_info["recommended_action"],
                        "data_source": batch_source_name,
                    })

                    # Also add high-risk accounts to session audit history
                    if risk_info["risk_category"] in ["High Risk", "Very High Risk"]:
                        add_audit_record({
                            "raw_input": row_dict,
                            "prediction": {"bot_probability": p, "predicted_class": int(p >= 0.5), "platform": platform},
                            "risk": risk_info,
                            "explanation": exp_info,
                            "review_status": "Pending Review",
                            "moderator_notes": "Batch ingestion alert",
                        })

                st.session_state.batch_results_df = pd.DataFrame(results)

        results_df = st.session_state.batch_results_df

        st.markdown("---")
        st.markdown("<h3 style='color:#0F2942;'>Batch Assessment Summary</h3>", unsafe_allow_html=True)

        # Batch Metrics
        b1, b2, b3, b4 = st.columns(4)
        total_b = len(results_df)
        low_b = sum(results_df["risk_category"] == "Low Risk")
        mod_b = sum(results_df["risk_category"] == "Moderate Risk")
        high_b = sum(results_df["risk_category"] == "High Risk")
        vhigh_b = sum(results_df["risk_category"] == "Very High Risk")

        with b1:
            st.metric("Total Analyzed", f"{total_b}")
        with b2:
            st.metric("Low Risk (Safe)", f"{low_b}", f"{round(low_b/total_b*100)}%")
        with b3:
            st.metric("Moderate Risk", f"{mod_b}")
        with b4:
            st.metric("High / Critical Risk", f"{high_b + vhigh_b}", delta_color="inverse")

        # Risk Distribution Histogram
        fig_dist = px.histogram(
            results_df,
            x="risk_score",
            nbins=20,
            color="risk_category",
            color_discrete_map={
                "Low Risk": "#10B981",
                "Moderate Risk": "#F59E0B",
                "High Risk": "#EA580C",
                "Very High Risk": "#DC2626",
            },
            title="Portfolio Risk Score Distribution",
        )
        fig_dist.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=260,
            margin=dict(l=20, r=20, t=35, b=20),
            xaxis=dict(title="Risk Score (0-100)", range=[0, 100]),
            yaxis=dict(title="Number of Accounts"),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # Dynamic Filters
        st.markdown("<h4 style='color:#0F2942;'>Filter & Inspect Accounts</h4>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

        with col_f1:
            plat_opts = ["All"] + list(results_df["platform"].unique())
            selected_plat = st.selectbox("Filter Platform", plat_opts)

        with col_f2:
            cat_opts = ["All"] + list(results_df["risk_category"].unique())
            selected_cat = st.selectbox("Filter Category", cat_opts)

        with col_f3:
            score_range = st.slider("Risk Score Range", 0.0, 100.0, (0.0, 100.0))

        filtered_df = results_df.copy()
        if selected_plat != "All":
            filtered_df = filtered_df[filtered_df["platform"] == selected_plat]
        if selected_cat != "All":
            filtered_df = filtered_df[filtered_df["risk_category"] == selected_cat]
        filtered_df = filtered_df[
            (filtered_df["risk_score"] >= score_range[0]) & (filtered_df["risk_score"] <= score_range[1])
        ]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        # CSV Export
        csv_export = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Analyzed Batch Results (CSV)",
            data=csv_export,
            file_name="socialshield_batch_risk_results.csv",
            mime="text/csv",
            type="primary",
        )
else:
    st.info("Upload a CSV file or click 'Load Sample Batch' above to test batch evaluation.")

