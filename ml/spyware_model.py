"""
CyberMind AI
Spyware Classifier Model
Classifies spyware and info-stealer indicators.
"""

from __future__ import annotations
from typing import Any
from core.logger import logger


class SpywareModel:
    """Spyware classification model."""

    @property
    def name(self) -> str:
        return "spyware_model"

    def predict(self, features: dict[str, Any] | list[float]) -> dict[str, Any]:
        score = 0.0
        indicators = []

        if isinstance(features, dict):
            if "GetAsyncKeyState" in str(features) or "SetWindowsHookEx" in str(features):
                score += 0.40
                indicators.append("Keylogger / input capture hook API")
            if features.get("js_eval") or features.get("obfuscated"):
                score += 0.25
                indicators.append("Obfuscated credential harvester script")

        probability = min(score, 1.0)
        return {
            "family": "Spyware",
            "probability": round(probability, 3),
            "is_threat": probability >= 0.5,
            "indicators": indicators
        }

    def health_check(self) -> dict[str, Any]:
        return {"model": "Spyware Classifier", "status": "Healthy"}


spyware_model = SpywareModel()
