"""
SocialShield AI - Verification & Test Suite
Executes end-to-end unit and scenario tests covering all Section 18 requirements.
"""

import os
import unittest
import pandas as pd
from datetime import datetime, timedelta

from modules.feature_extraction import extract_features_from_dict, extract_features_df, parse_date
from modules.preprocessing import clean_and_prepare_dataset, detect_column_mapping
from modules.prediction import get_model, predict_single_account, predict_batch_accounts
from modules.risk_scoring import calculate_risk_score, check_data_completeness
from modules.explainability import explain_account_risk
from modules.network_analysis import build_account_network, generate_network_demo_data
from modules.platform_adapters import fetch_x_account
from modules.report_generator import generate_single_account_report_df


class TestSocialShieldAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure model is initialized
        cls.model = get_model()
        assert cls.model is not None

    def test_scenario_1_genuine_account(self):
        """Scenario 1: Established, organic user profile."""
        account = {
            "username": "sarah_travels",
            "platform": "Instagram",
            "created_at": (datetime.now() - timedelta(days=1200)).strftime("%Y-%m-%d"),
            "followers_count": 2100,
            "following_count": 480,
            "total_posts": 350,
            "description": "Landscape photographer and mountain trekker. Canon R5.",
            "has_profile_picture": 1,
            "is_verified": 0,
        }
        pred = predict_single_account(account)
        risk = calculate_risk_score(pred["bot_probability"], account)
        exp = explain_account_risk(pred["features"], account, pred["bot_probability"])

        self.assertLess(risk["risk_score"], 40.0)
        self.assertEqual(risk["risk_category"], "Low Risk")
        self.assertTrue(len(exp["mitigating_indicators"]) > 0)
        print("✓ Scenario 1: Genuine account correctly assessed as Low Risk.")

    def test_scenario_2_suspicious_bot(self):
        """Scenario 2: Mass follow-farming spam bot."""
        account = {
            "username": "fast_crypto_pump_98471",
            "platform": "X (Twitter)",
            "created_at": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
            "followers_count": 12,
            "following_count": 4200,
            "total_posts": 620,
            "description": "🚀 100x GEM CRYPTO ALERT! Free airdrop links in bio 🔥 DM for promotion",
            "has_profile_picture": 0,
            "is_verified": 0,
        }
        pred = predict_single_account(account)
        risk = calculate_risk_score(pred["bot_probability"], account)
        exp = explain_account_risk(pred["features"], account, pred["bot_probability"])

        self.assertGreater(risk["risk_score"], 60.0)
        self.assertIn(risk["risk_category"], ["High Risk", "Very High Risk"])
        self.assertTrue(len(exp["suspicious_indicators"]) >= 2)
        print("✓ Scenario 2: Suspicious bot correctly flagged with High/Very High Risk.")

    def test_scenario_3_and_6_missing_date(self):
        """Scenario 3 & 6: New account with missing creation date."""
        account = {
            "username": "fresh_user_01",
            "platform": "Other",
            "created_at": None,
            "followers_count": 10,
            "following_count": 20,
            "total_posts": 1,
            "description": "Just joined",
            "has_profile_picture": 1,
            "is_verified": 0,
        }
        pred = predict_single_account(account)
        self.assertIsNotNone(pred["bot_probability"])
        print("✓ Scenario 3 & 6: Handled missing creation date gracefully.")

    def test_scenario_4_zero_followers(self):
        """Scenario 4: Account with exactly zero followers."""
        account = {
            "username": "zero_audience_99",
            "platform": "X (Twitter)",
            "created_at": "2024-01-01",
            "followers_count": 0,
            "following_count": 250,
            "total_posts": 5,
            "description": "",
            "has_profile_picture": 0,
            "is_verified": 0,
        }
        pred = predict_single_account(account)
        self.assertFalse(pd.isna(pred["bot_probability"]))
        print("✓ Scenario 4: Account with 0 followers computed without ZeroDivisionError.")

    def test_scenario_5_extreme_following(self):
        """Scenario 5: Unusually high following count (> 100,000)."""
        account = {
            "username": "mass_follower_bot",
            "platform": "X (Twitter)",
            "created_at": "2023-01-01",
            "followers_count": 50,
            "following_count": 150000,
            "total_posts": 1000,
            "description": "Mass follow train",
            "has_profile_picture": 0,
            "is_verified": 0,
        }
        pred = predict_single_account(account)
        risk = calculate_risk_score(pred["bot_probability"], account)
        self.assertGreater(risk["risk_score"], 60.0)
        print("✓ Scenario 5: Massive following count handled robustly.")

    def test_scenario_7_and_8_batch_csv(self):
        """Scenario 7 & 8: Batch DataFrame processing."""
        batch_df = pd.DataFrame([
            {"username": "user_a", "followers_count": 500, "following_count": 400, "total_posts": 200},
            {"username": "user_b_9482", "followers_count": 3, "following_count": 4000, "total_posts": 800},
        ])
        probs, preds, X = predict_batch_accounts(batch_df)
        self.assertEqual(len(probs), 2)
        self.assertEqual(len(preds), 2)
        print("✓ Scenario 7 & 8: Batch prediction pipeline operational.")

    def test_scenario_9_and_10_api_fallback(self):
        """Scenario 9 & 10: API credentials unavailable / failure fallback."""
        data, source, msg = fetch_x_account("jack", bearer_token="", socialcrawl_key="")
        self.assertIsNone(data)
        self.assertEqual(source, "Manual Input")
        self.assertIn("Manual Input", msg)
        print("✓ Scenario 9 & 10: Clean API token fallback with explicit status message.")

    def test_scenario_11_cross_platform_flags(self):
        """Scenario 11: Multi-platform transparency."""
        acc_x = {"username": "user_x", "platform": "X (Twitter)", "followers_count": 100}
        acc_ig = {"username": "user_ig", "platform": "Instagram", "followers_count": 100}
        res_x = predict_single_account(acc_x)
        res_ig = predict_single_account(acc_ig)
        self.assertTrue(res_x["is_platform_native"])
        self.assertFalse(res_ig["is_platform_native"])
        print("✓ Scenario 11: Multi-platform lineage transparency verified.")

    def test_scenario_12_insufficient_data(self):
        """Scenario 12: Account with insufficient critical data."""
        empty_acc = {"username": "", "followers_count": None, "following_count": None, "created_at": None}
        is_suff, note = check_data_completeness(empty_acc)
        self.assertFalse(is_suff)
        risk = calculate_risk_score(0.5, empty_acc)
        self.assertEqual(risk["risk_category"], "Insufficient Data")
        print("✓ Scenario 12: Correctly triggers 'Insufficient Data' state.")

    def test_network_graph_clustering(self):
        """Test NetworkX cluster detection."""
        demo_net = generate_network_demo_data()
        G, metrics = build_account_network(demo_net)
        self.assertGreater(metrics["total_nodes"], 10)
        self.assertGreater(metrics["clusters_detected"], 0)
        print(f"✓ Network Intelligence: Detected {metrics['clusters_detected']} coordinated clusters across {metrics['total_nodes']} nodes.")


if __name__ == "__main__":
    unittest.main()

