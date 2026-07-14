"""
CyberMind AI
ML Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from pathlib import Path
from typing import Any

from config.paths import ML_DIR
from core.logger import logger

from ml.model_loader import model_loader
from ml.preprocessing import preprocessing
from ml.feature_engineering import feature_engineering
from ml.trainer import trainer
from ml.metrics import metrics
from ml.evaluator import evaluator
from ml.prediction_engine import prediction_engine
from ml.explainability import explainability
from ml.ensemble_engine import ensemble_engine

from ml.url_model import url_model
from ml.website_model import website_model
from ml.domain_model import domain_model
from ml.email_model import email_model
from ml.ip_model import ip_model
from ml.file_model import file_model
from ml.qr_model import qr_model
from ml.phishing_model import phishing_model


class MLRoot:
    """
    Enterprise Machine Learning Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.base_path = Path(ML_DIR)

        self.engines = {

            "Model Loader": model_loader,

            "Preprocessing": preprocessing,

            "Feature Engineering": feature_engineering,

            "Trainer": trainer,

            "Metrics": metrics,

            "Evaluator": evaluator,

            "Prediction Engine": prediction_engine,

            "Explainability": explainability,

            "Ensemble Engine": ensemble_engine

        }

        self.models = {

            "URL": url_model,

            "Website": website_model,

            "Domain": domain_model,

            "Email": email_model,

            "IP": ip_model,

            "File": file_model,

            "QR": qr_model,

            "Phishing": phishing_model

        }

        logger.info(
            "ML Root Initialized."
        )

    def initialize(self) -> None:
        """
        Initialize ML layer.
        """

        logger.info(
            "Initializing Machine Learning..."
        )

        self.verify_ml_directory()

        self.verify_models_directory()

        self.initialize_engines()

        self.initialize_models()

        logger.info(
            "Machine Learning Ready."
        )

    def health_check(self) -> dict[str, Any]:
        """
        Machine Learning health check.
        """
        healthy = all(
            engine is not None for engine in self.engines.values()
        ) and all(
            model is not None for model in self.models.values()
        )

        return {
            "service": "Machine Learning",
            "status": "Healthy" if healthy else "Unhealthy",
            "engines": len(self.engines),
            "models": len(self.models)
        }

    def verify_ml_directory(self) -> bool:
        """
        Verify ML directory.
        """

        if self.base_path.exists():

            logger.info(
                "ML Directory Found."
            )

            return True

        logger.error(
            "ML Directory Missing."
        )

        return False

    def verify_models_directory(self) -> bool:
        """
        Verify trained models directory.
        """

        models = self.base_path / "models"

        if models.exists():

            logger.info(
                "Models Directory Found."
            )

            return True

        logger.warning(
            "Models Directory Missing."
        )

        models.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Models Directory Created."
        )

        return True

    def initialize_engines(self) -> None:
        """
        Initialize ML engines.
        """

        logger.info(
            "Loading ML Engines..."
        )

        for name in self.engines:

            logger.info(
                "%s Loaded.",
                name
            )

    def initialize_models(self) -> None:
        """
        Initialize ML models.
        """

        logger.info(
            "Loading ML Models..."
        )

        for name in self.models:

            logger.info(
                "%s Model Ready.",
                name
            )
            
            
    def load_default_models(self) -> None:
        """
        Load all trained models.
        """

        logger.info(
            "Loading trained models..."
        )

        for model in self.discover_models():

            try:

                model_loader.load(
                    str(model)
                )

                logger.info(
                    "%s Loaded.",
                    model.name
                )

            except Exception as error:

                logger.exception(error)

    def clear_cache(self) -> None:
        """
        Clear model cache.
        """

        model_loader.clear_cache()

        logger.info(
            "Model cache cleared."
        )

    def reload(self) -> None:
        """
        Reload Machine Learning layer.
        """

        logger.info(
            "Reloading Machine Learning..."
        )

        self.clear_cache()

        self.initialize()

        self.load_default_models()

    def shutdown(self) -> None:
        """
        Shutdown Machine Learning.
        """

        logger.info(
            "Shutting down Machine Learning..."
        )

        self.clear_cache()

        logger.info(
            "Machine Learning shutdown completed."
        )

    def list_engines(self) -> list[str]:
        """
        List all ML engines.
        """

        return sorted(
            self.engines.keys()
        )

    def list_models(self) -> list[str]:
        """
        List all registered models.
        """

        return sorted(
            self.models.keys()
        )

    def list_trained_models(self) -> list[str]:
        """
        List trained model files.
        """

        return [

            model.name

            for model

            in self.discover_models()

        ]

    def __len__(self) -> int:
        """
        Total registered models.
        """

        return self.registered_models()

    def discover_models(self) -> list[Path]:
        """
        Discover trained model files.
        """
        models_dir = self.base_path / "models"
        if not models_dir.exists():
            return []
        return list(models_dir.glob("*.joblib")) + list(models_dir.glob("*.pkl"))

    def registered_models(self) -> int:
        """
        Number of registered models.
        """
        return len(self.models)

    def engine_count(self) -> int:
        """
        Number of ML engines.
        """
        return len(self.engines)

    def model_count(self) -> int:
        """
        Number of trained model files.
        """
        return len(self.discover_models())

    def __repr__(self) -> str:
        """
        String representation.
        """

        return (

            f"MLRoot("
            f"engines={self.engine_count()}, "
            f"models={self.registered_models()}, "
            f"trained={self.model_count()}, "
            f"version='{self.VERSION}')"

        )


ml_root = MLRoot()