"""
CyberMind AI
Homograph Detection Service
Detects Unicode homograph/confusable attacks on domain names.
Offline — uses a static confusables table, no API key.
"""

from __future__ import annotations

from typing import Any

from core.logger import logger


# Static Unicode confusables table — maps visually similar chars to ASCII
CONFUSABLES: dict[str, str] = {
    "\u0430": "a",  # Cyrillic а
    "\u0435": "e",  # Cyrillic е
    "\u043e": "o",  # Cyrillic о
    "\u0440": "p",  # Cyrillic р
    "\u0441": "c",  # Cyrillic с
    "\u0443": "y",  # Cyrillic у
    "\u0445": "x",  # Cyrillic х
    "\u0456": "i",  # Cyrillic і
    "\u0458": "j",  # Cyrillic ј
    "\u043d": "h",  # Cyrillic н (loose)
    "\u0442": "t",  # Cyrillic т (loose)
    "\u0251": "a",  # Latin alpha
    "\u0261": "g",  # Latin script g
    "\u03b1": "a",  # Greek α
    "\u03bf": "o",  # Greek ο
    "\u03c1": "p",  # Greek ρ
    "\u03b5": "e",  # Greek ε
    "\u0501": "d",  # Cyrillic ԁ
    "\u050d": "g",  # Cyrillic ԍ
    "\u01c3": "!",  # Latin click
    "\uff41": "a",  # Fullwidth a
    "\uff45": "e",  # Fullwidth e
    "\uff4f": "o",  # Fullwidth o
    "\uff49": "i",  # Fullwidth i
    "\uff55": "u",  # Fullwidth u
    "\u0131": "i",  # Turkish ı
    "\u1d00": "a",  # Small-cap A
    "\u1d07": "e",  # Small-cap E
    "\u1d0f": "o",  # Small-cap O
    "\u0222": "ou", # Latin Ou
}

# Reverse: ASCII → set of confusable Unicode chars
_ASCII_TO_CONFUSABLES: dict[str, set[str]] = {}
for _u, _a in CONFUSABLES.items():
    _ASCII_TO_CONFUSABLES.setdefault(_a, set()).add(_u)


class HomographService:
    """
    Detects Unicode homograph / confusable attacks on domains.
    """

    @property
    def name(self) -> str:
        return "homograph_service"

    def detect(self, domain: str) -> dict[str, Any]:
        """
        Check whether *domain* contains Unicode homograph characters.

        Returns
        -------
        dict with keys:
            is_homograph    : bool
            confusable_chars: list[dict]  — each with char, ascii_equiv, position
            ascii_form      : str         — the domain with confusables replaced
            mixed_scripts   : bool        — True if multiple Unicode scripts used
        """
        confusable_chars = []
        ascii_parts = []
        scripts_seen: set[str] = set()

        for i, ch in enumerate(domain):
            if ch in CONFUSABLES:
                confusable_chars.append({
                    "char": ch,
                    "unicode": f"U+{ord(ch):04X}",
                    "ascii_equiv": CONFUSABLES[ch],
                    "position": i,
                })
                ascii_parts.append(CONFUSABLES[ch])
            else:
                ascii_parts.append(ch)

            # Script detection (simplified)
            cp = ord(ch)
            if 0x0400 <= cp <= 0x04FF:
                scripts_seen.add("Cyrillic")
            elif 0x0370 <= cp <= 0x03FF:
                scripts_seen.add("Greek")
            elif 0xFF00 <= cp <= 0xFFEF:
                scripts_seen.add("Fullwidth")
            elif cp < 0x0080:
                scripts_seen.add("Latin")
            else:
                scripts_seen.add("Other")

        mixed = len(scripts_seen - {"Latin"}) > 0 and "Latin" in scripts_seen

        return {
            "is_homograph": len(confusable_chars) > 0,
            "confusable_chars": confusable_chars,
            "ascii_form": "".join(ascii_parts),
            "mixed_scripts": mixed,
            "scripts_detected": sorted(scripts_seen),
        }

    def analyze(self, domain: str) -> dict[str, Any]:
        """Plugin interface."""
        return self.detect(domain)

    def health_check(self) -> dict[str, Any]:
        return {"service": "Homograph Service", "status": "Healthy"}


homograph_service = HomographService()
