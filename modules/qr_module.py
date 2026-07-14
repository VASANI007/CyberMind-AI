"""
CyberMind AI

QR Module wrapper for compatibility.
"""

from __future__ import annotations

from modules.qr_scanner import QRScanner


class QRModule(QRScanner):
    """
    QR Module wrapping QRScanner.
    """

    def __repr__(self) -> str:
        return "QRModule(Enterprise Version)"


qr_module = QRModule()
