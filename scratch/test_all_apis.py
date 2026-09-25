import os
import sys
import time
import json
import socket
import smtplib
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)

results = []

def record(name, key_name, status, status_code, latency_s, message, details=""):
    results.append({
        "name": name,
        "key_name": key_name,
        "status": status,
        "code": status_code,
        "latency": f"{latency_s:.2f}s",
        "message": message,
        "details": details
    })
    print(f"[{status}] {name} ({latency_s:.2f}s) -> Code: {status_code}, Msg: {message}")

print("=" * 70)
print("CYBERMIND AI - COMPREHENSIVE LIVE API HEALTH CHECK")
print("=" * 70)

# 1. GROQ CLOUD AI
groq_key = os.getenv("GROQ_API_KEY", "").strip()
if not groq_key:
    record("Groq Cloud AI", "GROQ_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        # Check models endpoint
        r_models = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {groq_key}"},
            timeout=10
        )
        lat = time.time() - t0
        if r_models.status_code == 200:
            models_data = [m["id"] for m in r_models.json().get("data", [])]
            # Try a quick test completion with active model
            # test models: llama-3.3-70b-versatile, llama-3.1-8b-instant
            test_model = "llama-3.3-70b-versatile" if "llama-3.3-70b-versatile" in models_data else (models_data[0] if models_data else "llama3-8b-8192")
            
            t1 = time.time()
            r_chat = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": test_model,
                    "messages": [{"role": "user", "content": "Respond with 'OK'"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            chat_lat = time.time() - t1
            if r_chat.status_code == 200:
                reply = r_chat.json()["choices"][0]["message"]["content"].strip()
                record("Groq Cloud AI", "GROQ_API_KEY", "PASS", 200, lat + chat_lat, f"Model '{test_model}' replied: {reply}", f"Available models count: {len(models_data)}")
            else:
                record("Groq Cloud AI", "GROQ_API_KEY", "FAIL", r_chat.status_code, lat + chat_lat, f"Chat test failed: {r_chat.text[:100]}", f"Models OK, chat error")
        else:
            record("Groq Cloud AI", "GROQ_API_KEY", "FAIL", r_models.status_code, lat, f"Auth/Request failed: {r_models.text[:100]}")
    except Exception as e:
        record("Groq Cloud AI", "GROQ_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 2. GOOGLE SAFE BROWSING
gsb_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
if not gsb_key:
    record("Google Safe Browsing", "GOOGLE_SAFE_BROWSING_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={gsb_key}"
        payload = {
            "client": {"clientId": "CyberMind-AI", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": "http://malware.testing.google.test/testing/malware/"}]
            }
        }
        r = requests.post(url, json=payload, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            matches = r.json().get("matches", [])
            record("Google Safe Browsing", "GOOGLE_SAFE_BROWSING_API_KEY", "PASS", 200, lat, f"Successfully queried. Found {len(matches)} test threat match.", str(matches[:1]))
        else:
            record("Google Safe Browsing", "GOOGLE_SAFE_BROWSING_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("Google Safe Browsing", "GOOGLE_SAFE_BROWSING_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 3. VIRUSTOTAL
vt_key = os.getenv("VIRUSTOTAL_API_KEY", "").strip()
if not vt_key:
    record("VirusTotal", "VIRUSTOTAL_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "https://www.virustotal.com/api/v3/domains/google.com"
        r = requests.get(url, headers={"x-apikey": vt_key, "User-Agent": "CyberMind AI/1.0"}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            stats = r.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            record("VirusTotal", "VIRUSTOTAL_API_KEY", "PASS", 200, lat, f"Domain check success. Harmless: {stats.get('harmless')}, Malicious: {stats.get('malicious')}")
        else:
            record("VirusTotal", "VIRUSTOTAL_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("VirusTotal", "VIRUSTOTAL_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 4. ABUSEIPDB
abuse_key = os.getenv("ABUSEIPDB_API_KEY", "").strip()
if not abuse_key:
    record("AbuseIPDB", "ABUSEIPDB_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "https://api.abuseipdb.com/api/v2/check"
        r = requests.get(url, headers={"Key": abuse_key, "Accept": "application/json"}, params={"ipAddress": "8.8.8.8", "maxAgeInDays": 90}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            record("AbuseIPDB", "ABUSEIPDB_API_KEY", "PASS", 200, lat, f"IP 8.8.8.8 check success. Abuse Score: {score}%")
        else:
            record("AbuseIPDB", "ABUSEIPDB_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("AbuseIPDB", "ABUSEIPDB_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 5. IPINFO
ipinfo_key = os.getenv("IPINFO_API_KEY", "").strip()
if not ipinfo_key:
    record("IPinfo", "IPINFO_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = f"https://ipinfo.io/8.8.8.8/json"
        r = requests.get(url, params={"token": ipinfo_key}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            org = data.get("org", "Unknown")
            country = data.get("country", "Unknown")
            record("IPinfo", "IPINFO_API_KEY", "PASS", 200, lat, f"IP 8.8.8.8 check success. Org: {org}, Country: {country}")
        else:
            record("IPinfo", "IPINFO_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("IPinfo", "IPINFO_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 6. URLSCAN.IO
urlscan_key = os.getenv("URLSCAN_API_KEY", "").strip()
if not urlscan_key:
    record("URLScan.io", "URLSCAN_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        # Check quota / user endpoint or search endpoint
        url = "https://urlscan.io/user/quotas/"
        r = requests.get(url, headers={"API-Key": urlscan_key, "User-Agent": "CyberMind AI/1.0"}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            record("URLScan.io", "URLSCAN_API_KEY", "PASS", 200, lat, f"Account active. Limits: {json.dumps(data)[:80]}")
        else:
            # Fallback test with search
            r2 = requests.get("https://urlscan.io/api/v1/search/?q=domain:google.com", headers={"API-Key": urlscan_key}, timeout=10)
            if r2.status_code == 200:
                record("URLScan.io", "URLSCAN_API_KEY", "PASS", 200, time.time() - t0, "Search query success.")
            else:
                record("URLScan.io", "URLSCAN_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("URLScan.io", "URLSCAN_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 7. ABSTRACTAPI IP INTELLIGENCE
abs_ip_key = os.getenv("ABSTRACTAPI_IP_KEY", "").strip()
if not abs_ip_key:
    record("AbstractAPI IP", "ABSTRACTAPI_IP_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "https://ip-intelligence.abstractapi.com/v1/"
        r = requests.get(url, params={"api_key": abs_ip_key, "ip_address": "8.8.8.8"}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            country = data.get("country", "Unknown")
            sec = data.get("security", {})
            record("AbstractAPI IP", "ABSTRACTAPI_IP_KEY", "PASS", 200, lat, f"Lookup 8.8.8.8 success. Country: {country}, Is VPN: {sec.get('is_vpn', False)}")
        else:
            record("AbstractAPI IP", "ABSTRACTAPI_IP_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("AbstractAPI IP", "ABSTRACTAPI_IP_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 8. ABSTRACTAPI PHONE INTELLIGENCE
abs_phone_key = os.getenv("ABSTRACTAPI_PHONE_KEY", "").strip()
if not abs_phone_key:
    record("AbstractAPI Phone", "ABSTRACTAPI_PHONE_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "https://phoneintelligence.abstractapi.com/v1/"
        r = requests.get(url, params={"api_key": abs_phone_key, "phone": "+14152007986"}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            valid = data.get("valid", False)
            carrier = data.get("carrier", "N/A")
            record("AbstractAPI Phone", "ABSTRACTAPI_PHONE_KEY", "PASS", 200, lat, f"Phone lookup success. Valid: {valid}, Carrier: {carrier}")
        else:
            record("AbstractAPI Phone", "ABSTRACTAPI_PHONE_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("AbstractAPI Phone", "ABSTRACTAPI_PHONE_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 9. NUMVERIFY PHONE INTELLIGENCE
numverify_key = os.getenv("NUMVERIFY_API_KEY", "").strip()
if not numverify_key:
    record("Numverify Phone", "NUMVERIFY_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "http://apilayer.net/api/validate"
        r = requests.get(url, params={"access_key": numverify_key, "number": "14152007986", "format": 1}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            if "error" in data:
                err_info = data["error"].get("info", data["error"].get("type", "Unknown error"))
                record("Numverify Phone", "NUMVERIFY_API_KEY", "FAIL", 200, lat, f"API returned error: {err_info}")
            else:
                valid = data.get("valid", False)
                carrier = data.get("carrier", "N/A")
                record("Numverify Phone", "NUMVERIFY_API_KEY", "PASS", 200, lat, f"Phone check success. Valid: {valid}, Carrier: {carrier}")
        else:
            record("Numverify Phone", "NUMVERIFY_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("Numverify Phone", "NUMVERIFY_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 10. VERIFICAREMAILS PHONE INTELLIGENCE
verificar_key = (os.getenv("VERIFICAREMAILS_API_KEY", "") or os.getenv("VERIFICAR_EMAILS_KEY", "")).strip()
if not verificar_key:
    record("VerificarEmails Phone", "VERIFICAREMAILS_API_KEY", "FAIL", "N/A", 0, "Key not found in .env")
else:
    t0 = time.time()
    try:
        url = "https://dashboard.verificaremails.com/myapi/phone/validate/single"
        r = requests.get(url, params={"auth-token": verificar_key, "term": "+14152007986"}, timeout=10)
        lat = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            record("VerificarEmails Phone", "VERIFICAREMAILS_API_KEY", "PASS", 200, lat, f"Check success: {json.dumps(data)[:80]}")
        else:
            record("VerificarEmails Phone", "VERIFICAREMAILS_API_KEY", "FAIL", r.status_code, lat, f"Response: {r.text[:150]}")
    except Exception as e:
        record("VerificarEmails Phone", "VERIFICAREMAILS_API_KEY", "FAIL", "ERR", time.time() - t0, str(e))

# 11. GMAIL SMTP SUPPORT AUTHENTICATION
smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_user = os.getenv("SMTP_USER", "").strip()
smtp_password = os.getenv("SMTP_PASSWORD", "").strip()

if not smtp_user or not smtp_password:
    record("Gmail SMTP Support", "SMTP_PASSWORD", "FAIL", "N/A", 0, "Credentials missing in .env")
else:
    t0 = time.time()
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.quit()
        lat = time.time() - t0
        record("Gmail SMTP Support", "SMTP_PASSWORD", "PASS", 235, lat, f"Successfully authenticated as {smtp_user}")
    except Exception as e:
        record("Gmail SMTP Support", "SMTP_PASSWORD", "FAIL", "ERR", time.time() - t0, str(e))

# 12. CRT.SH CERTIFICATE TRANSPARENCY
t0 = time.time()
try:
    url = "https://crt.sh/?q=google.com&output=json"
    r = requests.get(url, headers={"User-Agent": "CyberMind AI/1.0"}, timeout=12)
    lat = time.time() - t0
    if r.status_code == 200:
        data = r.json()
        record("crt.sh CT Logs", "Public API", "PASS", 200, lat, f"Found {len(data)} certificate transparency records")
    else:
        record("crt.sh CT Logs", "Public API", "FAIL", r.status_code, lat, f"Response: {r.text[:100]}")
except Exception as e:
    record("crt.sh CT Logs", "Public API", "FAIL", "ERR", time.time() - t0, str(e))

# 13. DNS & WHOIS
t0 = time.time()
try:
    import dns.resolver
    answers = dns.resolver.resolve("google.com", "A")
    lat = time.time() - t0
    ips = [str(a) for a in answers]
    record("DNS Resolution", "System Resolver", "PASS", 0, lat, f"Resolved google.com -> {ips[:2]}")
except Exception as e:
    record("DNS Resolution", "System Resolver", "FAIL", "ERR", time.time() - t0, str(e))

t0 = time.time()
try:
    import whois
    w = whois.whois("google.com")
    lat = time.time() - t0
    registrar = getattr(w, "registrar", "Unknown")
    record("WHOIS Service", "WHOIS Protocol", "PASS", 0, lat, f"WHOIS query google.com success. Registrar: {registrar}")
except Exception as e:
    record("WHOIS Service", "WHOIS Protocol", "FAIL", "ERR", time.time() - t0, str(e))

print("=" * 70)
print(f"TOTAL APIS TESTED: {len(results)}")
print(f"PASSED: {sum(1 for r in results if r['status'] == 'PASS')}")
print(f"FAILED: {sum(1 for r in results if r['status'] == 'FAIL')}")
print("=" * 70)
