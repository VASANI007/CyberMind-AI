"""
CyberMind AI

Website Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.website_scanner import WebsiteScanner


class WebsiteModule(WebsiteScanner):
    """
    Website Module wrapping WebsiteScanner.
    """

    def __repr__(self) -> str:
        return "WebsiteModule(Enterprise Version)"


website_module = WebsiteModule()
