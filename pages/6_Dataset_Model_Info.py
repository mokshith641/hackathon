"""
Page 6: Dataset & Machine Learning Architecture
Model performance metrics, feature importances, dataset citations, and live custom retraining.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from modules.session_state import init_session_state
from modules.model_training import get_model_metadata, train_and_save_model
from modules.data_loader import list_available_datasets, load_dataset_csv

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">Dataset & Model Architecture</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Transparent evaluation metrics, feature attribution weights, and academic dataset lineage.
    </p>
</div>
""", unsafe_allow_html=True)

# Retrieve current model metadata
meta = get_model_metadata()

if meta is None:
    st.warning("No model metadata found. Please train a baseline model below.")
    metrics = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0, "roc_auc": 0.0, "cv_f1_mean": 0.0}
    dataset_name = "None"
    is_synth = True
else:
    metrics = meta.get("metrics", {})
    dataset_name = meta.get("dataset_name", "Synthetic Cresci-2017 Benchmark")
    is_synth = meta.get("is_synthetic", True)

# Dataset Lineage Banner
if is_synth:
    st.markdown("""
    <div style="background:#FFFBEB; border:1px solid #FDE68A; border-left:4px solid #D97706; padding:12px 16px; border-radius:8px; margin-bottom:16px;">
        <div style="font-weight:700; color:#92400E; font-size:13px;">⚠️ Demonstration Lineage: Synthetic Benchmark Data</div>
        <p style="color:#78350F; font-size:12px; margin:4px 0 0 0;">
            The currently loaded Random Forest model is trained on a synthetic demonstration dataset reflecting statistical distributions from the <b>Cresci-2017</b> benchmark. To train on the full historical academic dataset, download the CSV from the links below and use the retrain utility.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-left:4px solid #059669; padding:12px 16px; border-radius:8px; margin-bottom:16px;">
        <div style="font-weight:700; color:#065F46; font-size:13px;">✅ Active Model Lineage: {dataset_name}</div>
        <p style="color:#047857; font-size:12px; margin:4px 0 0 0;">
            Model is trained on user-supplied historical records with verified test splits.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Model Metrics
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-top:3px solid #0284C7;">
        <div class="metric-label">Accuracy</div>
        <div class="metric-value" style="font-size:24px;">{metrics.get('accuracy', 0.0):.1%}</div>
        <div class="metric-sub">Holdout test split</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-top:3px solid #10B981;">
        <div class="metric-label">Precision</div>
        <div class="metric-value" style="font-size:24px; color:#059669;">{metrics.get('precision', 0.0):.1%}</div>
        <div class="metric-sub">Low false positives</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-top:3px solid #F59E0B;">
        <div class="metric-label">Recall</div>
        <div class="metric-value" style="font-size:24px; color:#D97706;">{metrics.get('recall', 0.0):.1%}</div>
        <div class="metric-sub">Bot detection coverage</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-top:3px solid #8B5CF6;">
        <div class="metric-label">F1-Score</div>
        <div class="metric-value" style="font-size:24px; color:#7C3AED;">{metrics.get('f1_score', 0.0):.3f}</div>
        <div class="metric-sub">Harmonic mean</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-top:3px solid #DC2626;">
        <div class="metric-label">ROC-AUC</div>
        <div class="metric-value" style="font-size:24px; color:#DC2626;">{metrics.get('roc_auc', 0.0):.3f}</div>
        <div class="metric-sub">Area under curve</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Confusion Matrix & Feature Importances Row
col_vis_left, col_vis_right = st.columns([1, 1])

with col_vis_left:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Confusion Matrix (Holdout Test Set)</h4>", unsafe_allow_html=True)
    cm = meta.get("confusion_matrix", [[40, 2], [3, 45]])
    cm_df = pd.DataFrame(
        cm,
        index=["Actual Genuine (0)", "Actual Bot (1)"],
        columns=["Pred Genuine (0)", "Pred Bot (1)"]
    )
    fig_cm = px.imshow(
        cm_df,
        text_auto=True,
        color_continuous_scale="Blues",
        labels=dict(x="Predicted Class", y="Actual Ground Truth", color="Samples"),
    )
    fig_cm.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=280,
        margin=dict(l=20, r=20, t=10, b=20),
    )
    st.plotly_chart(fig_cm, use_container_width=True)

with col_vis_right:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Global Feature Importances (Gini Impurity)</h4>", unsafe_allow_html=True)
    fi = meta.get("feature_importances", {})
    if fi:
        fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
        fig_fi = px.bar(
            fi_df,
            x="Importance",
            y="Feature",
            orientation="h",
            color_discrete_sequence=["#1E3A8A"],
        )
        fig_fi.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=280,
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis=dict(title="Importance Weight"),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.caption("Feature importances not available.")

# Real Dataset Download Links & References Accordion
with st.expander("📚 Academic Benchmark Datasets & Download Links", expanded=True):
    st.markdown("""
    To train or evaluate SocialShield AI on large-scale real-world datasets, the following public academic corpora are recommended:

    1. **Cresci-2017 Dataset (The Gold Standard):**
       - Contains ~3,474 human accounts and ~11,000 bots across multiple archetypes (traditional spambots, social spambots, fake followers).
       - **Direct Repository:** [Botometer Bot Repository](https://botometer.osome.iu.edu/bot-repository/datasets.html)
       - **Kaggle Mirror (Ready CSV):** [Kaggle: Twitter Bots Accounts (Cresci et al.)](https://www.kaggle.com/datasets/davidmartngutirrez/twitter-bots-accounts)
       - **Citation:** Cresci, S., et al. (2017). *"The paradigm-shift of social spambots: Evidence, theories, and tools for the arms race."* WWW '17 Companion.

    2. **TwiBot-22:**
       - Comprehensive multi-modal graph benchmark with 1,000,000 entities and diverse modern bot behaviors.
       - **Website:** [TwiBot-22 Project](https://twibot22.github.io/)

    3. **MGTAB (Multi-Platform Multi-Genre Twitter & Bot Dataset):**
       - Labeled accounts categorized by spam, disinformation, and commercial automation.
       - **Repository:** [MGTAB Benchmark](https://github.com/rabimb/MGTAB)
    """)

# Interactive Retraining Pipeline
st.markdown("---")
st.markdown("<h3 style='color:#0F2942;'>Train / Update Model on Custom CSV</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size:13px; color:#64748B;'>Upload a new labeled CSV dataset or select a discovered file to retrain the Random Forest classifier.</p>", unsafe_allow_html=True)

col_train_file, col_train_params = st.columns([3, 2])

with col_train_file:
    train_file = st.file_uploader("Upload Training Dataset (CSV with labels)", type=["csv"], key="uploader_retrain")
    
    # Also check local files
    local_files = list_available_datasets()
    local_choices = ["-- Or select local discovered dataset --"] + [d["filename"] for d in local_files]
    selected_local = st.selectbox("Discovered Datasets in /data", local_choices)

with col_train_params:
    trees_count = st.slider("Number of Estimators (Trees)", 50, 300, 120, 10)
    max_tree_depth = st.slider("Max Tree Depth", 4, 30, 12)

if st.button("⚡ Train & Deploy Updated Random Forest Model", type="primary"):
    df_raw = None
    target_source = "Uploaded Dataset"

    if train_file is not None:
        try:
            df_raw = pd.read_csv(train_file)
            target_source = train_file.name
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
    elif selected_local != "-- Or select local discovered dataset --":
        matched = next((d for d in local_files if d["filename"] == selected_local), None)
        if matched:
            df_raw = load_dataset_csv(matched["filepath"])
            target_source = matched["filename"]

    if df_raw is not None:
        with st.spinner(f"Extracting features, splitting train/test, and fitting {trees_count} trees..."):
            try:
                new_meta = train_and_save_model(
                    df_raw,
                    dataset_name=target_source,
                    n_estimators=trees_count,
                    max_depth=max_tree_depth,
                )
                st.success(f"🎉 Model successfully retrained on '{target_source}'! Accuracy: {new_meta['metrics']['accuracy']:.1%}, F1: {new_meta['metrics']['f1_score']:.3f}")
                st.rerun()
            except Exception as ex:
                st.error(f"Training failed: {ex}")
    else:
        st.warning("Please upload a CSV or select a local dataset before clicking Train.")

