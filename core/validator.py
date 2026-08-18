"""
===========================================================
CyberMind AI
Input Validation Utilities
===========================================================
"""

from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse

from core.constants import (
    MAX_DOMAIN_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_FILE_SIZE_MB,
    MAX_URL_LENGTH,
    SUPPORTED_FILE_EXTENSIONS,
)


# Regular Expressions


EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

DOMAIN_REGEX = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}$"
)

MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")

SHA1_REGEX = re.compile(r"^[a-fA-F0-9]{40}$")

SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")



# URL


def is_valid_url(url: str) -> bool:
    """
    Validate URL.
    """

    if not isinstance(url, str):

        return False

    url = url.strip()

    if len(url) > MAX_URL_LENGTH:

        return False

    try:

        result = urlparse(url)

        return (

            result.scheme in ("http", "https")

            and

            bool(result.netloc)

        )

    except Exception:

        return False



# Domain


def is_valid_domain(domain: str) -> bool:
    """
    Validate domain.
    """

    if not isinstance(domain, str):

        return False

    domain = domain.strip().lower()

    if len(domain) > MAX_DOMAIN_LENGTH:

        return False

    return bool(DOMAIN_REGEX.fullmatch(domain))



# Email


def is_valid_email(email: str) -> bool:
    """
    Validate email.
    """

    if not isinstance(email, str):

        return False

    email = email.strip()

    if len(email) > MAX_EMAIL_LENGTH:

        return False

    return bool(EMAIL_REGEX.fullmatch(email))



# IPv4


def is_valid_ipv4(ip: str) -> bool:
    """
    Validate IPv4.
    """

    try:

        return isinstance(
            ipaddress.ip_address(ip),
            ipaddress.IPv4Address
        )

    except ValueError:

        return False



# IPv6


def is_valid_ipv6(ip: str) -> bool:
    """
    Validate IPv6.
    """

    try:

        return isinstance(
            ipaddress.ip_address(ip),
            ipaddress.IPv6Address
        )

    except ValueError:

        return False



# IP


def is_valid_ip(ip: str) -> bool:
    """
    Validate any IP.
    """

    return (

        is_valid_ipv4(ip)

        or

        is_valid_ipv6(ip)

    )



# MD5


def is_valid_md5(value: str) -> bool:
    """
    Validate MD5 hash.
    """

    return bool(MD5_REGEX.fullmatch(value))



# SHA1


def is_valid_sha1(value: str) -> bool:
    """
    Validate SHA1 hash.
    """

    return bool(SHA1_REGEX.fullmatch(value))



# SHA256


def is_valid_sha256(value: str) -> bool:
    """
    Validate SHA256 hash.
    """

    return bool(SHA256_REGEX.fullmatch(value))



# Port


def is_valid_port(port: int) -> bool:
    """
    Validate TCP/UDP port.
    """

    return isinstance(port, int) and 1 <= port <= 65535



# File Extension


def is_supported_extension(filename: str) -> bool:
    """
    Check supported file extension.
    """

    extension = Path(filename).suffix.lower()

    return extension in SUPPORTED_FILE_EXTENSIONS



# File Size


def is_allowed_file_size(size_bytes: int) -> bool:
    """
    Validate maximum file size.
    """

    size_mb = size_bytes / (1024 * 1024)

    return size_mb <= MAX_FILE_SIZE_MB



# Hostname


def is_valid_hostname(hostname: str) -> bool:
    """
    Validate hostname.
    """

    return is_valid_domain(hostname)



# QR Payload


def contains_url(text: str) -> bool:
    """
    Check if payload contains URL.
    """

    return bool(

        re.search(

            r"https?://",

            text,

            re.IGNORECASE

        )

    )


