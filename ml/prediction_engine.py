"""
CyberMind AI
Prediction Engine
Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from core.logger import logger
from ml.model_loader import model_loader
from ml.preprocessing import preprocessing
from ml.feature_engineering import feature_engineering


class PredictionEngine:
    """
    Enterprise Prediction Engine.
    """

    def __init__(self) -> None:
        logger.info("Prediction Engine initialized.")

    def _prepare(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare input features.
        """

        dataframe = feature_engineering.pipeline(dataframe)
        dataframe = preprocessing.pipeline(
            dataframe,
            scaling="standard"
        )

        return dataframe

    def predict(
        self,
        model_path: str,
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Predict using trained model.
        """

        model = model_loader.load(model_path)

        dataframe = self._prepare(dataframe)

        prediction = model.predict(dataframe)

        probability = None

        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(dataframe)

        return {
            "prediction": prediction.tolist(),
            "probability": (
                probability.tolist()
                if probability is not None
                else None
            ),
            "rows": len(dataframe),
            "model": Path(model_path).name
        }

    def predict_one(
        self,
        model_path: str,
        features: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Predict single sample.
        """

        dataframe = pd.DataFrame([features])

        return self.predict(
            model_path,
            dataframe
        )

    def predict_batch(
        self,
        model_path: str,
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Batch prediction.
        """

        return self.predict(
            model_path,
            dataframe
        )

    def supported_formats(self) -> list[str]:
        """
        Supported model formats.
        """

        return [
            ".joblib",
            ".pkl"
        ]
        
    def confidence_score(
        self,
        probability: np.ndarray | None
    ) -> float:
        """
        Calculate confidence score.
        """

        if probability is None:
            return 0.0

        probability = np.asarray(probability)

        if probability.ndim == 1:
            return round(float(np.max(probability)) * 100, 2)

        return round(float(np.max(probability[0])) * 100, 2)

    def validate_prediction(
        self,
        result: dict[str, Any]
    ) -> bool:
        """
        Validate prediction result.
        """

        required = {
            "prediction",
            "probability",
            "rows",
            "model"
        }

        return required.issubset(result.keys())

    def predict_with_confidence(
        self,
        model_path: str,
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Prediction with confidence score.
        """

        result = self.predict(model_path, dataframe)

        probability = result.get("probability")

        if probability is not None:
            probability = np.asarray(probability)

        result["confidence"] = self.confidence_score(probability)
        result["valid"] = self.validate_prediction(result)

        return result

    def reset(self) -> None:
        """
        Reset prediction engine.
        """

        model_loader.clear_cache()

        logger.info("Prediction Engine reset.")

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "service": "Prediction Engine",
            "status": "Healthy",
            "cached_models": model_loader.cache_size(),
            "supported_formats": self.supported_formats()
        }

    def __repr__(self) -> str:
        return "PredictionEngine(Enterprise Version)"


prediction_engine = PredictionEngine()