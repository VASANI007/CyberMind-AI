import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.validator import validate_scanner_input


def test_validation():
    print("=== Testing Core Validator ===")

    # Domain Scanner Tests
    test_cases_domain = [
        ("google.com", True),
        ("sub.example.co.uk", True),
        ("https://google.com", False),
        ("google.com/path", False),
        ("user@google.com", False),
        ("8.8.8.8", False),
        ("invalid..domain", False),
    ]

    for val, expected in test_cases_domain:
        ok, msg = validate_scanner_input("Domain Scanner", val)
        assert ok == expected, f"Domain test failed for '{val}': expected {expected}, got {ok} ({msg})"
        print(f"[Domain] '{val}' -> ok={ok}, msg='{msg}'")

    # URL Scanner Tests
    test_cases_url = [
        ("https://google.com/search?q=123", True),
        ("http://example.org", True),
        ("user@gmail.com", False),
        ("8.8.8.8", False),
    ]

    for val, expected in test_cases_url:
        ok, msg = validate_scanner_input("URL Scanner", val)
        assert ok == expected, f"URL test failed for '{val}': expected {expected}, got {ok} ({msg})"
        print(f"[URL] '{val}' -> ok={ok}, msg='{msg}'")

    # IP Scanner Tests
    test_cases_ip = [
        ("8.8.8.8", True),
        ("192.168.1.1", True),
        ("2001:db8::1", True),
        ("https://8.8.8.8", False),
        ("google.com", False),
        ("user@domain.com", False),
        ("999.999.999.999", False),
    ]

    for val, expected in test_cases_ip:
        ok, msg = validate_scanner_input("IP Scanner", val)
        assert ok == expected, f"IP test failed for '{val}': expected {expected}, got {ok} ({msg})"
        print(f"[IP] '{val}' -> ok={ok}, msg='{msg}'")

    # Email Scanner Tests
    test_cases_email = [
        ("support@google.com", True),
        ("user.name+tag@example.co.in", True),
        ("https://google.com", False),
        ("google.com", False),
        ("8.8.8.8", False),
        ("invalid_email_format", False),
    ]

    for val, expected in test_cases_email:
        ok, msg = validate_scanner_input("Email Scanner", val)
        assert ok == expected, f"Email test failed for '{val}': expected {expected}, got {ok} ({msg})"
        print(f"[Email] '{val}' -> ok={ok}, msg='{msg}'")

    # Universal Scan Tests
    test_cases_universal = [
        ("support@google.com", True),
        ("8.8.8.8", True),
        ("google.com", True),
        ("https://google.com", True),
        ("d41d8cd98f00b204e9800998ecf8427e", True), # MD5
        ("invalid_random_string_123!!", False),
    ]

    for val, expected in test_cases_universal:
        ok, msg = validate_scanner_input("Universal Scan", val)
        assert ok == expected, f"Universal test failed for '{val}': expected {expected}, got {ok} ({msg})"
        print(f"[Universal] '{val}' -> ok={ok}, msg='{msg}'")

    print("\n✅ ALL VALIDATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_validation()
