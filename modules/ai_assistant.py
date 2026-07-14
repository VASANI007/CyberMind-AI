"""
CyberMind AI

AI Security Assistant

Hybrid online/offline companion. Uses Groq API for advanced context-aware chat
when GROQ_API_KEY is configured. Falls back to offline rule-based knowledge
base when offline or API key is missing.

Responsibilities
• Answer a wide range of cybersecurity and project questions
• Generate contextual suggestions from recent scan history
• Graceful offline fallback with zero external dependencies
"""

from __future__ import annotations

import re
import os
import requests
from typing import Any

import streamlit as st

from core.logger import logger


# ---------------------------------------------------------------------------
# Knowledge base: (keywords, tip). Matched with word boundaries so short
# keywords like "ip" or "url" don't accidentally match inside other words.
# Scored by number of keyword hits — best match wins, not just the first.
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE: list[tuple[list[str], str]] = [

    # --- Account & authentication -------------------------------------
    (["password", "passwd"],
     "Use a unique password for every account — at least 12-14 characters, mixing "
     "upper/lower case, numbers and symbols. A password manager (Bitwarden, 1Password) "
     "removes the need to remember or reuse them."),

    (["password manager", "bitwarden", "1password", "lastpass"],
     "A password manager generates and stores strong unique passwords for every site, "
     "so you only need to remember one master password. It also warns you about reused "
     "or breached passwords."),

    (["2fa", "otp", "two factor", "two-factor", "mfa"],
     "Enable Two-Factor Authentication on every account that supports it. Prefer an "
     "authenticator app (Google Authenticator, Authy) over SMS OTP, since SMS can be "
     "intercepted via SIM-swap attacks."),

    (["sim swap", "sim card cloned"],
     "SIM-swap fraud lets an attacker port your number to their SIM and receive your "
     "OTPs. Add a SIM-lock PIN with your telecom operator, and avoid SMS-only 2FA where "
     "possible."),

    (["security question", "recovery question"],
     "Avoid using real, guessable answers for security questions (mother's maiden name, "
     "pet name) since these are often public. Treat the answer like a second password."),

    (["account recovery", "recover my account", "locked out"],
     "Set up a recovery email and phone number for every important account in advance. "
     "Recovering a hacked account is far harder once you've lost access to both."),

    (["biometric", "fingerprint", "face unlock", "face id"],
     "Biometric locks (fingerprint, face unlock) are convenient but should be paired with "
     "a strong backup PIN, since biometric data can't be changed if ever compromised."),

    (["screen lock", "device lock", "lock screen"],
     "Always set a PIN, pattern, or biometric lock on your phone/laptop. An unlocked "
     "device gives an attacker instant access to your accounts and messages."),

    # --- Email / messaging threats --------------------------------------
    (["phishing", "fake email", "suspicious email"],
     "Never click links or open attachments from unexpected emails. Check the sender's "
     "real email address, hover over links before clicking, and verify money/credential "
     "requests through a separate, known channel."),

    (["smishing", "sms scam", "fake sms", "fake text message"],
     "Smishing is phishing via SMS — fake delivery, bank, or prize texts with a link. "
     "Never click links in unexpected texts; go directly to the official app or website "
     "instead."),

    (["spam"],
     "Mark unwanted emails as spam rather than just deleting them — this trains your "
     "provider's filter. Never reply to or unsubscribe from spam you didn't sign up for, "
     "since replying confirms your address is active."),

    (["breach", "data leak", "leaked", "hacked"],
     "Check whether your email has appeared in a known data breach (e.g. Have I Been "
     "Pwned), and change the password on any affected account right away."),

    (["spoof", "spf", "dkim", "dmarc"],
     "SPF, DKIM and DMARC are email authentication records that stop scammers from "
     "spoofing your domain. If you manage a domain, make sure all three are configured."),

    (["email encryption", "encrypt email", "pgp"],
     "For sensitive email content, use end-to-end encryption (PGP/GPG) or a provider "
     "with built-in encryption (ProtonMail). Standard email is not encrypted in transit "
     "by default."),

    (["secure messaging", "signal", "encrypted chat", "whatsapp hacked", "whatsapp safety"],
     "Prefer messaging apps with end-to-end encryption (Signal, WhatsApp). Enable "
     "two-step verification in WhatsApp settings so no one can register your number "
     "elsewhere without your PIN."),

    # --- Scams ------------------------------------------------------------
    (["scam call", "vishing", "social engineering"],
     "Scammers create urgency ('your account will be blocked') to bypass your judgement. "
     "Slow down, verify independently, and never share an OTP or password over a call."),

    (["tech support scam", "fake microsoft call", "remote access scam"],
     "Real companies never cold-call asking to remotely access your device. Hang up, and "
     "never install remote-access software (AnyDesk, TeamViewer) for someone who called "
     "you unsolicited."),

    (["lottery scam", "prize scam", "you won", "lucky draw"],
     "You cannot win a lottery or contest you never entered. Any message asking for a fee "
     "or your bank details to 'release' a prize is a scam — delete it."),

    (["job scam", "fake job offer", "work from home scam"],
     "Be wary of job offers that ask for money upfront, promise unusually high pay for "
     "little work, or move the conversation to a personal chat app quickly. Verify the "
     "company independently before sharing any documents."),

    (["romance scam", "dating scam", "online dating fraud"],
     "Be cautious if an online partner you've never met in person asks for money, gifts, "
     "or financial help, especially early in the relationship. Reverse-image-search their "
     "photos to check for fake profiles."),

    (["investment scam", "crypto scam", "cryptocurrency scam", "ponzi", "guaranteed returns"],
     "Be skeptical of any investment promising guaranteed high returns with no risk — "
     "this is the hallmark of a Ponzi scheme. Verify the platform is registered with a "
     "real financial regulator before investing."),

    (["online shopping scam", "fake shopping site", "too good to be true deal"],
     "Extremely discounted deals on unfamiliar websites are a common scam pattern. Check "
     "for a real physical address, return policy, and reviews outside the site itself "
     "before paying."),

    (["upi", "payment app", "gpay", "phonepe", "paytm fraud"],
     "Never share your UPI PIN with anyone, including someone claiming to be from your "
     "bank — a PIN is only needed to send money, never to receive it. Refunds and cashback "
     "never require your PIN."),

    (["identity theft", "someone using my identity", "impersonation"],
     "Limit how much personal information (birthdate, address, ID numbers) you share "
     "publicly. If you suspect identity theft, freeze your credit report and report it to "
     "your bank and local authorities immediately."),

    (["deepfake", "ai generated video", "fake video"],
     "Deepfakes can convincingly fake a person's voice or face. Be skeptical of urgent "
     "video/audio requests for money, and verify through a separate known channel before "
     "acting."),

    # --- Network & Wi-Fi ---------------------------------------------------
    (["vpn"],
     "A VPN encrypts your internet traffic, which helps on public Wi-Fi. Choose a "
     "reputable no-log provider — avoid free VPNs, since many monetize by selling data."),

    (["wifi", "wi-fi", "public wifi", "hotspot"],
     "Avoid logging into banking or sensitive accounts on public Wi-Fi. Use a VPN, and "
     "turn off auto-connect to open networks on your device."),

    (["router", "modem security", "home network"],
     "Change your router's default admin password and Wi-Fi password immediately after "
     "setup, use WPA3/WPA2 encryption, and keep the router's firmware updated."),

    (["bluetooth"],
     "Turn off Bluetooth when not in use, and don't accept pairing requests from unknown "
     "devices. Some attacks use Bluetooth to silently connect to nearby phones."),

    (["man in the middle", "mitm"],
     "A man-in-the-middle attack intercepts traffic between you and a website, often on "
     "unsecured Wi-Fi. Always check for HTTPS, and use a VPN on networks you don't trust."),

    (["dns spoofing", "dns hijack"],
     "DNS spoofing redirects you to a fake site even when you type the correct address. "
     "Using a trusted DNS provider (e.g. 1.1.1.1, 8.8.8.8) and checking for a valid SSL "
     "certificate helps protect against this."),

    (["firewall"],
     "Keep your device's firewall enabled — it blocks unsolicited inbound connections and "
     "is a basic first line of defense."),

    # --- Malware ------------------------------------------------------------
    (["ransomware"],
     "Keep regular offline backups of important data. Ransomware encrypts your files and "
     "demands payment — an offline backup is the most reliable protection."),

    (["malware", "virus", "trojan"],
     "Keep your OS and antivirus updated, avoid cracked/pirated software, and scan any "
     "downloaded file before opening it. This app's File Scanner can check a file for you."),

    (["spyware", "stalkerware"],
     "Spyware secretly monitors your activity. Watch for unusual battery drain, unknown "
     "apps, or spikes in data usage, and use a reputable mobile security app to scan for "
     "it."),

    (["adware", "unwanted popups", "browser popups"],
     "Persistent popup ads usually come from a browser extension or bundled software. "
     "Review and remove unfamiliar browser extensions and recently installed programs."),

    (["keylogger"],
     "A keylogger secretly records everything you type, including passwords. Avoid "
     "downloading software from untrusted sources, and use a password manager's "
     "autofill, which some keyloggers can't capture."),

    (["worm"],
     "A worm spreads automatically across a network without user action, often via "
     "unpatched vulnerabilities. Keeping systems patched and network segmented limits "
     "how far it can spread."),

    (["rootkit"],
     "A rootkit hides deep in the operating system to maintain persistent, hidden access. "
     "It's hard to detect with normal antivirus — a full OS reinstall is often the safest "
     "fix if one is confirmed."),

    (["botnet"],
     "A botnet is a network of infected devices controlled remotely, often used for DDoS "
     "attacks. Keeping IoT devices and routers updated prevents them from being recruited "
     "into one."),

    # --- Web / browsing -------------------------------------------------
    (["ssl", "https", "certificate"],
     "Always check a website uses HTTPS (padlock icon) before entering sensitive "
     "information. A missing or invalid SSL certificate is a red flag."),

    (["short url", "shortened", "bit.ly", "tinyurl"],
     "Be cautious with shortened links since they hide the real destination. Paste any "
     "URL into this app's URL Scanner to check it before clicking."),

    (["url", "link"],
     "Before clicking an unfamiliar link, check the domain carefully for lookalike "
     "spelling (e.g. 'paypa1.com'), and paste it into this app's URL Scanner to verify "
     "it first."),

    (["qr"],
     "Scan QR codes only from sources you trust. A malicious QR code can redirect to a "
     "phishing site or trigger a download — use this app's QR Scanner to check first."),

    (["ip address", "my ip", "ip lookup"],
     "An IP address alone won't reveal your identity, but it can reveal your rough "
     "location and ISP. Avoid sharing it publicly, and use a VPN if privacy matters."),

    (["domain", "whois"],
     "A newly registered domain (a few weeks or months old) is more likely to be used for "
     "scams. Check domain age and registrar reputation before trusting a site."),

    (["cookie", "tracking", "third party tracker"],
     "Cookies let websites track you across visits and, with third-party trackers, "
     "across other sites too. Regularly clear cookies, and use a privacy-focused browser "
     "or extension to block third-party trackers."),

    (["incognito", "private browsing"],
     "Incognito/private mode only stops your browser from saving local history — it does "
     "not hide your activity from your ISP, employer network, or the websites you visit."),

    (["browser extension", "extension safety", "add-on"],
     "Only install browser extensions from official stores, check reviews and permissions "
     "requested, and remove any extension you no longer actively use."),

    (["clickjacking"],
     "Clickjacking tricks you into clicking something different from what you see, using "
     "invisible overlay elements. Keeping your browser updated helps, since browsers "
     "patch known clickjacking techniques."),

    (["session hijack", "cookie theft", "stolen session"],
     "Session hijacking steals your active login session, often via a stolen cookie on an "
     "unsecured network. Log out of sensitive accounts when done, and avoid sensitive "
     "logins on public Wi-Fi."),

    # --- Files, devices & data --------------------------------------------
    (["usb", "pen drive", "flash drive"],
     "Never plug in an unknown USB drive you found or were given — it can silently "
     "install malware. Disable auto-run for removable media on your device."),

    (["cloud storage", "google drive safety", "dropbox safety", "icloud safety"],
     "Enable 2FA on your cloud storage account, avoid sharing folders with 'anyone with "
     "the link' if they contain sensitive files, and review shared-link access "
     "periodically."),

    (["app permission", "app permissions"],
     "Review app permissions periodically and revoke access to camera, microphone, or "
     "location for apps that don't genuinely need it for their core function."),

    (["iot", "smart device", "smart home", "cctv camera security"],
     "Change default passwords on smart cameras, routers, and other IoT devices "
     "immediately — default credentials are widely known and actively scanned for by "
     "attackers."),

    (["backup"],
     "Follow the 3-2-1 rule: 3 copies of important data, on 2 different media, with 1 "
     "copy kept offline or off-site."),

    (["encryption", "encrypt my data", "disk encryption"],
     "Full-disk encryption (BitLocker on Windows, FileVault on Mac) protects your data if "
     "your device is lost or stolen, making the contents unreadable without your "
     "password."),

    (["tor", "dark web"],
     "The dark web itself isn't illegal, but it hosts significant criminal activity "
     "alongside legitimate privacy uses. If you check whether your data is exposed there, "
     "use a reputable breach-monitoring service instead of browsing it directly."),

    (["digital footprint", "online privacy", "reduce my footprint"],
     "Regularly search your own name online, remove old accounts you no longer use, and "
     "review privacy settings on social media to limit what's publicly visible."),

    (["gdpr", "privacy rights", "data protection law"],
     "Most privacy laws (like GDPR) give you the right to request what data a company "
     "holds about you and to ask for it to be deleted — look for a 'privacy' or 'data "
     "request' option in the company's settings or support page."),

    # --- Social / children ----------------------------------------------
    (["social media privacy", "instagram privacy", "facebook privacy"],
     "Set your social profiles to private, limit what's visible to the public, and avoid "
     "posting real-time location details that reveal when you're away from home."),

    (["cyberbullying", "online harassment"],
     "Keep evidence (screenshots) of harassment, block and report the account on the "
     "platform, and avoid engaging directly with the harasser. Involve a trusted adult "
     "or authority if threats escalate."),

    (["child safety online", "parental control", "kids online safety"],
     "Use built-in parental controls on devices and apps, keep communication open about "
     "what your child encounters online, and place shared devices in common areas of the "
     "home."),

    # --- Organizational / technical (for the developer side) --------------
    (["update", "patch"],
     "Keep your OS, browser and apps updated. Most real-world attacks exploit a known "
     "vulnerability that a patch already fixed."),

    (["zero day", "zero-day"],
     "A zero-day is a vulnerability attackers exploit before a fix exists. Reducing your "
     "attack surface (fewer installed apps, least-privilege access) limits the damage a "
     "zero-day can do."),

    (["cve", "vulnerability database"],
     "CVE is a public catalog of known vulnerabilities. Checking your software's CVE "
     "history before adopting it can reveal how quickly its maintainers respond to "
     "security issues."),

    (["ddos", "denial of service"],
     "A DDoS attack floods a service with traffic to take it offline. For a website you "
     "run, a CDN or DDoS-protection service (e.g. Cloudflare) absorbs this kind of "
     "traffic."),

    (["brute force", "password guessing attack"],
     "Brute-force attacks try many password combinations quickly. Account lockouts after "
     "failed attempts, CAPTCHAs, and long unique passwords make this attack impractical."),

    (["sql injection"],
     "SQL injection lets an attacker manipulate a database through unvalidated input "
     "fields. Always use parameterized queries and never trust raw user input directly in "
     "a query."),

    (["xss", "cross site scripting"],
     "Cross-site scripting lets attackers inject malicious scripts into a webpage viewed "
     "by others. Sanitizing and escaping all user-supplied input before rendering it "
     "prevents this."),

    (["penetration test", "pen test", "ethical hacking"],
     "A penetration test is authorized, simulated hacking to find weaknesses before real "
     "attackers do. It should always be scoped, authorized in writing, and performed by "
     "a qualified tester."),

    (["bug bounty"],
     "A bug bounty program rewards researchers for responsibly reporting security flaws "
     "instead of exploiting them — a good way for organizations to crowdsource security "
     "testing."),

    (["endpoint protection", "antivirus", "which antivirus"],
     "A modern antivirus/endpoint protection tool plus regular OS updates covers most "
     "everyday threats. No single tool is perfect — safe browsing habits matter just as "
     "much."),

    (["sandbox", "sandboxing"],
     "Sandboxing runs untrusted code in an isolated environment so it can't affect the "
     "rest of the system — useful for safely testing a suspicious file before deciding "
     "whether it's safe."),

    (["air gap", "air-gapped"],
     "An air-gapped system has no network connection at all, used for extremely sensitive "
     "data. It protects against remote attacks but still requires physical security."),

    (["network segmentation"],
     "Splitting a network into separate zones (e.g. guest Wi-Fi separate from work "
     "devices) limits how far an attacker can move if one part is compromised."),

    (["cyber insurance"],
     "Cyber insurance can cover costs from a breach (legal, recovery, notification), but "
     "it doesn't replace good security practices — insurers often require baseline "
     "controls to be in place."),

    (["remote work security", "work from home security"],
     "Use a company VPN for work resources, keep your home Wi-Fi password strong, and "
     "avoid using personal, unmanaged devices for sensitive work tasks where possible."),
]

