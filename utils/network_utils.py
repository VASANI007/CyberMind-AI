"""
CyberMind AI

Network Utilities

Enterprise Production Version
"""

from __future__ import annotations

import socket

from urllib.parse import (
    urlparse
)

from typing import Any

from core.logger import logger


class NetworkUtils:
    """
    Enterprise Network Utility.

    Responsibilities

    • Hostname

    • IP Resolution

    • Port Check

    • URL Parsing

    • Reachability

    • Network Validation
    """

    DEFAULT_TIMEOUT = 5

    def __init__(
        self
    ) -> None:

        logger.info(

            "Network Utils initialized."

        )

    def hostname(
        self,
        url: str
    ) -> str:
        """
        Extract hostname.
        """

        parsed = urlparse(

            url

        )

        return (

            parsed.hostname

            or ""

        ).lower()

    def port(
        self,
        url: str
    ) -> int | None:
        """
        Extract port.
        """

        return urlparse(

            url

        ).port

    def scheme(
        self,
        url: str
    ) -> str:
        """
        Extract scheme.
        """

        return urlparse(

            url

        ).scheme.lower()

    def path(
        self,
        url: str
    ) -> str:
        """
        Extract path.
        """

        return urlparse(

            url

        ).path

    def query(
        self,
        url: str
    ) -> str:
        """
        Extract query.
        """

        return urlparse(

            url

        ).query

    def fragment(
        self,
        url: str
    ) -> str:
        """
        Extract fragment.
        """

        return urlparse(

            url

        ).fragment

    def resolve_ip(
        self,
        hostname: str
    ) -> str | None:
        """
        Resolve hostname.
        """

        try:

            return socket.gethostbyname(

                hostname

            )

        except Exception:

            return None

    def reverse_lookup(
        self,
        ip: str
    ) -> str | None:
        """
        Reverse DNS lookup.
        """

        try:

            return socket.gethostbyaddr(

                ip

            )[0]

        except Exception:

            return None

    def port_open(
        self,
        host: str,
        port: int,
        timeout: int = DEFAULT_TIMEOUT
    ) -> bool:
        """
        Check TCP port.
        """

        try:

            connection = socket.create_connection(

                (

                    host,

                    port

                ),

                timeout

            )

            connection.close()

            return True

        except Exception:

            return False

    def reachable(
        self,
        host: str
    ) -> bool:
        """
        Check host reachability.
        """

        return (

            self.resolve_ip(

                host

            )

            is not None

        )

    def socket_timeout(
        self,
        timeout: int
    ) -> None:
        """
        Set socket timeout.
        """

        socket.setdefaulttimeout(

            timeout

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Network Utils",

            "status":

                "Healthy",

            "default_timeout":

                self.DEFAULT_TIMEOUT

        }

    def __repr__(
        self
    ) -> str:

        return (

            "NetworkUtils("

            "Enterprise Version)"

        )


network_utils = NetworkUtils()