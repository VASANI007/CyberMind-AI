"""
CyberMind AI
JS Behaviour Service
Scans HTML content for suspicious JavaScript patterns.
Offline — regex-based, no API key required.
"""

from __future__ import annotations

import re
from typing import Any

from core.logger import logger


class JSBehaviorService:
    """
    Scans fetched HTML for suspicious JavaScript patterns
    such as eval(), document.write(), obfuscated content,
    base64 blobs, and known evasion techniques.
    """

    PATTERNS = [
        {
            "name": "eval()",
            "pattern": r"\beval\s*\(",
            "severity": "high",
            "description": "Dynamic code execution via eval()",
        },
        {
            "name": "document.write()",
            "pattern": r"\bdocument\.write\s*\(",
            "severity": "medium",
            "description": "Direct DOM manipulation via document.write()",
        },
        {
            "name": "unescape()",
            "pattern": r"\bunescape\s*\(",
            "severity": "high",
            "description": "String obfuscation via unescape()",
        },
        {
            "name": "Base64 Blob",
            "pattern": r"(?:atob|btoa)\s*\(|data:\s*(?:text|application)/[^;]+;base64,",
            "severity": "medium",
            "description": "Base64 encoded content detected",
        },
        {
            "name": "String.fromCharCode",
            "pattern": r"String\.fromCharCode\s*\(",
            "severity": "medium",
            "description": "Character code obfuscation",
        },
        {
            "name": "setTimeout/setInterval with string",
            "pattern": r"(?:setTimeout|setInterval)\s*\(\s*['\"]",
            "severity": "high",
            "description": "Timed code execution from string",
        },
        {
            "name": "Hidden iframe",
            "pattern": r"<iframe[^>]*(?:style\s*=\s*['\"][^'\"]*(?:display\s*:\s*none|visibility\s*:\s*hidden|width\s*:\s*0|height\s*:\s*0))",
            "severity": "high",
            "description": "Hidden iframe injection",
        },
        {
            "name": "window.location redirect",
            "pattern": r"window\.location\s*(?:\.href\s*)?=",
            "severity": "low",
            "description": "JavaScript-based redirect",
        },
        {
            "name": "Crypto-mining keywords",
            "pattern": r"(?:coinhive|cryptonight|stratum\+tcp|minero|coin-hive)",
            "severity": "critical",
            "description": "Crypto-mining script detected",
        },
        {
            "name": "Obfuscated variable names",
            "pattern": r"var\s+_0x[a-f0-9]{4,}",
            "severity": "high",
            "description": "Heavily obfuscated JavaScript (hex variable names)",
        },
    ]

    @property
    def name(self) -> str:
        return "js_behavior_service"

    def scan(self, html_content: str) -> dict[str, Any]:
        """
        Scan HTML for suspicious JS patterns.

        Returns
        -------
        dict with keys:
            flags      : list[dict] — each detected pattern with name, severity, count
            total      : int        — total flags found
            risk_score : int        — 0-100 risk contribution
        """
        if not html_content:
            return {"flags": [], "total": 0, "risk_score": 0}

        flags = []
        risk_score = 0

        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
        }

        for pattern_def in self.PATTERNS:
            try:
                matches = re.findall(
                    pattern_def["pattern"],
                    html_content,
                    re.IGNORECASE,
                )
                if matches:
                    count = len(matches)
                    flags.append({
                        "name": pattern_def["name"],
                        "severity": pattern_def["severity"],
                        "description": pattern_def["description"],
                        "count": count,
                    })
                    risk_score += severity_weights.get(
                        pattern_def["severity"], 5
                    ) * min(count, 3)
            except Exception as exc:
                logger.warning("JS pattern scan error: %s", exc)

        risk_score = min(risk_score, 100)

        return {
            "flags": flags,
            "total": len(flags),
            "risk_score": risk_score,
        }

    def analyze(self, html_content: str) -> dict[str, Any]:
        """Alias for scan() — plugin interface."""
        return self.scan(html_content)

    def health_check(self) -> dict[str, Any]:
        return {"service": "JS Behavior Service", "status": "Healthy"}


js_behavior_service = JSBehaviorService()
