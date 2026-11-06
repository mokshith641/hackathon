"""
Generates a clean, simple, professional 9-slide PowerPoint presentation
for SocialShield AI using simple English without jargon or cluttered graphics.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Professional Theme Palette
    COLOR_BG = RGBColor(248, 250, 252)       # Light Slate #F8FAFC
    COLOR_NAVY = RGBColor(15, 41, 66)        # Deep Navy #0F2942
    COLOR_BLUE = RGBColor(30, 58, 138)       # Royal Blue #1E3A8A
    COLOR_MUTED = RGBColor(71, 85, 105)      # Slate Text #475569
    COLOR_CARD = RGBColor(255, 255, 255)     # White #FFFFFF
    COLOR_BORDER = RGBColor(226, 232, 240)   # Light Border #E2E8F0
    COLOR_GREEN = RGBColor(16, 185, 129)     # Emerald Green #10B981
    COLOR_RED = RGBColor(220, 38, 38)        # Crimson Red #DC2626

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="SocialShield AI"):
        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(11)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_BLUE
        p_c.font.name = "Segoe UI"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = COLOR_NAVY
        p.font.name = "Segoe UI"

        # Accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_BORDER
        line.line.fill.background()

    def add_card(slide, left, top, width, height, title="", items=None, accent_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = COLOR_BORDER
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.3), top + Inches(0.25), width - Inches(0.6), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        if title:
            p_title = tf.paragraphs[0]
            p_title.text = title
            p_title.font.size = Pt(18)
            p_title.font.bold = True
            p_title.font.color.rgb = accent_color if accent_color else COLOR_NAVY
            p_title.font.name = "Segoe UI"
            p_title.space_after = Pt(12)

        if items:
            for item in items:
                p_item = tf.add_paragraph()
                p_item.text = f"•  {item}"
                p_item.font.size = Pt(14)
                p_item.font.color.rgb = COLOR_MUTED
                p_item.font.name = "Segoe UI"
                p_item.space_after = Pt(8)

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Center card
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_CARD
    card1.line.color.rgb = COLOR_BORDER
    card1.line.width = Pt(2)

    tb1 = s1.shapes.add_textbox(Inches(2.0), Inches(1.8), Inches(9.333), Inches(3.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "🛡️  COLLEGE HACKATHON 2026"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_BLUE
    p_badge.font.name = "Segoe UI"
    p_badge.space_after = Pt(14)

    p_t = tf1.add_paragraph()
    p_t.text = "SocialShield AI"
    p_t.font.size = Pt(40)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    p_t.font.name = "Segoe UI"
    p_t.space_after = Pt(10)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Intelligent Fake Social Media Account Detection & Risk Assessment"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = COLOR_MUTED
    p_sub.font.name = "Segoe UI"
    p_sub.space_after = Pt(24)

    p_desc = tf1.add_paragraph()
    p_desc.text = "An AI-powered tool that analyzes public social media profiles in real-time, spots fake accounts, and explains risk scores in simple terms."
    p_desc.font.size = Pt(14)
    p_desc.font.color.rgb = COLOR_MUTED
    p_desc.font.name = "Segoe UI"

    # ==========================================
    # SLIDE 2: The Problem
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "The Problem: Why Fake Accounts Matter", "Background")

    add_card(s2, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="1. Millions of Bots Everywhere",
             items=[
                 "Up to 15% of active accounts on major platforms show automated bot behaviors.",
                 "They manipulate public opinions, artificial follower numbers, and trend hashtags.",
                 "Used for automated cryptocurrency scams and malicious phishing."
             ],
             accent_color=COLOR_RED)

    add_card(s2, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="2. Hard for Humans to Spot",
             items=[
                 "Modern bot accounts use stolen profile photos and copied bios.",
                 "Casual users cannot easily tell which profiles are genuine and which are fake.",
                 "Manual review takes too much time for content moderators."
             ],
             accent_color=COLOR_RED)

    add_card(s2, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="3. 'Black Box' AI Tools",
             items=[
                 "Existing spam checkers only give a 'Yes or No' answer without giving reasons.",
                 "No explanation of why an account was labeled as suspicious.",
                 "High risk of falsely banning innocent human creators."
             ],
             accent_color=COLOR_RED)

    # ==========================================
    # SLIDE 3: The Solution
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Our Solution: SocialShield AI", "Introducing SocialShield AI")

    add_card(s3, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="What is SocialShield AI?",
             items=[
                 "A fast, web-based tool designed to check any social media profile in seconds.",
                 "Works with popular platforms like X (Twitter) and Instagram.",
                 "Provides a transparent Risk Score between 0 and 100.",
                 "Clearly states whether the profile is Genuine or a Potential Fake.",
                 "Explains the exact reasons behind every rating in plain English."
             ],
             accent_color=COLOR_BLUE)

    add_card(s3, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="Core Objectives",
             items=[
                 "🔗 Link-First Inspection: Just paste a public profile URL.",
                 "⚡ Instant Telemetry: Automatically reads followers, posts, bio, and creation date.",
                 "💡 Explainable AI: Shows positive factors and suspicious red flags.",
                 "⚖️ Ethical Decision Support: Assists human moderators without unfair auto-bans.",
                 "📡 Live or Offline: Works with live APIs or in offline manual mode."
             ],
             accent_color=COLOR_GREEN)

    # ==========================================
    # SLIDE 4: How It Works (3 Steps)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "How It Works: 3 Simple Steps", "Workflow")

    add_card(s4, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="Step 1: Paste Link",
             items=[
                 "User pastes any profile link into the search bar.",
                 "Example: https://x.com/elonmusk or https://instagram.com/nasa.",
                 "Our system automatically detects the platform and username handle."
             ],
             accent_color=COLOR_BLUE)

    add_card(s4, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="Step 2: Pull Telemetry",
             items=[
                 "Connects to the SocialCrawl live API gateway in real-time.",
                 "Fetches follower count, following count, total posts, and bio text.",
                 "Checks account creation date and verification badge."
             ],
             accent_color=COLOR_BLUE)

    add_card(s4, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8),
             title="Step 3: AI Verdict",
             items=[
                 "A trained Random Forest model inspects 14 behavioral patterns.",
                 "Computes a calibrated Risk Score from 0 to 100.",
                 "Displays a clear verdict (Green for Genuine, Red for Fake) with bulleted reasons."
             ],
             accent_color=COLOR_GREEN)

    # ==========================================
    # SLIDE 5: What the AI Looks At
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "What the AI Looks At: 14 Behavioral Signals", "Feature Engineering")

    add_card(s5, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="🚩 Red Flag Signals (Increase Risk)",
             items=[
                 "Follower Asymmetry: Following 4,500 accounts but only has 10 followers.",
                 "Unnatural Post Velocity: Publishing 60+ posts every day continuously.",
                 "Brand New Account: Created just 5 to 14 days ago with massive activity.",
                 "Bot Naming Scheme: Usernames with high numbers of trailing digits (user849201).",
                 "Spam Bio Keywords: Promotional phrases like '100x gem', 'follow for follow', 'airdrop link'."
             ],
             accent_color=COLOR_RED)

    add_card(s5, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="✅ Green Flag Signals (Lower Risk)",
             items=[
                 "Established Longevity: Account has existed actively for over 2+ years.",
                 "Balanced Social Graph: Healthy ratio between followers and accounts followed.",
                 "Human Posting Cadence: Normal user pace of 0.2 to 3 posts per day.",
                 "Platform Verification: Holds official verified credentials.",
                 "Descriptive Personal Bio: Coherent personal or professional bio."
             ],
             accent_color=COLOR_GREEN)

    # ==========================================
    # SLIDE 6: Explainable AI
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Explainable AI: Clear Reasons, No Guesswork", "Transparency")

    add_card(s6, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="The 'Why Was It Flagged?' Card",
             items=[
                 "Judges and moderators need to know why an account is marked suspicious.",
                 "Instead of a raw number, we show plain English indicator cards.",
                 "Example: 'Severity: High — Account follows 4,200 people with only 12 followers.'",
                 "Shows mitigating factors so creators are treated fairly."
             ],
             accent_color=COLOR_NAVY)

    add_card(s6, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="4 Simple Risk Tiers",
             items=[
                 "🟢 0 to 29 (Low Risk): Organic, genuine human account. No action needed.",
                 "🟡 30 to 59 (Moderate Risk): Mild anomalies. Worth periodic monitoring.",
                 "🟠 60 to 79 (High Risk): Suspicious behavior. Flagged for human review.",
                 "🔴 80 to 100 (Very High Risk): Strong automated bot or follow-farm traits."
             ],
             accent_color=COLOR_BLUE)

    # ==========================================
    # SLIDE 7: Dataset & Model Performance
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Model Results: 95% Accuracy on Real Data", "Validation & ML")

    add_card(s7, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="Training & Datasets",
             items=[
                 "Algorithm: Scikit-Learn Random Forest Classifier (120 decision trees).",
                 "Trained on real labeled benchmark social account datasets (576 records).",
                 "Evaluated on an independent holdout test dataset (120 records).",
                 "Balanced classes: 50% Genuine Human Profiles vs 50% Fake Spammer Accounts."
             ],
             accent_color=COLOR_NAVY)

    add_card(s7, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="Verified Performance Metrics",
             items=[
                 "🎯 Holdout Test Accuracy: 95.0%",
                 "⚖️ F1-Score: 0.952 (Balanced precision and recall)",
                 "📈 ROC-AUC Score: 0.974 (Outstanding discriminatory power)",
                 "🔄 5-Fold Cross-Validation: 93.2% consistent accuracy",
                 "⚡ Inference Speed: Less than 50 milliseconds per account"
             ],
             accent_color=COLOR_GREEN)

    # ==========================================
    # SLIDE 8: Live Demonstration & Features
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Live Demonstration Walkthrough", "Application Features")

    add_card(s8, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="1. Profile URL Inspector",
             items=[
                 "Paste https://x.com/elonmusk → Shows 240M followers, 4.2 Risk Score (Genuine).",
                 "Paste https://www.instagram.com/nasa/ → Shows 104M followers, Verified Org.",
                 "Click 1-Click Demo Bot → Shows 88.5 Risk Score (Fake Bot) with red alert banner."
             ],
             accent_color=COLOR_BLUE)

    add_card(s8, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="2. Overview Surveillance Dashboard",
             items=[
                 "KPI cards showing Total Accounts Audited and safe vs suspicious percentages.",
                 "Visual breakdown of platforms (X vs Instagram vs Others).",
                 "Risk category distribution charts.",
                 "Live session audit log tracking every account checked today."
             ],
             accent_color=COLOR_BLUE)

    # ==========================================
    # SLIDE 9: Ethical Mandate & Future Scope
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Ethical Principles & Future Vision", "Conclusion")

    add_card(s9, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="Responsible AI & Ethics",
             items=[
                 "Human-in-the-Loop: The tool provides advice — it never bans people autonomously.",
                 "Privacy Compliant: Uses only public profile metrics, no private passwords or DMs.",
                 "Data Transparency: Clearly tags data as 'Live API', 'Manual', or 'Demo'."
             ],
             accent_color=COLOR_NAVY)

    add_card(s9, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8),
             title="Next Steps & Future Roadmap",
             items=[
                 "Chrome Extension: Instantly score profiles directly while scrolling your feed.",
                 "Multi-Language NLP: Detect spam bios in Hindi, Spanish, and Arabic.",
                 "Content Originality: AI check on whether tweet photos are AI-generated deepfakes.",
                 "Thank You! We welcome your questions."
             ],
             accent_color=COLOR_GREEN)

    # Save presentation
    output_path = "SocialShield_AI_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    build_presentation()