FALLBACK_RESPONSE = (
    "I don't have a specific tip for that yet. As a general rule: verify before you "
    "trust, keep software updated, use unique passwords with 2FA, and run anything "
    "suspicious through this app's scanners before opening it. Try asking about "
    "passwords, phishing, VPN, 2FA, malware, scams, or SSL."
)

GREETINGS = ["hi", "hello", "hey", "namaste", "hii", "helo"]

THANKS = ["thanks", "thank you", "thanks!", "shukriya", "dhanyavad"]


def _keyword_pattern(keyword: str) -> re.Pattern:
    """
    Build a word-boundary-safe regex for a keyword so short terms
    (e.g. "ip", "url") don't match inside unrelated words.
    """
    escaped = re.escape(keyword.strip())
    return re.compile(rf"(?<!\w){escaped}(?!\w)")


# Pre-compile patterns once at import time for speed.
_COMPILED_KB: list[tuple[list[re.Pattern], str]] = [
    ([_keyword_pattern(kw) for kw in keywords], tip)
    for keywords, tip in KNOWLEDGE_BASE
]




def query_groq_api(messages: list[dict[str, str]]) -> str:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return "Error: GROQ_API_KEY is not configured. Please add it to your .env file or save it in the Connections page."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data["choices"][0]["message"]["content"].strip()
        else:
            return f"Groq API Error (Status {response.status_code}): {response.text}"
    except Exception as e:
        return f"Failed to connect to Groq API: {str(e)}"


