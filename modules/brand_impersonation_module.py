"""
CyberMind AI
Brand Impersonation Module
Checks domains against known brands using homograph + typosquat services.
Offline — uses static curated brand list.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "domain"


class BrandImpersonationModule:
    """
    Detects whether a domain is impersonating a well-known brand
    by combining homograph detection and typosquat analysis.
    """

    def __init__(self) -> None:
        self._brands: list[dict[str, Any]] = []
        self._load_brands()

    def _load_brands(self) -> None:
        path = _DATA_DIR / "known_brands.json"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._brands = json.load(f)
                logger.info(
                    "Loaded %d known brands for impersonation detection.",
                    len(self._brands),
                )
        except Exception as exc:
            logger.warning("Could not load known brands: %s", exc)

    @property
    def name(self) -> str:
        return "brand_impersonation_module"

    def check(self, domain: str) -> dict[str, Any]:
        """
        Check if *domain* is impersonating a known brand.

        Returns
        -------
        dict with keys:
            is_impersonation : bool
            brand            : str | None   — matched brand name
            brand_domain     : str | None   — official brand domain
            method           : str          — 'homograph', 'typosquat', or 'keyword'
            confidence       : float        — 0.0 to 1.0
        """
        import difflib

        domain_lower = domain.lower().strip()
        base = domain_lower.split(".")[0] if "." in domain_lower else domain_lower

        best_match = None
        best_confidence = 0.0
        best_method = ""

        for brand_entry in self._brands:
            brand_name = brand_entry.get("name", "")
            brand_domains = brand_entry.get("domains", [])
            brand_keywords = brand_entry.get("keywords", [])

            for bd in brand_domains:
                bd_lower = bd.lower()
                bd_base = bd_lower.split(".")[0]

                # Exact match → not impersonation
                if domain_lower == bd_lower or base == bd_base:
                    return {
                        "is_impersonation": False,
                        "brand": brand_name,
                        "brand_domain": bd,
                        "method": "exact_match",
                        "confidence": 0.0,
                    }

                # Typosquat check
                ratio = difflib.SequenceMatcher(None, base, bd_base).ratio()
                if ratio >= 0.80 and ratio > best_confidence:
                    best_match = brand_entry
                    best_confidence = ratio
                    best_method = "typosquat"

            # Keyword-in-domain check
            for kw in brand_keywords:
                if kw.lower() in base and base != kw.lower():
                    conf = 0.70
                    if conf > best_confidence:
                        best_match = brand_entry
                        best_confidence = conf
                        best_method = "keyword"

        # Homograph check
        try:
            from services.homograph_service import homograph_service
            hg = homograph_service.detect(domain_lower)
            if hg.get("is_homograph"):
                ascii_form = hg.get("ascii_form", "")
                for brand_entry in self._brands:
                    for bd in brand_entry.get("domains", []):
                        bd_base = bd.lower().split(".")[0]
                        ascii_base = ascii_form.split(".")[0]
                        ratio = difflib.SequenceMatcher(
                            None, ascii_base, bd_base
                        ).ratio()
                        if ratio >= 0.85 and ratio > best_confidence:
                            best_match = brand_entry
                            best_confidence = ratio
                            best_method = "homograph"
        except Exception as exc:
            logger.warning("Homograph check failed: %s", exc)

        if best_match and best_confidence >= 0.70:
            return {
                "is_impersonation": True,
                "brand": best_match.get("name", "Unknown"),
                "brand_domain": best_match.get("domains", [""])[0],
                "method": best_method,
                "confidence": round(best_confidence, 3),
            }

        return {
            "is_impersonation": False,
            "brand": None,
            "brand_domain": None,
            "method": "",
            "confidence": 0.0,
        }

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.check(domain)

    def health_check(self) -> dict[str, Any]:
        return {
            "module": "Brand Impersonation Module",
            "status": "Healthy",
            "brands_loaded": len(self._brands),
        }


brand_impersonation_module = BrandImpersonationModule()
