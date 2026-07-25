"""
CyberMind AI
Ransomware Classifier Model
Classifies ransomware indicators and risk probability.
"""

from __future__ import annotations
from typing import Any
import numpy as np
from core.logger import logger


class RansomwareModel:
    """Ransomware classification model."""

    @property
    def name(self) -> str:
        return "ransomware_model"

    def predict(self, features: dict[str, Any] | list[float]) -> dict[str, Any]:
        """
        Predict ransomware probability.
        """
        # Heuristic scoring based on file/payload attributes
        score = 0.0
        indicators = []

        if isinstance(features, dict):
            if features.get("entropy", 0.0) > 7.2:
                score += 0.35
                indicators.append("High file entropy / encryption payload")
            if features.get("vba_macros_suspicious"):
                score += 0.30
                indicators.append("Suspicious macro execution routines")
            if "VirtualProtect" in str(features) or "WriteProcessMemory" in str(features):
                score += 0.25
                indicators.append("Process injection / memory modification API")

        probability = min(score, 1.0)
        return {
            "family": "Ransomware",
            "probability": round(probability, 3),
            "is_threat": probability >= 0.5,
            "indicators": indicators
        }

    def health_check(self) -> dict[str, Any]:
        return {"model": "Ransomware Classifier", "status": "Healthy"}


ransomware_model = RansomwareModel()
