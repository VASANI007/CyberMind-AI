"""
CyberMind AI

Entropy Service
"""

from __future__ import annotations

import math
from collections import Counter


class EntropyService:

    def calculate(
        self,
        text: str
    ) -> float:
        """
        Calculate Shannon entropy.
        """

        if not text:

            return 0.0

        counts = Counter(text)

        length = len(text)

        entropy = 0.0

        for count in counts.values():

            probability = count / length

            entropy -= probability * math.log2(
                probability
            )

        return round(
            entropy,
            4
        )

    def risk_level(
        self,
        entropy: float
    ) -> str:
        """
        Return entropy risk level.
        """

        if entropy < 3.0:

            return "Low"

        if entropy < 4.0:

            return "Medium"

        if entropy < 4.8:

            return "High"

        return "Critical"

    def is_suspicious(
        self,
        text: str,
        threshold: float = 4.0
    ) -> bool:
        """
        Check whether text is suspicious.
        """

        return self.calculate(
            text
        ) >= threshold

    def analyze(
        self,
        text: str
    ) -> dict:
        """
        Analyze text entropy.
        """

        entropy = self.calculate(
            text
        )

        return {

            "text": text,

            "length": len(text),

            "entropy": entropy,

            "risk_level": self.risk_level(
                entropy
            ),

            "is_suspicious": self.is_suspicious(
                text
            )

        }


entropy_service = EntropyService()