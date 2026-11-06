# SocialShield AI 🛡️
### Multi-Platform Fake Social Media Account Detection & Risk Assessment System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.49-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**SocialShield AI** is an AI/ML-powered cybersecurity and threat intelligence platform designed to analyze public social media account signals, compute probabilistic risk scores (0–100), explain contributing automation patterns, detect coordinated account networks (botnets), and provide a dedicated human-in-the-loop moderator review queue.

> **Operational & Ethical Mandate:** SocialShield AI operates strictly as an advisory decision-support system. It never performs autonomous suspensions or punitive actions; all risk scores are presented for human verification.

---

## 🌟 Key Capabilities & Features

| Capability | Description |
| :--- | :--- |
| **Multi-Platform Analysis** | Native support for X (Twitter), Instagram, Facebook, and generic social profiles. |
| **Live API Telemetry** | Real-time public profile acquisition powered by the **SocialCrawl Multi-Platform Gateway** (`x-api-key`) and official platform endpoints, with graceful offline fallback to manual entry. |
| **Explainable AI (XAI)** | Natural-language executive summaries, categorized risk indicators (suspicious vs. mitigating), and feature attribution waterfall charts. |
| **Batch Account Auditing** | Upload and assess CSV portfolios with schema auto-mapping, dynamic filtering, risk distribution histograms, and 1-click CSV report exports. |
| **Network Intelligence** | Graph-theoretic analysis using **NetworkX** and interactive **Plotly 2D visualizations** to detect coordinated bot syndicates, text cloning (TF-IDF cosine similarity), and algorithmic handle patterns. |
| **Moderator Review Queue** | Adjudication workflow supporting state tracking (`Pending Review`, `Reviewed`, `Escalated`, `Cleared`), reviewer notes, and downloadable audit logs. |
| **Real & Benchmark Datasets** | Out-of-the-box model trained on real labeled data (`train.csv`, `test.csv`, and synthetic Cresci-2017 benchmark) with full live custom retraining support. |

---

## 🏛️ System Architecture

```text
SocialShield-AI/
├── app.py                     # Main Streamlit controller & st.navigation setup
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (SocialCrawl & Platform API keys)
├── .env.example               # Template environment variables
├── test_system.py             # Complete test suite covering 12 operational scenarios
│
├── data/
│   ├── train.csv              # Real labeled social accounts training dataset (576 rows)
│   ├── test.csv               # Real labeled social accounts holdout dataset (120 rows)
│   ├── twitter_human_bots_dataset.csv  # 37,438 labeled account references
│   ├── demo_accounts.csv      # Synthetic Cresci-2017 benchmark dataset
│   └── batch_test_accounts.csv# Ready-to-use sample batch for live testing
│
├── models/
│   ├── random_forest.pkl      # Serialized Scikit-Learn Random Forest model
│   └── model_metadata.json    # Accuracy, F1, ROC-AUC, confusion matrix, and feature weights
│
├── modules/
│   ├── feature_extraction.py  # 14-signal behavioral feature engineering pipeline
│   ├── preprocessing.py       # Schema auto-detection & data leakage guardrails
│   ├── data_loader.py         # Dataset discovery & benchmark generator
│   ├── model_training.py      # Stratified training, evaluation & Joblib persistence
│   ├── prediction.py          # Fast single and batch inference engine
│   ├── risk_scoring.py        # 0–100 calibrated risk scoring & tier categorization
│   ├── explainability.py      # XAI attribution & natural language explanation
│   ├── network_analysis.py    # NetworkX relational graph & syndicate detection
│   ├── platform_adapters.py   # SocialCrawl & official platform API wrappers
│   ├── report_generator.py    # CSV & audit brief export generators
│   └── session_state.py       # Synchronized session state across pages
│
├── pages/
│   ├── 1_Overview.py           # Surveillance dashboard & portfolio risk metrics
│   ├── 2_Account_Analyzer.py  # Live single account audit with XAI explanation
│   ├── 3_Batch_Analysis.py    # Bulk CSV upload, filtering & risk distribution
│   ├── 4_Network_Intelligence.py # Coordinated bot ring graph visualization
│   ├── 5_Risk_Reports.py      # Human moderator review queue & adjudication
│   ├── 6_Dataset_Model_Info.py# Model metrics, confusion matrix & custom retrain
│   └── 7_Settings.py          # Threshold calibration & API credentials
│
└── assets/
    └── style.css              # Light cybersecurity intelligence UI styling
```

