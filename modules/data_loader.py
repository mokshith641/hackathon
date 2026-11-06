"""
Data Loader Module for SocialShield AI
Loads local datasets, detects schemas, and generates benchmark synthetic samples
clearly labeled as synthetic demonstration data when external datasets are not yet provided.
"""

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def list_available_datasets() -> List[Dict[str, Any]]:
    """Scans data/ directory and subdirectories for available CSV datasets."""
    datasets = []
    patterns = [
        os.path.join(DATA_DIR, "*.csv"),
        os.path.join(DATA_DIR, "raw", "*.csv"),
        os.path.join(DATA_DIR, "processed", "*.csv"),
    ]
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            try:
                filename = os.path.basename(filepath)
                size_kb = round(os.path.getsize(filepath) / 1024, 2)
                # Read header
                df_head = pd.read_csv(filepath, nrows=5)
                row_count = sum(1 for _ in open(filepath, "r", encoding="utf-8", errors="ignore")) - 1

                is_synthetic = "synthetic" in filename.lower() or "demo" in filename.lower()
                datasets.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size_kb": size_kb,
                    "rows": max(0, row_count),
                    "columns": list(df_head.columns),
                    "is_synthetic": is_synthetic,
                    "label": f"{filename} ({row_count} rows, {size_kb} KB)" + (" [Synthetic Demo]" if is_synthetic else " [User Dataset]"),
                })
            except Exception as e:
                continue
    return datasets


def load_dataset_csv(filepath: str) -> pd.DataFrame:
    """Safely loads a CSV dataset with UTF-8 encoding handling."""
    try:
        return pd.read_csv(filepath, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding="latin1")


