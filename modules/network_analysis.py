"""
Network Intelligence & Coordinated Account Detection Module
Builds NetworkX graphs, computes multi-signal similarities (bio, naming, synchronicity),
detects coordinated bot rings/clusters, and produces interactive Plotly visualizations.
"""

import re
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_string_similarity(s1: str, s2: str) -> float:
    """Computes bigram Dice coefficient for username naming pattern similarity."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if len(s1) < 2 or len(s2) < 2:
        return 0.0

    b1 = set(s1[i:i+2] for i in range(len(s1)-1))
    b2 = set(s2[i:i+2] for i in range(len(s2)-1))
    intersection = len(b1.intersection(b2))
    return (2.0 * intersection) / (len(b1) + len(b2))


def build_account_network(
    accounts_df: pd.DataFrame,
    bio_similarity_threshold: float = 0.55,
    username_similarity_threshold: float = 0.65,
    time_window_days: int = 15,
) -> Tuple[nx.Graph, Dict[str, Any]]:
    """
    Builds a NetworkX graph linking accounts exhibiting coordinated or suspicious similarity.
    Edges carry metadata about the detected coordinating mechanism.
    """
    G = nx.Graph()
    n = len(accounts_df)

    if n == 0:
        return G, {"total_nodes": 0, "total_edges": 0, "clusters_detected": 0}

    # Add nodes with attributes
    for idx, row in accounts_df.iterrows():
        username = str(row.get("username", f"user_{idx}"))
        risk_score = float(row.get("risk_score", 50.0)) if "risk_score" in row and not pd.isna(row["risk_score"]) else 50.0
        platform = str(row.get("platform", "X (Twitter)"))
        bio = str(row.get("description", ""))

        G.add_node(
            username,
            risk_score=risk_score,
            platform=platform,
            bio=bio,
            followers=int(row.get("followers_count", 0)),
            following=int(row.get("following_count", 0)),
            label=username,
        )

    # 1. Bio Text Similarity via TF-IDF
    bios = accounts_df["description"].fillna("").astype(str).tolist()
    bio_edges = 0
    if any(len(b.strip()) > 5 for b in bios):
        try:
            tfidf = TfidfVectorizer(stop_words="english", min_df=1, ngram_range=(1, 2))
            bio_matrix = tfidf.fit_transform(bios)
            sim_matrix = cosine_similarity(bio_matrix)

            usernames = accounts_df["username"].tolist()
            for i in range(n):
                for j in range(i + 1, n):
                    sim = sim_matrix[i, j]
                    # Exclude empty bios matching
                    if sim >= bio_similarity_threshold and len(bios[i].strip()) > 8 and len(bios[j].strip()) > 8:
                        u1, u2 = usernames[i], usernames[j]
                        G.add_edge(u1, u2, weight=round(float(sim), 3), reason=f"High Bio Similarity ({int(sim*100)}%)", edge_type="bio_clone")
                        bio_edges += 1
        except Exception:
            pass

    # 2. Syntactic Username Pattern Similarity & Coordinated Timestamps
    usernames = accounts_df["username"].tolist()
    names_and_dates = accounts_df[["username", "account_age_days"]].to_dict("records") if "account_age_days" in accounts_df.columns else []

    coord_edges = 0
    for i in range(n):
        u1 = usernames[i]
        for j in range(i + 1, n):
            u2 = usernames[j]
            if G.has_edge(u1, u2):
                continue

            u_sim = compute_string_similarity(u1, u2)
            # Check for shared bot prefix (e.g., 'crypto_gem_12' and 'crypto_gem_99')
            p1 = re.sub(r"\d+$", "", u1).rstrip("_")
            p2 = re.sub(r"\d+$", "", u2).rstrip("_")
            shared_prefix = len(p1) > 4 and p1 == p2

            age_diff = 9999
            if names_and_dates:
                age1 = names_and_dates[i].get("account_age_days", 999)
                age2 = names_and_dates[j].get("account_age_days", 999)
                age_diff = abs(age1 - age2)

            if shared_prefix or (u_sim >= username_similarity_threshold and age_diff <= time_window_days):
                reason = "Shared Automated Naming Scheme" if shared_prefix else f"Username Pattern Match ({int(u_sim*100)}%) & Synchronized Registration"
                G.add_edge(u1, u2, weight=0.8, reason=reason, edge_type="naming_sync")
                coord_edges += 1

    # Detect Connected Clusters / Botnets
    components = list(nx.connected_components(G))
    suspicious_clusters = [comp for comp in components if len(comp) >= 2]

    # Assign cluster ids
    cluster_map = {}
    for c_id, comp in enumerate(suspicious_clusters, start=1):
        for node in comp:
            cluster_map[node] = f"Cluster #{c_id}"

    for node in G.nodes():
        G.nodes[node]["cluster"] = cluster_map.get(node, "Isolated Account")

    metrics = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "clusters_detected": len(suspicious_clusters),
        "cluster_sizes": [len(c) for c in suspicious_clusters],
        "density": round(nx.density(G), 4) if G.number_of_nodes() > 1 else 0.0,
    }

    return G, metrics


def generate_network_demo_data() -> pd.DataFrame:
    """
    Generates a structured multi-account dataset with 2 intentional coordinated bot rings
    and organic genuine community clusters for live hackathon demonstration.
    """
    records = []

    # Cluster A: Crypto Promo Botnet (Identical bio phrases, shared prefix, identical creation window)
    for i in range(1, 7):
        records.append({
            "username": f"crypto_alpha_bot_{100 + i * 17}",
            "platform": "X (Twitter)",
            "account_age_days": 18,
            "followers_count": 24 + i,
            "following_count": 2800 + i * 50,
            "total_posts": 450 + i * 20,
            "posts_per_day": 26.0,
            "description": "🚀 100x GEM CRYPTO ALERT! Free airdrop links in bio 🔥 DM for promotion",
            "has_profile_picture": 0 if i % 2 == 0 else 1,
            "is_verified": 0,
            "risk_score": 88.5,
            "cluster_label": "Crypto Promo Botnet (Coordinated)",
        })

    # Cluster B: Engagement Follow-Farm Ring (Copy-paste bio, mass follow back)
    for i in range(1, 6):
        records.append({
            "username": f"fast_growth_f4f_{i * 88}",
            "platform": "Instagram",
            "account_age_days": 42,
            "followers_count": 1400 + i * 30,
            "following_count": 4900 + i * 10,
            "total_posts": 120,
            "posts_per_day": 3.0,
            "description": "Follow for immediate follow back! Fast follower booster 24/7 automated! #f4f",
            "has_profile_picture": 1,
            "is_verified": 0,
            "risk_score": 76.0,
            "cluster_label": "Follow-Farm Sybil Ring",
        })

    # Cluster C: Organic Tech Creators (Different bios, normal activity, occasional mutual follows)
    tech_names = ["sarah_cloud_dev", "marcus_cybersec", "alex_ai_research", "priya_frontend", "chen_systems"]
    tech_bios = [
        "Cloud architect @ FinTech. Docker, Kubernetes, and Golang.",
        "Security researcher & incident responder. Threat intel nerd.",
        "Applied ML scientist. LLMs, model evaluation & fairness.",
        "Staff UI engineer. Building accessible web interfaces.",
        "Distributed systems engineer. Rust, databases & performance.",
    ]
    for idx, (name, bio) in enumerate(zip(tech_names, tech_bios)):
        records.append({
            "username": name,
            "platform": "X (Twitter)",
            "account_age_days": 1200 + idx * 200,
            "followers_count": 1500 + idx * 400,
            "following_count": 400 + idx * 50,
            "total_posts": 2800 + idx * 300,
            "posts_per_day": 1.8,
            "description": bio,
            "has_profile_picture": 1,
            "is_verified": 1 if idx == 0 else 0,
            "risk_score": 14.0,
            "cluster_label": "Organic Professional Community",
        })

    return pd.DataFrame(records)


def render_network_plotly(G: nx.Graph) -> go.Figure:
    """Builds a high-performance, interactive 2D network diagram with Plotly."""
    if G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(title="No network nodes available.")
        return fig

    # Layout using Spring layout (Fruchterman-Reingold)
    pos = nx.spring_layout(G, k=0.45, iterations=60, seed=42)

    # Edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#CBD5E1"),
        hoverinfo="none",
        mode="lines",
    )

    # Node traces
    node_x = []
    node_y = []
    node_color = []
    node_text = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        data = G.nodes[node]
        risk = data.get("risk_score", 50.0)
        cluster = data.get("cluster", "Isolated Account")
        platform = data.get("platform", "X")
        followers = data.get("followers", 0)
        following = data.get("following", 0)
        bio = data.get("bio", "No bio")[:60]

        node_color.append(risk)
        node_size.append(18 + min(risk // 4, 16))

        hover = (
            f"<b>@{node}</b> ({platform})<br>"
            f"Risk Score: <b>{risk:.1f}/100</b><br>"
            f"Group: <b>{cluster}</b><br>"
            f"Followers: {followers:,} | Following: {following:,}<br>"
            f"Bio: <i>{bio}...</i>"
        )
        node_text.append(hover)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=[f"@{node}" if G.nodes[node].get("risk_score", 0) > 60 else "" for node in G.nodes()],
        textposition="top center",
        textfont=dict(size=10, color="#1E293B"),
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale=[
                [0.0, "#10B981"],   # Green (Low risk)
                [0.3, "#34D399"],
                [0.55, "#F59E0B"],  # Amber (Moderate risk)
                [0.75, "#EA580C"],  # Orange (High risk)
                [1.0, "#DC2626"],   # Red (Very high risk)
            ],
            color=node_color,
            size=node_size,
            colorbar=dict(
                thickness=12,
                title=dict(text="Risk Score", font=dict(size=11, color="#334155")),
                xanchor="left",
                len=0.7,
            ),
            line=dict(width=2, color="#FFFFFF"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=10, l=10, r=10, t=30),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#F8FAFC",
            paper_bgcolor="#FFFFFF",
            height=540,
        ),
    )

    return fig

