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

    _cache: dict[str, tuple[float, dict]] = {}

    def fetch_headers(
        self,
        url: str
    ) -> dict:
        """
        Fetch HTTP headers using fast HEAD/GET stream request and in-memory TTL caching.
        """
        import time
        import copy

        url_key = url.strip()
        now = time.time()
        if url_key in self._cache:
            ts, cached_val = self._cache[url_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        headers = {}
        ua = {"User-Agent": "CyberMind-AI/1.0"}
        try:
            # Try HEAD first (fastest - headers only, no body)
            resp = requests.head(url_key, timeout=3.0, allow_redirects=True, headers=ua)
            if resp.headers:
                headers = dict(resp.headers)
        except Exception:
            pass

        if not headers:
            try:
                # Fallback to GET with stream=True so body is not downloaded
                resp = requests.get(url_key, timeout=3.0, allow_redirects=True, stream=True, headers=ua)
                if resp.headers:
                    headers = dict(resp.headers)
            except Exception:
                pass

        self._cache[url_key] = (now, headers)
        return copy.deepcopy(headers)

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