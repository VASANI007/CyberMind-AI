"""
CyberMind AI
Base ML Model
Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from core.logger import logger
from ml.evaluator import evaluator
from ml.model_loader import model_loader


class BaseMLModel:
    """
    Base class for all ML models.
    """

    def __init__(
        self,
        model_name: str,
        model: Any | None = None
    ) -> None:

        self.model_name = model_name
        self.model = model

        logger.info(
            "%s initialized.",
            self.model_name
        )

    @property
    def is_loaded(self) -> bool:
        """
        Check whether model is loaded.
        """

        return self.model is not None

    def load(
        self,
        model_path: str
    ) -> Any:
        """
        Load trained model.
        """

        self.model = model_loader.load(model_path)

        return self.model

    def save(
        self,
        model_path: str
    ) -> str:
        """
        Save model.
        """

        if self.model is None:
            raise ValueError("Model not loaded.")

        path = Path(model_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            self.model,
            path
        )

        logger.info(
            "%s saved.",
            self.model_name
        )

        return str(path)

    def predict(
        self,
        dataframe: pd.DataFrame
    ):
        """
        Predict.
        """

        if self.model is None:
            raise ValueError("Model not loaded.")

        return self.model.predict(dataframe)

    def predict_proba(
        self,
        dataframe: pd.DataFrame
    ):
        """
        Predict probability.
        """

        if self.model is None:
            raise ValueError("Model not loaded.")

        if hasattr(
            self.model,
            "predict_proba"
        ):
            return self.model.predict_proba(
                dataframe
            )

        return None

    def evaluate(
        self,
        x_test: pd.DataFrame,
        y_test
    ) -> dict[str, Any]:
        """
        Evaluate model.
        """

        return evaluator.evaluate_classification(
            self.model,
            x_test,
            y_test
        )

    def unload(self) -> None:
        """
        Unload model.
        """

        self.model = None

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "model": self.model_name,
            "loaded": self.is_loaded,
            "status": "Healthy"
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(model='{self.model_name}')"
        )