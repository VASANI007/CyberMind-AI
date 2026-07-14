"""
CyberMind AI
URL Model
Enterprise Production Version
"""

from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier

from core.logger import logger
from ml.base_model import BaseMLModel


class URLModel(BaseMLModel):
    """
    URL Phishing Detection Model.
    """

    def __init__(self) -> None:
        super().__init__(
            model_name="URL Model",
            model=RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
        )

    def train(
        self,
        x_train,
        y_train
    ) -> None:
        """
        Train URL model.
        """

        self.model.fit(
            x_train,
            y_train
        )

        logger.info(
            "URL Model trained successfully."
        )

    def feature_names(self) -> list[str]:
        """
        Supported URL features.
        """

        return [
            "url_length",
            "hostname_length",
            "digit_count",
            "letter_count",
            "special_character_count",
            "subdomain_count"
        ]

    def model_type(self) -> str:
        """
        Model type.
        """

        return "Random Forest"

    def health_check(self) -> dict:
        """
        Health status.
        """

        health = super().health_check()

        health.update({
            "type": self.model_type(),
            "features": len(
                self.feature_names()
            )
        })

        return health

    def __repr__(self) -> str:
        return "URLModel(Enterprise Version)"


url_model = URLModel()