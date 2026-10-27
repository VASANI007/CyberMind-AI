import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

sys.stdout.reconfigure(encoding="utf-8")

input_pptx = r"reports/CyberMind AI – Project Review III.pptx"
output_pptx = r"reports/CyberMind AI – Project Review IV.pptx"

prs = Presentation(input_pptx)
print(f"Loaded base presentation with {len(prs.slides)} slides.")

# Color constants matching Review 3 exactly
C_DARK_NAVY  = RGBColor(0x24, 0x35, 0x41)
C_TITLE_TEXT = RGBColor(0x0F, 0x17, 0x2A)
C_MUTED_TEXT = RGBColor(0x64, 0x74, 0x8B)
C_BODY_TEXT  = RGBColor(0x1E, 0x29, 0x3B)
C_CARD_BG    = RGBColor(0xF8, 0xFA, 0xFC)
C_CARD_BORDER= RGBColor(0xCB, 0xD5, 0xE1)
C_BLUE       = RGBColor(0x29, 0x80, 0xB9)
C_GREEN      = RGBColor(0x33, 0xB6, 0x7D)
C_AMBER      = RGBColor(0xF5, 0x9E, 0x0B)
C_RED        = RGBColor(0xEF, 0x44, 0x44)
C_PURPLE     = RGBColor(0x8B, 0x5C, 0xF6)
C_CYAN       = RGBColor(0x06, 0xB6, 0xD4)
C_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
C_ROW_ALT    = RGBColor(0xF1, 0xF5, 0xF9)

# Adjust slide count to exactly 14
while len(prs.slides) > 14:
    rId = prs.slides._sldIdLst[-1].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[-1]

print(f"Adjusted to exactly {len(prs.slides)} slides.")

def clear_slide_content(slide):
    to_delete = []
    for shape in slide.shapes:
        top = shape.top
        if top >= 6180000: # footer elements
            continue
        if shape.name in ["TextBox 1", "Title 1"] and top < 1000000:
            continue
        if shape.name in ["Rectangle 2"] and top < 1100000:
            continue
        to_delete.append(shape)
    for shape in to_delete:
        sp = shape._element
        sp.getparent().remove(sp)

def set_slide_header(slide, title_text, slide_num):
    found_title = False
    for shape in slide.shapes:
        if shape.has_text_frame and shape.top < 1000000 and shape.left < 500000:
            tf = shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = "Arial"
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = C_TITLE_TEXT
            found_title = True
            break
            
    if not found_title:
        tb = slide.shapes.add_textbox(0, 0, 10500000, 930000)
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = C_TITLE_TEXT
        
        has_rect = False
        for shape in slide.shapes:
            if shape.name == "Rectangle 2" or (shape.top > 900000 and shape.top < 1000000 and shape.left == 0):
                has_rect = True
                break
        if not has_rect:
            rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 931985, 2479431, 25000)
            rect.fill.solid()
            rect.fill.fore_color.rgb = C_DARK_NAVY
            rect.line.fill.background()
            
    for shape in slide.shapes:
        if shape.has_text_frame and shape.top >= 6180000 and shape.left > 10000000:
            tf = shape.text_frame
            p = tf.paragraphs[0]
            p.text = str(slide_num)
            p.font.name = "Arial"
            p.font.size = Pt(32)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            break

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_pill(slide, left, top, width, height, text, bg_color=C_BLUE, text_color=C_WHITE, font_size=11):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.bold = True
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return shape

def add_text_box(slide, left, top, width, height, lines_data):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    
    for idx, item in enumerate(lines_data):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = item.get('text', '')
        p.font.name = "Arial"
        p.font.size = Pt(item.get('size', 11))
        p.font.bold = item.get('bold', False)
        p.font.italic = item.get('italic', False)
        p.font.color.rgb = item.get('color', C_BODY_TEXT)
        if 'space_after' in item:
            p.space_after = Pt(item['space_after'])
        if 'align' in item:
            p.alignment = item['align']
    return tb

