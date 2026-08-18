"""
CyberMind AI
IPQualityScore (IPQS) Threat Intelligence Service
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class IPQSService:
    """
    IPQualityScore API Service Integration for CyberMind AI.
    Handles Phone Validation, Phone Abuse Reporting, and Email/DarkWeb Exposure Checks.
    """

    BASE_PHONE_URL = "https://www.ipqualityscore.com/api/json/phone"
    BASE_EMAIL_URL = "https://www.ipqualityscore.com/api/json/email"
    BASE_REPORT_URL = "https://www.ipqualityscore.com/api/json/report"

    def __init__(self) -> None:
        self.api_key = os.getenv("IPQS_API_KEY", "").strip()
        self._memory_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        """
        Check if IPQS API key is available.
        """
        return bool(self.api_key)

    def validate_phone(self, phone_number: str) -> dict[str, Any]:
        """
        Validate phone number and fetch threat intelligence from IPQS.
        """
        clean_phone = phone_number.strip()
        cache_key = f"ipqs_phone_{clean_phone}"

        # 1. Check memory cache (1 hr TTL)
        now = time.time()
        if cache_key in self._memory_cache:
            ts, data = self._memory_cache[cache_key]
            if now - ts < 3600:
                logger.info("IPQS Phone validation cache hit for %s", clean_phone)
                return data


        if not self.is_configured():
            logger.info("IPQS_API_KEY not configured. Falling back to rule-based phone intelligence.")
            fallback = {
                "success": False,
                "configured": False,
                "message": "IPQS API Key not set in environment. Operating in heuristic mode.",
                "raw": {}
            }
            return fallback

        url = f"{self.BASE_PHONE_URL}/{self.api_key}/{clean_phone}"
        headers = {"IPQS-KEY": self.api_key}

        try:
            logger.info("Querying IPQS Phone API for target: %s", clean_phone)
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                result = {
                    "success": data.get("success", False),
                    "configured": True,
                    "valid": data.get("valid", True),
                    "country": data.get("country", "Not Available"),
                    "region": data.get("region", "Not Available"),
                    "city": data.get("city", "Not Available"),
                    "carrier": data.get("carrier", "Available"),
                    "line_type": data.get("line_type", "Mobile / VoIP / Landline"),
                    "prepaid": data.get("prepaid", False),
                    "voip": data.get("VOIP", False),
                    "recent_abuse": data.get("recent_abuse", False),
                    "fraud_score": data.get("fraud_score", 0),
                    "risky": data.get("risky", False),
                    "spammer": data.get("spammer", False),
                    "name": data.get("name", "Not Available"),
                    "leaked": data.get("leaked", False),
                    "associated_email": data.get("associated_email", "Not Available"),
                    "active": data.get("active", None),
                    "raw": data
                }
                self._memory_cache[cache_key] = (now, result)
                return result
            else:
                logger.warning("IPQS Phone API returned status code %s", res.status_code)
                return {
                    "success": False,
                    "configured": True,
                    "error": f"HTTP {res.status_code}",
                    "raw": {}
                }
        except Exception as exc:
            logger.error("Error querying IPQS Phone API: %s", exc)
            return {
                "success": False,
                "configured": True,
                "error": str(exc),
                "raw": {}
            }

    def verify_email_darkweb(self, email: str) -> dict[str, Any]:
        """
        Verify email and check dark web breach exposure via IPQS.
        """
        clean_email = email.strip().lower()
        cache_key = f"ipqs_email_{clean_email}"

        now = time.time()
        if cache_key in self._memory_cache:
            ts, data = self._memory_cache[cache_key]
            if now - ts < 3600:
                return data

        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "leaked": False,
                "message": "IPQS API Key not configured."
            }

        url = f"{self.BASE_EMAIL_URL}/{self.api_key}/{clean_email}"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                result = {
                    "success": data.get("success", False),
                    "configured": True,
                    "valid": data.get("valid", True),
                    "disposable": data.get("disposable", False),
                    "leaked": data.get("leaked", False),
                    "recent_abuse": data.get("recent_abuse", False),
                    "fraud_score": data.get("fraud_score", 0),
                    "sanitized_email": data.get("sanitized_email", clean_email),
                    "domain": data.get("domain", ""),
                    "raw": data
                }
                self._memory_cache[cache_key] = (now, result)
                return result

            return {"success": False, "configured": True, "leaked": False}
        except Exception as exc:
            logger.error("Error calling IPQS Email API: %s", exc)
            return {"success": False, "configured": True, "leaked": False, "error": str(exc)}

    def report_phone(self, phone_number: str, category: str, notes: str = "") -> dict[str, Any]:
        """
        Report suspicious phone number locally & submit to IPQS if key active.
        """
        logger.info("Reporting phone number %s under category: %s", phone_number, category)
        result = {
            "reported": True,
            "phone_number": phone_number,
            "category": category,
            "notes": notes,
            "ipqs_submitted": False
        }
        if self.is_configured():
            try:
                # IPQS endpoint for phone abuse reporting
                res = requests.post(
                    self.BASE_REPORT_URL,
                    data={
                        "key": self.api_key,
                        "phone": phone_number,
                        "reason": category,
                        "notes": notes
                    },
                    timeout=5
                )
                if res.status_code == 200 and res.json().get("success"):
                    result["ipqs_submitted"] = True
            except Exception as exc:
                logger.warning("Could not submit phone report to IPQS upstream: %s", exc)

        return result

    def health_check(self) -> dict[str, Any]:
        """
        Health check status.
        """
        return {
            "service": "IPQS Service",
            "status": "Healthy",
            "configured": self.is_configured()
        }


ipqs_service = IPQSService()
