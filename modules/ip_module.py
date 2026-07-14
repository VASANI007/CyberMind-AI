"""
CyberMind AI

IP Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.ip_scanner import IPScanner


class IPModule(IPScanner):
    """
    IP Module wrapping IPScanner.
    """

    def __repr__(self) -> str:
        return "IPModule(Enterprise Version)"


ip_module = IPModule()
