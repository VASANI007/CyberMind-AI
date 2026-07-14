"""
CyberMind AI
Universal Scan Module Tests
"""

from __future__ import annotations

import pytest
from modules.universal_scan_module import universal_scan_module

def test_classify_input():
    assert universal_scan_module.classify_input("google.com") == "domain"
    assert universal_scan_module.classify_input("sub.domain.co.uk") == "domain"
    
    assert universal_scan_module.classify_input("abc@gmail.com") == "email"
    assert universal_scan_module.classify_input("test.user@company.co") == "email"
    
    assert universal_scan_module.classify_input("http://example.com") == "url"
    assert universal_scan_module.classify_input("https://site.org/path/to/page?q=1") == "url"
    assert universal_scan_module.classify_input("domain.com/path") == "url"

def test_analyze_email():
    res = universal_scan_module.analyze("test@gmail.com")
    assert res["success"] is True
    assert res["input_type"] == "email"
    assert res["value"] == "test@gmail.com"
    assert "risk_score" in res
    assert "risk_level" in res
    assert "details" in res
    
    details = res["details"]
    assert details["input_type"] == "email"
    assert "is_valid" in details
    assert "mx_available" in details
    assert "is_disposable" in details
    assert "breach_found" in details

def test_analyze_domain():
    res = universal_scan_module.analyze("google.com")
    assert res["success"] is True
    assert res["input_type"] == "domain"
    assert res["value"] == "google.com"
    assert "risk_score" in res
    
    details = res["details"]
    assert details["input_type"] == "domain"
    assert "registrar" in details
    assert "ssl_valid" in details
    assert "ips" in details

def test_analyze_url():
    res = universal_scan_module.analyze("https://google.com")
    assert res["success"] is True
    assert res["input_type"] == "url"
    
    details = res["details"]
    assert details["input_type"] == "url"
    assert "ssl_valid" in details
    assert "redirect_count" in details
    assert "is_malicious" in details
