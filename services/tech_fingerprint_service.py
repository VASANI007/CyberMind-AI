"""
CyberMind AI
Technology Fingerprint Service
Identifies web technologies from response headers and HTML.
Offline — uses a static signatures JSON, no API key.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.logger import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "security"


class TechFingerprintService:
    """
    Identifies web technologies (frameworks, servers, CMS, etc.)
    from HTTP response headers and HTML meta/script tags.
    """

    def __init__(self) -> None:
        self._signatures: list[dict] = []
        self._load_signatures()

    def _load_signatures(self) -> None:
        """Load technology signatures from data file."""
        path = _DATA_DIR / "tech_signatures.json"
        try:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._signatures = json.load(f)
                logger.info(
                    "Loaded %d tech signatures.", len(self._signatures)
                )
        except Exception as exc:
            logger.warning("Could not load tech signatures: %s", exc)

    @property
    def name(self) -> str:
        return "tech_fingerprint_service"

    def identify(
        self,
        headers: dict[str, str] | None = None,
        html: str = "",
    ) -> dict[str, Any]:
        """
        Identify technologies from headers and/or HTML.

        Returns
        -------
        dict with keys:
            technologies : list[dict] — name, category, confidence, evidence
            count        : int
        """
        headers = headers or {}
        detected: list[dict[str, Any]] = []

        headers_lower = {k.lower(): v for k, v in headers.items()}
        html_lower = html.lower() if html else ""

        for sig in self._signatures:
            matched = False
            evidence = ""

            # Check headers
            for hdr_rule in sig.get("headers", []):
                hdr_name = hdr_rule.get("name", "").lower()
                hdr_pattern = hdr_rule.get("pattern", "")
                if hdr_name in headers_lower:
                    val = headers_lower[hdr_name]
                    if hdr_pattern:
                        if re.search(hdr_pattern, val, re.IGNORECASE):
                            matched = True
                            evidence = f"Header {hdr_name}: {val}"
                    else:
                        matched = True
                        evidence = f"Header {hdr_name} present"

            # Check HTML patterns
            if not matched:
                for html_pattern in sig.get("html", []):
                    if re.search(html_pattern, html_lower, re.IGNORECASE):
                        matched = True
                        evidence = f"HTML pattern: {html_pattern[:50]}"
                        break

            # Check meta tags
            if not matched:
                for meta_rule in sig.get("meta", []):
                    meta_name = meta_rule.get("name", "")
                    meta_pattern = meta_rule.get("pattern", "")
                    regex = (
                        rf'<meta[^>]*name\s*=\s*["\']?{re.escape(meta_name)}["\']?'
                        rf'[^>]*content\s*=\s*["\']([^"\']*)["\']'
                    )
                    match = re.search(regex, html_lower, re.IGNORECASE)
                    if match:
                        if meta_pattern:
                            if re.search(meta_pattern, match.group(1), re.IGNORECASE):
                                matched = True
                                evidence = f"Meta {meta_name}: {match.group(1)[:40]}"
                        else:
                            matched = True
                            evidence = f"Meta tag: {meta_name}"
                        if matched:
                            break

            # Check script sources
            if not matched:
                for script_pattern in sig.get("scripts", []):
                    if re.search(script_pattern, html_lower, re.IGNORECASE):
                        matched = True
                        evidence = f"Script: {script_pattern[:50]}"
                        break

            if matched:
                detected.append({
                    "name": sig.get("name", "Unknown"),
                    "category": sig.get("category", "Other"),
                    "website": sig.get("website", ""),
                    "confidence": sig.get("confidence", "medium"),
                    "evidence": evidence,
                })

        return {
            "technologies": detected,
            "count": len(detected),
        }

    def analyze(
        self,
        headers: dict[str, str] | None = None,
        html: str = "",
    ) -> dict[str, Any]:
        """Plugin interface."""
        return self.identify(headers=headers, html=html)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Tech Fingerprint Service",
            "status": "Healthy",
            "signatures_loaded": len(self._signatures),
        }


tech_fingerprint_service = TechFingerprintService()
