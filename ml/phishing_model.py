"""
CyberMind AI
Phishing Detection Model
Enterprise Production Version
"""

from __future__ import annotations

from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier
)

from core.logger import logger
from ml.base_model import BaseMLModel


class PhishingModel(BaseMLModel):
    """
    AI Phishing Detection Model.
    """

    def __init__(self) -> None:

        rf = RandomForestClassifier(
            n_estimators=300,
            max_depth=25,
            random_state=42,
            n_jobs=-1
        )

        gb = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            random_state=42
        )

        et = ExtraTreesClassifier(
            n_estimators=300,
            max_depth=25,
            random_state=42,
            n_jobs=-1
        )

        ensemble = VotingClassifier(
            estimators=[
                ("rf", rf),
                ("gb", gb),
                ("et", et)
            ],
            voting="soft"
        )

        super().__init__(
            model_name="Phishing Model",
            model=ensemble
        )

    def train(self, x_train, y_train) -> None:
        """
        Train phishing model.
        """

        self.model.fit(x_train, y_train)

        logger.info(
            "Phishing Model trained successfully."
        )

    def feature_names(self) -> list[str]:
        """
        Supported phishing features.
        """

        return [

            "url_length",

            "hostname_length",

            "domain_age",

            "subdomain_count",

            "special_character_count",

            "digit_count",

            "https",

            "ssl_valid",

            "redirect_count",

            "iframe_count",

            "popup_count",

            "external_links",

            "internal_links",

            "favicon_match",

            "form_action",

            "email_in_page",

            "javascript_events",

            "blacklist_score",

            "virustotal_score",

            "reputation_score",

            "risk_score"

        ]

    def model_type(self) -> str:
        """
        Model type.
        """

        return "Soft Voting Ensemble"

    def algorithms(self) -> list[str]:
        """
        Algorithms.
        """

        return [

            "Random Forest",

            "Gradient Boosting",

            "Extra Trees"

        ]

    def health_check(self) -> dict:

        health = super().health_check()

        health.update({

            "type": self.model_type(),

            "algorithms": self.algorithms(),

            "features": len(
                self.feature_names()
            )

        })

        return health

    def __repr__(self) -> str:
        return "PhishingModel(Enterprise Version)"


phishing_model = PhishingModel()