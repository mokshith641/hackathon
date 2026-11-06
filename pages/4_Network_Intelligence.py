"""
Page 4: Network Intelligence & Coordinated Account Detection
Graph-based syndicate detection, bio similarity analysis, and interactive cluster visualization.
"""

import streamlit as st
import pandas as pd
import networkx as nx

from modules.session_state import init_session_state
from modules.network_analysis import (
    build_account_network,
    generate_network_demo_data,
    render_network_plotly,
)

init_session_state()

st.markdown("""
<div style="margin-bottom:18px;">
    <h2 style="color:#0F2942; margin:0; font-weight:800;">Network Intelligence & Syndicate Detection</h2>
    <p style="color:#64748B; margin:4px 0 0 0; font-size:14px;">
        Identify coordinated bot rings, sybil clusters, and astroturfing campaigns through relational graph analytics.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="review-notice">
    <b>🔬 Demonstration Transparency:</b> Social platforms do not provide unrestricted public follower-follower graphs via standard APIs. The network intelligence module synthesizes text similarity (TF-IDF cosine metrics), naming heuristics, and synchronized registration windows to reconstruct latent coordinated rings.
</div>
""", unsafe_allow_html=True)

# Graph Source Selector
col_source, col_btn = st.columns([3, 2])
with col_source:
    data_source_mode = st.radio(
        "Network Data Feed",
        ["Simulated Multi-Syndicate Benchmark (Recommended for Demo)", "Currently Audited Session Accounts"],
        horizontal=True,
    )

with st.sidebar:
    st.markdown("### ⚙️ Graph Detection Sensitivity")
    bio_sim_thresh = st.slider("Bio Text Similarity Threshold", 0.30, 0.90, 0.55, 0.05,
                               help="Cosine similarity score on TF-IDF n-grams to flag copy-pasted bot bios.")
    user_sim_thresh = st.slider("Username Pattern Threshold", 0.40, 0.95, 0.65, 0.05,
                                help="Lexical pattern threshold to detect mass-generated username permutations.")
    time_window = st.slider("Synchronicity Window (Days)", 1, 60, 15,
                            help="Flag accounts registered within a narrow chronological window.")

# Load or assemble accounts DataFrame
if "Simulated" in data_source_mode:
    net_df = generate_network_demo_data()
else:
    # Build from session state audit history
    records = []
    for r in st.session_state.audit_history:
        raw = r.get("raw_input", {})
        risk = r.get("risk", {})
        records.append({
            "username": raw.get("username", "unknown"),
            "platform": raw.get("platform", "X (Twitter)"),
            "account_age_days": raw.get("account_age_days", 100),
            "followers_count": raw.get("followers_count", 0),
            "following_count": raw.get("following_count", 0),
            "total_posts": raw.get("total_posts", 0),
            "description": raw.get("description", ""),
            "has_profile_picture": raw.get("has_profile_picture", 1),
            "is_verified": raw.get("is_verified", 0),
            "risk_score": risk.get("risk_score", 50.0),
        })
    if len(records) < 4:
        st.warning("Fewer than 4 accounts in session audit history. Displaying benchmark syndicate network for demonstration.")
        net_df = generate_network_demo_data()
    else:
        net_df = pd.DataFrame(records)

# Build Graph
G, metrics = build_account_network(
    net_df,
    bio_similarity_threshold=bio_sim_thresh,
    username_similarity_threshold=user_sim_thresh,
    time_window_days=time_window,
)

# Network KPI Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="shield-metric-card">
        <div class="metric-label">Analyzed Nodes</div>
        <div class="metric-value">{metrics['total_nodes']}</div>
        <div class="metric-sub">Monitored profiles</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="shield-metric-card">
        <div class="metric-label">Detected Correlations</div>
        <div class="metric-value" style="color:#0284C7;">{metrics['total_edges']}</div>
        <div class="metric-sub">Similarity linkages</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="shield-metric-card" style="border-left:4px solid #DC2626;">
        <div class="metric-label">Coordinated Clusters</div>
        <div class="metric-value" style="color:#DC2626;">{metrics['clusters_detected']}</div>
        <div class="metric-sub">Potential bot syndicates</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="shield-metric-card">
        <div class="metric-label">Graph Density</div>
        <div class="metric-value">{metrics['density']}</div>
        <div class="metric-sub">Cohesion coefficient</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Interactive Plotly Network Diagram
st.markdown("<h4 style='color:#0F2942;'>Interactive Relational Graph Visualization</h4>", unsafe_allow_html=True)
fig_net = render_network_plotly(G)
st.plotly_chart(fig_net, use_container_width=True)

# Coordinated Cluster Analysis Table
col_cl_left, col_cl_right = st.columns([3, 2])

with col_cl_left:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Detected Coordinated Syndicates</h4>", unsafe_allow_html=True)
    components = [list(c) for c in nx.connected_components(G) if len(c) >= 2]

    if components:
        cluster_rows = []
        for c_idx, comp in enumerate(components, 1):
            sub_nodes = [net_df[net_df["username"] == u] for u in comp if not net_df[net_df["username"] == u].empty]
            if sub_nodes:
                sub_df = pd.concat(sub_nodes)
                avg_risk = round(sub_df["risk_score"].mean(), 1) if "risk_score" in sub_df.columns else 50.0
                sample_bio = sub_df["description"].iloc[0][:50] if "description" in sub_df.columns and len(sub_df["description"].iloc[0]) > 0 else "N/A"
            else:
                avg_risk = 50.0
                sample_bio = "N/A"

            cluster_rows.append({
                "Cluster": f"Syndicate #{c_idx}",
                "Members": len(comp),
                "Sample Handles": ", ".join([f"@{u}" for u in list(comp)[:3]]),
                "Avg Risk": f"{avg_risk}/100",
                "Shared Bio Excerpt": sample_bio,
            })
        st.dataframe(pd.DataFrame(cluster_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No multi-node coordinated clusters detected at the current sensitivity thresholds.")

with col_cl_right:
    st.markdown("<h4 style='color:#0F2942; margin-bottom:8px;'>Syndicate Forensic Signatures</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:14px; font-size:12px; color:#334155;">
        <p style="margin:0 0 8px 0;"><b>Detected Correlation Vectors:</b></p>
        <ul style="margin:0; padding-left:18px; line-height:1.6;">
            <li><b>Text Cloning:</b> Identical promotional pitches pointing to Telegram channels / airdrop URLs.</li>
            <li><b>Naming Suffix Pattern:</b> Algorithmic handle generation using common roots (e.g. <code>crypto_alpha_bot_XXX</code>).</li>
            <li><b>Temporal Burst:</b> Batch registration of nodes within 48 hours of each other.</li>
            <li><b>Asymmetrical Graph:</b> Massive outbound followings with negligible inbound follower reciprocation.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

