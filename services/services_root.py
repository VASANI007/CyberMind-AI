"""
CyberMind AI
Services Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import io
import pathlib
import sys

# Add project root to path for direct execution support
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from typing import Any
from core.logger import logger

from services.abuseipdb_service import abuseipdb_service
from services.blacklist_service import blacklist_service
from services.dns_service import dns_service
from services.domain_service import domain_service
from services.email_service import email_service
from services.entropy_service import entropy_service
from services.file_service import file_service
from services.geo_service import geo_service
from services.google_safe_browsing_service import google_safe_browsing_service
from services.ip_service import ip_service
from services.ipinfo_service import ipinfo_service
from services.metadata_service import metadata_service
from services.punycode_service import punycode_service
from services.qr_service import qr_service
from services.reputation_service import reputation_service
from services.security_headers_service import security_headers_service
from services.shorturl_service import shorturl_service
from services.ssl_service import ssl_service
from services.tld_service import tld_service
from services.url_feature_service import url_feature_service
from services.url_service import url_service
from services.virustotal_service import virustotal_service
from services.website_service import website_service
from services.whois_service import whois_service
from services.breach_intelligence_service import breach_intelligence_service


class ServicesRoot:
    """
    Services Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:
        self.services = {
            "abuseipdb_service": abuseipdb_service,
            "blacklist_service": blacklist_service,
            "dns_service": dns_service,
            "domain_service": domain_service,
            "email_service": email_service,
            "entropy_service": entropy_service,
            "file_service": file_service,
            "geo_service": geo_service,
            "google_safe_browsing_service": google_safe_browsing_service,
            "ip_service": ip_service,
            "ipinfo_service": ipinfo_service,
            "metadata_service": metadata_service,
            "punycode_service": punycode_service,
            "qr_service": qr_service,
            "reputation_service": reputation_service,
            "security_headers_service": security_headers_service,
            "shorturl_service": shorturl_service,
            "ssl_service": ssl_service,
            "tld_service": tld_service,
            "url_feature_service": url_feature_service,
            "url_service": url_service,
            "virustotal_service": virustotal_service,
            "website_service": website_service,
            "whois_service": whois_service,
            "breach_intelligence_service": breach_intelligence_service
        }

    def initialize(self) -> None:
        """
        Initialize all services.
        """
        logger.info("Initializing Services...")
        for name, service in self.services.items():
            if hasattr(service, "initialize"):
                try:
                    service.initialize()
                except Exception as e:
                    logger.error(f"Error initializing service {name}: {e}")
            logger.info(f"Service {name} loaded.")

    def health_check(self) -> dict[str, Any]:
        """
        Services health check.
        """
        results = {}
        healthy = True
        for name, service in self.services.items():
            try:
                status = service.health_check() if hasattr(service, "health_check") else {"status": "Healthy"}
                results[name] = status
                if status.get("status") != "Healthy":
                    healthy = False
            except Exception as e:
                healthy = False
                results[name] = {"status": "Unhealthy", "error": str(e)}

        return {
            "service": "Services",
            "status": "Healthy" if healthy else "Unhealthy",
            "services": results
        }

    def status(self) -> dict[str, Any]:
        """
        Services status.
        """
        return {
            "version": self.VERSION,
            "total_services": len(self.services),
            "health": self.health_check()
        }

    def reload(self) -> None:
        """
        Reload services.
        """
        logger.info("Reloading Services...")
        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown services.
        """
        logger.info("Shutting down Services...")
        for name, service in self.services.items():
            if hasattr(service, "shutdown"):
                try:
                    service.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down service {name}: {e}")

    def list_services(self) -> list[str]:
        """
        List all services.
        """
        return sorted(list(self.services.keys()))

    def __len__(self) -> int:
        return len(self.services)

    def __repr__(self) -> str:
        return (
            f"ServicesRoot("
            f"services={len(self.services)}, "
            f"version='{self.VERSION}')"
        )


services_root = ServicesRoot()

if __name__ == "__main__":
    # Configure stdout and stderr to support UTF-8 characters (emojis) on Windows terminals
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 60)
    print("             🛡️  CyberMind AI - Services Runner 🛡️             ")
    print("=" * 60)
    services_root.initialize()
    health = services_root.health_check()
    print(f"Status: {health['status']}")
    for name, stat in health["services"].items():
        print(f"  - {name}: {stat.get('status')}")
    print("=" * 60)
