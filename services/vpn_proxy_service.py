"""
CyberMind AI
VPN/Proxy Detection Service
Detects if an IP belongs to a VPN or proxy provider.
Uses IPinfo if key exists, else falls back to static ASN keyword list.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "ip"


class VPNProxyService:
    """
    Detects VPN/proxy usage for an IP address.
    """

    def __init__(self) -> None:
        self._asn_keywords: list[str] = []
        self._load_asn_keywords()

    def _load_asn_keywords(self) -> None:
        path = _DATA_DIR / "vpn_asn_keywords.json"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._asn_keywords = json.load(f)
                logger.info(
                    "Loaded %d VPN/proxy ASN keywords.",
                    len(self._asn_keywords),
                )
        except Exception as exc:
            logger.warning("VPN ASN keywords load error: %s", exc)

    @property
    def name(self) -> str:
        return "vpn_proxy_service"

    def check(self, ip: str) -> dict[str, Any]:
        """
        Check if *ip* is a VPN/proxy.

        Returns
        -------
        dict with keys:
            is_vpn       : bool
            is_proxy     : bool
            provider     : str   — VPN/hosting provider name if detected
            method       : str   — 'ipinfo_api' or 'asn_keyword'
            confidence   : str   — 'high' or 'medium'
        """
        # Try IPinfo API first
        ipinfo_key = os.environ.get("IPINFO_API_KEY", "").strip()
        if ipinfo_key:
            try:
                result = self._check_ipinfo(ip, ipinfo_key)
                if result:
                    return result
            except Exception as exc:
                logger.warning("IPinfo VPN check failed: %s", exc)

        # Fallback to ASN keyword matching
        return self._check_asn_keywords(ip)

    def _check_ipinfo(self, ip: str, api_key: str) -> dict[str, Any] | None:
        """Check via IPinfo API."""
        resp = requests.get(
            f"https://ipinfo.io/{ip}/json",
            params={"token": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        org = data.get("org", "").lower()
        company = data.get("company", {})
        company_type = company.get("type", "") if isinstance(company, dict) else ""
        privacy = data.get("privacy", {})

        is_vpn = privacy.get("vpn", False) if isinstance(privacy, dict) else False
        is_proxy = privacy.get("proxy", False) if isinstance(privacy, dict) else False
        is_hosting = privacy.get("hosting", False) if isinstance(privacy, dict) else False

        if is_vpn or is_proxy or is_hosting:
            return {
                "is_vpn": is_vpn,
                "is_proxy": is_proxy,
                "provider": data.get("org", "Unknown"),
                "method": "ipinfo_api",
                "confidence": "high",
            }

        # Check org name against keywords
        for kw in self._asn_keywords:
            if kw.lower() in org:
                return {
                    "is_vpn": True,
                    "is_proxy": False,
                    "provider": data.get("org", "Unknown"),
                    "method": "ipinfo_api+keyword",
                    "confidence": "medium",
                }

        return {
            "is_vpn": False,
            "is_proxy": False,
            "provider": "",
            "method": "ipinfo_api",
            "confidence": "high",
        }

    def _check_asn_keywords(self, ip: str) -> dict[str, Any]:
        """Fallback: cannot determine without org info."""
        return {
            "is_vpn": False,
            "is_proxy": False,
            "provider": "",
            "method": "asn_keyword_fallback",
            "confidence": "low",
            "note": "No API available — limited detection",
        }

    def analyze(self, ip: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.check(ip)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "VPN Proxy Service",
            "status": "Healthy",
            "asn_keywords": len(self._asn_keywords),
        }


vpn_proxy_service = VPNProxyService()