def get_offline_response(user_message: str) -> str | None:
    """
    Looks up user_message in KNOWLEDGE_BASE using compiled keyword patterns.
    Returns the best matching tip (highest score of keyword hits > 0), or None.
    """
    clean_msg = (user_message or "").strip().lower()
    if not clean_msg:
        return None
        
    # Check simple greetings
    if any(g == clean_msg or clean_msg.startswith(g + " ") for g in GREETINGS):
        return "Hello! I am CyberMind AI, your security assistant. Ask me anything about passwords, phishing, VPNs, malware, or our scanning tools!"
        
    if any(t == clean_msg or clean_msg.startswith(t + " ") for t in THANKS):
        return "You're welcome! Stay safe online, and let me know if you have more questions."

    best_tip = None
    best_score = 0
    
    for patterns, tip in _COMPILED_KB:
        score = 0
        for pattern in patterns:
            if pattern.search(clean_msg):
                score += 1
        if score > best_score:
            best_score = score
            best_tip = tip
            
    return best_tip


def get_chat_response(user_message: str) -> str:
    """
    Queries the Groq API for a contextual, intelligent chat response.
    If GROQ_API_KEY is not configured or the API request fails, falls back
    to the offline rule-based KNOWLEDGE_BASE.
    """
    msg = (user_message or "").strip()

    if not msg:
        return "Ask me anything about online safety — passwords, phishing, VPNs, 2FA, malware, scams, and more."

    # Check for GROQ API Key existence
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    if api_key:
        system_prompt = (
            "You are CyberMind AI, an advanced, professional cybersecurity chatbot. "
            "You have deep, comprehensive knowledge about the CyberMind AI project itself. Here is the project context:\n"
            "### About CyberMind AI:\n"
            "- **What is it?** CyberMind AI is a Streamlit-based, multi-tool cybersecurity risk-assessment and threat-intelligence dashboard (built as an M.Sc. Data Science project). It allows users to check the safety of a URL, website, domain, email, IP address, QR code, or file, and view aggregated analytics over their scan history.\n"
            "- **Scanner Modules & Capabilities:**\n"
            "  1. **URL Scanner:** Checks URLs for phishing/malicious indicators. Uses a RandomForest classifier (`phishing_url_model.pkl`, trained on the PhiUSIIL dataset with 235,795 samples and 50 features) for phishing/legitimate verdicts. Also uses a second model (`online_valid_model.pkl`) that predicts which real-world brand a phishing URL is impersonating based on 18 lexical URL features.\n"
            "  2. **Website Scanner:** Analyzes website security posture, including SSL/TLS certificate validity, security headers, and DNS records.\n"
            "  3. **Domain Scanner:** Performs WHOIS lookup, checks domain age, registrar reputation, and blacklist status.\n"
            "  4. **IP Scanner (IP Intelligence):** Checks IP reputation via AbuseIPDB, retrieves ISP/ASN/hostname via the IPinfo API, and geolocates IPs using a local MaxMind GeoLite2 City database (`.mmdb`, offline lookup, no API call needed for location).\n"
            "  5. **Email Scanner:** Checks SPF/DKIM/DMARC records, detects disposable email providers, and validates MX record presence.\n"
            "  6. **QR Code Scanner:** Decodes a QR code's embedded content and runs it through the same risk checks as the URL scanner before the user opens it.\n"
            "  7. **File Scanner / Malware Analysis:** Analyzes a file's signature/magic-bytes, extension, and metadata, using a RandomForest model (`file_signatures_model.pkl`) to classify risk as Low, Medium, or High.\n"
            "  8. **Analytics page:** Features scan trends, risk-level distribution, a live threat map, and a 'Most Targeted Countries' breakdown, all built from real scan history stored in a local SQLite database (`scan_history` table).\n"
            "  9. **ML Model Performance panel:** Displays transparent metrics (Accuracy, Precision, Recall, F1, ROC-AUC) of the trained models, computed via 5-fold Stratified Cross-Validation.\n"
            "- **External Threat Intelligence APIs Used:** Google Safe Browsing, VirusTotal, URLScan.io, AbuseIPDB, IPinfo.\n"
            "- **Tech Stack:** Python, Streamlit for UI, scikit-learn (RandomForestClassifier) + joblib for ML inference, SQLite for local scan history storage, MaxMind GeoLite2 for offline IP geolocation, and ReportLab for exporting PDF scan reports.\n"
            "- **Data Privacy:** Scan history is stored locally in SQLite and is not sent to third-party servers, except for the specific threat-intelligence API calls each scanner needs to perform its checks.\n"
            "- **Honesty Guardrails (Crucial):**\n"
            "  - **Is it fully offline?** No. Most scanners depend on live external APIs (Google Safe Browsing, VirusTotal, URLScan.io, AbuseIPDB, IPinfo) to function. Only the IP geolocation (via local mmdb) and the 4 ML model predictions are genuinely offline/local. If asked, explain this honestly.\n"
            "  - **Known Limitations:** The data-breach sector classifier model (`breaches_model.pkl`) has lower accuracy (~36%) due to a small training dataset of 515 samples. Do not oversell its reliability.\n\n"
            "Your primary function is to assist users with cybersecurity concepts, threat intelligence, "
            "security recommendations, and questions about the CyberMind AI system itself. "
            "Always answer questions about CyberMind AI (like what it is, how it works, what it does, why it is special) with complete, enthusiastic, and accurate details. "
            "Keep your responses helpful, precise, formatted clearly in Markdown, and directly related "
            "to cybersecurity, computer safety, and CyberMind AI. If the question is completely unrelated, "
            "gently remind the user that your expertise is in computer security and CyberMind AI."
        )
        
        # Build messages thread
        messages = [{"role": "system", "content": system_prompt}]
        
        # Retrieve recent history from session state
        active_page = st.session_state.get("active_page")
        if active_page == "AI Security Assistant":
            history = st.session_state.get("ai_page_chat_history", [])
        else:
            history = st.session_state.get("ai_chat_history", [])
            
        # Append recent 10 messages for context
        for role, text in history[-10:]:
            messages.append({
                "role": "user" if role == "user" else "assistant",
                "content": text
            })
            
        # Append active query
        messages.append({"role": "user", "content": user_message})
        
        # Send query to Groq
        response = query_groq_api(messages)
        if not response.startswith("Error") and not response.startswith("Failed") and not response.startswith("Groq API Error"):
            return response
            
    # Fallback to KNOWLEDGE_BASE
    offline_response = get_offline_response(user_message)
    if offline_response:
        return offline_response
        
    return FALLBACK_RESPONSE




