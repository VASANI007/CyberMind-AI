"""
CyberMind AI

Email Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.email_scanner import EmailScanner


class EmailModule(EmailScanner):
    """
    Email Module wrapping EmailScanner.
    """

    def __repr__(self) -> str:
        return "EmailModule(Enterprise Version)"


email_module = EmailModule()
