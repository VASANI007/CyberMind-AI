"""
CyberMind AI

Security Headers Service
"""

from __future__ import annotations

import requests

from core.constants import API_TIMEOUT


class SecurityHeadersService:

    SECURITY_HEADERS = {

        "Strict-Transport-Security": "HSTS",

        "Content-Security-Policy": "CSP",

        "X-Frame-Options": "Clickjacking Protection",

        "X-Content-Type-Options": "MIME Sniffing Protection",

        "Referrer-Policy": "Referrer Policy",

        "Permissions-Policy": "Permissions Policy"

    }

    def fetch_headers(
        self,
        url: str
    ) -> dict:
        """
        Fetch HTTP headers.
        """

        try:

            response = requests.get(
                url,
                timeout=API_TIMEOUT,
                allow_redirects=True
            )

            return dict(
                response.headers
            )

        except Exception:

            return {}

    def analyze(
        self,
        url: str
    ) -> dict:
        """
        Analyze security headers.
        """

        headers = self.fetch_headers(
            url
        )

        if not headers:

            return {

                "success": False,

                "headers": {},

                "score": 0,

                "missing": list(
                    self.SECURITY_HEADERS.keys()
                )

            }

        available = {}

        missing = []

        score = 0

        headers_lower = {k.lower(): v for k, v in headers.items()}

        for header in self.SECURITY_HEADERS:

            if header.lower() in headers_lower:

                available[header] = headers_lower[header.lower()]

                score += 1

            else:

                missing.append(header)

        percentage = round(

            (score / len(self.SECURITY_HEADERS)) * 100,

            2

        )

        return {

            "success": True,

            "headers": available,

            "missing": missing,

            "score": percentage

        }


security_headers_service = SecurityHeadersService()