# ---------------------------------------------------------------------------
# Auto-suggestions based on recent scan history already in session state
# ---------------------------------------------------------------------------
RISK_TIPS: dict[str, str] = {
    "URL Scanner": "A risky URL was scanned recently — avoid clicking it, and never enter credentials on it.",
    "Website Scanner": "A recently analyzed website looked risky — double-check its SSL certificate and domain age before trusting it.",
    "Domain Scanner": "A recently checked domain looked risky — newly registered or low-reputation domains are common in scams.",
    "Email Scanner": "A recently checked email address looked risky — be cautious with messages from it and avoid clicking its links.",
    "IP Scanner": "A recently checked IP address showed a poor reputation — avoid connections to/from it where possible.",
    "QR Code Scanner": "A recently scanned QR code looked risky — don't open the link it contained.",
    "File Scanner": "A recently scanned file looked risky — do not open or execute it, and consider deleting it.",
    "Malware Analysis": "A recent sample was flagged as malicious — isolate the affected device and run a full antivirus scan.",
}

RISKY_LEVELS = {"malicious", "suspicious", "high"}


def get_auto_suggestions() -> list[str]:
    """
    Reads existing scan history from session state (no new scans triggered)
    and returns short, offline, contextual security suggestions.
    """
    suggestions: list[str] = []

    try:
        histories: dict[str, Any] = st.session_state.get("histories", {})

        for scanner_name, entries in histories.items():
            for entry in entries[:3]:
                level = str(entry.get("level", "")).lower()
                if level in RISKY_LEVELS:
                    tip = RISK_TIPS.get(scanner_name)
                    if tip and tip not in suggestions:
                        suggestions.append(tip)
                    break
    except Exception as exc:
        logger.warning(f"AI Assistant: could not read scan history ({exc}).")

    if not suggestions:
        suggestions.append(
            "No risky scans detected recently. Keep scanning any new link, file, or QR "
            "code before you open it."
        )

    return suggestions


