"""
CyberMind AI
Metrics
Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from core.logger import logger


class Metrics:
    """
    Enterprise Metrics Engine.
    """

    def __init__(self) -> None:
        logger.info("Metrics initialized.")

    def accuracy(self, y_true, y_pred) -> float:
        return round(
            accuracy_score(y_true, y_pred),
            4
        )

    def precision(self, y_true, y_pred, average="weighted") -> float:
        return round(
            precision_score(
                y_true,
                y_pred,
                average=average,
                zero_division=0
            ),
            4
        )

    def recall(self, y_true, y_pred, average="weighted") -> float:
        return round(
            recall_score(
                y_true,
                y_pred,
                average=average,
                zero_division=0
            ),
            4
        )

    def f1(self, y_true, y_pred, average="weighted") -> float:
        return round(
            f1_score(
                y_true,
                y_pred,
                average=average,
                zero_division=0
            ),
            4
        )

    def roc_auc(self, y_true, y_score) -> float | None:
        try:
            return round(
                roc_auc_score(
                    y_true,
                    y_score,
                    multi_class="ovr"
                ),
                4
            )
        except Exception:
            return None

    def confusion(self, y_true, y_pred) -> list[list[int]]:
        return confusion_matrix(
            y_true,
            y_pred
        ).tolist()

    def classification(
        self,
        y_true,
        y_pred
    ) -> dict[str, Any]:
        return classification_report(
            y_true,
            y_pred,
            output_dict=True,
            zero_division=0
        )

    def mae(self, y_true, y_pred) -> float:
        return round(
            mean_absolute_error(
                y_true,
                y_pred
            ),
            4
        )

    def mse(self, y_true, y_pred) -> float:
        return round(
            mean_squared_error(
                y_true,
                y_pred
            ),
            4
        )

    def rmse(self, y_true, y_pred) -> float:
        return round(
            mean_squared_error(
                y_true,
                y_pred
            ) ** 0.5,
            4
        )

    def r2(self, y_true, y_pred) -> float:
        return round(
            r2_score(
                y_true,
                y_pred
            ),
            4
        )

    def classification_metrics(
        self,
        y_true,
        y_pred,
        y_score=None
    ) -> dict[str, Any]:

        return {
            "accuracy": self.accuracy(y_true, y_pred),
            "precision": self.precision(y_true, y_pred),
            "recall": self.recall(y_true, y_pred),
            "f1_score": self.f1(y_true, y_pred),
            "roc_auc": (
                self.roc_auc(y_true, y_score)
                if y_score is not None
                else None
            ),
            "confusion_matrix": self.confusion(
                y_true,
                y_pred
            ),
            "classification_report": self.classification(
                y_true,
                y_pred
            )
        }

    def regression_metrics(
        self,
        y_true,
        y_pred
    ) -> dict[str, float]:

        return {
            "mae": self.mae(y_true, y_pred),
            "mse": self.mse(y_true, y_pred),
            "rmse": self.rmse(y_true, y_pred),
            "r2_score": self.r2(y_true, y_pred)
        }

    def health_check(self) -> dict[str, Any]:

        return {
            "service": "Metrics",
            "status": "Healthy",
            "version": "2.0"
        }

    def __repr__(self) -> str:
        return "Metrics(Enterprise Version)"


metrics = Metrics()