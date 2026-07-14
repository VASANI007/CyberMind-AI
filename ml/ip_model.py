"""
CyberMind AI
IP Model
Enterprise Production Version
"""

from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier

from core.logger import logger
from ml.base_model import BaseMLModel


class IPModel(BaseMLModel):
    """
    IP Reputation & Threat Detection Model.
    """

    def __init__(self) -> None:
        super().__init__(
            model_name="IP Model",
            model=RandomForestClassifier(
                n_estimators=250,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
        )

    def train(self, x_train, y_train) -> None:
        """
        Train IP model.
        """

        self.model.fit(x_train, y_train)

        logger.info(
            "IP Model trained successfully."
        )

    def feature_names(self) -> list[str]:
        """
        Supported IP features.
        """

        return [
            "ip_version",
            "country_code",
            "region_code",
            "city_code",
            "asn",
            "isp",
            "organization",
            "proxy_detected",
            "vpn_detected",
            "tor_detected",
            "hosting_provider",
            "abuse_score",
            "blacklist_score",
            "reputation_score",
            "latitude",
            "longitude"
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
            "features": len(self.feature_names())
        })

        return health

    def __repr__(self) -> str:
        return "IPModel(Enterprise Version)"


ip_model = IPModel()