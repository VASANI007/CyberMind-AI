"""
CyberMind AI

Short URL Service
"""

from __future__ import annotations

from urllib.parse import urlparse

import requests

from core.constants import (
    URL_SHORTENERS,
    API_TIMEOUT
)


class ShortURLService:

    def is_short_url(
        self,
        url: str
    ) -> bool:
        """
        Check whether URL belongs to a known URL shortener.
        """

        try:

            hostname = urlparse(
                url
            ).hostname

            if hostname is None:

                return False

            hostname = hostname.lower()

            if hostname.startswith("www."):

                hostname = hostname[4:]

            return hostname in URL_SHORTENERS

        except Exception:

            return False

    def expand_url(
        self,
        url: str
    ) -> str:
        """
        Expand shortened URL.
        """

        try:

            response = requests.get(
                url,
                allow_redirects=True,
                timeout=API_TIMEOUT
            )

            return response.url

        except Exception:

            return url

    def get_redirect_count(
        self,
        url: str
    ) -> int:
        """
        Return redirect count.
        """

        try:

            response = requests.get(
                url,
                allow_redirects=True,
                timeout=API_TIMEOUT
            )

            return len(
                response.history
            )

        except Exception:

            return 0

    def analyze(
        self,
        url: str
    ) -> dict:
        """
        Analyze shortened URL.
        """

        is_short = self.is_short_url(
            url
        )

        expanded = self.expand_url(
            url
        ) if is_short else url

        redirects = self.get_redirect_count(
            url
        )

        return {

            "is_shortened": is_short,

            "original_url": expanded,

            "redirect_count": redirects

        }


shorturl_service = ShortURLService()