"""
CyberMind AI

SSL Service
"""

from __future__ import annotations

import socket
import ssl
from datetime import datetime


class SSLService:

    def get_certificate(
        self,
        hostname: str,
        port: int = 443
    ) -> dict:
        """
        Fetch SSL certificate.
        """

        try:

            context = ssl.create_default_context()

            with socket.create_connection(
                (hostname, port),
                timeout=5
            ) as sock:

                with context.wrap_socket(
                    sock,
                    server_hostname=hostname
                ) as secure_socket:

                    certificate = secure_socket.getpeercert()

                    protocol = secure_socket.version()

                    cipher = secure_socket.cipher()

            return {

                "available": True,

                "certificate": certificate,

                "protocol": protocol,

                "cipher": cipher

            }

        except Exception:

            return {

                "available": False

            }

    def expiry_date(
        self,
        hostname: str
    ) -> datetime | None:
        """
        Return certificate expiry date.
        """

        result = self.get_certificate(hostname)

        if not result["available"]:

            return None

        expires = result["certificate"].get(
            "notAfter"
        )

        return datetime.strptime(

            expires,

            "%b %d %H:%M:%S %Y %Z"

        )

    def days_remaining(
        self,
        hostname: str
    ) -> int | None:
        """
        Remaining certificate days.
        """

        expiry = self.expiry_date(
            hostname
        )

        if expiry is None:

            return None

        return (

            expiry - datetime.utcnow()

        ).days

    def is_valid(
        self,
        hostname: str
    ) -> bool:
        """
        Check SSL validity.
        """

        days = self.days_remaining(
            hostname
        )

        if days is None:

            return False

        return days > 0

    def analyze(
        self,
        hostname: str
    ) -> dict:
        """
        SSL analysis.
        """

        result = self.get_certificate(
            hostname
        )

        if not result["available"]:

            return {

                "hostname": hostname,

                "ssl_available": False,

                "valid": False

            }

        certificate = result["certificate"]

        return {

            "hostname": hostname,

            "ssl_available": True,

            "issuer": certificate.get(

                "issuer"

            ),

            "subject": certificate.get(

                "subject"

            ),

            "serial_number": certificate.get(

                "serialNumber"

            ),

            "version": certificate.get(

                "version"

            ),

            "issued_on": certificate.get(

                "notBefore"

            ),

            "expires_on": certificate.get(

                "notAfter"

            ),

            "protocol": result["protocol"],

            "cipher": result["cipher"],

            "valid": self.is_valid(

                hostname

            ),

            "remaining_days": self.days_remaining(

                hostname

            )

        }


ssl_service = SSLService()