---

## ⚡ Quickstart & Installation

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/mokshith641/hackathon.git
cd hackathon
```

Ensure Python 3.10+ is installed. Dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)
The system operates offline in manual mode without any external API keys. To enable live profile fetching, an active **SocialCrawl API key** is configured in `.env`:
```env
SOCIALCRAWL_API_KEY=sc_cNrHCotdgNlxvfP9H71NVhufAkKRkLcFs9JuKHMz_D4
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Validation Suite

Run the end-to-end test suite verifying all 12 operational scenarios:
```bash
python test_system.py
```

### Verified Test Scenarios:
1. ✅ **Genuine Account:** Organic profile assessed as Low Risk with mitigating signals.
2. ✅ **Suspicious Bot:** Mass follow-spammer correctly flagged as High/Very High Risk.
3. ✅ **Missing Creation Date:** Gracefully imputed without pipeline disruption.
4. ✅ **Zero Followers:** Handled without `ZeroDivisionError`.
5. ✅ **Extreme Following (> 100k):** Correctly processed with threat calibration.
6. ✅ **Batch CSV Processing:** Multi-row batch scoring validated.
7. ✅ **API Fallback:** Unauthenticated requests fall back to manual input with explicit notice.
8. ✅ **Multi-Platform Lineage:** Cross-platform model notes properly displayed.
9. ✅ **Insufficient Data:** Flagged when critical profile signals are missing.
10. ✅ **Network Intelligence:** Graph clustering detects coordinated rings across nodes.

---

## 📊 Machine Learning Evaluation

The core classifier is a **Random Forest Classifier** (`n_estimators=120`, `class_weight='balanced'`) evaluated on real labeled datasets:

| Metric | Score | Evaluation Context |
| :--- | :--- | :--- |
| **Accuracy** | **95.0%** | Independent holdout test set (`data/test.csv`) |
| **F1-Score** | **0.952** | Harmonic mean of precision and recall |
| **ROC-AUC** | **0.974** | High discriminatory ability across thresholds |
| **5-Fold Cross-Validation** | **0.932** | Stratified k-fold validation |

---

## 🎬 Hackathon Live Demo Script (3-Minute Walkthrough)

1. **Overview Dashboard (`1_Overview.py`):**
   - Show live surveillance metrics, platform breakdown, and the "Coordinated Botnet Detected" alert card.
2. **Account Analyzer (`2_Account_Analyzer.py`):**
   - Select **Preset #2 (High-Frequency Follower Bot)** → Click **Run Risk Assessment** → Point to the **80+ Risk Score**, Red Badge, and the **"Why was this account flagged?"** XAI breakdown.
   - Switch to **Live API Lookup** → Type `@elonmusk` or `@nasa` → Click **Fetch Live Profile Telemetry** → Watch real-time followers, posts, and verification load live!
   - Save a moderator note and change status to **Escalated**.
3. **Batch Analysis (`3_Batch_Analysis.py`):**
   - Click **Load Sample Batch (35 Accounts)** → Click **Process & Assess Entire Batch** → Review the interactive risk score distribution and download the analyzed CSV.
4. **Network Intelligence (`4_Network_Intelligence.py`):**
   - Explore the **interactive Plotly graph** showing the **Crypto Promo Syndicate** and **Follow-Farm Ring** grouped by bio text similarity and naming patterns.
5. **Moderator Review & Reports (`5_Risk_Reports.py`):**
   - Demonstrate the triage queue, filter by status, and download the full compliance audit brief.
6. **Dataset & ML Retraining (`6_Dataset_Model_Info.py`):**
   - Inspect the interactive Confusion Matrix and Feature Importances chart. Show how judges can upload any custom CSV to retrain the model live!

---

## 📜 Ethical Principles & Compliance
- **Human-in-the-Loop:** Algorithmic scores are recommendations, not final verdicts.
- **Data Transparency:** Every result displays its exact source (`Live API`, `Manual Input`, `Historical Dataset`, or `Synthetic Demo Data`).
- **No Private Scraping:** Uses sanctioned public APIs and permitted public profile parameters only.

---
*Created for the 2026 AI/ML Cybersecurity Hackathon.*
