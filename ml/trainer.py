"""
CyberMind AI
Trainer
Enterprise Production Version
"""

from __future__ import annotations
import io
import os
import sys
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from core.logger import logger
from ml.preprocessing import preprocessing
from ml.feature_engineering import feature_engineering


class Trainer:
    """
    Enterprise Model Trainer.
    """

    def __init__(self) -> None:
        logger.info("Trainer initialized.")

    def prepare(
        self,
        dataframe: pd.DataFrame,
        target_column: str
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training dataset.
        """

        dataframe = feature_engineering.pipeline(dataframe)
        dataframe = preprocessing.pipeline(dataframe)

        x = dataframe.drop(columns=[target_column])
        y = dataframe[target_column]

        return x, y

    def split(
        self,
        x: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ):
        """
        Train/Test split.
        """

        return train_test_split(
            x,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y if len(y.unique()) > 1 else None
        )

    def train(
        self,
        x_train: pd.DataFrame,
        y_train: pd.Series,
        **kwargs
    ) -> RandomForestClassifier:
        """
        Train Random Forest model.
        """

        model = RandomForestClassifier(
            random_state=42,
            **kwargs
        )

        model.fit(
            x_train,
            y_train
        )

        return model

    def save(
        self,
        model: Any,
        path: str
    ) -> str:
        """
        Save trained model.
        """

        model_path = Path(path)

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            model,
            model_path
        )

        logger.info(
            "Model saved: %s",
            model_path
        )

        return str(model_path)
    
    
    def fit(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
        **kwargs
    ) -> tuple[Any, dict[str, Any]]:
        """
        Complete training pipeline.
        """

        x, y = self.prepare(
            dataframe,
            target_column
        )

        x_train, x_test, y_train, y_test = self.split(
            x,
            y
        )

        model = self.train(
            x_train,
            y_train,
            **kwargs
        )

        metrics = {
            "training_samples": len(x_train),
            "testing_samples": len(x_test),
            "features": list(x.columns),
            "feature_count": len(x.columns),
            "target": target_column
        }

        logger.info("Model training completed.")

        return model, metrics

    def train_and_save(
        self,
        dataframe: pd.DataFrame,
        target_column: str,
        model_path: str,
        **kwargs
    ) -> dict[str, Any]:
        """
        Train and save model.
        """

        model, metrics = self.fit(
            dataframe,
            target_column,
            **kwargs
        )

        saved_path = self.save(
            model,
            model_path
        )

        return {
            "success": True,
            "model_path": saved_path,
            "metrics": metrics
        }

    def reset(self) -> None:
        """
        Reset trainer.
        """

        logger.info("Trainer reset.")

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        return {
            "service": "Trainer",
            "status": "Healthy",
            "algorithm": "RandomForestClassifier",
            "version": "2.0"
        }

    def __repr__(self) -> str:
        return "Trainer(Enterprise Version)"


trainer = Trainer()