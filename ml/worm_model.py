"""
CyberMind AI
Worm Classifier Model
Classifies worm propagation indicators.
"""

from __future__ import annotations
from typing import Any
from core.logger import logger


class WormModel:
    """Worm classification model."""

    @property
    def name(self) -> str:
        return "worm_model"

    def predict(self, features: dict[str, Any] | list[float]) -> dict[str, Any]:
        score = 0.0
        indicators = []

        if isinstance(features, dict):
            if features.get("subdomains_count", 0) > 30:
                score += 0.50
                indicators.append("Mass subdomain propagation / scanning activity")
            if features.get("disposable_email"):
                score += 0.25
                indicators.append("Automated email propagation address")

        probability = min(score, 1.0)
        return {
            "family": "Worm",
            "probability": round(probability, 3),
            "is_threat": probability >= 0.5,
            "indicators": indicators
        }

    def health_check(self) -> dict[str, Any]:
        return {"model": "Worm Classifier", "status": "Healthy"}


worm_model = WormModel()
