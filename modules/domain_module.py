"""
CyberMind AI

Domain Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.domain_scanner import DomainScanner


class DomainModule(DomainScanner):
    """
    Domain Module wrapping DomainScanner.
    """

    def __repr__(self) -> str:
        return "DomainModule(Enterprise Version)"


domain_module = DomainModule()
