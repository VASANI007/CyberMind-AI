import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

sys.stdout.reconfigure(encoding="utf-8")

prs = Presentation(r"reports/CyberMind AI – Project Review III.pptx")
print(f"Loaded Presentation with {len(prs.slides)} slides.")

# ==============================================================================
# 1. SLIDE 2: Project Overview
# ==============================================================================
slide2 = prs.slides[1]
for shape in slide2.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "02 | 30+ External TI APIs" in p.text:
                p.text = "02 | 13 External APIs & 30+ Services"
                p.font.name = "Arial"
                p.font.size = Pt(13)
                p.font.bold = True
                p.font.color.rgb = RGBColor(0x29, 0x80, 0xB9)
            elif "trained on over 240,000 security samples" in p.text:
                p.text = "•  4 Scikit-Learn Random Forest models trained on 242,341 verified security samples."
            elif "VirusTotal, AbuseIPDB, Google Safe Browsing, & Veriphone" in p.text:
                p.text = "•  Real-time enrichment via 13 APIs: VirusTotal, AbuseIPDB, Google Safe Browsing, Groq, Veriphone, Numverify, Abstract, IPinfo, IPQS, VerificarEmails."

print("Slide 2 updated.")

# ==============================================================================
# 2. SLIDE 3: Review 2 -> Review 3 Progress
# ==============================================================================
slide3 = prs.slides[2]
for shape in slide3.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "30+ Threat Intelligence Services Layer" in p.text:
                p.text = "✔ 13 External APIs & 30+ Threat Intelligence Services Layer"
            elif "Provider-agnostic connectors querying VirusTotal, AbuseIPDB, Veriphone, Google Safe Browsing" in p.text:
                p.text = "    Provider-agnostic connectors querying VirusTotal, AbuseIPDB, Google Safe Browsing, Groq, Veriphone, Numverify, Abstract, IPinfo, IPQS, and VerificarEmails."
            elif "92.32% CV accuracy" in p.text:
                p.text = "    Random Forest models achieving 96.67% CV accuracy (99.40% ROC-AUC) for phishing, malware, & breaches."
            elif "114+ real scan logs" in p.text:
                p.text = "    Live persistence across 15 relational tables with 131 real scan records logged in cybermind.db."

print("Slide 3 updated.")

# ==============================================================================
# 3. SLIDE 6: API & Threat Intelligence Integration (8-Card Layout)
# ==============================================================================
slide6 = prs.slides[5]

# Update top pipeline banner text
for shape in slide6.shapes:
    if shape.has_text_frame and "SERVICES LAYER INTEGRATION PIPELINE" in shape.text:
        shape.text_frame.text = "13 EXTERNAL APIS & 30+ THREAT SERVICES: Scanner Engine ➔ Provider-Agnostic Services Layer (services/) ➔ External TI APIs ➔ Normalized Schema ➔ Risk Engine"
        p = shape.text_frame.paragraphs[0]
        p.font.name = "Arial"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0x29, 0x80, 0xB9)

