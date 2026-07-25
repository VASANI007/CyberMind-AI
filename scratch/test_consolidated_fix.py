import os
import sys
import time
import socket

sys.path.insert(0, os.path.abspath("."))

from modules.ai_summary_module import ai_summary_module
from app import compute_scan_display
from services.whois_service import whois_service

def test_bug_a_and_summary():
    print("--- Testing Bug A: AI Summary ---")
    
    # Test case URL scan: 100/100 Critical
    url_scan_result = {
        "value": "http://testsafebrowsing.appspot.com/s/malware.html",
        "risk_score": 100,
        "risk_level": "Critical",
        "raw": {
            "risk": {
                "score": 100,
                "level": "Critical",
                "reasons": ["Google Safe Browsing flagged malware", "Malicious URL path"]
            }
        }
    }
    
    summary = ai_summary_module.generate_summary(url_scan_result)
    print("Generated Summary:", summary)
    assert "testsafebrowsing.appspot.com" in summary
    assert "100" in summary
    assert "appears to be **SAFE**" not in summary  # correctly flagged as HIGH RISK / Critical
    print("SUCCESS: Bug A Test Passed!")

def test_bug_b_c_d_e_f():
    print("\n--- Testing Bugs B, C, D, E, F ---")
    
    # Case 1: File Scanner
    file_result = {
        "value": "test_audio.m4a",
        "risk_score": 65,
        "risk_level": "Medium",
        "duration": "0.30 sec",
        "raw": {
            "analysis": {
                "lexical": {"entropy": 6.8}
            }
        }
    }
    d_file = compute_scan_display(file_result, scanner_key="File Scanner")
    assert d_file["threat_desc"] == "Suspicious file"  # Bug C
    assert d_file["has_real_ml"] is False  # Bug B
    assert d_file["ml_card_title"] == "Threat Assessment"
    assert d_file["ml_subtitle"] == "Risk-Derived Estimate"
    print("SUCCESS: File Scanner Display Test Passed!")

    # Case 2: IP Scanner
    ip_result = {
        "value": "185.220.101.1",
        "risk_score": 50,
        "risk_level": "Medium",
        "duration": "0.40 sec",
        "raw": {}
    }
    d_ip = compute_scan_display(ip_result, scanner_key="IP Scanner")
    assert d_ip["threat_desc"] == "Suspicious host"  # Bug C
    assert d_ip["ml_card_title"] == "Threat Assessment"
    assert d_ip["ml_subtitle"] == "Risk-Derived Estimate"  # Bug B: Not fake 50.0% confidence
    print("SUCCESS: IP Scanner Display Test Passed!")

    # Case 3: Domain Scanner
    dom_result = {
        "value": "malicious-domain.com",
        "risk_score": 23,
        "risk_level": "Low",
        "duration": "0.50 sec",
        "raw": {}
    }
    d_dom = compute_scan_display(dom_result, scanner_key="Domain Scanner")
    summary_dom = ai_summary_module.generate_summary(dom_result)
    assert "malicious-domain.com" in summary_dom
    assert "23" in summary_dom
    print("SUCCESS: Domain Scanner Test Passed!")

    # Case 4: Website Scanner with HTTPS scheme
    web_result = {
        "value": "https://malware-site.net",
        "risk_score": 15,
        "risk_level": "Low",
        "duration": "0.35 sec",
        "raw": {}
    }
    d_web = compute_scan_display(web_result, scanner_key="Website Scanner")
    # malware-site.net cannot be reached over TLS, so verify_https returns False
    assert d_web["is_https"] == "No" # Bug E false positive fixed
    print("SUCCESS: Website Scanner Test Passed!")

    # Case 5: URL Scanner with http:// scheme
    url_http_result = {
        "value": "http://testsafebrowsing.appspot.com/s/malware.html",
        "risk_score": 100,
        "risk_level": "Critical",
        "duration": "0.25 sec",
        "raw": {}
    }
    d_url = compute_scan_display(url_http_result, scanner_key="URL Scanner")
    assert d_url["is_https"] == "No"  # Bug E false positive fixed for plain http://
    assert d_url["threat_desc"] == "Threat flagged"
    print("SUCCESS: URL Scanner Test Passed!")

    # Case 6: Email Scanner
    email_result = {
        "value": "info@secure.org",
        "risk_score": 15,
        "risk_level": "Safe",
        "duration": "0.20 sec",
        "raw": {}
    }
    d_email = compute_scan_display(email_result, scanner_key="Email Scanner")
    assert d_email["threat_desc"] == "No immediate threat"
    assert d_email["ml_card_title"] == "Threat Assessment"
    summary_email = ai_summary_module.generate_summary(email_result)
    assert "info@secure.org" in summary_email
    print("SUCCESS: Email Scanner Test Passed!")

    # Mock Data Warning Test (Bug F)
    mock_result = {
        "value": "example.com",
        "risk_score": 50,
        "risk_level": "Medium",
        "is_mock": True,
        "scan_error": "Connection timed out",
        "raw": {"is_mock": True}
    }
    d_mock = compute_scan_display(mock_result, scanner_key="Domain Scanner")
    assert d_mock["simulated"] is True
    assert d_mock["scan_error"] == "Connection timed out"
    print("SUCCESS: Mock Data Warning Test Passed!")

def test_bug_g_and_h():
    print("\n--- Testing Bug G (WHOIS Timeout) and Bug H ---")
    orig_timeout = socket.getdefaulttimeout()
    t0 = time.time()
    res = whois_service.lookup("malicious-domain.com")
    elapsed = time.time() - t0
    print(f"WHOIS lookup completed in {elapsed:.2f} seconds.")
    assert elapsed < 10.0  # Must finish within strict timeout bound (6 sec timeout + slight overhead)
    assert socket.getdefaulttimeout() == orig_timeout  # Global timeout properly restored
    print("SUCCESS: Bug G WHOIS Timeout Test Passed!")

if __name__ == "__main__":
    test_bug_a_and_summary()
    test_bug_b_c_d_e_f()
    test_bug_g_and_h()
    print("\nALL CONSOLIDATED & PERFORMANCE FIX TESTS PASSED SUCCESSFULLY!")
