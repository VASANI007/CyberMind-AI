"""
CyberMind AI
Evaluator
Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from core.logger import logger
from ml.metrics import metrics


class Evaluator:
    """
    Enterprise Model Evaluator.
    """

    def __init__(self) -> None:
        logger.info("Evaluator initialized.")

    def evaluate_classification(
        self,
        model: Any,
        x_test: pd.DataFrame,
        y_test
    ) -> dict[str, Any]:
        """
        Evaluate classification model.
        """

        predictions = model.predict(x_test)

        probability = None

        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(x_test)

        return metrics.classification_metrics(
            y_true=y_test,
            y_pred=predictions,
            y_score=probability
        )

    def evaluate_regression(
        self,
        model: Any,
        x_test: pd.DataFrame,
        y_test
    ) -> dict[str, Any]:
        """
        Evaluate regression model.
        """

        predictions = model.predict(x_test)

        return metrics.regression_metrics(
            y_true=y_test,
            y_pred=predictions
        )

    def feature_importance(
        self,
        model: Any,
        feature_names: list[str]
    ) -> dict[str, float]:
        """
        Feature importance.
        """

        if not hasattr(model, "feature_importances_"):
            return {}

        importance = model.feature_importances_

        return {
            feature: round(float(score), 6)
            for feature, score in zip(
                feature_names,
                importance
            )
        }

    def summary(
        self,
        results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluation summary.
        """

        return {
            "accuracy": results.get("accuracy"),
            "precision": results.get("precision"),
            "recall": results.get("recall"),
            "f1_score": results.get("f1_score"),
            "roc_auc": results.get("roc_auc")
        }

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "service": "Evaluator",
            "status": "Healthy",
            "version": "2.0"
        }

    def __repr__(self) -> str:
        return "Evaluator(Enterprise Version)"


evaluator = Evaluator()