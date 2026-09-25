"""
CyberMind AI
AbstractAPI IP Geolocation & Intelligence Service
Enterprise Production Version
"""

from __future__ import annotations

import os
import time
import requests
from typing import Any
from core.logger import logger


class AbstractIPService:
    """
    AbstractAPI IP Geolocation Integration for CyberMind AI.
    Provides IP geolocation, ISP, organization, timezone, VPN/proxy detection.
    Supplements existing ipinfo_service and geo_service.
    """

    BASE_URL = "https://ip-intelligence.abstractapi.com/v1/"

    def __init__(self) -> None:
        self.api_key = os.getenv("ABSTRACTAPI_IP_KEY", "").strip()
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def lookup(self, ip_address: str) -> dict[str, Any]:
        """
        Look up IP address via AbstractAPI IP Intelligence.
        Returns country, city, ISP, organization, VPN/proxy flags.
        """
        clean_ip = ip_address.strip()
        cache_key = f"abstractip_{clean_ip}"

        now = time.time()
        if cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if now - ts < 3600:
                logger.info("AbstractAPI IP cache hit for %s", clean_ip)
                return data

        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "message": "ABSTRACTAPI_IP_KEY not set in environment."
            }

        params = {
            "api_key": self.api_key,
            "ip_address": clean_ip
        }

        try:
            logger.info("Querying AbstractAPI IP Intelligence for: %s", clean_ip)
            res = requests.get(self.BASE_URL, params=params, timeout=10)

            if res.status_code == 200:
                data = res.json()

                if data.get("error"):
                    err = data["error"]
                    logger.warning("AbstractAPI IP error: %s", err)
                    return {
                        "success": False,
                        "configured": True,
                        "error": err.get("message", "AbstractAPI IP error"),
                        "error_code": err.get("code")
                    }

                # Extract nested fields from IP Intelligence schema or fallback
                security = data.get("security", {}) or {}
                location = data.get("location", {}) or {}
                asn_data = data.get("asn", {}) or {}
                company_data = data.get("company", {}) or {}
                connection = data.get("connection", {}) or {}
                timezone_data = data.get("timezone", {}) or {}

                city = location.get("city") or data.get("city") or "Not Available"
                region = location.get("region") or data.get("region") or "Not Available"
                country = (
                    location.get("country")
                    or (data.get("country") if isinstance(data.get("country"), str) else "")
                    or "Not Available"
                )
                country_code = location.get("country_code") or data.get("country_code") or ""
                continent = location.get("continent") or data.get("continent") or ""
                latitude = location.get("latitude") or data.get("latitude") or 0.0
                longitude = location.get("longitude") or data.get("longitude") or 0.0
                postal_code = location.get("postal_code") or data.get("postal_code") or ""

                isp = (
                    company_data.get("name")
                    or asn_data.get("name")
                    or connection.get("isp_name")
                    or ""
                )
                org = (
                    company_data.get("name")
                    or connection.get("organization_name")
                    or ""
                )
                asn = str(asn_data.get("asn") or connection.get("autonomous_system_number") or "")
                conn_type = company_data.get("type") or asn_data.get("type") or connection.get("connection_type") or ""

                is_vpn = bool(security.get("is_vpn", False))
                is_proxy = bool(security.get("is_proxy", False))
                is_tor = bool(security.get("is_tor", False))
                is_hosting = bool(security.get("is_hosting", False))
                is_relay = bool(security.get("is_relay", False))
                is_abuse = bool(security.get("is_abuse", False))

                # Compute threat score
                threat_score = security.get("threat_score")
                if threat_score is None:
                    calc_threat = 0
                    if is_tor:
                        calc_threat += 45
                    if is_vpn:
                        calc_threat += 25
                    if is_proxy:
                        calc_threat += 30
                    if is_abuse:
                        calc_threat += 40
                    if is_hosting:
                        calc_threat += 10
                    threat_score = min(calc_threat, 100)

                result = {
                    "success": True,
                    "configured": True,
                    "ip": clean_ip,
                    "city": city,
                    "region": region,
                    "country": country,
                    "country_code": country_code,
                    "continent": continent,
                    "latitude": latitude,
                    "longitude": longitude,
                    "postal_code": postal_code,
                    "timezone": timezone_data.get("name", "") if isinstance(timezone_data, dict) else str(timezone_data),
                    # ISP / Connection
                    "isp": isp,
                    "organization": org,
                    "asn": asn,
                    "connection_type": conn_type,
                    # Security signals
                    "is_vpn": is_vpn,
                    "is_proxy": is_proxy,
                    "is_tor": is_tor,
                    "is_hosting": is_hosting,
                    "is_relay": is_relay,
                    "is_abuse": is_abuse,
                    "threat_score": threat_score,
                    "raw": data
                }
                self._cache[cache_key] = (now, result)
                return result

            elif res.status_code == 429:
                logger.warning("AbstractAPI IP rate limit hit for %s", clean_ip)
                return {
                    "success": False,
                    "configured": True,
                    "error": "Rate limit exceeded",
                    "rate_limited": True
                }

            elif res.status_code == 401:
                logger.warning("AbstractAPI IP unauthorized — key may be invalid")
                return {
                    "success": False,
                    "configured": True,
                    "error": "Invalid API key",
                    "error_code": "unauthorized"
                }

            else:
                logger.warning("AbstractAPI IP HTTP %s for %s", res.status_code, clean_ip)
                return {
                    "success": False,
                    "configured": True,
                    "error": f"HTTP {res.status_code}"
                }

        except Exception as exc:
            logger.error("AbstractAPI IP error for %s: %s", clean_ip, exc)
            return {
                "success": False,
                "configured": True,
                "error": str(exc)
            }

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "AbstractAPI IP Service",
            "status": "Healthy",
            "configured": self.is_configured()
        }


abstract_ip_service = AbstractIPService()
