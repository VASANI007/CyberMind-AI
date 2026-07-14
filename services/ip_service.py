"""
CyberMind AI

IP Service

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any
import ipaddress

from core.logger import logger
from core.validator import is_valid_ip

from services.geo_service import geo_service
from services.ipinfo_service import ipinfo_service
from services.abuseipdb_service import abuseipdb_service
from services.blacklist_service import blacklist_service
from services.reputation_service import reputation_service


class IPService:
    """
    Enterprise IP Analysis Service.
    """

    def __init__(self) -> None:
        logger.info("IP Service initialized.")

    def validate(self, ip: str) -> bool:
        """
        Validate IP address.
        """
        return is_valid_ip(ip)

    def analyze(self, ip: str) -> dict[str, Any]:
        """
        Analyze IP address.
        """
        ip = ip.strip()
        if not self.validate(ip):
            raise ValueError(f"Invalid IP address: {ip}")

        try:
            addr = ipaddress.ip_address(ip)
            version = "IPv6" if addr.version == 6 else "IPv4"
        except Exception:
            version = "IPv4"

        geo_data = geo_service.lookup(ip) or {}
        ipinfo_data = ipinfo_service.lookup(ip) or {}
        abuse_data = abuseipdb_service.lookup(ip) or {}
        blacklist_data = blacklist_service.lookup(ip) or {}

        analysis = {
            "scanner": "ip",
            "ip": ip,
            "version": version,
            "hostname": ipinfo_data.get("hostname") or geo_data.get("hostname") or "",
            "isp": ipinfo_data.get("isp") or geo_data.get("isp") or "",
            "organization": ipinfo_data.get("org") or "",
            "asn": ipinfo_data.get("asn") or "",
            "country": geo_data.get("country") or ipinfo_data.get("country_name") or "",
            "region": geo_data.get("state") or ipinfo_data.get("region") or "",
            "city": geo_data.get("city") or ipinfo_data.get("city") or "",
            "latitude": geo_data.get("latitude") or ipinfo_data.get("latitude") or 0.0,
            "longitude": geo_data.get("longitude") or ipinfo_data.get("longitude") or 0.0,
            "timezone": geo_data.get("timezone") or ipinfo_data.get("timezone") or "",
            "geo": geo_data,
            "abuseipdb": abuse_data,
            "ipinfo": ipinfo_data,
            "blacklist": blacklist_data,
            "reputation": {}
        }

        reputation = reputation_service.analyze(analysis) or {}
        analysis["reputation"] = reputation

        return analysis

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """
        return {
            "service": "IP Service",
            "status": "Healthy"
        }

    def __repr__(self) -> str:
        return "IPService(Enterprise Version)"


ip_service = IPService()