def validate_scanner_input(scanner_key: str, value: str) -> tuple[bool, str]:
    """
    Validate user input for a given scanner page.
    Returns (is_valid: bool, error_message: str).
    """
    if not isinstance(value, str):
        return False, "Input must be a valid string."

    val = value.strip()
    if not val:
        label = scanner_key.lower().replace("scanner", "").strip()
        return False, f"Please enter a {label} first."

    val_lower = val.lower()

    if scanner_key in ("Domain Scanner", "Domain Intelligence"):
        if val_lower.startswith(("http://", "https://")) or "/" in val:
            return False, "⚠️ Invalid Domain format: You entered a URL. Domain Scanner expects a plain domain name without 'http://', 'https://', or paths (e.g., 'google.com'). Please use the URL Scanner for full URLs."
        if "@" in val:
            return False, "⚠️ Invalid Domain format: You entered an email address. Domain Scanner expects a domain name (e.g., 'example.com'). Please use the Email Scanner."
        if is_valid_ip(val):
            return False, "⚠️ Invalid Domain format: You entered an IP address. Domain Scanner expects a domain name (e.g., 'example.com'). Please use the IP Scanner."
        if not is_valid_domain(val):
            return False, "⚠️ Invalid Domain format. Please enter a valid domain name (e.g., google.com or example.co.uk)."
        return True, ""

    elif scanner_key in ("URL Scanner", "URL"):
        if "@" in val and not (val_lower.startswith("http://") or val_lower.startswith("https://")):
            return False, "⚠️ Invalid URL format: You entered an email address. Please use the Email Scanner."
        if is_valid_ip(val):
            return False, "⚠️ Invalid URL format: If scanning a web server IP, include protocol (e.g., http://8.8.8.8) or use the IP Scanner."
        if not is_valid_url(val):
            if not val_lower.startswith(("http://", "https://")) and is_valid_url("https://" + val):
                pass
            else:
                return False, "⚠️ Invalid URL format. Please enter a valid URL starting with http:// or https:// (e.g., https://example.com/path)."
        return True, ""

    elif scanner_key in ("Website Scanner", "Website Analyzer"):
        if "@" in val:
            return False, "⚠️ Invalid Website address: You entered an email address. Please use the Email Scanner."
        if is_valid_ip(val):
            return False, "⚠️ Invalid Website address: You entered a raw IP address. If scanning a web IP, enter http://IP or use the IP Scanner."
        if not (is_valid_url(val) or is_valid_domain(val) or is_valid_url("https://" + val)):
            return False, "⚠️ Invalid Website address. Please enter a valid website URL or domain (e.g., https://example.com or example.com)."
        return True, ""

    elif scanner_key in ("IP Scanner", "IP Intelligence"):
        if val_lower.startswith(("http://", "https://")) or "/" in val:
            return False, "⚠️ Invalid IP address: You entered a URL. IP Scanner expects a numerical IPv4 or IPv6 address (e.g., 8.8.8.8). Please use the URL Scanner."
        if "@" in val:
            return False, "⚠️ Invalid IP address: You entered an email address. Please use the Email Scanner."
        if is_valid_domain(val):
            return False, "⚠️ Invalid IP address: You entered a domain name. IP Scanner expects a numerical IPv4 or IPv6 address (e.g., 8.8.8.8). Please use the Domain Scanner."
        if not is_valid_ip(val):
            return False, "⚠️ Invalid IP address format. Please enter a valid IPv4 or IPv6 address (e.g., 8.8.8.8 or 192.168.1.1)."
        return True, ""

    elif scanner_key in ("Email Scanner", "Email Intelligence"):
        if val_lower.startswith(("http://", "https://")):
            return False, "⚠️ Invalid Email format: You entered a URL. Please use the URL Scanner."
        if is_valid_domain(val):
            return False, "⚠️ Invalid Email format: You entered a domain name. Email Scanner expects an email address with '@' (e.g., user@example.com). Please use the Domain Scanner."
        if is_valid_ip(val):
            return False, "⚠️ Invalid Email format: You entered an IP address. Please use the IP Scanner."
        if not is_valid_email(val):
            return False, "⚠️ Invalid Email format. Please enter a valid email address (e.g., user@example.com)."
        return True, ""

    elif scanner_key in ("File Scanner", "File Analyzer"):
        if is_valid_md5(val) or is_valid_sha1(val) or is_valid_sha256(val):
            return True, ""
        if Path(val).suffix and is_supported_extension(val):
            return True, ""
        return False, "⚠️ Invalid File target or hash. Please enter a valid MD5 (32 hex), SHA1 (40 hex), or SHA256 (64 hex) hash, or upload a supported file."

    elif scanner_key == "Universal Scan":
        if is_valid_email(val):
            return True, ""
        if is_valid_ip(val):
            return True, ""
        if is_valid_md5(val) or is_valid_sha1(val) or is_valid_sha256(val):
            return True, ""
        if is_valid_domain(val):
            return True, ""
        if is_valid_url(val):
            return True, ""
        if not val_lower.startswith(("http://", "https://")) and "/" in val:
            host_part = val.split("/")[0].split(":")[0]
            if is_valid_domain(host_part) or is_valid_ip(host_part):
                return True, ""

        return False, "⚠️ Unrecognized scan target. Please enter a valid URL, Domain, IP address, Email, or File Hash."


    return True, ""