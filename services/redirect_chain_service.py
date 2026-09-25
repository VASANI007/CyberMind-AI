"""
CyberMind AI
Redirect Chain Service
Follows HTTP redirects and returns the full hop chain.
Offline — no API key required.
"""

from __future__ import annotations

from typing import Any

import requests

from core.logger import logger


class RedirectChainService:
    """
    Follows HTTP 3xx redirects step by step
    and returns the complete redirect chain.
    """

    MAX_HOPS = 6
    TIMEOUT = 3.0
    _cache: dict[str, tuple[float, dict]] = {}

    @property
    def name(self) -> str:
        return "redirect_chain_service"

    def follow(self, url: str) -> dict[str, Any]:
        """
        Follow redirects from *url* and return the chain.
        """
        import time
        import copy

        url_key = url.strip()
        now = time.time()
        if url_key in self._cache:
            ts, cached_val = self._cache[url_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        chain: list[dict[str, Any]] = []
        visited: set[str] = set()
        current = url_key
        loop_detected = False

        for _ in range(self.MAX_HOPS):
            if current in visited:
                loop_detected = True
                break
            visited.add(current)

            try:
                resp = requests.get(
                    current,
                    allow_redirects=False,
                    timeout=self.TIMEOUT,
                    headers={"User-Agent": "CyberMind-AI/1.0"},
                    verify=False,
                    stream=True,
                )

                hop = {
                    "url": current,
                    "status_code": resp.status_code,
                    "server": resp.headers.get("Server", ""),
                    "content_type": resp.headers.get("Content-Type", ""),
                }
                chain.append(hop)

                if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get("Location", "")
                    if not location:
                        break
                    # Handle relative redirects
                    if location.startswith("/"):
                        from urllib.parse import urlparse
                        parsed = urlparse(current)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    current = location
                else:
                    break

            except Exception as exc:
                logger.warning("Redirect chain error at %s: %s", current, exc)
                chain.append({
                    "url": current,
                    "status_code": 0,
                    "error": str(exc),
                })
                break

        return {
            "chain": chain,
            "hops": max(len(chain) - 1, 0),
            "final": chain[-1]["url"] if chain else url,
            "loop": loop_detected,
        }

    def analyze(self, url: str) -> dict[str, Any]:
        """Alias for follow() — plugin interface."""
        return self.follow(url)

    def health_check(self) -> dict[str, Any]:
        return {"service": "Redirect Chain Service", "status": "Healthy"}


redirect_chain_service = RedirectChainService()
