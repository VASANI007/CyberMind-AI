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
from services.abstract_ip_service import abstract_ip_service


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

        import concurrent.futures

        task_map = {
            "geo": lambda: geo_service.lookup(ip) or {},
            "ipinfo": lambda: ipinfo_service.lookup(ip) or {},
            "abuse": lambda: abuseipdb_service.lookup(ip) or {},
            "blacklist": lambda: blacklist_service.lookup(ip) or {},
            "abstract": lambda: abstract_ip_service.lookup(ip) or {},
        }
        res_map = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(task_map)) as executor:
            future_to_key = {executor.submit(fn): k for k, fn in task_map.items()}
            for future in concurrent.futures.as_completed(future_to_key):
                k = future_to_key[future]
                try:
                    res_map[k] = future.result()
                except Exception:
                    res_map[k] = {}

        geo_data = res_map.get("geo", {})
        ipinfo_data = res_map.get("ipinfo", {})
        abuse_data = res_map.get("abuse", {})
        blacklist_data = res_map.get("blacklist", {})
        abstract_data = res_map.get("abstract", {})
        abstract_active = bool(abstract_data.get("configured") and abstract_data.get("success"))

        analysis = {
            "scanner": "ip",
            "ip": ip,
            "version": version,
            "hostname": ipinfo_data.get("hostname") or geo_data.get("hostname") or "",
            "isp": abstract_data.get("isp") or ipinfo_data.get("isp") or geo_data.get("isp") or "",
            "organization": abstract_data.get("organization") or ipinfo_data.get("org") or "",
            "asn": abstract_data.get("asn") or ipinfo_data.get("asn") or "",
            "country": abstract_data.get("country") or geo_data.get("country") or ipinfo_data.get("country_name") or "",
            "region": abstract_data.get("region") or geo_data.get("state") or ipinfo_data.get("region") or "",
            "city": abstract_data.get("city") or geo_data.get("city") or ipinfo_data.get("city") or "",
            "latitude": abstract_data.get("latitude") or geo_data.get("latitude") or ipinfo_data.get("latitude") or 0.0,
            "longitude": abstract_data.get("longitude") or geo_data.get("longitude") or ipinfo_data.get("longitude") or 0.0,
            "timezone": abstract_data.get("timezone") or geo_data.get("timezone") or ipinfo_data.get("timezone") or "",
            "connection_type": abstract_data.get("connection_type") or "",
            # Security signals from AbstractAPI
            "is_vpn": abstract_data.get("is_vpn", False),
            "is_proxy": abstract_data.get("is_proxy", False),
            "is_tor": abstract_data.get("is_tor", False),
            "is_hosting": abstract_data.get("is_hosting", False),
            "threat_score": abstract_data.get("threat_score", 0),
            "abstract_ip_integrated": abstract_active,
            # Sub-dicts for deeper analysis
            "geo": geo_data,
            "abuseipdb": abuse_data,
            "ipinfo": ipinfo_data,
            "blacklist": blacklist_data,
            "abstract_ip": abstract_data,
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
