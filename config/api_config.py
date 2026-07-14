"""
API Configuration
"""

import os

from config.env import *


def _get_clean_env(key: str) -> str | None:
    val = os.getenv(key)
    return val.strip() if val else None

GOOGLE_SAFE_BROWSING_API_KEY = _get_clean_env(
    "GOOGLE_SAFE_BROWSING_API_KEY"
)

VIRUSTOTAL_API_KEY = _get_clean_env(
    "VIRUSTOTAL_API_KEY"
)

URLSCAN_API_KEY = _get_clean_env(
    "URLSCAN_API_KEY"
)

ABUSEIPDB_API_KEY = _get_clean_env(
    "ABUSEIPDB_API_KEY"
)

IPINFO_API_KEY = _get_clean_env(
    "IPINFO_API_KEY"
)


HEADERS = {
    "User-Agent": "CyberMind AI/1.0"
}