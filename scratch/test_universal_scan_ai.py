import os
import sys

sys.path.insert(0, os.path.abspath("."))

from modules.universal_scan_module import universal_scan_module
from modules.ai_summary_module import ai_summary_module

def test_universal_scan_ai():
    print("--- Testing Universal Scan AI Integration ---")
    
    # 1. Test URL Input
    res_url = universal_scan_module.analyze("https://malware-site.net")
    print("Universal Scan URL Result:", res_url)
    assert res_url["success"] is True
    assert res_url["input_type"] == "url"
    
    summary_url = ai_summary_module.generate_summary(res_url)
    print("Generated AI Summary for URL:", summary_url)
    assert summary_url is not None and len(summary_url) > 10

    # 2. Test Email Input
    res_email = universal_scan_module.analyze("phishing@malicious.com")
    print("Universal Scan Email Result:", res_email)
    assert res_email["success"] is True
    assert res_email["input_type"] == "email"

    summary_email = ai_summary_module.generate_summary(res_email)
    print("Generated AI Summary for Email:", summary_email)
    assert summary_email is not None and len(summary_email) > 10

    # 3. Test Domain Input
    res_dom = universal_scan_module.analyze("malicious-domain.com")
    print("Universal Scan Domain Result:", res_dom)
    assert res_dom["success"] is True
    assert res_dom["input_type"] == "domain"

    summary_dom = ai_summary_module.generate_summary(res_dom)
    print("Generated AI Summary for Domain:", summary_dom)
    assert summary_dom is not None and len(summary_dom) > 10

    print("\nSUCCESS: Universal Scan AI Integration Passed!")

if __name__ == "__main__":
    test_universal_scan_ai()
