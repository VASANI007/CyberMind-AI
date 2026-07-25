"""
CyberMind AI
SPF/DKIM/DMARC Service
Checks email authentication records via DNS TXT lookups.
Free — uses dnspython (already installed), no API key.
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


class SPFDKIMDMARCService:
    """
    Checks SPF, DKIM, and DMARC DNS records for an email domain.
    """

    DNS_TIMEOUT = 5

    @property
    def name(self) -> str:
        return "spf_dkim_dmarc_service"

    def check(self, domain: str) -> dict[str, Any]:
        """
        Check SPF, DKIM, and DMARC records for *domain*.

        Returns
        -------
        dict with keys:
            spf   : dict — present, record, valid
            dkim  : dict — present, record (checks default selector)
            dmarc : dict — present, record, policy
            score : int  — 0-100 authentication score
        """
        spf = self._check_spf(domain)
        dkim = self._check_dkim(domain)
        dmarc = self._check_dmarc(domain)

        # Score: +33 for each present record
        score = 0
        if spf.get("present"):
            score += 33
        if dkim.get("present"):
            score += 33
        if dmarc.get("present"):
            score += 34

        return {
            "spf": spf,
            "dkim": dkim,
            "dmarc": dmarc,
            "score": score,
        }

    def _check_spf(self, domain: str) -> dict[str, Any]:
        """Check SPF (TXT record starting with 'v=spf1')."""
        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = self.DNS_TIMEOUT
            resolver.lifetime = self.DNS_TIMEOUT

            answers = resolver.resolve(domain, "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt.lower().startswith("v=spf1"):
                    return {
                        "present": True,
                        "record": txt[:200],
                        "valid": True,
                    }

            return {"present": False, "record": "", "valid": False}

        except Exception as exc:
            logger.debug("SPF check for %s: %s", domain, exc)
            return {"present": False, "record": "", "valid": False, "error": str(exc)}

    def _check_dkim(self, domain: str) -> dict[str, Any]:
        """Check DKIM (TXT record at default._domainkey.domain)."""
        selectors = ["default", "google", "selector1", "selector2", "k1", "dkim"]

        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = self.DNS_TIMEOUT
            resolver.lifetime = self.DNS_TIMEOUT

            for selector in selectors:
                try:
                    qname = f"{selector}._domainkey.{domain}"
                    answers = resolver.resolve(qname, "TXT")
                    for rdata in answers:
                        txt = str(rdata).strip('"')
                        if "v=dkim1" in txt.lower() or "p=" in txt:
                            return {
                                "present": True,
                                "record": txt[:200],
                                "selector": selector,
                            }
                except Exception:
                    continue

            return {"present": False, "record": "", "selector": ""}

        except Exception as exc:
            logger.debug("DKIM check for %s: %s", domain, exc)
            return {"present": False, "record": "", "selector": "", "error": str(exc)}

    def _check_dmarc(self, domain: str) -> dict[str, Any]:
        """Check DMARC (TXT record at _dmarc.domain)."""
        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = self.DNS_TIMEOUT
            resolver.lifetime = self.DNS_TIMEOUT

            qname = f"_dmarc.{domain}"
            answers = resolver.resolve(qname, "TXT")

            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt.lower().startswith("v=dmarc1"):
                    # Extract policy
                    policy = "none"
                    for part in txt.split(";"):
                        part = part.strip()
                        if part.lower().startswith("p="):
                            policy = part.split("=", 1)[1].strip()
                            break

                    return {
                        "present": True,
                        "record": txt[:200],
                        "policy": policy,
                    }

            return {"present": False, "record": "", "policy": ""}

        except Exception as exc:
            logger.debug("DMARC check for %s: %s", domain, exc)
            return {"present": False, "record": "", "policy": "", "error": str(exc)}

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.check(domain)

    def health_check(self) -> dict[str, Any]:
        return {"service": "SPF DKIM DMARC Service", "status": "Healthy"}


spf_dkim_dmarc_service = SPFDKIMDMARCService()
