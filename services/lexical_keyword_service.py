"""
CyberMind AI

Lexical Keyword Service
Scans target strings (URLs, domains, filenames, email addresses) for suspicious/alarming keywords.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from core.logger import logger

HIGH_SEVERITY_DEFAULT = {
    "malicious", "malware", "virus", "trojan", "ransomware", "hack", "hacked", "exploit",
    "phish", "phishing", "spyware", "keylogger", "backdoor", "rootkit",
    "botnet", "payload", "stealer", "infostealer", "rat", "fake", "scam",
    "fraud", "cheat", "spoof", "attack", "credential", "bypass", "login-page", "signin-verify"
}

MEDIUM_SEVERITY_DEFAULT = {
    "secure", "security", "verify", "verification", "account", "billing", "update",
    "login", "signin", "confirm", "confirm-identity", "secure-login",
    "account-suspended", "update-billing", "unlock-account", "urgent-action", "verify-paypal",
    "login-verify", "security-update", "banking-secure", "account-update",
    "passcode-reset", "wallet-connect", "login-auth", "auth-verify", "customer-support-help",
    "bank", "paypal"
}


class LexicalKeywordService:
    def __init__(self) -> None:
        self.high_severity: set[str] = set(HIGH_SEVERITY_DEFAULT)
        self.medium_severity: set[str] = set(MEDIUM_SEVERITY_DEFAULT)
        self.popular_domains: set[str] = set()
        self._load_keywords()
        self._load_popular_domains()

    def _load_popular_domains(self) -> None:
        try:
            pop_path = Path(__file__).parent.parent / "data" / "domain" / "popular_domains.json"
            if pop_path.exists():
                with open(pop_path, "r", encoding="utf-8") as f:
                    domains = json.load(f)
                    if isinstance(domains, list):
                        self.popular_domains = set(d.lower().strip() for d in domains if isinstance(d, str))
        except Exception as exc:
            logger.warning("Could not load popular_domains.json in lexical keyword service: %s", exc)

    def _load_keywords(self) -> None:
        try:
            kw_path = Path(__file__).parent.parent / "data" / "security" / "suspicious_keywords.json"
            if kw_path.exists():
                with open(kw_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "high_severity" in data:
                        self.high_severity.update(data["high_severity"])
                    if "medium_severity" in data:
                        # Exclude generic everyday terms like support and service
                        filtered_medium = [
                            kw for kw in data["medium_severity"]
                            if kw not in ("support", "service")
                        ]
                        self.medium_severity.update(filtered_medium)
        except Exception as exc:
            logger.warning("Could not load suspicious_keywords.json: %s", exc)

    def check_suspicious_keywords(self, target: str) -> dict[str, Any]:
        """
        Scans target string for suspicious keywords.
        Returns:
            {
                "matched_keywords": list[str],
                "has_suspicious_keywords": bool,
                "severity": "high" | "medium" | "none"
            }
        """
        if not target:
            return {
                "matched_keywords": [],
                "has_suspicious_keywords": False,
                "severity": "none"
            }

        target_lower = str(target).lower()

        # Check if target belongs to a trusted popular domain
        target_domain = target_lower
        if "://" in target_domain:
            target_domain = target_domain.split("://")[1].split("/")[0].split(":")[0]
        elif "@" in target_domain:
            target_domain = target_domain.split("@")[1].split("/")[0].split(":")[0]
        elif "/" in target_domain:
            target_domain = target_domain.split("/")[0].split(":")[0]
        if ":" in target_domain:
            target_domain = target_domain.split(":")[0]
        if target_domain.startswith("www."):
            target_domain = target_domain[4:]

        is_popular = any(
            target_domain == pop or target_domain.endswith("." + pop)
            for pop in self.popular_domains
        )

        high_matches = [kw for kw in sorted(self.high_severity, key=len, reverse=True) if kw in target_lower]
        
        # Authentic popular domains are exempt from generic medium keywords (e.g. account, login, update)
        if is_popular:
            medium_matches = []
        else:
            medium_matches = [kw for kw in sorted(self.medium_severity, key=len, reverse=True) if kw in target_lower and kw not in high_matches]

        all_matched = high_matches + medium_matches
        severity = "none"
        if high_matches:
            severity = "high"
        elif medium_matches:
            severity = "medium"

        return {
            "matched_keywords": all_matched,
            "has_suspicious_keywords": len(all_matched) > 0,
            "severity": severity
        }


lexical_keyword_service = LexicalKeywordService()
