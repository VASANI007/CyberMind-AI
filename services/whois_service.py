"""
CyberMind AI

WHOIS Service
"""

from __future__ import annotations

from datetime import datetime

import whois


class WhoisService:

    def lookup(
        self,
        domain: str
    ) -> dict:
        """
        Perform WHOIS lookup.
        """

        try:

            result = whois.whois(domain)

            return self._format(result)

        except Exception:

            return {}

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

        created = result.get(
            "creation_date"
        )

        if created is None:

            return None

        if hasattr(created, "tzinfo") and created.tzinfo is not None:
            created = created.replace(tzinfo=None)

        return (

            datetime.now() - created

        ).days

    def expires_in(
        self,
        domain: str
    ) -> int | None:
        """
        Return remaining days until expiration.
        """

        result = self.lookup(domain)

        expiry = result.get(
            "expiration_date"
        )

        if expiry is None:

            return None

        if hasattr(expiry, "tzinfo") and expiry.tzinfo is not None:
            expiry = expiry.replace(tzinfo=None)

        return (

            expiry - datetime.now()

        ).days

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

        return {

            "domain": domain,

            "exists": True,

            "registrar": result.get(
                "registrar"
            ),

            "creation_date": result.get(
                "creation_date"
            ),

            "expiration_date": result.get(
                "expiration_date"
            ),

            "updated_date": result.get(
                "updated_date"
            ),

            "name_servers": result.get(
                "name_servers"
            ),

            "status": result.get(
                "status"
            ),

            "emails": result.get(
                "emails"
            ),

            "dnssec": result.get(
                "dnssec"
            ),

            "age_days": self.age(
                domain
            ),

            "domain_age_days": self.age(
                domain
            ),

            "expires_in_days": self.expires_in(
                domain
            )

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