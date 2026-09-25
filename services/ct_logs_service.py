"""
CyberMind AI
Certificate Transparency Logs Service
Queries crt.sh for SSL certificates issued to a domain.
Free API — no key required.
"""

from __future__ import annotations

from typing import Any

import requests

from core.logger import logger


class CTLogsService:
    """
    Queries crt.sh (Certificate Transparency log aggregator)
    for certificates issued to a given domain.
    """

    CRT_SH_URL = "https://crt.sh/"
    TIMEOUT = 3.0
    _cache: dict[str, tuple[float, dict]] = {}

    @property
    def name(self) -> str:
        return "ct_logs_service"

    def get_certificates(self, domain: str) -> dict[str, Any]:
        """
        Query crt.sh for certificates matching *domain*.
        """
        import time
        import copy

        domain_key = domain.strip().lower()
        now = time.time()
        if domain_key in self._cache:
            ts, cached_val = self._cache[domain_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        from core.offline_mode import offline_mode
        if offline_mode.is_enabled:
            return {"certificates": [], "count": 0, "subdomains": [], "offline": True}
        try:
            resp = requests.get(
                self.CRT_SH_URL,
                params={"q": f"%.{domain_key}", "output": "json"},
                timeout=self.TIMEOUT,
                headers={"User-Agent": "CyberMind-AI/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("crt.sh query failed for %s: %s", domain_key, exc)
            res = {"certificates": [], "count": 0, "subdomains": []}
            self._cache[domain_key] = (now, res)
            return res

        seen_names: set[str] = set()
        certs = []

        for entry in data[:100]:  # Cap at 100
            common_name = entry.get("common_name", "")
            name_value = entry.get("name_value", "")

            cert = {
                "issuer": entry.get("issuer_name", ""),
                "common_name": common_name,
                "name_value": name_value,
                "not_before": entry.get("not_before", ""),
                "not_after": entry.get("not_after", ""),
                "serial": entry.get("serial_number", ""),
            }
            certs.append(cert)

            # Extract subdomains
            for name in name_value.split("\n"):
                name = name.strip().lower()
                if name and name.endswith(domain.lower()):
                    seen_names.add(name)

        subdomains = sorted(seen_names)

        return {
            "certificates": certs[:50],
            "count": len(certs),
            "subdomains": subdomains,
        }

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.get_certificates(domain)

    def health_check(self) -> dict[str, Any]:
        return {"service": "CT Logs Service", "status": "Healthy"}


ct_logs_service = CTLogsService()
