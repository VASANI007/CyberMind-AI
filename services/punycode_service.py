"""
CyberMind AI

Punycode Service
"""

from __future__ import annotations


class PunycodeService:

    def encode(
        self,
        domain: str
    ) -> str:
        """
        Convert Unicode domain to Punycode.
        """

        try:

            return domain.encode(
                "idna"
            ).decode(
                "ascii"
            )

        except Exception:

            return domain

    def decode(
        self,
        domain: str
    ) -> str:
        """
        Convert Punycode to Unicode.
        """

        try:

            return domain.encode(
                "ascii"
            ).decode(
                "idna"
            )

        except Exception:

            return domain

    def is_punycode(
        self,
        domain: str
    ) -> bool:
        """
        Check whether domain is Punycode.
        """

        return "xn--" in domain.lower()

    def contains_unicode(
        self,
        domain: str
    ) -> bool:
        """
        Check whether domain contains Unicode characters.
        """

        try:

            domain.encode(
                "ascii"
            )

            return False

        except UnicodeEncodeError:

            return True

    def normalize(
        self,
        domain: str
    ) -> str:
        """
        Return normalized ASCII domain.
        """

        return self.encode(
            domain.strip().lower()
        )


punycode_service = PunycodeService()