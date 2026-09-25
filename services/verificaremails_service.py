"""
CyberMind AI
VerificarEmails Phone Intelligence Service
Third-tier fallback phone validation via VerificarEmails API (dashboard.verificaremails.com).
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class VerificarEmailsService:
    """
    VerificarEmails Phone Validation API Integration for CyberMind AI.
    Used as the 3rd-tier fallback when AbstractAPI and Numverify are unavailable.
    Endpoint: https://dashboard.verificaremails.com/myapi/phone/validate/single
    """

    BASE_URL = "https://dashboard.verificaremails.com/myapi/phone/validate/single"

    def __init__(self) -> None:
        self.api_key = (
            os.getenv("VERIFICAREMAILS_API_KEY", "")
            or os.getenv("VERIFICAR_EMAILS_KEY", "")
        ).strip()
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def validate_phone(self, phone_number: str) -> dict[str, Any]:
        """
        Validate phone number via VerificarEmails API.
        Returns validation status, carrier, line_type, country.
        """
        clean = phone_number.strip().replace(" ", "").replace("-", "")
        cache_key = f"verificaremails_{clean}"

        now = time.time()
        if cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if now - ts < 3600:
                logger.info("VerificarEmails cache hit for %s", clean)
                return data

        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "message": "VERIFICAREMAILS_API_KEY not set in environment."
            }

        params = {
            "auth-token": self.api_key,
            "term": clean
        }

        try:
            logger.info("Querying VerificarEmails Phone API for: %s", clean)
            res = requests.get(self.BASE_URL, params=params, timeout=12)

            if res.status_code == 200:
                data = res.json()

                if data.get("error"):
                    err = data["error"]
                    logger.warning("VerificarEmails error: %s", err)
                    return {
                        "success": False,
                        "configured": True,
                        "error": err.get("msg", "VerificarEmails API error"),
                        "error_code": err.get("code")
                    }

                result_type = str(data.get("result_type", "")).strip()
                result_code = str(data.get("result_code", "")).strip()

                # Detailed inner payload if available
                inner_result = data.get("result", {})
                if not isinstance(inner_result, dict):
                    inner_result = {}

                current_net = inner_result.get("current_network", {}) or {}
                original_net = inner_result.get("original_network", {}) or {}

                # Determine validity: code 1 is Invalid, 6 is no coverage, 101/connected is active
                is_valid = result_code not in ("1", "104", "105") and "inválido" not in result_type.lower()
                is_reachable = inner_result.get("reachable", "")
                if is_reachable == "connected":
                    is_valid = True

                # Determine line type
                raw_type = str(inner_result.get("number_type", "mobile")).lower()
                if "mobile" in raw_type or "móvil" in raw_type:
                    line_type = "Mobile"
                elif "landline" in raw_type or "fijo" in raw_type:
                    line_type = "Landline"
                elif "voip" in raw_type:
                    line_type = "VoIP"
                else:
                    line_type = raw_type.title() if raw_type else "Mobile"

                carrier = (
                    current_net.get("network_name")
                    or original_net.get("network_name")
                    or "Telecom Provider Available"
                )
                country = (
                    current_net.get("country_name")
                    or original_net.get("country_name")
                    or "Not Available"
                )
                region = current_net.get("area") or "Not Available"

                result = {
                    "success": True,
                    "configured": True,
                    "valid": is_valid,
                    "phone": data.get("term", clean),
                    "result_type": result_type,
                    "result_code": result_code,
                    "carrier": carrier,
                    "line_type": line_type,
                    "country": country,
                    "region": region,
                    "is_ported": inner_result.get("is_ported", False),
                    "raw": data
                }
                self._cache[cache_key] = (now, result)
                return result

            elif res.status_code == 429:
                logger.warning("VerificarEmails rate limit hit for %s", clean)
                return {
                    "success": False,
                    "configured": True,
                    "error": "Rate limit exceeded",
                    "rate_limited": True
                }

            elif res.status_code in (401, 403):
                logger.warning("VerificarEmails unauthorized / token invalid: HTTP %s", res.status_code)
                return {
                    "success": False,
                    "configured": True,
                    "error": "Invalid or unauthorized API token",
                    "error_code": "unauthorized"
                }

            else:
                logger.warning("VerificarEmails HTTP %s for %s", res.status_code, clean)
                return {
                    "success": False,
                    "configured": True,
                    "error": f"HTTP {res.status_code}"
                }

        except Exception as exc:
            logger.error("VerificarEmails API error for %s: %s", clean, exc)
            return {
                "success": False,
                "configured": True,
                "error": str(exc)
            }

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "VerificarEmails Phone Service",
            "status": "Healthy",
            "configured": self.is_configured()
        }


verificaremails_service = VerificarEmailsService()
