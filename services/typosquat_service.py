"""
CyberMind AI
Typosquat Detection Service
Detects typosquatting domains using edit-distance matching.
Offline — uses difflib (stdlib) against a static popular-domains list.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "domain"


class TyposquatService:
    """
    Checks whether a domain is a typosquat of a well-known domain
    using difflib.SequenceMatcher for edit-distance similarity.
    """

    SIMILARITY_THRESHOLD = 0.80  # Minimum ratio to flag

    def __init__(self) -> None:
        self._popular_domains: list[str] = []
        self._load_domains()

    def _load_domains(self) -> None:
        """Load popular domains list from data file."""
        path = _DATA_DIR / "popular_domains.json"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self._popular_domains = [
                    d.lower().strip() for d in data if isinstance(d, str)
                ]
                logger.info(
                    "Loaded %d popular domains for typosquat detection.",
                    len(self._popular_domains),
                )
        except Exception as exc:
            logger.warning("Could not load popular domains: %s", exc)

    @property
    def name(self) -> str:
        return "typosquat_service"

    def check(self, domain: str) -> dict[str, Any]:
        """
        Check if *domain* is a typosquat of any popular domain.

        Returns
        -------
        dict with keys:
            is_typosquat : bool
            matches      : list[dict] — each with domain, similarity
            closest      : str | None — closest popular domain
            similarity   : float      — similarity ratio of closest match
        """
        domain = domain.lower().strip()
        # Remove TLD for comparison
        base = domain.split(".")[0] if "." in domain else domain

        matches = []

        for popular in self._popular_domains:
            pop_base = popular.split(".")[0] if "." in popular else popular

            # Skip exact match
            if base == pop_base:
                continue

            ratio = difflib.SequenceMatcher(
                None, base, pop_base
            ).ratio()

            if ratio >= self.SIMILARITY_THRESHOLD:
                matches.append({
                    "domain": popular,
                    "similarity": round(ratio, 3),
                })

        # Sort by similarity descending
        matches.sort(key=lambda m: m["similarity"], reverse=True)
        top = matches[:5]

        return {
            "is_typosquat": len(top) > 0,
            "matches": top,
            "closest": top[0]["domain"] if top else None,
            "similarity": top[0]["similarity"] if top else 0.0,
        }

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.check(domain)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Typosquat Service",
            "status": "Healthy",
            "domains_loaded": len(self._popular_domains),
        }


typosquat_service = TyposquatService()