# Define 8 comprehensive API cards
cards_data = [
    # Row 1
    {
        "title": "VirusTotal API",
        "sub": "70+ AV Engines | services/virustotal_service.py",
        "color": RGBColor(0x29, 0x80, 0xB9),
        "bullets": [
            "Queries 70+ antivirus vendor engines simultaneously.",
            "Extracts detection ratios, engine flags, & reputation score.",
            "Covers URLs, domain reputation, & SHA-256/MD5 hashes."
        ]
    },
    {
        "title": "AbuseIPDB API",
        "sub": "IP Reputation | services/abuseipdb_service.py",
        "color": RGBColor(0xEF, 0x44, 0x44),
        "bullets": [
            "Calculates confidence of abuse score (0–100%).",
            "Retrieves total reported abuse incidents & reporter count.",
            "Checks ISP name, usage type (Datacenter/VPN), & country."
        ]
    },
    {
        "title": "Google Safe Browsing",
        "sub": "Real-Time Blacklist | google_safe_browsing_service.py",
        "color": RGBColor(0x22, 0xC5, 0x5E),
        "bullets": [
            "Lookup against Google's global threat databases v4.",
            "Identifies active malware distribution & deceptive phishing.",
            "Instantly escalates target severity score upon match."
        ]
    },
    {
        "title": "Groq Cloud Generative AI",
        "sub": "Llama-3 70B Engine | modules/ai_assistant.py",
        "color": RGBColor(0x8B, 0x5C, 0xF6),
        "bullets": [
            "Translates complex JSON telemetry in <1.2s latency.",
            "Plain-language threat diagnosis for non-technical stakeholders.",
            "Actionable mitigation steps for SOC analysts & executives."
        ]
    },
    # Row 2
    {
        "title": "Veriphone & Numverify",
        "sub": "Telephony Intel | veriphone & numverify_service.py",
        "color": RGBColor(0x24, 0x35, 0x41),
        "bullets": [
            "Parses international phone numbers to E.164 standard.",
            "Identifies carrier name, line type (Mobile/VoIP/Landline).",
            "Flags disposable VoIP numbers used in phishing & scams."
        ]
    },
    {
        "title": "Abstract IP & Phone APIs",
        "sub": "Telecom & IP Risk | abstract_ip & phone services",
        "color": RGBColor(0x06, 0xB6, 0xD4),
        "bullets": [
            "Deep telecom carrier fraud profiling & country risk scores.",
            "IP security assessment, commercial proxy & VPN flags.",
            "Real-time roaming status & telecom validity verification."
        ]
    },
    {
        "title": "IPinfo & IPQS Services",
        "sub": "Geo & Fraud Scoring | ipinfo_service & ipqs_service.py",
        "color": RGBColor(0x33, 0xB6, 0x7D),
        "bullets": [
            "Provides city, country, & precise latitude/longitude.",
            "Extracts Autonomous System Number (ASN) & org info.",
            "Flags commercial VPNs, open proxies, & Tor exit nodes."
        ]
    },
    {
        "title": "VerificarEmails & WHOIS",
        "sub": "Email & Domain | verificaremails, whois, dns_service",
        "color": RGBColor(0xF5, 0x9E, 0x0B),
        "bullets": [
            "Deep email verification, disposable domain & SMTP handshake.",
            "Executes RDAP/WHOIS for registrar & creation/expiry dates.",
            "Validates DNSSEC, MX records, & crt.sh CT certificate logs."
        ]
    }
]

# We need to replace the old 6 card shapes with 8 card shapes
# Old shape indices on Slide 6:
# Shapes 8, 9 (Box 1)
# Shapes 10, 11 (Box 2)
# Shapes 12, 13 (Box 3)
# Shapes 14, 15 (Box 4)
# Shapes 16, 17 (Box 5)
# Shapes 18, 19 (Box 6)

old_card_shape_indices = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

# Delete old card shapes in reverse order
for s_idx in sorted(old_card_shape_indices, reverse=True):
    sp = slide6.shapes[s_idx]._element
    sp.getparent().remove(sp)

# Layout for 8 cards: 4 columns x 2 rows
card_width = 2720000
card_height = 1650000
col_gap = 170000
row_gap = 100000

start_left = 300000
row1_top = 1830000
row2_top = 3580000

for i, c_data in enumerate(cards_data):
    col = i % 4
    row = i // 4
    left = start_left + col * (card_width + col_gap)
    top = row1_top if row == 0 else row2_top
    
    # 1. Background rounded rectangle
    rect = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_width, card_height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
    rect.line.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    rect.line.width = Pt(1)
    
    # 2. Text Box inside
    tb = slide6.shapes.add_textbox(left + 100000, top + 50000, card_width - 180000, card_height - 90000)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    
    # Title
    p_title = tf.paragraphs[0]
    p_title.text = c_data["title"]
    p_title.font.name = "Arial"
    p_title.font.size = Pt(12)
    p_title.font.bold = True
    p_title.font.color.rgb = c_data["color"]
    p_title.space_after = Pt(1)
    
    # Subtitle
    p_sub = tf.add_paragraph()
    p_sub.text = c_data["sub"]
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(8.5)
    p_sub.font.italic = True
    p_sub.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    p_sub.space_after = Pt(4)
    
    # Bullets
    for b_text in c_data["bullets"]:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b_text}"
        p_b.font.name = "Arial"
        p_b.font.size = Pt(8.5)
        p_b.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        p_b.space_after = Pt(2)

