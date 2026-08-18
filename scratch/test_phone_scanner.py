"""
Scratch Verification Script: Phone Threat Intelligence & IPQS Integration
"""

import io
import sys
from pathlib import Path

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to sys.path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.validator import is_valid_phone, validate_scanner_input
from services.ipqs_service import ipqs_service
from services.phone_service import phone_service
from modules.phone_scanner import phone_scanner
from modules.scanner_engine import scanner_engine
from services.email_service import email_service


def test_validation():
    print("--- 1. Testing Phone Input Validation ---")
    valid_numbers = ["+91 9876543210", "+18005550199", "9876543210", "+447911123456"]
    invalid_numbers = ["123", "abc", "https://google.com", "user@example.com"]

    for num in valid_numbers:
        assert is_valid_phone(num), f"Should be valid: {num}"
        ok, msg = validate_scanner_input("Phone Threat Intelligence", num)
        assert ok, f"Input validation failed for {num}: {msg}"

    for num in invalid_numbers:
        assert not is_valid_phone(num), f"Should be invalid: {num}"

    print("✅ Input validation passed for all test vectors.")


def test_ipqs_and_phone_service():
    print("\n--- 2. Testing IPQS & Phone Service ---")
    res = phone_service.analyze("+91 9876543210")
    print(f"Target: {res['target']}")
    print(f"Country: {res['country']}")
    print(f"Carrier: {res['carrier']}")
    print(f"Line Type: {res['line_type']}")
    print(f"Scam Risk: {res['scam_risk']}")
    print(f"Fraud Score: {res['fraud_score']}")
    print(f"Reputation: {res['reputation']}")
    print(f"Recommendation: {res['recommendation']}")

    assert res["valid"] is True
    assert "India" in res["country"]
    print("✅ Phone service analysis verified successfully.")


def test_phone_scanner_module():
    print("\n--- 3. Testing PhoneScanner Module & Risk Engine ---")
    res = phone_scanner.analyze("+91 9876543210")
    assert res["success"] is True
    assert res["scanner"] == "phone"
    assert "risk" in res
    print(f"Unified Risk Score: {res['risk']['score']} / 100 ({res['risk']['level']})")
    print("✅ PhoneScanner module verified successfully.")


def test_scanner_engine_routing():
    print("\n--- 4. Testing Master Scanner Engine Auto-Detection ---")
    detected = scanner_engine.detect("+919876543210")
    print(f"Detected scanner for '+919876543210': {detected}")
    assert detected == "phone"

    scan_res = scanner_engine.scan("+919876543210")
    assert scan_res["success"] is True
    assert scan_res["scanner"] == "phone"
    print("✅ Scanner Engine routing verified successfully.")


def test_email_darkweb_exposure():
    print("\n--- 5. Testing Email Scanner Dark Web Exposure ---")
    res = email_service.analyze("test@example.com")
    assert "darkweb_exposure" in res
    print(f"Darkweb Status: {res['darkweb_exposure']['status']}")
    print("✅ Email Scanner Dark Web Exposure check verified.")


if __name__ == "__main__":
    print("==========================================================")
    print("     🛡️ CyberMind AI - Phone Intelligence Test Suite 🛡️     ")
    print("==========================================================")
    test_validation()
    test_ipqs_and_phone_service()
    test_phone_scanner_module()
    test_scanner_engine_routing()
    test_email_darkweb_exposure()
    print("==========================================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("==========================================================")
