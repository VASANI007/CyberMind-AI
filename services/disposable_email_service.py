"""
CyberMind AI
Disposable Email Service
Checks if an email domain is a disposable/temporary email provider.
Tries live refresh weekly from GitHub, falls back to local domain lists.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "disposable_email"
_LIVE_CACHE = _DATA_DIR / "live_blocklist.conf"
_LIVE_URL = (
    "https://raw.githubusercontent.com/disposable-email-domains/"
    "disposable-email-domains/master/disposable_email_blocklist.conf"
)
_CACHE_TTL_SECONDS = 7 * 86400  # 7 days


class DisposableEmailService:
    """
    Checks whether an email domain is a known
    disposable/temporary email provider.
    """

    def __init__(self) -> None:
        self._domains: set[str] = set()
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._refresh_live_list()
        self._load_domains()

    def _is_cache_fresh(self) -> bool:
        """Return True if live cache is present and within TTL."""
        if not _LIVE_CACHE.exists():
            return False
        return (time.time() - _LIVE_CACHE.stat().st_mtime) < _CACHE_TTL_SECONDS

    def _refresh_live_list(self) -> None:
        """
        Fetch the upstream disposable-email-domains blocklist weekly.
        Caches to data/disposable_email/live_blocklist.conf.
        Silently skips on network failure — static files used as fallback.
        """
        if self._is_cache_fresh():
            return
        try:
            resp = requests.get(_LIVE_URL, timeout=10, headers={"User-Agent": "CyberMind-AI/1.0"})
            if resp.status_code == 200:
                _LIVE_CACHE.write_text(resp.text, encoding="utf-8", errors="ignore")
                logger.info("Disposable email blocklist refreshed from GitHub (%d bytes).", len(resp.text))
        except Exception as exc:
            logger.warning("Disposable email live refresh failed: %s", exc)

    def _load_domains(self) -> None:
        """Load disposable domains: live cache first, then static files."""
        try:
            # Load live cache (highest priority)
            if _LIVE_CACHE.exists():
                with open(_LIVE_CACHE, encoding="utf-8") as f:
                    for line in f:
                        d = line.strip().lower()
                        if d and not d.startswith("#"):
                            self._domains.add(d)

            # Also load any local static .txt / .conf files
            if _DATA_DIR.exists():
                for txt_file in _DATA_DIR.glob("*.txt"):
                    with open(txt_file, encoding="utf-8") as f:
                        for line in f:
                            d = line.strip().lower()
                            if d and not d.startswith("#"):
                                self._domains.add(d)
                for conf_file in _DATA_DIR.glob("*.conf"):
                    if conf_file == _LIVE_CACHE:
                        continue  # already loaded above
                    with open(conf_file, encoding="utf-8") as f:
                        for line in f:
                            d = line.strip().lower()
                            if d and not d.startswith("#"):
                                self._domains.add(d)

            logger.info("Loaded %d disposable email domains.", len(self._domains))
        except Exception as exc:
            logger.warning("Disposable email list load error: %s", exc)

    @property
    def name(self) -> str:
        return "disposable_email_service"

    def is_disposable(self, email_or_domain: str) -> dict[str, Any]:
        """
        Check if an email or domain is disposable.

        Parameters
        ----------
        email_or_domain : email address or domain string

        Returns
        -------
        dict with keys:
            is_disposable    : bool
            domain           : str
            risk_contribution : int — 0 or 25
        """
        # Extract domain
        if "@" in email_or_domain:
            domain = email_or_domain.split("@", 1)[1].lower().strip()
        else:
            domain = email_or_domain.lower().strip()

        is_disposable = domain in self._domains

        return {
            "is_disposable": is_disposable,
            "domain": domain,
            "risk_contribution": 25 if is_disposable else 0,
        }

    def analyze(self, email_or_domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.is_disposable(email_or_domain)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Disposable Email Service",
            "status": "Healthy",
            "domains_loaded": len(self._domains),
            "live_cache_exists": _LIVE_CACHE.exists(),
        }


disposable_email_service = DisposableEmailService()
