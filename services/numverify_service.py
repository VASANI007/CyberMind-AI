"""
CyberMind AI
Numverify Phone Intelligence Service
Fallback phone validation via Numverify (apilayer.net) API.
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class NumverifyService:
    """
    Numverify (apilayer) API Integration for CyberMind AI.
    Provides phone validation, carrier detection, line type, and geographic data.
    Used as fallback when AbstractAPI Phone is unavailable.
    """

    BASE_URL = "http://apilayer.net/api/validate"

    def __init__(self) -> None:
        self.api_key = os.getenv("NUMVERIFY_API_KEY", "").strip()
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def validate_phone(self, phone_number: str) -> dict[str, Any]:
        """
        Validate phone number via Numverify API.
        Returns carrier, line_type, country, location data.
        """
        clean = phone_number.strip().replace(" ", "").replace("-", "")
        # Remove leading '+' for numverify
        digits_only = clean.lstrip("+")
        cache_key = f"numverify_{digits_only}"

        now = time.time()
        if cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if now - ts < 3600:
                logger.info("Numverify cache hit for %s", clean)
                return data

        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "message": "NUMVERIFY_API_KEY not set in environment."
            }

        params = {
            "access_key": self.api_key,
            "number": digits_only,
            "format": 1
        }

        try:
            logger.info("Querying Numverify API for: %s", clean)
            res = requests.get(self.BASE_URL, params=params, timeout=10)

            if res.status_code == 200:
                data = res.json()

                # Numverify returns error object on failure
                if data.get("error"):
                    err = data["error"]
                    logger.warning("Numverify error: %s", err)
                    return {
                        "success": False,
                        "configured": True,
                        "error": err.get("info", "Numverify API error"),
                        "error_code": err.get("code")
                    }

                # Standardize line_type
                raw_line = str(data.get("line_type", "mobile")).lower()
                if raw_line == "mobile":
                    line_type = "Mobile"
                elif raw_line == "landline":
                    line_type = "Landline"
                elif "voip" in raw_line:
                    line_type = "VoIP"
                elif "toll" in raw_line:
                    line_type = "Toll Free"
                else:
                    line_type = raw_line.title()

                result = {
                    "success": True,
                    "configured": True,
                    "valid": data.get("valid", False),
                    "number": data.get("number", clean),
                    "international_format": data.get("international_format", clean),
                    "local_format": data.get("local_format", ""),
                    "country": data.get("country_name", "Not Available"),
                    "country_code": data.get("country_code", ""),
                    "country_prefix": data.get("country_prefix", ""),
                    "location": data.get("location", "Not Available"),
                    "carrier": data.get("carrier", "Not Available"),
                    "line_type": line_type,
                    "region": data.get("location", "Not Available"),
                    "raw": data
                }
                self._cache[cache_key] = (now, result)
                return result

            else:
                logger.warning("Numverify HTTP %s", res.status_code)
                return {
                    "success": False,
                    "configured": True,
                    "error": f"HTTP {res.status_code}"
                }

        except Exception as exc:
            logger.error("Numverify API error for %s: %s", clean, exc)
            return {
                "success": False,
                "configured": True,
                "error": str(exc)
            }

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Numverify Service",
            "status": "Healthy",
            "configured": self.is_configured()
        }


numverify_service = NumverifyService()
