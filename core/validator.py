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