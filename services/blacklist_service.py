"""
CyberMind AI

Blacklist Service
"""

import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from config.settings import DATASET_PATH

_CACHE_DIR = DATASET_PATH / "url" / "blacklist_cache"
_OPENPHISH_LIVE = _CACHE_DIR / "openphish_live.txt"
_PHISHTANK_LIVE = _CACHE_DIR / "phishtank_live.csv"
_CACHE_TTL_SECONDS = 86400  # 24 hours


class BlacklistService:

    def __init__(self):
        self.blacklist = set()
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.refresh_live_feeds()
        self.load()

    def _is_cache_fresh(self, path: Path) -> bool:
        """Return True if cache file exists and was written within TTL."""
        if not path.exists():
            return False
        return (time.time() - path.stat().st_mtime) < _CACHE_TTL_SECONDS

    def refresh_live_feeds(self, auto_updates_enabled: bool = True):
        """
        Fetch live OpenPhish + PhishTank feeds and cache them locally.
        Gated behind settings_auto_updates toggle.
        """
        try:
            import streamlit as st
            if not st.session_state.get("settings_auto_updates", True):
                auto_updates_enabled = False
        except Exception:
            pass

        if not auto_updates_enabled:
            return

        feeds = [
            ("https://openphish.com/feed.txt", _OPENPHISH_LIVE),
            ("https://data.phishtank.com/data/online-valid.csv", _PHISHTANK_LIVE),
        ]
        for url, cache_path in feeds:
            if self._is_cache_fresh(cache_path):
                continue
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "CyberMind-AI/1.0"})
                if resp.status_code == 200:
                    cache_path.write_text(resp.text, encoding="utf-8", errors="ignore")
            except Exception:
                # Network unavailable — fall back to cached/static file
                pass

    def get_cache_info(self) -> dict:
        auto_enabled = True
        try:
            import streamlit as st
            auto_enabled = st.session_state.get("settings_auto_updates", True)
        except Exception:
            pass

        mtime = None
        for p in [_OPENPHISH_LIVE, _PHISHTANK_LIVE]:
            if p.exists():
                mtime = max(mtime or 0, p.stat().st_mtime)

        if mtime:
            from datetime import datetime
            dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            note = f"Using cached threat data from {dt_str}" if auto_enabled else f"Auto-updates disabled — using data cached on {dt_str}"
        else:
            note = "Using bundled static threat intelligence snapshot"

        return {
            "auto_updates": auto_enabled,
            "cache_note": note,
            "cached_at": dt_str if mtime else None
        }

    def load(self):
        """
        Load blacklist datasets. Prefers live-cached files; falls back
        to bundled static snapshots if cache is missing or empty.
        """
        # Prefer live cache if available, otherwise use static snapshots
        files = [
            (_OPENPHISH_LIVE if _OPENPHISH_LIVE.exists() else
             DATASET_PATH / "datasets" / "url" / "raw" / "openphish_feed.txt"),
            (_PHISHTANK_LIVE if _PHISHTANK_LIVE.exists() else
             DATASET_PATH / "datasets" / "url" / "raw" / "phishtank_urls.csv"),
        ]

        for file in files:
            if not file.exists():
                continue
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if "," in line:
                        line = line.split(",")[0]
                    self.blacklist.add(line.lower())

    def normalize(self, url: str) -> str:
        """Normalize URL."""
        parsed = urlparse(url)
        return parsed.geturl().lower()

    def domain(self, url: str) -> str:
        """Extract domain."""
        parsed = urlparse(url)
        return (parsed.hostname or "").lower()

    def is_blacklisted(self, url: str) -> bool:
        """Check blacklist."""
        url = self.normalize(url)
        domain = self.domain(url)
        if url in self.blacklist:
            return True
        if domain in self.blacklist:
            return True
        return False

    def analyze(self, url: str) -> dict:
        """Analyze blacklist."""
        return {
            "url": url,
            "blacklisted": self.is_blacklisted(url),
        }

    def lookup(self, target: str) -> dict:
        """Lookup target in blacklist."""
        return self.analyze(target)

    def total_entries(self) -> int:
        """Total blacklist entries."""
        return len(self.blacklist)


blacklist_service = BlacklistService()