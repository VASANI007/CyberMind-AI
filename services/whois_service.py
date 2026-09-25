"""
CyberMind AI

WHOIS Service
"""

from __future__ import annotations

from datetime import datetime

import whois


class WhoisService:

    _cache: dict[str, tuple[float, dict]] = {}

    def lookup(
        self,
        domain: str
    ) -> dict:
        """
        Perform WHOIS lookup with strict 2.5-second thread execution timeout and in-memory TTL caching.
        """
        import time
        import copy
        import socket
        import concurrent.futures

        domain_key = domain.strip().lower()
        now = time.time()
        if domain_key in self._cache:
            ts, cached_val = self._cache[domain_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        def _raw_whois():
            old_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(2.5)
                return whois.whois(domain_key)
            finally:
                socket.setdefaulttimeout(old_timeout)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_raw_whois)
                result = future.result(timeout=2.5)
                formatted = self._format(result)
                self._cache[domain_key] = (now, formatted)
                return formatted
        except Exception:
            empty = {}
            self._cache[domain_key] = (now, empty)
            return empty

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