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

    DNS_TIMEOUT = 1.0
    _cache: dict[str, tuple[float, dict]] = {}

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
        Discover subdomains for *domain* with in-memory TTL caching and parallel DNS resolution.
        """
        import time
        import copy
        import concurrent.futures

        domain_key = domain.strip().lower()
        now = time.time()
        if domain_key in self._cache:
            ts, cached_val = self._cache[domain_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        all_subdomains: dict[str, dict] = {}

        # 1. CT Logs
        try:
            from services.ct_logs_service import ct_logs_service
            ct_result = ct_logs_service.get_certificates(domain_key)
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

        # 2. DNS Brute-force in parallel
        dns_found = 0
        try:
            import dns.resolver

            prefixes_to_test = [
                p for p in self._wordlist[:12]
                if f"{p}.{domain_key}" not in all_subdomains
            ]

            def _resolve_sub(prefix: str):
                fqdn = f"{prefix}.{domain_key}"
                try:
                    res = dns.resolver.Resolver()
                    res.timeout = self.DNS_TIMEOUT
                    res.lifetime = self.DNS_TIMEOUT
                    ans = res.resolve(fqdn, "A")
                    ips = [str(rdata) for rdata in ans]
                    return fqdn, ips[0] if ips else ""
                except Exception:
                    return fqdn, None

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(_resolve_sub, p) for p in prefixes_to_test]
                done, not_done = concurrent.futures.wait(futures, timeout=1.5)
                for future in done:
                    try:
                        fqdn, ip = future.result()
                        if ip:
                            all_subdomains[fqdn] = {
                                "name": fqdn,
                                "source": "DNS Brute-force",
                                "ip": ip,
                            }
                            dns_found += 1
                    except Exception:
                        pass

        except ImportError:
            logger.warning("dnspython not available for subdomain brute-force")
        except Exception as exc:
            logger.warning("DNS brute-force error: %s", exc)

        results = sorted(all_subdomains.values(), key=lambda x: x["name"])

        res = {
            "subdomains": results,
            "ct_count": ct_count,
            "dns_count": dns_found,
            "total": len(results),
        }
        self._cache[domain_key] = (now, res)
        return copy.deepcopy(res)

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
