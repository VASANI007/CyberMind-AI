"""
CyberMind AI
Explainability Engine
Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from core.logger import logger
from ml.prediction_engine import prediction_engine


class Explainability:
    """
    Enterprise Explainability Engine.

    Responsibilities

    • Prediction Explanation

    • Feature Importance

    • Confidence Analysis

    • Human Readable Output
    """

    def __init__(self) -> None:
        logger.info("Explainability Engine initialized.")

    def explain(
        self,
        model_path: str,
        dataframe: pd.DataFrame,
        feature_names: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Explain prediction.
        """

        result = prediction_engine.predict_with_confidence(
            model_path,
            dataframe
        )

        explanation = {
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "model": result["model"],
            "rows": result["rows"],
            "summary": self.summary(result)
        }

        if feature_names:
            explanation["features"] = feature_names

        return explanation

    def summary(
        self,
        prediction: dict[str, Any]
    ) -> str:
        """
        Human readable explanation.
        """

        confidence = prediction.get(
            "confidence",
            0
        )

        if confidence >= 90:
            return "Very High Confidence"

        if confidence >= 75:
            return "High Confidence"

        if confidence >= 50:
            return "Medium Confidence"

        return "Low Confidence"

    def feature_importance(
        self,
        model: Any,
        feature_names: list[str]
    ) -> dict[str, float]:
        """
        Feature importance.
        """

        if not hasattr(
            model,
            "feature_importances_"
        ):
            return {}

        importance = model.feature_importances_

        return dict(
            zip(
                feature_names,
                importance.tolist()
            )
        )

    def top_features(
        self,
        importance: dict[str, float],
        top_n: int = 10
    ) -> dict[str, float]:
        """
        Top important features.
        """

        return dict(
            sorted(
                importance.items(),
                key=lambda item: item[1],
                reverse=True
            )[:top_n]
        )
        
    def prediction_report(
        self,
        model_path: str,
        dataframe: pd.DataFrame,
        feature_names: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Generate prediction report.
        """

        report = self.explain(
            model_path,
            dataframe,
            feature_names
        )

        report["status"] = (
            "Success"
            if report["confidence"] >= 50
            else "Low Confidence"
        )

        return report

    def supported_methods(self) -> list[str]:
        """
        Supported explainability methods.
        """

        return [
            "Feature Importance",
            "Confidence Score",
            "Human Readable Summary",
            "Prediction Report"
        ]

    def reset(self) -> None:
        """
        Reset explainability engine.
        """

        logger.info("Explainability Engine reset.")

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "service": "Explainability Engine",
            "status": "Healthy",
            "supported_methods": self.supported_methods(),
            "version": "2.0"
        }

    def __repr__(self) -> str:
        return "Explainability(Enterprise Version)"


explainability = Explainability()