def add_table_shape(slide, left, top, width, height, headers, rows_data, col_widths=None, font_size=10):
    rows = len(rows_data) + 1
    cols = len(headers)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    if col_widths and len(col_widths) == cols:
        for idx, w in enumerate(col_widths):
            table.columns[idx].width = w
            
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_DARK_NAVY
        cell.text_frame.margin_left = cell.text_frame.margin_right = Pt(5)
        cell.text_frame.margin_top = cell.text_frame.margin_bottom = Pt(4)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = "Arial"
        p.font.size = Pt(font_size + 0.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER
        
    # Data Rows
    for r_idx, r_data in enumerate(rows_data):
        row_num = r_idx + 1
        bg = C_WHITE if r_idx % 2 == 0 else C_ROW_ALT
        for c_idx, val in enumerate(r_data):
            cell = table.cell(row_num, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.text_frame.margin_left = cell.text_frame.margin_right = Pt(5)
            cell.text_frame.margin_top = cell.text_frame.margin_bottom = Pt(3)
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.name = "Arial"
            p.font.size = Pt(font_size)
            p.font.color.rgb = C_BODY_TEXT
            if "Pass" in str(val) or "Safe" in str(val) or "100.0%" in str(val):
                p.font.bold = True
                p.font.color.rgb = C_GREEN
            elif "Critical" in str(val) or "Malware" in str(val):
                p.font.bold = True
                p.font.color.rgb = C_RED
            elif "High" in str(val) or "Suspicious" in str(val):
                p.font.bold = True
                p.font.color.rgb = C_AMBER
            elif c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_DARK_NAVY
    return table_shape

# ==============================================================================
# SLIDE 1: TITLE SLIDE
# ==============================================================================
slide1 = prs.slides[0]
for shape in slide1.shapes:
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            if "PROJECT REVIEW" in p.text:
                p.text = "PROJECT REVIEW – IV"
                p.font.bold = True
            elif "Under the Guidance of" in p.text:
                p.text = "Under the Guidance of:\nMs. Ritika Savaliya\nSOCCA – Silver Oak University | M.Sc. Data Science"

print("Slide 1 updated for Review IV.")

# ==============================================================================
# SLIDE 2: PROJECT OVERVIEW & FINAL STATUS
# ==============================================================================
slide2 = prs.slides[1]
clear_slide_content(slide2)
set_slide_header(slide2, "Project Overview & Final Status", 2)

# Top summary card
add_card(slide2, 300000, 1150000, 11592000, 1000000)
add_text_box(slide2, 450000, 1200000, 11292000, 900000, [
    {
        'text': "CyberMind AI is an enterprise-grade Cyber Threat Intelligence (CTI) and Malware Analysis Platform consolidating multi-vector security telemetry into a unified single pane of glass. It bridges rule-based heuristics, 4 supervised Random Forest classifiers (96.67% accuracy), and Groq Llama-3 70B AI explanations to produce a standardized 0–100 cyber risk score and automated executive mitigation reports.",
        'size': 13.5,
        'color': C_BODY_TEXT
    }
])

# 4 Pillars Grid
col_w = 2720000
col_gap = 237000
start_l = 300000
grid_top = 2300000
card_h = 3700000

pillars = [
    {
        "num": "01 | 10 Specialized Scanners",
        "sub": "MODULAR MULTI-VECTOR ENGINES",
        "color": C_BLUE,
        "bullets": [
            "Full-spectrum threat surface coverage across Web, Network, Files, and Endpoints.",
            "Dedicated modules for URL, Website, Domain, Email, IP, Phone, File/PE, and QR.",
            "Universal Auto-Scanner with intelligent regex input inference & automated dispatch."
        ]
    },
    {
        "num": "02 | 13 External APIs & 30+ Services",
        "sub": "AGGREGATED THREAT FEEDS",
        "color": C_GREEN,
        "bullets": [
            "Real-time enrichment via 13 APIs: VirusTotal, AbuseIPDB, Google Safe Browsing, Groq, Veriphone, Numverify, Abstract, IPinfo, IPQS, VerificarEmails.",
            "Deep IP geolocation, ASN lookup, and commercial proxy / Tor exit node detection.",
            "Strict 5s async timeouts with resilient local deterministic heuristic fallbacks."
        ]
    },
    {
        "num": "03 | Machine Learning (96.7% Acc)",
        "sub": "SUPERVISED THREAT CLASSIFIERS",
        "color": C_DARK_NAVY,
        "bullets": [
            "4 Scikit-Learn Random Forest models trained on 242,341 verified security samples.",
            "50 lexical and structural URL features extracted in real time (<18.5ms latency).",
            "PE header anomaly detection, section entropy, and hex signature analysis."
        ]
    },
    {
        "num": "04 | Generative AI & Reports",
        "sub": "GROQ LLAMA-3 70B SYNTHESIS",
        "color": C_AMBER,
        "bullets": [
            "Translates complex JSON telemetry into concise 3-sentence executive summaries (<1.2s).",
            "Tailored defensive recommendations for both SOC analysts and executive leaders.",
            "Automated branded PDF & JSON security report generation with MITRE ATT&CK mapping."
        ]
    }
]

for idx, p_info in enumerate(pillars):
    c_left = start_l + idx * (col_w + col_gap)
    add_card(slide2, c_left, grid_top, col_w, card_h)
    add_pill(slide2, c_left + 120000, grid_top + 150000, col_w - 240000, 600000, p_info["num"], p_info["color"], font_size=12)
    
    lines = [{'text': p_info["sub"], 'size': 10, 'bold': True, 'color': C_MUTED_TEXT, 'space_after': 6}]
    for b in p_info["bullets"]:
        lines.append({'text': f"•  {b}", 'size': 11, 'color': C_BODY_TEXT, 'space_after': 5})
    add_text_box(slide2, c_left + 140000, grid_top + 850000, col_w - 280000, card_h - 950000, lines)

print("Slide 2 generated.")

# ==============================================================================
# SLIDE 3: FINAL SYSTEM ARCHITECTURE
# ==============================================================================
slide3 = prs.slides[2]
clear_slide_content(slide3)
set_slide_header(slide3, "Final System Architecture", 3)

# Subtitle Pill Banner
add_pill(slide3, 300000, 1100000, 11592000, 420000, "DECOUPLED 3-TIER ENTERPRISE ARCHITECTURE & END-TO-END PROCESSING PIPELINE", C_DARK_NAVY, font_size=12)

# 6 Horizontal Workflow Step Cards
step_w = 1780000
step_gap = 182000
step_top = 1650000
step_h = 2400000

steps_data = [
    {"num": "STEP 1", "title": "Target Input", "desc": "Analyst submits URL, Domain, IP, Email, Phone, File, or QR code via Streamlit / API.", "color": C_BLUE},
    {"num": "STEP 2", "title": "Validation", "desc": "core/validator.py executes schema sanitization, regex matching, and boundary checks.", "color": C_CYAN},
    {"num": "STEP 3", "title": "Scanner Engine", "desc": "modules/scanner_engine.py routes target; executes 30+ services across 13 TI APIs concurrently.", "color": C_GREEN},
    {"num": "STEP 4", "title": "ML Inference", "desc": "4 Random Forest models extract 50 features and calculate class probabilities in <18.5ms.", "color": C_PURPLE},
    {"num": "STEP 5", "title": "Risk Engine", "desc": "Weighted fusion: Score = 0.45*API + 0.35*ML + 0.20*Heuristics with critical overrides.", "color": C_AMBER},
    {"num": "STEP 6", "title": "AI & Reports", "desc": "Groq Llama-3 70B synthesizes executive diagnosis; logged to cybermind.db & exported to PDF.", "color": C_RED},
]

for idx, s_info in enumerate(steps_data):
    s_left = 300000 + idx * (step_w + step_gap)
    add_card(slide3, s_left, step_top, step_w, step_h)
    add_pill(slide3, s_left + 100000, step_top + 120000, step_w - 200000, 360000, s_info["num"], s_info["color"], font_size=11)
    add_text_box(slide3, s_left + 100000, step_top + 550000, step_w - 200000, step_h - 600000, [
        {'text': s_info["title"], 'size': 12, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 4},
        {'text': s_info["desc"], 'size': 10, 'color': C_BODY_TEXT}
    ])

# 3 Bottom Architecture Highlights
b_card_w = 3690000
b_card_gap = 260000
b_top = 4200000
b_h = 1800000

b_cards = [
    {
        "title": "✔ Decoupled 3-Tier Layering",
        "desc": "Presentation (Streamlit), Application (Services/Modules/ML), and Storage (SQLite) are strictly isolated for zero coupling, modular testability, and enterprise maintainability.",
        "color": C_BLUE
    },
    {
        "title": "✔ Provider-Agnostic Services",
        "desc": "All 13 external APIs are accessed via modular service wrappers in services/, ensuring core security algorithms remain completely independent of external vendor changes.",
        "color": C_GREEN
    },
    {
        "title": "✔ Zero-Downtime Offline Fallbacks",
        "desc": "Every external connector implements graceful local heuristic fallbacks with strict 5-second asynchronous timeouts, guaranteeing 100% platform availability offline.",
        "color": C_AMBER
    }
]

for idx, bc in enumerate(b_cards):
    bc_left = 300000 + idx * (b_card_w + b_card_gap)
    add_card(slide3, bc_left, b_top, b_card_w, b_h)
    add_text_box(slide3, bc_left + 180000, b_top + 160000, b_card_w - 360000, b_h - 320000, [
        {'text': bc["title"], 'size': 13, 'bold': True, 'color': bc["color"], 'space_after': 6},
        {'text': bc["desc"], 'size': 11, 'color': C_BODY_TEXT}
    ])

print("Slide 3 generated.")

# ==============================================================================
# SLIDE 4: FINAL MODULE IMPLEMENTATION
# ==============================================================================
slide4 = prs.slides[3]
clear_slide_content(slide4)
set_slide_header(slide4, "Final Module Implementation", 4)

add_pill(slide4, 300000, 1100000, 11592000, 380000, "VERIFIED STATUS OF ALL 10 CYBER THREAT INTELLIGENCE SCANNERS (100% PASS RATE)", C_DARK_NAVY, font_size=12)

headers4 = ["Scanner Module", "Target Vector", "Key Capabilities & Core Demonstrable Features", "Implementation Status"]
rows4 = [
    ["1. URL Scanner", "URLs & Web Links", "50 lexical features, Shannon entropy, redirect tracing, Google Safe Browsing / VirusTotal", "Verified Pass ✔"],
    ["2. Website Scanner", "Web Applications", "SSL/TLS cert chain audit, cipher security, security headers (CSP/HSTS), tech stack fingerprinting", "Verified Pass ✔"],
    ["3. Domain Scanner", "Domains & DNS", "WHOIS registry audit, creation/expiration dates, DNS A/MX/NS resolution, DNSSEC validation", "Verified Pass ✔"],
    ["4. Email Scanner", "Email Deliverability", "MX host resolution, SPF/DKIM/DMARC records audit, disposable burner domain blocklist", "Verified Pass ✔"],
    ["5. IP Scanner", "IP Addresses & ASNs", "AbuseIPDB reputation (0-100%), IPinfo geo-coordinates, ASN lookup, Tor exit node detection", "Verified Pass ✔"],
    ["6. Phone Threat Intel", "Telephony Vectors", "International E.164 parsing, Veriphone carrier identification, line type (VoIP/Mobile/Landline)", "Verified Pass ✔"],
    ["7. File/PE Malware", "Binaries & Static Files", "MD5/SHA-256 hash lookup, PE section entropy, header anomalies, hex signatures detection", "Verified Pass ✔"],
    ["8. QR Code Scanner", "QR Payloads / Quishing", "Direct image payload decoding, UPI payment URI parameter validation, malicious redirect check", "Verified Pass ✔"],
    ["9. Device Security", "Host Hardening", "Local OS hardening audit, open TCP port scan, Windows Firewall status, Windows Defender state", "Verified Pass ✔"],
    ["10. Universal Scanner", "Multi-Vector Auto-Route", "Intelligent regex input inference auto-routing to URL, Domain, IP, Email, or File scanner", "Verified Pass ✔"],
]
col_w4 = [Inches(2.2), Inches(1.8), Inches(7.0), Inches(1.7)]
add_table_shape(slide4, 300000, 1550000, 11592000, 4400000, headers4, rows4, col_widths=col_w4, font_size=10)

print("Slide 4 generated.")

# ==============================================================================
# SLIDE 5: ACTUAL UI & DASHBOARD
# ==============================================================================
slide5 = prs.slides[4]
clear_slide_content(slide5)
set_slide_header(slide5, "Actual UI & Dashboard Architecture", 5)

add_pill(slide5, 300000, 1100000, 11592000, 380000, "PRODUCTION STREAMLIT INTERFACE & CYBER THREAT TELEMETRY VISUALIZATION", C_DARK_NAVY, font_size=12)

# 4 UI Feature Cards
ui_cards = [
    {
        "title": "01 | Executive Security Dashboard",
        "sub": "REAL-TIME TELEMETRY HUD & METRICS",
        "color": C_BLUE,
        "bullets": [
            "Futuristic top telemetry HUD: Live SQLite DB status, 96.7% accuracy indicator, active clock.",
            "4 Core KPI metric cards: System Accuracy (96.7%), Total Threat Scans (176), Malicious Elements (38), Avg Threat Score (32.1).",
            "Real-time scan stream table with one-click re-audit drawer and floating AI assistant."
        ]
    },
    {
        "title": "02 | Multi-Vector Scanner Workspace",
        "sub": "INTERACTIVE SCANNER INTERFACE",
        "color": C_GREEN,
        "bullets": [
            "Intuitive scanning input with quick 1-click example pill buttons for rapid testing.",
            "Dynamic client-side error validation highlighting malformed targets instantly.",
            "Asynchronous animated scanning spinner providing clear multi-stage telemetry progress."
        ]
    },
    {
        "title": "03 | Analytics & Global Threat Map",
        "sub": "INTERACTIVE PLOTLY DATA VISUALIZATION",
        "color": C_PURPLE,
        "bullets": [
            "Interactive 7/30/90-day scan volume trends and risk score progression charts.",
            "Donut breakdown chart: Safe (70), Medium (49), High (22), Low (19), Critical (16).",
            "Interactive Plotly Scattergeo threat map plotting geolocation of scanned IPs/domains."
        ]
    },
    {
        "title": "04 | Historical Audit & Reporting",
        "sub": "COMPLIANCE & FORENSIC EXPORTS",
        "color": C_AMBER,
        "bullets": [
            "Full paginated search and multi-filter audit table across all 176 SQLite records.",
            "One-click scan re-hydration restoring complete historical analysis in milliseconds.",
            "Automated branded PDF security reports with MITRE ATT&CK matrix and JSON export."
        ]
    }
]

u_w = 5650000
u_gap = 292000
u_top1 = 1600000
u_top2 = 3850000
u_h = 2100000

for idx, u_info in enumerate(ui_cards):
    col = idx % 2
    row = idx // 2
    c_left = 300000 + col * (u_w + u_gap)
    c_top = u_top1 if row == 0 else u_top2
    
    add_card(slide5, c_left, c_top, u_w, u_h)
    add_pill(slide5, c_left + 150000, c_top + 140000, u_w - 300000, 420000, u_info["title"], u_info["color"], font_size=12)
    
    lines = [{'text': u_info["sub"], 'size': 10, 'bold': True, 'color': C_MUTED_TEXT, 'space_after': 4}]
    for b in u_info["bullets"]:
        lines.append({'text': f"•  {b}", 'size': 11, 'color': C_BODY_TEXT, 'space_after': 4})
    add_text_box(slide5, c_left + 160000, c_top + 650000, u_w - 320000, u_h - 750000, lines)

print("Slide 5 generated.")

# ==============================================================================
# SLIDE 6: LIVE SCAN DEMONSTRATION
# ==============================================================================
slide6 = prs.slides[5]
clear_slide_content(slide6)
set_slide_header(slide6, "Live Scan Demonstration", 6)

add_pill(slide6, 300000, 1100000, 11592000, 380000, "STEP-BY-STEP THREAT ANALYSIS LIFECYCLE (VERIFIED LIVE DEMO EXECUTION)", C_DARK_NAVY, font_size=12)

stages = [
    {
        "step": "STAGE 1",
        "title": "Target Input Entry",
        "color": C_BLUE,
        "detail": "Analyst enters target (e.g. testsafebrowsing.appspot.com/s/malware.html or 8.8.8.8) via Universal Scan or dedicated scanner pane."
    },
    {
        "step": "STAGE 2",
        "title": "Sanitization & Validation",
        "color": C_CYAN,
        "detail": "core/validator.py sanitizes input, validates regex patterns, strips malicious injection sequences, and extracts host/domain entities."
    },
    {
        "step": "STAGE 3",
        "title": "Parallel TI & ML Inference",
        "color": C_GREEN,
        "detail": "Services layer queries VirusTotal (70+ engines), AbuseIPDB, and WHOIS while the Random Forest classifier extracts 50 URL features in <18.5ms."
    },
    {
        "step": "STAGE 4",
        "title": "Unified Risk Score Synthesis",
        "color": C_AMBER,
        "detail": "modules/risk_engine.py applies mathematical weighting (0.45*API + 0.35*ML + 0.20*Heuristics); triggers Critical Override on malware match."
    },
    {
        "step": "STAGE 5",
        "title": "AI Diagnosis & Report Export",
        "color": C_RED,
        "detail": "Groq Llama-3 70B produces plain-English executive summary, analyst mitigation directives (iptables/DNS sinkholing), logs to SQLite, and exports PDF."
    }
]

st_w = 2170000
st_gap = 185000
st_top = 1650000
st_h = 4300000

for idx, st_data in enumerate(stages):
    st_left = 300000 + idx * (st_w + st_gap)
    add_card(slide6, st_left, st_top, st_w, st_h)
    add_pill(slide6, st_left + 100000, st_top + 140000, st_w - 200000, 420000, st_data["step"], st_data["color"], font_size=12)
    
    add_text_box(slide6, st_left + 120000, st_top + 680000, st_w - 240000, st_h - 800000, [
        {'text': st_data["title"], 'size': 13, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 10},
        {'text': st_data["detail"], 'size': 11, 'color': C_BODY_TEXT, 'space_after': 8}
    ])

print("Slide 6 generated.")

# ==============================================================================
# SLIDE 7: REAL TEST CASES & RESULT ANALYSIS
# ==============================================================================
slide7 = prs.slides[6]
clear_slide_content(slide7)
set_slide_header(slide7, "Real Test Cases & Result Analysis", 7)

add_pill(slide7, 300000, 1100000, 11592000, 380000, "EMPIRICAL SYSTEM VALIDATION ACROSS CONTRASTING BENIGN & WEAPONIZED TEST TARGETS", C_DARK_NAVY, font_size=12)

headers7 = ["Target Input", "Vector", "Expected Classification", "Actual Live Scan Result", "Unified Risk", "Severity Band", "Status"]
rows7 = [
    ["https://example.com", "URL / Web", "Legitimate Web Target", "Clean across 70+ engines, Valid SSL cert", "8.0 / 100", "Safe 🟢", "Passed ✔"],
    ["testsafebrowsing.appspot.com", "URL / Phishing", "Known Security Phishing Test", "Flagged by Google Safe Browsing & VirusTotal", "100.0 / 100", "Critical 🔴", "Passed ✔"],
    ["phishing@malicious.com", "Email / Deliverability", "High Risk / Burner Email", "Disposable burner domain detected, No active MX", "80.0 / 100", "High 🟠", "Passed ✔"],
    ["8.8.8.8 (Google DNS)", "IP Address", "Trusted Anycast Public DNS", "Verified Clean, 0% AbuseIPDB confidence score", "10.0 / 100", "Safe 🟢", "Passed ✔"],
    ["185.220.101.1", "IP Address", "Tor Exit Node / Anonymizer", "Flagged in AbuseIPDB database & Tor directory", "85.0 / 100", "Critical 🔴", "Passed ✔"],
    ["sample_document.pdf", "File / Static", "Benign Clean Document", "Normal Shannon entropy (<6.5), Clean headers", "5.0 / 100", "Safe 🟢", "Passed ✔"],
]
col_w7 = [Inches(2.4), Inches(1.4), Inches(2.1), Inches(3.2), Inches(1.1), Inches(1.2), Inches(1.2)]
add_table_shape(slide7, 300000, 1550000, 11592000, 3600000, headers7, rows7, col_widths=col_w7, font_size=10)

# Bottom Key Findings Card
add_card(slide7, 300000, 5300000, 11592000, 750000)
add_text_box(slide7, 450000, 5380000, 11292000, 600000, [
    {'text': "Key Empirical Findings:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "• Zero false positives observed across legitimate baseline domains, ensuring high operational fidelity for SOC analysts.", 'size': 10.5, 'color': C_BODY_TEXT},
    {'text': "• Critical Override logic reliably escalated weaponized threat feeds to 90–100 risk score, bypassing intermediate benign weights.", 'size': 10.5, 'color': C_BODY_TEXT}
])

print("Slide 7 generated.")

# ==============================================================================
# SLIDE 8: MACHINE LEARNING EVALUATION
# ==============================================================================
slide8 = prs.slides[7]
clear_slide_content(slide8)
set_slide_header(slide8, "Machine Learning Evaluation", 8)

add_pill(slide8, 300000, 1100000, 11592000, 380000, "EMPIRICAL MODEL BENCHMARKS (cybermind_metrics.json — 242,341 TOTAL SAMPLES)", C_DARK_NAVY, font_size=12)

headers8 = ["Model Name", "Base Dataset & Samples", "Task Classification", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
rows8 = [
    ["1. PhiUSIIL Phishing URL", "234,987 samples, 50 features", "Binary Classification", "100.0% (CV) / 94.5% (Feed)", "100.0%", "100.0%", "100.0%", "1.0000"],
    ["2. File Signatures PE Risk", "1,024 samples, 9 features", "Multi-Class Risk", "97.56%", "97.67%", "97.56%", "97.57%", "0.9985"],
    ["3. Online-Valid Target Brand", "5,810 samples, 10,080 features", "Multi-Class Brand Target", "90.26%", "90.79%", "90.26%", "90.19%", "0.9777"],
    ["4. Data Breach Root-Cause", "520 samples, 6 features", "5-Class Root-Cause", "98.85%", "98.88%", "98.85%", "98.75%", "1.0000"],
]
col_w8 = [Inches(2.2), Inches(2.2), Inches(1.8), Inches(1.8), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1)]
add_table_shape(slide8, 300000, 1550000, 11592000, 2700000, headers8, rows8, col_widths=col_w8, font_size=10)

# Bottom 3 ML Summary Cards
ml_cards = [
    {
        "title": "Overall System Accuracy: 96.67%",
        "sub": "5-FOLD STRATIFIED CROSS-VALIDATION",
        "desc": "Tested across 242,341 verified security samples combining phishing URLs, static PE binaries, brand targets, and database breach incidents.",
        "color": C_BLUE
    },
    {
        "title": "Overall ROC-AUC Score: 0.9940",
        "sub": "HIGH DISCRIMINATION THRESHOLD",
        "desc": "Demonstrates near-perfect true positive vs. false positive separation, ensuring dependable probability calibration in the Unified Risk Engine.",
        "color": C_GREEN
    },
    {
        "title": "Inference Latency: <18.5 ms",
        "sub": "SUB-SECOND HIGH THROUGHPUT",
        "desc": "Pre-trained models loaded via thread-safe singleton cache in ml/model_loader.py, enabling real-time inline evaluation without UI bottleneck.",
        "color": C_PURPLE
    }
]

ml_w = 3690000
ml_gap = 260000
ml_top = 4450000
ml_h = 1550000

for idx, mc in enumerate(ml_cards):
    mc_left = 300000 + idx * (ml_w + ml_gap)
    add_card(slide8, mc_left, ml_top, ml_w, ml_h)
    add_text_box(slide8, mc_left + 160000, ml_top + 140000, ml_w - 320000, ml_h - 260000, [
        {'text': mc["title"], 'size': 12.5, 'bold': True, 'color': mc["color"], 'space_after': 3},
        {'text': mc["sub"], 'size': 9, 'bold': True, 'color': C_MUTED_TEXT, 'space_after': 4},
        {'text': mc["desc"], 'size': 10.5, 'color': C_BODY_TEXT}
    ])

print("Slide 8 generated.")

# ==============================================================================
# SLIDE 9: FINAL TESTING & QA RESULTS
# ==============================================================================
slide9 = prs.slides[8]
clear_slide_content(slide9)
set_slide_header(slide9, "Final Testing & QA Results", 9)

# 4 Metric Pills Strip
pill_w = 2720000
pill_gap = 237000
pill_top = 1100000

qa_metrics = [
    ("156 / 156 Passed", "100% Pass Rate", C_GREEN),
    ("8.42 Seconds", "Suite Duration", C_BLUE),
    ("16 Test Files", "tests/ Directory", C_DARK_NAVY),
    ("10 / 10 Healthy", "Manager Diagnostic", C_AMBER)
]

for idx, (m_val, m_lbl, m_col) in enumerate(qa_metrics):
    p_left = 300000 + idx * (pill_w + pill_gap)
    add_pill(slide9, p_left, pill_top, pill_w, 480000, f"{m_val} ({m_lbl})", m_col, font_size=11)

# 4 Testing Category Cards
qa_categories = [
    {
        "title": "1. Scanner & Module Functional Tests",
        "files": "test_modules.py & test_universal_scan.py",
        "bullets": [
            "Validates parameter parsing, routing, and return payload structure across all 10 specialized scanners.",
            "Asserts Universal Scanner input classifier auto-detection for emails, IPs, URLs, domains, and hashes."
        ]
    },
    {
        "title": "2. External API Fallback & Timeout Tests",
        "files": "test_api.py & test_services.py",
        "bullets": [
            "Enforces 5-second asynchronous timeouts across all external threat intelligence service connectors.",
            "Validates deterministic local heuristic fallbacks when third-party APIs return 429 rate-limit or 503."
        ]
    },
    {
        "title": "3. Machine Learning Inference & Array Tests",
        "files": "test_ml.py & test_new_ml.py",
        "bullets": [
            "Asserts 50-feature array shapes and normalization bounds generated by feature_engineering.py.",
            "Verifies probability calibration and thread-safe singleton model deserialization in model_loader.py."
        ]
    },
    {
        "title": "4. Database Integrity & Security Sanitization",
        "files": "test_database.py, test_schemas.py & test_utils.py",
        "bullets": [
            "Asserts SQLite schema migrations, foreign key cascading, and multi-thread safe database transactions.",
            "Rigorous testing against malformed inputs, SQL injection strings, and cross-site scripting (XSS) payloads."
        ]
    }
]

q_w = 5650000
q_gap = 292000
q_top1 = 1750000
q_top2 = 3850000
q_h = 2050000

for idx, q_info in enumerate(qa_categories):
    col = idx % 2
    row = idx // 2
    c_left = 300000 + col * (q_w + q_gap)
    c_top = q_top1 if row == 0 else q_top2
    
    add_card(slide9, c_left, c_top, q_w, q_h)
    
    lines = [
        {'text': q_info["title"], 'size': 12.5, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 2},
        {'text': f"Target Suites: {q_info['files']}", 'size': 9.5, 'italic': True, 'color': C_BLUE, 'space_after': 6}
    ]
    for b in q_info["bullets"]:
        lines.append({'text': f"•  {b}", 'size': 11, 'color': C_BODY_TEXT, 'space_after': 4})
    add_text_box(slide9, c_left + 160000, c_top + 160000, q_w - 320000, q_h - 300000, lines)

print("Slide 9 generated.")

# ==============================================================================
# SLIDE 10: RISK ENGINE & AI EXPLAINABILITY
# ==============================================================================
slide10 = prs.slides[9]
clear_slide_content(slide10)
set_slide_header(slide10, "Risk Engine & AI Explainability", 10)

add_pill(slide10, 300000, 1100000, 11592000, 380000, "MATHEMATICAL RISK FUSION & GENERATIVE NATURAL LANGUAGE MITIGATION SYNTHESIS", C_DARK_NAVY, font_size=12)

re_w = 5650000
re_gap = 292000
re_top = 1600000
re_h = 4400000

# Left Card: Risk Engine
add_card(slide10, 300000, re_top, re_w, re_h)
add_pill(slide10, 450000, re_top + 150000, re_w - 300000, 420000, "UNIFIED 0–100 RISK ENGINE (modules/risk_engine.py)", C_BLUE, font_size=12)

re_lines = [
    {'text': "Multi-Factor Mathematical Formulation:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "Risk Score = (0.45 · S_API) + (0.35 · S_ML) + (0.20 · S_Heuristics)", 'size': 11, 'bold': True, 'color': C_BLUE, 'space_after': 8},
    {'text': "Critical Override Logic:", 'size': 11, 'bold': True, 'color': C_RED, 'space_after': 3},
    {'text': "If VirusTotal flags > 5 OR Google Safe Browsing triggers, the score immediately escalates to 90–100 (Critical), overriding benign heuristic weights.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 8},
    {'text': "5 Standardized Severity Bands:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 4},
    {'text': "• 🟢 SAFE (0–20): Clean reputation, valid SSL, 0 vendor blacklist hits.", 'size': 10.5, 'color': C_GREEN, 'space_after': 3},
    {'text': "• 🔵 LOW (21–40): Minor issues (missing CSP headers, newly registered domain).", 'size': 10.5, 'color': C_BLUE, 'space_after': 3},
    {'text': "• 🟡 MEDIUM (41–60): Elevated entropy, suspicious redirects, or spam keywords.", 'size': 10.5, 'color': C_AMBER, 'space_after': 3},
    {'text': "• 🟠 HIGH (61–80): Multiple threat flags, elevated abuse confidence score.", 'size': 10.5, 'color': C_RED, 'space_after': 3},
    {'text': "• 🔴 CRITICAL (81–100): Active malware distribution, verified phishing, C2 IP.", 'size': 10.5, 'color': C_RED, 'space_after': 3}
]
add_text_box(slide10, 450000, re_top + 680000, re_w - 300000, re_h - 800000, re_lines)

# Right Card: Groq Generative AI
add_card(slide10, 300000 + re_w + re_gap, re_top, re_w, re_h)
add_pill(slide10, 300000 + re_w + re_gap + 150000, re_top + 150000, re_w - 300000, 420000, "GROQ LLAMA-3 70B AI EXPLANATION ENGINE", C_PURPLE, font_size=12)

ai_lines = [
    {'text': "✔ Contextual Threat Translation:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "Synthesizes multi-page JSON payloads from VirusTotal, AbuseIPDB, and ML models into a clean 3-sentence executive summary in <1.2 seconds.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 8},
    {'text': "✔ Actionable Role-Specific Recommendations:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• For SOC Analysts: Specific iptables block rules, DNS sinkhole targets, and SHA-256 IOC blacklist values.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• For Leadership: Business risk overview, user credential revocation advice, and corporate policy adjustments.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 8},
    {'text': "✔ Embedded Deterministic Offline Templates:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "Includes a rule-based advisory template engine that provides immediate human-readable remediation even if offline or when GROQ_API_KEY is not set.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 8}
]
add_text_box(slide10, 300000 + re_w + re_gap + 150000, re_top + 680000, re_w - 300000, re_h - 800000, ai_lines)

print("Slide 10 generated.")

# ==============================================================================
# SLIDE 11: DATABASE, HISTORY & REPORT GENERATION
# ==============================================================================
slide11 = prs.slides[10]
clear_slide_content(slide11)
set_slide_header(slide11, "Database, History & Report Generation", 11)

add_pill(slide11, 300000, 1100000, 11592000, 380000, "RELATIONAL PERSISTENCE & COMPLIANCE-READY FORENSIC REPORT GENERATION", C_DARK_NAVY, font_size=12)

db_w = 3690000
db_gap = 260000
db_top = 1600000
db_h = 4400000

# Col 1: DB Architecture
add_card(slide11, 300000, db_top, db_w, db_h)
add_pill(slide11, 420000, db_top + 140000, db_w - 240000, 420000, "15 RELATIONAL TABLES (SQLite 3)", C_BLUE, font_size=11)
add_text_box(slide11, 440000, db_top + 680000, db_w - 280000, db_h - 780000, [
    {'text': "Core Configuration:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• SQLite 3 database located at database/cybermind.db.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• 11 optimized B-Tree indexes on scan_time, risk_level, target for sub-millisecond query execution.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• Foreign key cascading (PRAGMA foreign_keys = ON;).", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "Normalized Table Schema:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• scan_history (Master audit entity)", 'size': 10, 'bold': True, 'color': C_BLUE},
    {'text': "• url_scans, website_scans, domain_scans, email_scans, ip_scans, file_scans, qr_scans", 'size': 9.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• api_logs, reports, settings, scan_statistics, feedback, support_tickets, users", 'size': 9.5, 'color': C_MUTED_TEXT}
])

# Col 2: Live Audit Log
add_card(slide11, 300000 + db_w + db_gap, db_top, db_w, db_h)
add_pill(slide11, 300000 + db_w + db_gap + 120000, db_top + 140000, db_w - 240000, 420000, "176 REAL SCANS LOGGED IN DB", C_GREEN, font_size=11)
add_text_box(slide11, 300000 + db_w + db_gap + 140000, db_top + 680000, db_w - 280000, db_h - 780000, [
    {'text': "Live Scans by Module Type:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• Universal Scan: 77 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• Device Security Check: 25 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• Website Scanner: 20 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• Phone Threat Intel: 17 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• URL Scanner: 12 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• File / Malware Scanner: 7 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• IP & Email Scanners: 12 scans", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• Domain & QR Scanners: 6 scans", 'size': 10, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "Severity Distribution:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• Safe: 70 | Medium: 49 | High: 22", 'size': 10, 'color': C_BODY_TEXT},
    {'text': "• Low: 19 | Critical: 16", 'size': 10, 'color': C_RED}
])

# Col 3: Report Generation
add_card(slide11, 300000 + 2 * (db_w + db_gap), db_top, db_w, db_h)
add_pill(slide11, 300000 + 2 * (db_w + db_gap) + 120000, db_top + 140000, db_w - 240000, 420000, "AUTOMATED FORENSIC REPORTS", C_PURPLE, font_size=11)
add_text_box(slide11, 300000 + 2 * (db_w + db_gap) + 140000, db_top + 680000, db_w - 280000, db_h - 780000, [
    {'text': "Forensic PDF Export:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• Generates branded executive PDF security reports in under 1 second.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• Includes visual risk score dial, executive summary, and defensive checklist.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• MITRE ATT&CK Matrix mapping of identified adversary techniques.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "Raw JSON Telemetry Export:", 'size': 11, 'bold': True, 'color': C_DARK_NAVY, 'space_after': 3},
    {'text': "• Complete machine-readable JSON payload exports for seamless enterprise SIEM ingestion.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 3},
    {'text': "• Cryptographic SHA-256 hash stamp ensuring chain of custody integrity.", 'size': 10.5, 'color': C_BODY_TEXT}
])

print("Slide 11 generated.")

# ==============================================================================
# SLIDE 12: INNOVATION & TECHNICAL CONTRIBUTION
# ==============================================================================
slide12 = prs.slides[11]
clear_slide_content(slide12)
set_slide_header(slide12, "Innovation & Technical Contribution", 12)

add_pill(slide12, 300000, 1100000, 11592000, 380000, "KEY TECHNICAL ADVANCEMENTS EVALUATED AGAINST REVIEW 4 RUBRIC", C_DARK_NAVY, font_size=12)

innovations = [
    {
        "title": "01 | Unified Multi-Vector Single Pane of Glass",
        "color": C_BLUE,
        "bullets": [
            "Eliminates cybersecurity tool sprawl by consolidating Web, Network, Email, Telephony, Binary, and Endpoint vectors into one dashboard.",
            "Universal Auto-Scanner intelligently parses and auto-dispatches any input target."
        ]
    },
    {
        "title": "02 | Hybrid Threat Intelligence & ML Fusion",
        "color": C_GREEN,
        "bullets": [
            "Combines 13 external live threat feeds, rule-based heuristics, 4 supervised Random Forest ML models (96.7% accuracy), and Groq Llama-3 70B AI.",
            "Yields comprehensive contextual threat visibility unmatched by single-vector tools."
        ]
    },
    {
        "title": "03 | Calibrated 0–100 Unified Risk Scoring",
        "color": C_PURPLE,
        "bullets": [
            "Solves divergent vendor scoring scales by delivering a normalized mathematical score.",
            "Critical Override logic ensures verified weaponized threats immediately trigger Critical alerts."
        ]
    },
    {
        "title": "04 | Resilient Offline-First Architecture",
        "color": C_AMBER,
        "bullets": [
            "Every external service connector implements local deterministic heuristic algorithms.",
            "Guarantees 100% operational availability during network outages or API rate-limits."
        ]
    }
]

in_w = 5650000
in_gap = 292000
in_top1 = 1600000
in_top2 = 3850000
in_h = 2100000

for idx, in_info in enumerate(innovations):
    col = idx % 2
    row = idx // 2
    c_left = 300000 + col * (in_w + in_gap)
    c_top = in_top1 if row == 0 else in_top2
    
    add_card(slide12, c_left, c_top, in_w, in_h)
    add_pill(slide12, c_left + 150000, c_top + 140000, in_w - 300000, 420000, in_info["title"], in_info["color"], font_size=12)
    
    lines = []
    for b in in_info["bullets"]:
        lines.append({'text': f"•  {b}", 'size': 11.5, 'color': C_BODY_TEXT, 'space_after': 8})
    add_text_box(slide12, c_left + 160000, c_top + 700000, in_w - 320000, in_h - 800000, lines)

print("Slide 12 generated.")

# ==============================================================================
# SLIDE 13: LIMITATIONS, FUTURE SCOPE & CONCLUSION
# ==============================================================================
slide13 = prs.slides[12]
clear_slide_content(slide13)
set_slide_header(slide13, "Limitations, Future Scope & Conclusion", 13)

add_pill(slide13, 300000, 1100000, 11592000, 380000, "ARCHITECTURAL BOUNDARIES, FUTURE ROADMAP (PLANNED) & FINAL CONCLUSION", C_DARK_NAVY, font_size=12)

lim_w = 5650000
lim_gap = 292000
lim_top = 1600000
lim_h = 3300000

# Left: Limitations
add_card(slide13, 300000, lim_top, lim_w, lim_h)
add_pill(slide13, 450000, lim_top + 140000, lim_w - 300000, 420000, "CURRENT SYSTEM LIMITATIONS", C_RED, font_size=12)
add_text_box(slide13, 450000, lim_top + 680000, lim_w - 300000, lim_h - 800000, [
    {'text': "• External API Rate Limits & Quotas:", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "Free-tier external threat APIs impose strict per-minute query constraints and variable internet latency.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "• Static Malware Analysis Boundary:", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "PE and file scanner currently performs static header, hash, and section entropy checks without live kernel runtime detonation.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "• Model Retraining Cycles:", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "Model weights are static artifacts; continuous retraining currently requires offline dataset curation pipelines.", 'size': 10.5, 'color': C_BODY_TEXT}
])

# Right: Future Scope
add_card(slide13, 300000 + lim_w + lim_gap, lim_top, lim_w, lim_h)
add_pill(slide13, 300000 + lim_w + lim_gap + 150000, lim_top + 140000, lim_w - 300000, 420000, "FUTURE SCOPE & ROADMAP (PLANNED)", C_GREEN, font_size=12)
add_text_box(slide13, 300000 + lim_w + lim_gap + 150000, lim_top + 680000, lim_w - 300000, lim_h - 800000, [
    {'text': "• Dynamic Malware Detonation Sandbox (Planned):", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "Containerized microVM sandbox to safely execute suspicious binaries and observe behavioral system calls.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "• Enterprise SIEM / SOAR Webhooks (Planned):", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "Direct real-time webhook alert streaming to Splunk, Elastic Security, and Microsoft Sentinel.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "• Automated Firewall Active Response (Planned):", 'size': 11.5, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "Automated generation and host-level deployment of Windows Firewall and Linux iptables blocking scripts.", 'size': 10.5, 'color': C_BODY_TEXT}
])

# Bottom: Conclusion
add_card(slide13, 300000, 5050000, 11592000, 1000000)
add_text_box(slide13, 450000, 5150000, 11292000, 800000, [
    {'text': "PROJECT CONCLUSION:", 'size': 12, 'bold': True, 'color': C_DARK_NAVY},
    {'text': "CyberMind AI successfully delivers a fully functional, enterprise-grade cyber intelligence platform bridging multi-vector threat signals, supervised machine learning (96.67% accuracy), and explainable generative AI. The platform meets and exceeds all Project Review – IV deliverables with 10 operational modules, 176 live database scans, and 156/156 passing automated test cases.", 'size': 11, 'color': C_BODY_TEXT}
])

print("Slide 13 generated.")

# ==============================================================================
# SLIDE 14: REFERENCES & THANK YOU
# ==============================================================================
slide14 = prs.slides[13]
clear_slide_content(slide14)
set_slide_header(slide14, "References & Acknowledgements", 14)

add_pill(slide14, 300000, 1100000, 11592000, 380000, "RESEARCH REFERENCES, THREAT INTELLIGENCE STANDARDS & ACKNOWLEDGEMENTS", C_DARK_NAVY, font_size=12)

# Left Box: References
add_card(slide14, 300000, 1600000, 6800000, 4400000)
add_pill(slide14, 450000, 1740000, 6500000, 420000, "ACADEMIC & INDUSTRY REFERENCES", C_DARK_NAVY, font_size=12)
add_text_box(slide14, 450000, 2300000, 6500000, 3500000, [
    {'text': "1. UCI Machine Learning Repository:", 'size': 11, 'bold': True, 'color': C_BLUE},
    {'text': "   PhiUSIIL Phishing URL Dataset (234,987 verified security samples, 50 features).", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "2. VirusTotal API v3 & Google Safe Browsing:", 'size': 11, 'bold': True, 'color': C_GREEN},
    {'text': "   Multi-engine antivirus telemetry, domain reputation standards, and malware blacklist protocols.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "3. AbuseIPDB & IPinfo Threat Feeds:", 'size': 11, 'bold': True, 'color': C_RED},
    {'text': "   IP reputation scoring, Autonomous System Number (ASN) verification, and Tor exit node tracking.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "4. Meta AI & Groq Cloud:", 'size': 11, 'bold': True, 'color': C_PURPLE},
    {'text': "   Llama-3 70B parameter open foundation model for low-latency contextual cyber risk synthesis.", 'size': 10.5, 'color': C_BODY_TEXT, 'space_after': 6},
    {'text': "5. MITRE Corporation:", 'size': 11, 'bold': True, 'color': C_AMBER},
    {'text': "   MITRE ATT&CK Enterprise Matrix for structured cyber threat mapping and forensic compliance.", 'size': 10.5, 'color': C_BODY_TEXT}
])

# Right Box: Thank You Card
add_card(slide14, 7300000, 1600000, 4592000, 4400000)
add_pill(slide14, 7500000, 1740000, 4192000, 420000, "THANK YOU / QUESTIONS & ANSWERS", C_BLUE, font_size=12)
add_text_box(slide14, 7500000, 2350000, 4192000, 3450000, [
    {'text': "CyberMind AI", 'size': 26, 'bold': True, 'color': C_DARK_NAVY, 'align': PP_ALIGN.CENTER, 'space_after': 4},
    {'text': "AI-Powered Cyber Intelligence Platform", 'size': 13, 'bold': True, 'color': C_BLUE, 'align': PP_ALIGN.CENTER, 'space_after': 14},
    {'text': "Stay Secure, Stay Smart, Stay Ahead.", 'size': 12, 'italic': True, 'color': C_MUTED_TEXT, 'align': PP_ALIGN.CENTER, 'space_after': 20},
    {'text': "Presented by:", 'size': 11, 'color': C_MUTED_TEXT, 'align': PP_ALIGN.CENTER},
    {'text': "Daksh Vasani", 'size': 14, 'bold': True, 'color': C_DARK_NAVY, 'align': PP_ALIGN.CENTER},
    {'text': "Enrollment No.: 2504070500037", 'size': 11, 'color': C_BODY_TEXT, 'align': PP_ALIGN.CENTER, 'space_after': 14},
    {'text': "Under the Guidance of:", 'size': 11, 'color': C_MUTED_TEXT, 'align': PP_ALIGN.CENTER},
    {'text': "Ms. Ritika Savaliya", 'size': 13, 'bold': True, 'color': C_DARK_NAVY, 'align': PP_ALIGN.CENTER},
    {'text': "SOCCA – Silver Oak University | M.Sc. Data Science", 'size': 10.5, 'color': C_MUTED_TEXT, 'align': PP_ALIGN.CENTER}
])

print("Slide 14 generated.")

prs.save(output_pptx)
print(f"Successfully generated Review 4 presentation at: {output_pptx}")
