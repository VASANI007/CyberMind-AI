import os
import sys

sys.path.insert(0, os.path.abspath("."))

from modules.risk_engine import risk_engine
from services.lexical_keyword_service import lexical_keyword_service
from modules.domain_scanner import domain_scanner
from modules.website_scanner import website_scanner

def test_keyword_detection():
    print("--- Test 1: Lexical Keyword Detection ---")
    res1 = lexical_keyword_service.check_suspicious_keywords("https://malware-site.net")
    print("malware-site.net:", res1)
    assert res1["has_suspicious_keywords"] is True
    assert "malware" in res1["matched_keywords"]
    assert res1["severity"] == "high"

    res2 = lexical_keyword_service.check_suspicious_keywords("https://paypal-verify-account.com")
    print("paypal-verify-account.com:", res2)
    assert res2["has_suspicious_keywords"] is True
    assert res2["severity"] in ("high", "medium")

    res3 = lexical_keyword_service.check_suspicious_keywords("google.com")
    print("google.com:", res3)
    assert res3["has_suspicious_keywords"] is False
    assert res3["severity"] == "none"
    print("SUCCESS: Lexical Keyword Detection Passed!")

def test_risk_engine_unverified_and_keywords():
    print("\n--- Test 2: Risk Engine Scoring & Unverified Level ---")
    
    # 1. Google (Clean & High Completeness)
    google_report = {
        "reputation": {"score": 95},
        "blacklist": {"detected": False},
        "ssl": {"valid": True},
        "google_safe_browsing": {"safe": True},
        "virustotal": {"malicious": 0},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("google.com")
    }
    risk_g = risk_engine.calculate(google_report)
    print("Google Risk Output:", risk_g)
    assert risk_g["level"] == "Safe"
    assert risk_g["score"] < 20

    # 2. malware-site.net (Has High Severity Keyword "malware")
    malware_report = {
        "reputation": {},  # missing source
        "blacklist": {},   # missing source
        "ssl": {"valid": False},
        "google_safe_browsing": {},
        "virustotal": {},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("malware-site.net")
    }
    risk_m = risk_engine.calculate(malware_report)
    print("malware-site.net Risk Output:", risk_m)
    assert risk_m["level"] != "Safe"
    assert risk_m["score"] >= 35
    assert any("malware" in r for r in risk_m["reasons"])

    # 3. Unverifiable domain (Low score, low completeness < 50%, no keywords)
    unverified_report = {
        "reputation": {},
        "blacklist": {},
        "ssl": {},
        "google_safe_browsing": {},
        "virustotal": {},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("obscure-domain.xy")
    }
    risk_u = risk_engine.calculate(unverified_report)
    print("Unverifiable Target Risk Output:", risk_u)
    assert risk_u["level"] == "Unverified"

    # 4. malicious-domain.com (From user screenshot: must be flagged with high keyword score)
    malicious_domain_report = {
        "reputation": {},
        "blacklist": {},
        "ssl": {"valid": False},
        "google_safe_browsing": {},
        "virustotal": {},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("malicious-domain.com")
    }
    risk_md = risk_engine.calculate(malicious_domain_report)
    print("malicious-domain.com Risk Output:", risk_md)
    assert risk_md["level"] not in ("Safe", "Low")
    assert risk_md["score"] >= 40

    # 5. info@secure.org (From user screenshot: "secure" keyword match)
    secure_org_report = {
        "reputation": {},
        "blacklist": {},
        "ssl": {"valid": True},
        "google_safe_browsing": {},
        "virustotal": {},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("info@secure.org")
    }
    risk_so = risk_engine.calculate(secure_org_report)
    print("info@secure.org Risk Output:", risk_so)
    assert risk_so["level"] in ("Unverified", "Low", "Medium")

    # 6. GitHub.com (Clean & High Completeness)
    github_report = {
        "reputation": {"score": 90},
        "blacklist": {"detected": False},
        "ssl": {"valid": True},
        "google_safe_browsing": {"safe": True},
        "virustotal": {"malicious": 0},
        "lexical_keywords": lexical_keyword_service.check_suspicious_keywords("github.com")
    }
    risk_gh = risk_engine.calculate(github_report)
    print("GitHub Risk Output:", risk_gh)
    assert risk_gh["level"] == "Safe"

    print("SUCCESS: Risk Engine Unverified & Keywords Test Passed!")

if __name__ == "__main__":
    test_keyword_detection()
    test_risk_engine_unverified_and_keywords()
    print("\nALL VERIFICATION CHECKLIST TESTS PASSED SUCCESSFULLY!")
