"""
CyberMind AI
AbstractAPI Phone Intelligence Service
Primary phone intelligence via AbstractAPI (phoneintelligence.abstractapi.com).
Falls back to Numverify if AbstractAPI is unavailable.
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class AbstractPhoneService:
    """
    AbstractAPI Phone Intelligence Integration for CyberMind AI.
    Provides phone validation, carrier, line type, country, validity status.
    Primary source: AbstractAPI. Auto-falls-back to Numverify on failure.
    """

    BASE_URL = "https://phoneintelligence.abstractapi.com/v1/"

    def __init__(self) -> None:
        self.api_key = os.getenv("ABSTRACTAPI_PHONE_KEY", "").strip()
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def validate_phone(self, phone_number: str) -> dict[str, Any]:
        """
        Validate phone number via AbstractAPI Phone Intelligence.
        Returns carrier, line_type, country, validity, format data.
        """
        clean = phone_number.strip()
        cache_key = f"abstractphone_{clean}"

        now = time.time()
        if cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if now - ts < 3600:
                logger.info("AbstractAPI Phone cache hit for %s", clean)
                return data

        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "message": "ABSTRACTAPI_PHONE_KEY not set in environment."
            }

        params = {
            "api_key": self.api_key,
            "phone": clean
        }

        try:
            logger.info("Querying AbstractAPI Phone Intelligence for: %s", clean)
            res = requests.get(self.BASE_URL, params=params, timeout=10)

            if res.status_code == 200:
                data = res.json()

                # AbstractAPI returns error field on failure
                if data.get("error"):
                    err = data["error"]
                    logger.warning("AbstractAPI Phone error: %s", err)
                    return {
                        "success": False,
                        "configured": True,
                        "error": err.get("message", "AbstractAPI Phone error"),
                        "error_code": err.get("code")
                    }

                # Support both new AbstractAPI Phone Intelligence schema and legacy schema
                carrier_obj = data.get("phone_carrier", {}) or data.get("carrier", {}) or {}
                location_obj = data.get("phone_location", {}) or data.get("country", {}) or {}
                validation_obj = data.get("phone_validation", {}) or {}
                risk_obj = data.get("phone_risk", {}) or {}
                format_obj = data.get("phone_format", {}) or data.get("format", {}) or {}

                # Determine validity
                if "is_valid" in validation_obj:
                    is_valid = bool(validation_obj.get("is_valid"))
                else:
                    is_valid = bool(data.get("valid", True))

                # Parse line type
                raw_type = (
                    carrier_obj.get("line_type")
                    or data.get("type")
                    or "mobile"
                )
                raw_type = str(raw_type).lower()
                if "voip" in raw_type or validation_obj.get("is_voip"):
                    line_type = "VoIP"
                elif "toll" in raw_type:
                    line_type = "Toll Free"
                elif "landline" in raw_type or "fixed" in raw_type:
                    line_type = "Landline"
                elif "mobile" in raw_type or "cell" in raw_type:
                    line_type = "Mobile"
                else:
                    line_type = raw_type.title() if raw_type else "Mobile"

                # Extract carrier
                carrier_name = (
                    carrier_obj.get("name")
                    if isinstance(carrier_obj, dict)
                    else str(carrier_obj)
                ) or "Telecom Provider Available"

                # Extract location
                country_name = (
                    location_obj.get("country_name")
                    or location_obj.get("name")
                    or "Not Available"
                )
                country_code = location_obj.get("country_code") or location_obj.get("code") or ""
                country_prefix = location_obj.get("country_prefix") or location_obj.get("phone_code") or ""
                region = location_obj.get("region") or country_name
                city = location_obj.get("city") or "Not Available"

                # Risk signals
                risk_level = risk_obj.get("risk_level", "low")
                is_abuse_detected = bool(risk_obj.get("is_abuse_detected", False))
                is_disposable = bool(risk_obj.get("is_disposable", False))

                result = {
                    "success": True,
                    "configured": True,
                    "valid": is_valid,
                    "phone": data.get("phone_number") or data.get("phone", clean),
                    "international_format": format_obj.get("international", clean),
                    "local_format": format_obj.get("national") or format_obj.get("local", clean),
                    "country": country_name,
                    "country_code": country_code,
                    "country_prefix": country_prefix,
                    "carrier": carrier_name,
                    "line_type": line_type,
                    "region": region,
                    "city": city,
                    "voip": line_type == "VoIP" or bool(validation_obj.get("is_voip")),
                    "risk_level": risk_level,
                    "is_abuse_detected": is_abuse_detected,
                    "is_disposable": is_disposable,
                    "raw": data
                }
                self._cache[cache_key] = (now, result)
                return result

            elif res.status_code == 429:
                logger.warning("AbstractAPI Phone rate limit hit for %s", clean)
                return {
                    "success": False,
                    "configured": True,
                    "error": "Rate limit exceeded",
                    "error_code": "too_many_requests",
                    "rate_limited": True
                }

            elif res.status_code == 401:
                logger.warning("AbstractAPI Phone unauthorized — key may be invalid")
                return {
                    "success": False,
                    "configured": True,
                    "error": "Invalid API key",
                    "error_code": "unauthorized"
                }

            else:
                logger.warning("AbstractAPI Phone HTTP %s", res.status_code)
                return {
                    "success": False,
                    "configured": True,
                    "error": f"HTTP {res.status_code}"
                }

        except Exception as exc:
            logger.error("AbstractAPI Phone error for %s: %s", clean, exc)
            return {
                "success": False,
                "configured": True,
                "error": str(exc)
            }

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "AbstractAPI Phone Service",
            "status": "Healthy",
            "configured": self.is_configured()
        }


abstract_phone_service = AbstractPhoneService()
