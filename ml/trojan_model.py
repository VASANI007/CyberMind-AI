"""
CyberMind AI
Trojan Classifier Model
Classifies Trojan horse indicators.
"""

from __future__ import annotations
from typing import Any
from core.logger import logger


class TrojanModel:
    """Trojan classification model."""

    @property
    def name(self) -> str:
        return "trojan_model"

    def predict(self, features: dict[str, Any] | list[float]) -> dict[str, Any]:
        score = 0.0
        indicators = []

        if isinstance(features, dict):
            if features.get("brand_impersonation"):
                score += 0.40
                indicators.append("Brand impersonation / fake software delivery")
            if features.get("redirect_hops", 0) > 2:
                score += 0.25
                indicators.append("Multi-hop dropper redirect chain")

        probability = min(score, 1.0)
        return {
            "family": "Trojan",
            "probability": round(probability, 3),
            "is_threat": probability >= 0.5,
            "indicators": indicators
        }

    def health_check(self) -> dict[str, Any]:
        return {"model": "Trojan Classifier", "status": "Healthy"}


trojan_model = TrojanModel()
