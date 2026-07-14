"""
CyberMind AI
Ensemble Engine
Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from core.logger import logger
from ml.prediction_engine import prediction_engine


class EnsembleEngine:
    """
    Enterprise Ensemble Engine.

    Supports

    • Voting
    • Average Probability
    • Multi Model Prediction
    """

    def __init__(self) -> None:
        logger.info("Ensemble Engine initialized.")

    def predict(
        self,
        model_paths: list[str],
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Predict using multiple models.
        """

        if not model_paths:
            raise ValueError("No models provided.")

        predictions = []
        probabilities = []

        for model in model_paths:

            result = prediction_engine.predict(
                model,
                dataframe
            )

            predictions.append(result["prediction"])

            if result["probability"] is not None:
                probabilities.append(result["probability"])

        return {
            "predictions": predictions,
            "probabilities": probabilities,
            "models": len(model_paths)
        }

    def majority_vote(
        self,
        predictions: list[list[Any]]
    ) -> list[Any]:
        """
        Majority voting.
        """

        prediction_array = np.asarray(predictions)

        votes = []

        for column in prediction_array.T:

            values, counts = np.unique(
                column,
                return_counts=True
            )

            votes.append(
                values[np.argmax(counts)]
            )

        return votes

    def average_probability(
        self,
        probabilities: list[Any]
    ) -> list[Any]:
        """
        Average probabilities.
        """

        if not probabilities:
            return []

        probability_array = np.asarray(probabilities)

        return np.mean(
            probability_array,
            axis=0
        ).tolist()
        
        
    def predict_ensemble(
        self,
        model_paths: list[str],
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Ensemble prediction.
        """

        result = self.predict(
            model_paths,
            dataframe
        )

        final_prediction = self.majority_vote(
            result["predictions"]
        )

        average_probability = self.average_probability(
            result["probabilities"]
        )

        confidence = 0.0

        if average_probability:
            confidence = round(
                float(np.max(average_probability)) * 100,
                2
            )

        return {
            "prediction": final_prediction,
            "probability": average_probability,
            "confidence": confidence,
            "models": result["models"]
        }

    def supported_methods(self) -> list[str]:
        """
        Supported ensemble methods.
        """

        return [
            "Majority Voting",
            "Average Probability"
        ]

    def reset(self) -> None:
        """
        Reset ensemble engine.
        """

        logger.info("Ensemble Engine reset.")

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "service": "Ensemble Engine",
            "status": "Healthy",
            "methods": self.supported_methods(),
            "version": "2.0"
        }

    def __repr__(self) -> str:
        return "EnsembleEngine(Enterprise Version)"


ensemble_engine = EnsembleEngine()