"""
CyberMind AI

WHOIS Service
"""

from __future__ import annotations

from datetime import datetime

import whois


class WhoisService:

    _cache: dict[str, tuple[float, dict]] = {}

    def _parse_iso_date(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        try:
            clean_str = str(date_str).replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
            return dt.replace(tzinfo=None)
        except Exception:
            return None

    def _lookup_rdap(self, domain: str) -> dict | None:
        """
        Query modern RDAP (Registration Data Access Protocol) over HTTPS port 443.
        Bypasses port 43 socket blocks and timeouts.
        """
        import requests
        try:
            url = f"https://rdap.org/domain/{domain}"
            headers = {"User-Agent": "CyberMindAI/1.0 (Security Scanner)"}
            resp = requests.get(url, headers=headers, timeout=2.5, allow_redirects=True)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not isinstance(data, dict):
                return None

            creation_date = None
            expiration_date = None
            updated_date = None
            for event in data.get("events", []):
                act = str(event.get("eventAction", "")).lower()
                d_val = event.get("eventDate")
                if "registration" in act:
                    creation_date = self._parse_iso_date(d_val)
                elif "expiration" in act:
                    expiration_date = self._parse_iso_date(d_val)
                elif "last changed" in act or "last update" in act:
                    if not updated_date:
                        updated_date = self._parse_iso_date(d_val)

            registrar = None
            emails = []
            for entity in data.get("entities", []):
                roles = [str(r).lower() for r in entity.get("roles", [])]
                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1 and isinstance(vcard[1], list):
                    for item in vcard[1]:
                        if len(item) >= 4:
                            if item[0] == "fn" and "registrar" in roles and not registrar:
                                registrar = str(item[3])
                            elif item[0] == "email":
                                emails.append(str(item[3]))
                if not registrar and "registrar" in roles and entity.get("handle"):
                    registrar = str(entity.get("handle"))

            nameservers = []
            for ns in data.get("nameservers", []):
                ldh = ns.get("ldhName")
                if ldh:
                    nameservers.append(str(ldh).lower())

            status = data.get("status", [])
            dnssec = None
            sec_dns = data.get("secureDNS", {})
            if isinstance(sec_dns, dict):
                dnssec = sec_dns.get("delegationSigned")

            return {
                "registrar": registrar,
                "creation_date": creation_date,
                "expiration_date": expiration_date,
                "updated_date": updated_date,
                "name_servers": sorted(list(set(nameservers))),
                "status": status,
                "emails": emails if emails else None,
                "dnssec": dnssec,
            }
        except Exception:
            return None

    def lookup(
        self,
        domain: str
    ) -> dict:
        """
        Perform WHOIS/RDAP lookup with in-memory TTL caching and HTTPS-first fallback.
        """
        import time
        import copy
        import socket
        import concurrent.futures
        import io
        import sys

        domain_key = domain.strip().lower()
        now = time.time()
        if domain_key in self._cache:
            ts, cached_val = self._cache[domain_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        # 1. Primary: Fast, reliable RDAP over HTTPS (Port 443)
        rdap_res = self._lookup_rdap(domain_key)
        if rdap_res and (rdap_res.get("creation_date") or rdap_res.get("registrar")):
            self._cache[domain_key] = (now, rdap_res)
            return rdap_res

        # 2. Fallback: Raw WHOIS with stderr silence to suppress socket timeout noise
        def _raw_whois():
            old_timeout = socket.getdefaulttimeout()
            old_err = sys.stderr
            try:
                socket.setdefaulttimeout(2.5)
                sys.stderr = io.StringIO()
                return whois.whois(domain_key)
            finally:
                sys.stderr = old_err
                socket.setdefaulttimeout(old_timeout)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_raw_whois)
                result = future.result(timeout=2.5)
                formatted = self._format(result)
                self._cache[domain_key] = (now, formatted)
                return formatted
        except Exception:
            final_res = rdap_res if rdap_res else {}
            self._cache[domain_key] = (now, final_res)
            return final_res

    def _calc_age(self, created) -> int | None:
        if created is None:
            return None
        if hasattr(created, "tzinfo") and created.tzinfo is not None:
            created = created.replace(tzinfo=None)
        try:
            return (datetime.now() - created).days
        except Exception:
            return None

    def _calc_expires(self, expiry) -> int | None:
        if expiry is None:
            return None
        if hasattr(expiry, "tzinfo") and expiry.tzinfo is not None:
            expiry = expiry.replace(tzinfo=None)
        try:
            return (expiry - datetime.now()).days
        except Exception:
            return None

    def exists(
        self,
        domain: str
    ) -> bool:
        """
        Check whether domain exists.
        """
        result = self.lookup(domain)
        return bool(result)

    def age(
        self,
        domain: str
    ) -> int | None:
        """
        Return domain age in days.
        """
        result = self.lookup(domain)
        return self._calc_age(result.get("creation_date"))

    def expires_in(
        self,
        domain: str
    ) -> int | None:
        """
        Return remaining days until expiration.
        """
        result = self.lookup(domain)
        return self._calc_expires(result.get("expiration_date"))

    def analyze(
        self,
        domain: str
    ) -> dict:
        """
        Analyze domain.
        """
        result = self.lookup(domain)

        if not result:
            return {
                "domain": domain,
                "exists": False
            }

        created = result.get("creation_date")
        expiry = result.get("expiration_date")
        age_days = self._calc_age(created)
        expires_days = self._calc_expires(expiry)

        return {
            "domain": domain,
            "exists": True,
            "registrar": result.get("registrar"),
            "creation_date": created,
            "expiration_date": expiry,
            "updated_date": result.get("updated_date"),
            "name_servers": result.get("name_servers"),
            "status": result.get("status"),
            "emails": result.get("emails"),
            "dnssec": result.get("dnssec"),
            "age_days": age_days,
            "domain_age_days": age_days,
            "expires_in_days": expires_days
        }

    def _normalize_date(
        self,
        value
    ):
        """
        Normalize WHOIS date.
        """

        if isinstance(
            value,
            list
        ):

            if value:

                return value[0]

            return None

        return value

    def _format(
        self,
        data
    ) -> dict:
        """
        Format WHOIS response.
        """

        return {

            "registrar": data.registrar,

            "creation_date": self._normalize_date(
                data.creation_date
            ),

            "expiration_date": self._normalize_date(
                data.expiration_date
            ),

            "updated_date": self._normalize_date(
                data.updated_date
            ),

            "name_servers": sorted(

                list(

                    set(

                        data.name_servers or []

                    )

                )

            ),

            "status": data.status,

            "emails": data.emails,

            "dnssec": getattr(

                data,

                "dnssec",

                None

            )

        }


whois_service = WhoisService()