def generate_benchmark_dataset(num_records: int = 300, save: bool = True) -> pd.DataFrame:
    """
    Generates a realistic benchmark training dataset modeled after Cresci-2017 & public bot studies.
    Explicitly labeled as 'Synthetic Benchmark Data' to ensure academic integrity.
    
    Contains 50% Genuine Human profiles and 50% Automated / Bot profiles across varying behaviors.
    """
    np.random.seed(42)
    records = []
    now = datetime.now()

    genuine_bios = [
        "Software engineer & open source enthusiast. Coffee, tech, and cycling.",
        "Graphic designer, nature lover. Sharing my latest UI work and photography.",
        "Journalist covering tech, cyber policy and international news. Views are mine.",
        "High school biology teacher. Avid reader, runner, and science communicator.",
        "Product Manager @ FinTech. Passionate about ethical AI, dogs, and indie games.",
        "PhD candidate in Ecology. Field research notes, climate science & conservation.",
        "Indie filmmaker and podcast host. Stories that make us think.",
        "Chef and food blogger. Exploring street food around the world.",
        "Architecture student, urban photography and minimalism.",
        "Digital marketing specialist, gamer, and weekend hiker.",
    ]

    bot_bios = [
        "🚀 100x GEM CRYPTO ALERT! DM for promo! Free airdrop links in bio 🔥🔥🔥",
        "Follow for immediate follow back! Fast follower booster 24/7 automated! #f4f",
        "Make $500/day working 15 minutes from home! Click link to claim your bonus now 💰",
        "BEST DEALS & DISCOUNTS! Auto-posting hot Amazon promo codes every hour!",
        "🔥 Hottest viral clips & memes updated hourly! DM for promos & shoutouts.",
        "CLICK HERE TO WIN FREE IPHONE 16 PRO MAX! Limited time giveaway entry!",
        "",  # Many bots have empty bios
        "Automated breaking news bot powered by RSS feeds. Retweets not endorsements.",
        "Free followers, fast likes, cheap engagement packages! Visit link in bio.",
        "",
    ]

    genuine_usernames = [
        "alex_rivers", "sophia_tech", "marcus_design", "elena_writes", "david_code",
        "chloe_bakes", "liam_runner", "maya_visuals", "noah_audio", "olivia_dev",
        "samuel_craft", "nina_nature", "lucas_pixels", "zoe_reads", "ethan_cloud",
        "claire_art", "daniel_lens", "emma_travels", "ryan_builds", "lily_science"
    ]

    bot_prefixes = [
        "cryptogem", "followtrain", "dealsalert", "promobot", "airdrop_now",
        "freebonus", "boostfast", "viralclipz", "giveawaybot", "earnfast"
    ]

    platforms = ["X (Twitter)", "Instagram", "Facebook", "Other"]

    for i in range(num_records):
        is_bot = 1 if i % 2 == 1 else 0

        if is_bot:
            # Bot characteristics
            # High digit counts in username
            prefix = np.random.choice(bot_prefixes)
            digits = str(np.random.randint(1000, 999999))
            username = f"{prefix}_{digits}"
            
            # Account age: often newer
            age_days = int(np.random.exponential(scale=180)) + 3
            created_at = (now - timedelta(days=age_days)).strftime("%Y-%m-%d %H:%M:%S")

            # Follower / Following: asymmetric or follow-spammer
            bot_archetype = np.random.choice(["spammer", "follower_farm", "impersonator", "scraper", "aged_zombie"])
            if bot_archetype == "aged_zombie":
                # Hijacked or aged purchased bot
                age_days = int(np.random.uniform(600, 2800))
                following = np.random.randint(5000, 80000)
                followers = np.random.randint(10, 250)
                total_posts = np.random.randint(10, 600)
            elif bot_archetype == "spammer":
                following = np.random.randint(1500, 25000)
                followers = np.random.randint(5, 150)
                total_posts = int(age_days * np.random.uniform(15, 75))
            elif bot_archetype == "follower_farm":
                following = np.random.randint(2000, 15000)
                followers = np.random.randint(1800, 14000)
                total_posts = int(age_days * np.random.uniform(5, 30))
            elif bot_archetype == "scraper":
                following = np.random.randint(50, 400)
                followers = np.random.randint(500, 2500)
                total_posts = int(age_days * np.random.uniform(50, 150))
            else:  # impersonator
                following = np.random.randint(200, 1200)
                followers = np.random.randint(10, 80)
                total_posts = np.random.randint(0, 15)

            bio = np.random.choice(bot_bios)
            has_profile_pic = 1 if np.random.rand() > 0.45 else 0  # 45% default avatar
            is_verified = 0 if np.random.rand() > 0.03 else 1  # rarely verified

        else:
            # Genuine Human characteristics
            base_name = np.random.choice(genuine_usernames)
            suffix = str(np.random.randint(1, 99)) if np.random.rand() > 0.6 else ""
            username = f"{base_name}{suffix}"

            # Account age: usually established
            age_days = int(np.random.uniform(300, 3800))
            created_at = (now - timedelta(days=age_days)).strftime("%Y-%m-%d %H:%M:%S")

            # Realistic organic followings
            followers = int(np.random.lognormal(mean=6.0, sigma=1.2))  # ~200 - 3000
            following = int(np.random.lognormal(mean=5.5, sigma=0.9))  # ~150 - 1500
            posts_per_day_est = np.random.uniform(0.1, 3.5)
            total_posts = max(5, int(age_days * posts_per_day_est))

            bio = np.random.choice(genuine_bios)
            has_profile_pic = 1 if np.random.rand() > 0.05 else 0  # 95% have profile pic
            is_verified = 1 if np.random.rand() > 0.88 else 0  # 12% verified

        platform = np.random.choice(platforms, p=[0.55, 0.25, 0.15, 0.05])
        posts_per_day = round(total_posts / (age_days + 1), 3)

        # Introduce realistic borderline noise (~5% of subtle bots mimic humans, ~5% of new users look empty)
        if is_bot and np.random.rand() < 0.06:
            # Sophisticated bot mimicking human profile
            bio = "Photography & outdoor trips. Tech enthusiast."
            has_profile_pic = 1
            following = np.random.randint(200, 600)
            followers = np.random.randint(180, 550)
            posts_per_day = round(np.random.uniform(0.5, 2.0), 3)
        elif not is_bot and np.random.rand() < 0.06:
            # Genuine lurker / new human account with minimal info
            bio = ""
            has_profile_pic = 0
            following = np.random.randint(30, 200)
            followers = np.random.randint(0, 15)

        records.append({
            "username": username,
            "platform": platform,
            "created_at": created_at,
            "account_age_days": age_days,
            "followers_count": followers,
            "following_count": following,
            "total_posts": total_posts,
            "posts_per_day": posts_per_day,
            "description": bio,
            "has_profile_picture": has_profile_pic,
            "is_verified": is_verified,
            "is_bot": is_bot,
            "data_source": "Synthetic Benchmark Data",
        })

    df = pd.DataFrame(records)

    if save:
        os.makedirs(DATA_DIR, exist_ok=True)
        out_path = os.path.join(DATA_DIR, "demo_accounts.csv")
        df.to_csv(out_path, index=False)

        # Also create a small batch testing CSV without labels
        batch_df = df.sample(35, random_state=123).drop(columns=["is_bot", "data_source"]).copy()
        batch_path = os.path.join(DATA_DIR, "batch_test_accounts.csv")
        batch_df.to_csv(batch_path, index=False)

    return df