# ---------------------------------------------------------------------------
# Sidebar panel renderer
# ---------------------------------------------------------------------------
def render_ai_assistant_panel() -> None:
    """
    Renders the AI Assistant section inside the sidebar:
    - Auto security suggestions based on recent scans
    - A small offline rule-based chat box

    Fully offline — safe to call on every rerun, no external requests.
    """
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    with st.expander("🤖 AI Security Assistant", expanded=False):
        st.markdown("**Suggestions**")
        for tip in get_auto_suggestions():
            st.markdown(f"- {tip}")

        st.markdown("---")
        st.markdown("**Ask a question**")

        user_input = st.text_input(
            "Type your question",
            key="ai_assistant_input",
            label_visibility="collapsed",
            placeholder="e.g. How do I stay safe on public Wi-Fi?",
        )

        col_send, col_clear = st.columns([1, 1])
        with col_send:
            send_clicked = st.button("Ask", key="ai_assistant_send", use_container_width=True)
        with col_clear:
            clear_clicked = st.button("Clear chat", key="ai_assistant_clear", use_container_width=True)

        if clear_clicked:
            st.session_state.ai_chat_history = []
            st.rerun()

        if send_clicked and user_input.strip():
            response = get_chat_response(user_input)
            st.session_state.ai_chat_history.append(("user", user_input))
            st.session_state.ai_chat_history.append(("assistant", response))

        for role, text in st.session_state.ai_chat_history[-8:]:
            if role == "user":
                st.markdown(f"🧑 **You:** {text}")
            else:
                st.markdown(f"🤖 **Assistant:** {text}")