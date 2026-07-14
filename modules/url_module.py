"""
CyberMind AI

URL Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.url_scanner import URLScanner


class URLModule(URLScanner):
    """
    URL Module wrapping URLScanner.
    """

    def __repr__(self) -> str:
        return "URLModule(Enterprise Version)"


url_module = URLModule()
