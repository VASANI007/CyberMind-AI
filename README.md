# 🛡️ CyberMind AI
---
🔗 **Live Project Link:** [Click Here to View App](https://cybermind-ai.streamlit.app/)

---
> **AI-Powered Cyber Risk Assessment & Threat Intelligence Platform Using Machine Learning**

CyberMind AI is a research-oriented cybersecurity platform developed as part of an **M.Sc. Data Science** project. The application combines Artificial Intelligence, Machine Learning, and Cyber Threat Intelligence to analyze cyber risks from multiple sources within a single, user-friendly dashboard.

Unlike traditional security tools that perform only one type of analysis, CyberMind AI integrates multiple cybersecurity modules into one platform, helping users identify potential cyber threats, understand risks, and receive intelligent security recommendations.

---

# 🎯 Project Objective

The main objective of CyberMind AI is to provide a unified cybersecurity analysis platform capable of analyzing:

* URLs
* Websites
* Domains
* Email Addresses
* IP Addresses
* QR Codes
* File Metadata

The platform generates a comprehensive cyber risk assessment using Machine Learning, rule-based analysis, and publicly available cybersecurity information.

---

# 🚀 Features

## Current Development

* Professional Streamlit Dashboard
* Modern User Interface
* SQLite Database
* Scan History
* Analytics Dashboard
* Professional Reports
* Modular Architecture

---

## Planned Modules

### 🔗 URL Scanner

* URL Validation
* Suspicious URL Detection
* HTTPS Verification
* Redirect Analysis
* Machine Learning Phishing Detection
* Risk Score

---

### 🌐 Website Security Analyzer

* SSL Certificate
* Security Headers
* Robots.txt
* Sitemap
* Response Time
* Website Security Score

---

### 🌍 Domain Intelligence

* WHOIS Lookup
* Domain Age
* Registrar Information
* DNS Records
* MX Records
* Domain Health Score

---

### 📧 Email Intelligence

* Email Validation
* MX Record Verification
* SPF Check
* DKIM Check
* DMARC Check
* Disposable Email Detection

---

### 🖥️ IP Intelligence

* IP Validation
* Country
* City
* ISP
* ASN
* Reverse DNS
* Geolocation

---

### 📱 QR Scanner

* QR Code Detection
* URL Extraction
* Automatic Security Analysis

---

### 📄 File Analyzer

* SHA256
* SHA1
* MD5
* File Metadata
* File Type Detection
* Entropy Analysis

---

### 🤖 AI & Machine Learning

* Phishing Detection
* URL Classification
* Risk Prediction
* Model Comparison
* Explainable AI

---

### 📊 Analytics

* Scan Statistics
* Risk Distribution
* Interactive Charts
* Historical Analysis

---

### 📑 Reports

Generate reports in:

* PDF
* Excel
* Word
* CSV
* JSON

---

# 🧠 Technology Stack

## Frontend

* Streamlit

## Programming Language

* Python

## Database

* SQLite

## Machine Learning

* Scikit-learn

## Data Analysis

* Pandas
* NumPy

## Visualization

* Plotly

## Reports

* ReportLab
* OpenPyXL
* python-docx

---
## .env
```
# CyberMind AI Environment Variables
APP_NAME=CyberMind AI
APP_VERSION=1.0.0
DEBUG=True

# Google Safe Browsing
GOOGLE_SAFE_BROWSING_API_KEY= 

# VirusTotal
VIRUSTOTAL_API_KEY= 

# URLScan.io
URLSCAN_API_KEY=

# AbuseIPDB
ABUSEIPDB_API_KEY=

# IPinfo
IPINFO_API_KEY= 

# Groq
GROQ_API_KEY= 

# Database
DATABASE_NAME=cybermind.db

# Paths
DATA_DIR=data
DATASET_DIR=data/datasets
MODEL_DIR=ml/models
REPORT_DIR=reports
CACHE_DIR=data/cache

# Reports
REPORT_AUTHOR=Daksh Vasani
REPORT_COMPANY=CyberMind AI
```
---

# 📂 Project Structure

```text
CyberMind-AI/

app.py

config/

core/

services/

modules/

pages/

database/

ml/

reports/

utils/

assets/

data/

exports/

logs/

docs/

tests/
```

---

# 🛠️ Installation

Clone the repository

```bash
git clone https://github.com/your-username/cybermind-ai.git
```

Open the project

```bash
cd cybermind-ai
```

Create virtual environment

```bash
python -m venv .venv
```

Activate virtual environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 📈 Development Roadmap

* ✅ Phase 1 – Planning
* ✅ Phase 2 – Architecture
* 🔄 Phase 3 – Foundation Development
* ⏳ Phase 4 – Universal Smart Scanner
* ⏳ Phase 5 – URL Scanner
* ⏳ Phase 6 – Website Analyzer
* ⏳ Phase 7 – Domain Intelligence
* ⏳ Phase 8 – Email Intelligence
* ⏳ Phase 9 – IP Intelligence
* ⏳ Phase 10 – QR Scanner
* ⏳ Phase 11 – File Analyzer
* ⏳ Phase 12 – Machine Learning
* ⏳ Phase 13 – Explainable AI
* ⏳ Phase 14 – Reports
* ⏳ Phase 15 – Testing & Deployment

---

# 📊 Project Status

**Version:** v1.0 (Development)

Current Stage:

**Foundation Development**

---

# 🎓 Academic Information

**Project Title**

AI-Powered Cyber Risk Assessment & Threat Intelligence Platform Using Machine Learning

Project Type:

Research-Based Project

Program:

M.Sc. Data Science

---

# 🔒 Disclaimer

CyberMind AI is designed exclusively for educational, research, and cybersecurity awareness purposes.

The application analyzes only publicly available information and open-source intelligence. It does not collect, access, or expose private user information, perform unautho# 🚀 Future Enhancements: Ultimate Future Roadmap (30 Advanced Features)

We have designed CyberMind AI as a next-generation, enterprise-grade, AI-powered cybersecurity platform. The system is built on modular, scalable, and future-ready principles, allowing new modules and plugins to be added without core refactoring.

> [!TIP]
> ### ⭐ Top 5 — For Live Presentation / Viva
> 1. **Dynamic Sandbox Analysis**: Running suspicious links and files in an isolated environment to monitor run-time behaviors.
> 2. **Dark Web Monitoring**: Scanning breached credential databases and underground forums to detect leaked user information.
> 3. **AI-Based Malware Family Classification**: Going beyond binary classification to categorize threats into specific malware families.
> 4. **Behavioral Anomaly Detection**: Utilizing machine learning to flag outliers in network activity and system logs.
> 5. **Real-Time SOC Dashboard**: Building a security operations center visualization with live alert notifications.
>
> _Note: The full 30-feature developmental roadmap containing all tracks and design principles is detailed below._

---

## 🚀 30 Advanced Features

### 1. AI Threat Intelligence Engine
- AI Threat Correlation Engine
- Multi-Source Threat Intelligence Fusion
- AI Threat Prediction
- AI Confidence Score
- Explainable AI (SHAP/LIME)
- *Tools:* Scikit-learn, SHAP, LIME

### 2. Smart URL & Website Security
- Dynamic URL Behavior Analysis
- Redirect Chain Analysis
- JavaScript Behavior Detection
- Drive-by Download Detection
- Homograph Domain Detection
- Typosquatting Detection
- Website Technology Fingerprinting
- *Tools:* URLScan.io, Wappalyzer, WHOIS, DNS

### 3. Advanced Threat Detection
- Phishing Detection
- Malware Reputation
- Ransomware Indicators
- Spyware Indicators
- Trojan Indicators
- Rootkit Indicators
- Worm Indicators
- Zero-Day Risk Prediction

### 4. Intelligent File Analysis
- Hex Signature Analysis
- Magic Byte Verification
- File Entropy Analysis
- Hash Reputation (MD5/SHA1/SHA256)
- Executable Metadata Analysis
- Macro Detection
- Suspicious File Scoring
- *Tools:* pefile, python-magic, YARA

### 5. IP & Network Intelligence
- GeoIP Analytics
- ASN Intelligence
- ISP Intelligence
- VPN/Proxy Detection
- TOR Exit Node Detection
- Blacklist Reputation
- Network Risk Score
- *Tools:* GeoLite2, AbuseIPDB, IPinfo

### 6. Email Intelligence
- Email Breach Detection
- SPF Validation
- DKIM Validation
- DMARC Validation
- Disposable Email Detection
- Domain Reputation
- Email Risk Score

### 7. QR Security
- QR URL Detection
- Hidden Redirect Detection
- Fake Payment QR Detection
- QR Reputation
- QR Risk Score

### 8. Device Security
- Firewall Status
- Antivirus Status
- Open Ports
- Running Services
- Installed Security Updates
- Device Risk Score

### 9. AI Security Assistant
- Explain Results
- Threat Education
- Security Recommendations
- Incident Guidance
- Interactive Chat
- *Tools:* Groq API (Free Tier)

### 10. Security Analytics
- Threat Heat Map
- Attack Timeline
- Risk Trends
- Country-wise Threats
- Threat Distribution
- Security Score Dashboard

### 11. Enterprise Reporting
- PDF Report
- Excel Report
- JSON Export
- Executive Summary
- Technical Report
- Compliance Report

### 12. OSINT Intelligence
- WHOIS
- DNS Records
- Certificate Transparency Logs
- Subdomain Discovery
- Organization Intelligence

### 13. AI Anomaly Detection
- Unusual URL Detection
- Suspicious Domain Behaviour
- Outlier Detection
- Unknown Threat Detection
- *Tools:* Isolation Forest, One-Class SVM

### 14. Threat Knowledge Graph
- Relationship Graph for URLs, Domains, IPs, Emails and Files
- *Tools:* NetworkX, Plotly

### 15. MITRE ATT&CK Mapping
- Map detected threats to MITRE ATT&CK techniques

### 16. IOC Extraction
- MD5
- SHA1
- SHA256
- URLs
- Domains
- Emails
- IP Addresses

### 17. AI Risk Decision Engine
- Unified Cyber Risk Score using URL Risk, Domain Risk, IP Risk, Threat Intelligence, and ML Prediction

### 18. Global Threat Dashboard
- World Threat Map
- Threat Categories
- Top Malicious Countries
- Attack Statistics

### 19. Cyber Threat Knowledge Base
- Phishing, Malware, Ransomware, SQL Injection, XSS, DDoS, CVEs, and MITRE ATT&CK concepts

### 20. Offline AI Mode
- Offline ML Models
- Cached WHOIS
- GeoLite2 Database
- Local Rules
- Offline Risk Scoring

### 21. AI Attack Path Prediction
- Predict possible attacker movement from initial compromise to final impact

### 22. Dark Web Intelligence
- Public Credential Leak Detection
- Email Exposure Monitoring
- Domain Exposure Monitoring

### 23. Brand Impersonation Detection
- Detect fake brands using typosquatting and homograph analysis

### 24. Software Supply Chain Risk Analysis
- Dependency Risk
- Package Reputation
- Vulnerable Libraries

### 25. CVE Intelligence Engine
- Latest CVEs, CVSS Scores, Severity, and Security Recommendations

### 26. Attack Surface Discovery
- Public Domains, Subdomains, SSL Certificates, and Exposed Technologies

### 27. Security Compliance Analyzer
- Assessment against NIST CSF, CIS Controls, ISO 27001, and OWASP Top 10

### 28. AI Threat Explainability Dashboard
- Visualize feature importance and AI decision explanations using SHAP/LIME

### 29. Continuous Threat Learning
- Support user feedback and scheduled model retraining to improve accuracy

### 30. Plugin-Based Security Architecture
- Design a modular plugin framework so new scanners, APIs, AI models, and integrations can be added without changing the core application

---

## 🎨 Design Principles

- **Modular Architecture**: Independent modules for scan operations, database connection, risk assessment, and reporting.
- **Offline + Online Support**: Hybrid operational modes using local cached databases when offline and external APIs when online.
- **Free/Open-Source First**: Prioritizing open intelligence sources, free API tiers, and open-source python packages.
- **AI + ML + Rule-Based Hybrid Detection**: Layered security scoring combining rules, signatures, heuristics, and trained scikit-learn models.
- **Explainable AI**: Translating complex model features into actionable threat insights and explainable risk scores.
- **Scalable Plugin System**: Abstract scanner interface enabling frictionless integration of new cybersecurity telemetry tools.
- **Enterprise-Grade Reporting**: Automated multi-format export files for executive and engineering consumers.
- **Professional Dashboard**: Clean, responsive layout with visual status indicators and unified risk telemetry.
- **Security by Design**: Secure handling of scans and credentials with strictly scoped local database schemas.
- **Future-Ready Architecture**: Decoupled design patterns optimized for continuous integration and scaling.ty & Threat Sharing
* Crowdsourced Threat Intelligence Sharing (community-reported malicious links)
* Blockchain-Based Threat Intelligence Verification (tamper-proof threat logs)

---

## 📄 License

This project is licensed under the MIT License.
