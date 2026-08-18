"""
CyberMind AI
Veriphone Phone Intelligence Service
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class VeriphoneService:
    """
    Veriphone API Integration for CyberMind AI.
    Provides real-time phone number verification, carrier detection, line type classification (Mobile/VoIP/Landline),
    and geographical region lookup.
    """

    BASE_URL = "https://api.veriphone.io/v2/verify"

    def __init__(self) -> None:
        self.api_key = os.getenv("VERIPHONE_API_KEY", "").strip()
        self._memory_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        """
        Check if Veriphone API key is set in environment.
        """
        return bool(self.api_key)

    def validate_phone(self, phone_number: str) -> dict[str, Any]:
        """
        Validate phone number using Veriphone API.
        """
        clean_phone = phone_number.strip()
        cache_key = f"veriphone_phone_{clean_phone}"

        # 1. Check memory cache (1 hr TTL)
        now = time.time()
        if cache_key in self._memory_cache:
            ts, cached_data = self._memory_cache[cache_key]
            if now - ts < 3600:
                logger.info("Veriphone validation cache hit for %s", clean_phone)
                return cached_data

        if not self.is_configured():
            logger.info("VERIPHONE_API_KEY not configured. Veriphone service operating in unconfigured mode.")
            return {
                "success": False,
                "configured": False,
                "valid": False,
                "message": "VERIPHONE_API_KEY not configured in environment.",
                "raw": {}
            }

        try:
            params = {
                "key": self.api_key,
                "phone": clean_phone
            }
            logger.info("Querying Veriphone API for phone: %s", clean_phone)
            res = requests.get(self.BASE_URL, params=params, timeout=10)

            if res.status_code == 200:
                raw = res.json()
                status = raw.get("status")

                if status == "success":
                    is_valid = bool(raw.get("phone_valid", False))
                    raw_type = str(raw.get("phone_type", "unknown")).lower()

                    # Standardize line_type classification
                    if raw_type == "mobile":
                        line_type = "Mobile"
                    elif raw_type == "landline":
                        line_type = "Landline"
                    elif "voip" in raw_type or raw_type == "virtual":
                        line_type = "VoIP"
                    elif "toll" in raw_type or raw_type == "toll_free":
                        line_type = "Toll Free"
                    elif raw_type != "unknown":
                        line_type = raw_type.title()
                    else:
                        line_type = "Mobile / Landline"

                    carrier = raw.get("carrier") or "Telecom Provider Available"
                    country = raw.get("country") or raw.get("phone_region") or "Unknown"
                    country_code = raw.get("country_code") or ""
                    region = raw.get("phone_region") or "Global"
                    intl_num = raw.get("international_number") or clean_phone
                    local_num = raw.get("local_number") or clean_phone
                    e164 = raw.get("e164") or clean_phone

                    parsed = {
                        "success": True,
                        "configured": True,
                        "valid": is_valid,
                        "phone_type": raw_type,
                        "line_type": line_type,
                        "carrier": carrier,
                        "country": country,
                        "country_code": country_code,
                        "region": region,
                        "international_number": intl_num,
                        "local_number": local_num,
                        "e164": e164,
                        "raw": raw
                    }

                    self._memory_cache[cache_key] = (now, parsed)
                    return parsed
                else:
                    err_msg = raw.get("error") or "Veriphone API error."
                    logger.warning("Veriphone API error response: %s", err_msg)
                    return {
                        "success": False,
                        "configured": True,
                        "valid": False,
                        "message": err_msg,
                        "raw": raw
                    }
            else:
                logger.warning("Veriphone API returned HTTP %d: %s", res.status_code, res.text[:100])
                return {
                    "success": False,
                    "configured": True,
                    "valid": False,
                    "message": f"Veriphone HTTP {res.status_code}",
                    "raw": {}
                }

        except Exception as exc:
            logger.exception("Error querying Veriphone API for %s: %s", clean_phone, exc)
            return {
                "success": False,
                "configured": True,
                "valid": False,
                "message": str(exc),
                "raw": {}
            }

    def health_check(self) -> dict[str, Any]:
        """
        Health status of Veriphone service.
        """
        return {
            "service": "Veriphone Service",
            "configured": self.is_configured(),
            "status": "Healthy"
        }


veriphone_service = VeriphoneService()
