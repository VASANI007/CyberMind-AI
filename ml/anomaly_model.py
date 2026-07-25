"""
CyberMind AI
Anomaly Detection Model
Uses IsolationForest to detect statistical outliers / unusual pattern anomalies.
Offline — scikit-learn based.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from core.logger import logger


class AnomalyModel:
    """
    Unsupervised Anomaly Detection Model using IsolationForest.
    Identifies zero-day / outlier patterns in feature vectors.
    """

    def __init__(self, contamination: float = 0.05) -> None:
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        self.is_fitted = False
        logger.info("AnomalyModel (IsolationForest) initialized.")

    def fit(self, X: pd.DataFrame | np.ndarray) -> None:
        """Fit IsolationForest model on normal feature distribution."""
        try:
            self.model.fit(X)
            self.is_fitted = True
            logger.info("AnomalyModel successfully fitted on %d samples.", len(X))
        except Exception as exc:
            logger.error("Failed to fit AnomalyModel: %s", exc)

    def detect_anomaly(self, feature_vector: list[float] | np.ndarray | pd.DataFrame) -> dict[str, Any]:
        """
        Detect whether a given feature vector is anomalous.

        Returns
        -------
        dict with keys:
            is_anomaly    : bool
            anomaly_score : float (0.0 to 1.0, higher means more anomalous)
            raw_score     : float
        """
        if isinstance(feature_vector, list):
            X = np.array([feature_vector])
        elif isinstance(feature_vector, pd.DataFrame):
            X = feature_vector.values
        else:
            X = feature_vector
            if X.ndim == 1:
                X = np.array([X])

        if not self.is_fitted:
            # Simple heuristic score if un-fitted
            std_dev = np.std(X)
            is_anom = bool(std_dev > 2.5)
            return {
                "is_anomaly": is_anom,
                "anomaly_score": round(min(float(std_dev / 5.0), 1.0), 3),
                "raw_score": float(std_dev),
                "note": "Heuristic fallback (model un-fitted)"
            }

        try:
            pred = self.model.predict(X)[0]  # -1 for anomaly, 1 for normal
            score = self.model.score_samples(X)[0] # lower score means more anomalous
            
            # Normalize decision function score roughly to 0..1 scale
            normalized_score = round(max(0.0, min(1.0, float(0.5 - score))), 3)

            return {
                "is_anomaly": bool(pred == -1),
                "anomaly_score": normalized_score,
                "raw_score": float(score)
            }
        except Exception as exc:
            logger.warning("Anomaly detection error: %s", exc)
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "raw_score": 0.0,
                "error": str(exc)
            }

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Anomaly Detection Model",
            "status": "Healthy" if self.is_fitted else "Unfitted (Heuristic Mode)",
            "contamination": self.contamination
        }


anomaly_model = AnomalyModel()
