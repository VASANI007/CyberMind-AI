"""
CyberMind AI
TOR Exit Node Service
Checks if an IP is a known TOR exit node.
Free — uses the torproject.org public bulk exit list.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import requests

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "ip"
_CACHE_FILE = _DATA_DIR / "tor_exit_nodes.txt"
_CACHE_MAX_AGE = 86400  # 24 hours


class TorExitNodeService:
    """
    Checks whether an IP address is a known TOR exit node.
    Downloads the list from torproject.org and caches locally.
    """

    TOR_LIST_URL = "https://check.torproject.org/torbulkexitlist"

    def __init__(self) -> None:
        self._nodes: set[str] = set()
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached TOR exit node list."""
        try:
            if _CACHE_FILE.exists():
                age = time.time() - _CACHE_FILE.stat().st_mtime
                with open(_CACHE_FILE, encoding="utf-8") as f:
                    self._nodes = {
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    }
                logger.info(
                    "Loaded %d TOR exit nodes (age: %.0fh).",
                    len(self._nodes), age / 3600,
                )
                # Refresh if stale
                if age > _CACHE_MAX_AGE:
                    self._refresh()
            else:
                self._refresh()
        except Exception as exc:
            logger.warning("TOR exit node cache load error: %s", exc)

    def _refresh(self) -> None:
        """Download fresh TOR exit node list."""
        try:
            resp = requests.get(
                self.TOR_LIST_URL,
                timeout=15,
                headers={"User-Agent": "CyberMind-AI/1.0"},
            )
            resp.raise_for_status()
            lines = resp.text.strip().split("\n")
            nodes = {
                line.strip()
                for line in lines
                if line.strip() and not line.startswith("#")
            }
            if nodes:
                self._nodes = nodes
                _DATA_DIR.mkdir(parents=True, exist_ok=True)
                with open(_CACHE_FILE, "w", encoding="utf-8") as f:
                    f.write("\n".join(sorted(nodes)))
                logger.info("Refreshed TOR exit nodes: %d entries.", len(nodes))
        except Exception as exc:
            logger.warning("TOR list download failed: %s", exc)

    @property
    def name(self) -> str:
        return "tor_exit_node_service"

    def is_tor_exit(self, ip: str) -> dict[str, Any]:
        """
        Check if *ip* is a TOR exit node.

        Returns
        -------
        dict with keys:
            is_tor   : bool
            ip       : str
            nodes_db : int — total nodes in database
        """
        return {
            "is_tor": ip.strip() in self._nodes,
            "ip": ip.strip(),
            "nodes_db": len(self._nodes),
        }

    def analyze(self, ip: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.is_tor_exit(ip)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "TOR Exit Node Service",
            "status": "Healthy",
            "nodes_loaded": len(self._nodes),
        }


tor_exit_node_service = TorExitNodeService()
