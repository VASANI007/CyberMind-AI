"""
CyberMind AI

SSL Service
"""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone


def verify_https(hostname: str, timeout: float = 4.0) -> dict:
    """Performs a REAL TLS handshake and certificate check — not a string match."""
    try:
        if not hostname:
            return {"valid": False, "reason": "Empty hostname provided."}
        if "://" in hostname:
            hostname = hostname.split("://")[1].split("/")[0]
        elif "/" in hostname:
            hostname = hostname.split("/")[0]
        if ":" in hostname:
            hostname = hostname.split(":")[0]

        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                days_left = (not_after - datetime.now(timezone.utc)).days
                return {
                    "valid": True,
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "expires": not_after.isoformat(),
                    "days_until_expiry": days_left,
                    "expiring_soon": days_left < 14,
                }
    except (socket.timeout, socket.gaierror, ConnectionRefusedError):
        return {"valid": False, "reason": "Could not connect on port 443 — site may not support HTTPS or is unreachable."}
    except ssl.SSLCertVerificationError as e:
        return {"valid": False, "reason": f"Certificate verification failed: {e}"}
    except Exception as e:
        return {"valid": False, "reason": f"Unexpected error: {e}"}


class SSLService:
    def verify_https(self, hostname: str, timeout: float = 4.0) -> dict:
        return verify_https(hostname, timeout=timeout)


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