print("Slide 6 updated with 8 comprehensive API cards covering all 13 APIs.")

# ==============================================================================
# 4. SLIDE 7: Machine Learning Implementation
# ==============================================================================
slide7 = prs.slides[6]
for shape in slide7.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "OVERALL SYSTEM ML PERFORMANCE" in p.text:
                p.text = "OVERALL SYSTEM ML PERFORMANCE (5-Fold Stratified CV):\n• Accuracy: 96.67%  |  Precision: 96.84%  |  Recall: 96.67%\n• F1-Score: 96.63%  |  ROC-AUC: 0.9940  |  Ensemble: Random Forest"
            elif "Online-Valid Phishing Model" in p.text:
                p.text = "✔ Online-Valid Phishing Model (online_valid_model.pkl)\n5,810 samples, 10,080 features | Multi-Class Target Classifier\n• Accuracy: 90.26% | Precision: 90.79% | F1: 90.19% | ROC-AUC: 0.9777 (PayPal, Blizzard, Orkut, Sulake, Other)"
            elif "Data Breaches Model (breaches_model.pkl)" in p.text:
                p.text = "✔ Data Breaches Model (breaches_model.pkl)\n520 samples, 6 features | 5-Class Root-Cause Classifier\n• Accuracy: 98.85% | Precision: 98.88% | F1: 98.75% | ROC-AUC: 1.0000"

print("Slide 7 updated with actual 96.67% ML metrics.")

# ==============================================================================
# 5. SLIDE 9: Database Implementation
# ==============================================================================
slide9 = prs.slides[8]
for shape in slide9.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "114+ REAL SCAN RECORDS LOGGED" in p.text:
                p.text = "131 REAL SCAN RECORDS LOGGED"
            elif "• Performance: 11 B-Tree indexes on scan_time, risk_level, target" in p.text:
                p.text = "• support_tickets: 9 customer incident & technical support records\n• Performance: 9 B-Tree indexes on scan_time, risk_level, target"

print("Slide 9 updated with 131 real scan records and support_tickets table.")

# ==============================================================================
# 6. SLIDE 10: Working Prototype & UI Dashboard
# ==============================================================================
slide10 = prs.slides[9]
for shape in slide10.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "Streamlit Main Dashboard: Total Scans (25)" in p.text:
                p.text = "✔ Streamlit Main Dashboard: 131 Total Scans, 50 Safe (38.2%), 35 Threats Detected, 46 Suspicious/Medium, 38/100 Avg Risk Score, and 10 Analysis Modules"
            elif "System ML Accuracy (94.0%)" in p.text:
                p.text = "✔ Analytics & Threat Intelligence Panel: System ML Accuracy (96.7%), 7-day scan trendlines, risk score trajectory graph, and live geographical threat map"

print("Slide 10 updated with exact live dashboard data.")

# ==============================================================================
# 7. SLIDE 14: Current Project Progress & Roadmap
# ==============================================================================
slide14 = prs.slides[13]
for shape in slide14.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if p.text.strip() == "68%":
                p.text = "90%"
            elif p.text.strip() == "92.3%":
                p.text = "96.7%"
            elif "VirusTotal, AbuseIPDB, Veriphone, Google Safe Browsing, IPinfo, and IPQS." in p.text:
                p.text = "    VirusTotal, AbuseIPDB, Google Safe Browsing, Groq, Veriphone, Numverify, Abstract, IPinfo, IPQS, and VerificarEmails."
            elif "92.32% CV accuracy across 240,000+ samples." in p.text:
                p.text = "    Random Forest models achieving 96.67% CV accuracy (99.40% ROC-AUC) across 242,341 samples."

print("Slide 14 updated with 90% implementation and 96.7% ML accuracy.")

# Save updated presentation
prs.save(r"reports/CyberMind AI – Project Review III.pptx")
print("Saved updated Presentation: reports/CyberMind AI – Project Review III.pptx successfully!")
