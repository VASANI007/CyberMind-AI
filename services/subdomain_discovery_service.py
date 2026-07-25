"""
CyberMind AI
Subdomain Discovery Service
Discovers subdomains via CT logs + DNS brute-force.
Free — uses crt.sh + dnspython against a local wordlist.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "domain"


class SubdomainDiscoveryService:
    """
    Discovers subdomains by combining:
    1. Certificate Transparency logs (via ct_logs_service)
    2. DNS brute-force against a common subdomains wordlist
    """

    DNS_TIMEOUT = 3

    def __init__(self) -> None:
        self._wordlist: list[str] = []
        self._load_wordlist()

    def _load_wordlist(self) -> None:
        path = _DATA_DIR / "common_subdomains.txt"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._wordlist = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                logger.info(
                    "Loaded %d subdomain prefixes.", len(self._wordlist)
                )
        except Exception as exc:
            logger.warning("Could not load subdomain wordlist: %s", exc)

    @property
    def name(self) -> str:
        return "subdomain_discovery_service"

    def discover(self, domain: str) -> dict[str, Any]:
        """
        Discover subdomains for *domain*.

        Returns
        -------
        dict with keys:
            subdomains   : list[dict] — each with name, source, ip (if resolved)
            ct_count     : int        — subdomains from CT logs
            dns_count    : int        — subdomains from DNS brute-force
            total        : int
        """
        all_subdomains: dict[str, dict] = {}

        # 1. CT Logs
        try:
            from services.ct_logs_service import ct_logs_service
            ct_result = ct_logs_service.get_certificates(domain)
            for sub in ct_result.get("subdomains", []):
                if sub not in all_subdomains:
                    all_subdomains[sub] = {
                        "name": sub,
                        "source": "CT Logs",
                        "ip": "",
                    }
        except Exception as exc:
            logger.warning("CT log subdomain discovery failed: %s", exc)

        ct_count = len(all_subdomains)

        # 2. DNS Brute-force (limited to wordlist)
        dns_found = 0
        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = self.DNS_TIMEOUT
            resolver.lifetime = self.DNS_TIMEOUT

            for prefix in self._wordlist[:12]:
                fqdn = f"{prefix}.{domain}"
                if fqdn in all_subdomains:
                    continue

                try:
                    answers = resolver.resolve(fqdn, "A")
                    ips = [str(rdata) for rdata in answers]
                    all_subdomains[fqdn] = {
                        "name": fqdn,
                        "source": "DNS Brute-force",
                        "ip": ips[0] if ips else "",
                    }
                    dns_found += 1
                except (
                    dns.resolver.NXDOMAIN,
                    dns.resolver.NoAnswer,
                    dns.resolver.Timeout,
                    dns.resolver.NoNameservers,
                    Exception,
                ):
                    continue

        except ImportError:
            logger.warning("dnspython not available for subdomain brute-force")
        except Exception as exc:
            logger.warning("DNS brute-force error: %s", exc)

        results = sorted(all_subdomains.values(), key=lambda x: x["name"])

        return {
            "subdomains": results,
            "ct_count": ct_count,
            "dns_count": dns_found,
            "total": len(results),
        }

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.discover(domain)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Subdomain Discovery Service",
            "status": "Healthy",
            "wordlist_size": len(self._wordlist),
        }


subdomain_discovery_service = SubdomainDiscoveryService()
