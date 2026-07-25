"""
CyberMind AI
File Entropy Service
Calculates Shannon entropy of file contents.
Offline — uses numpy (already installed).
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np

from core.logger import logger


class FileEntropyService:
    """
    Calculates Shannon entropy of file contents.
    High entropy (>7.0 for 8-bit data) may indicate
    encryption, compression, or packing.
    """

    # Thresholds for 8-bit byte entropy (max = 8.0)
    THRESHOLD_PACKED = 7.2     # Likely packed/encrypted
    THRESHOLD_SUSPICIOUS = 6.5  # Possibly compressed/obfuscated
    THRESHOLD_NORMAL = 4.5      # Normal structured data

    @property
    def name(self) -> str:
        return "file_entropy_service"

    def _shannon_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of a byte sequence."""
        if not data:
            return 0.0

        counts = Counter(data)
        length = len(data)
        entropy = 0.0

        for count in counts.values():
            if count == 0:
                continue
            p = count / length
            entropy -= p * math.log2(p)

        return round(entropy, 4)

    def calculate(self, file_bytes: bytes) -> dict[str, Any]:
        """
        Calculate file entropy.

        Parameters
        ----------
        file_bytes : complete file bytes

        Returns
        -------
        dict with keys:
            overall_entropy : float — Shannon entropy (0-8)
            classification  : str   — 'Normal', 'Suspicious', 'Packed/Encrypted'
            section_entropies : list[dict] — entropy per 1KB section (first 10)
            is_suspicious   : bool
            risk_contribution : int — 0-30
        """
        if not file_bytes:
            return {
                "overall_entropy": 0.0,
                "classification": "Empty",
                "section_entropies": [],
                "is_suspicious": False,
                "risk_contribution": 0,
            }

        overall = self._shannon_entropy(file_bytes)

        # Section-level entropy (1KB chunks, max 10)
        chunk_size = 1024
        sections = []
        for i in range(0, min(len(file_bytes), chunk_size * 10), chunk_size):
            chunk = file_bytes[i : i + chunk_size]
            if len(chunk) < 64:
                continue
            ent = self._shannon_entropy(chunk)
            sections.append({
                "offset": f"0x{i:04X}",
                "size": len(chunk),
                "entropy": ent,
            })

        # Classification
        if overall >= self.THRESHOLD_PACKED:
            classification = "Packed/Encrypted"
            risk = 25
        elif overall >= self.THRESHOLD_SUSPICIOUS:
            classification = "Suspicious"
            risk = 12
        elif overall >= self.THRESHOLD_NORMAL:
            classification = "Normal"
            risk = 0
        else:
            classification = "Low Entropy"
            risk = 0

        return {
            "overall_entropy": overall,
            "classification": classification,
            "section_entropies": sections,
            "is_suspicious": overall >= self.THRESHOLD_SUSPICIOUS,
            "risk_contribution": risk,
        }

    def analyze(self, file_bytes: bytes) -> dict[str, Any]:
        """Plugin interface."""
        return self.calculate(file_bytes)

    def health_check(self) -> dict[str, Any]:
        return {"service": "File Entropy Service", "status": "Healthy"}


file_entropy_service = FileEntropyService()
