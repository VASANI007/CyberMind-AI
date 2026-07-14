"""
CyberMind AI

Model Loader

Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path

from typing import Any

import pickle

import joblib

from core.logger import logger


class ModelLoader:
    """
    Enterprise Model Loader.

    Responsibilities

    • Load Models

    • Cache Models

    • Reload Models

    • Unload Models

    • Model Information
    """

    def __init__(
        self
    ) -> None:

        self._cache: dict[

            str,

            Any

        ] = {}

        logger.info(

            "Model Loader initialized."

        )

    def _load_pickle(
        self,
        path: Path
    ) -> Any:
        """
        Load Pickle model.

        Note: Uses joblib.load rather than pickle.load because models saved with
        joblib.dump (which stores large numpy arrays as separate .npy files in a
        zip container) are not compatible with the standard pickle module.
        joblib.load handles both joblib-format and plain-pickle .pkl files.
        """

        return joblib.load(

            path

        )

    def _load_joblib(
        self,
        path: Path
    ) -> Any:
        """
        Load Joblib model.
        """

        return joblib.load(

            path

        )

    def load(
        self,
        model_path: str | None = None
    ) -> Any:
        """
        Load model.

        Supports

        • .joblib

        • .pkl
        """

        if model_path is None:
            logger.info("Model Loader: no model path provided, skipping.")
            return True

        path = Path(

            model_path

        )


        if not path.exists():

            raise FileNotFoundError(

                model_path

            )

        cache_key = str(

            path.resolve()

        )

        if cache_key in self._cache:

            logger.info(

                "Model loaded from cache : %s",

                cache_key

            )

            return self._cache[

                cache_key

            ]

        logger.info(

            "Loading model : %s",

            cache_key

        )

        suffix = path.suffix.lower()

        if suffix == ".joblib":

            model = self._load_joblib(

                path

            )

        elif suffix == ".pkl":

            model = self._load_pickle(

                path

            )

        else:

            raise ValueError(

                f"Unsupported model format: {suffix}"

            )

        self._cache[

            cache_key

        ] = model

        return model

    def exists(
        self,
        model_path: str
    ) -> bool:
        """
        Check model exists.
        """

        return Path(

            model_path

        ).is_file()

    def cached_models(
        self
    ) -> list[str]:
        """
        Cached model list.
        """

        return list(

            self._cache.keys()

        )

    def cache_size(
        self
    ) -> int:
        """
        Total cached models.
        """

        return len(

            self._cache

        )
        
        
    def unload(
        self,
        model_path: str
    ) -> bool:
        """
        Unload model from cache.
        """

        cache_key = str(

            Path(

                model_path

            ).resolve()

        )

        if cache_key not in self._cache:

            return False

        del self._cache[

            cache_key

        ]

        logger.info(

            "Model unloaded : %s",

            cache_key

        )

        return True

    def reload(
        self,
        model_path: str
    ) -> Any:
        """
        Reload model.
        """

        self.unload(

            model_path

        )

        return self.load(

            model_path

        )

    def clear_cache(
        self
    ) -> None:
        """
        Clear model cache.
        """

        self._cache.clear()

        logger.info(

            "Model cache cleared."

        )

    def model_info(
        self,
        model_path: str
    ) -> dict[str, Any]:
        """
        Model information.
        """

        path = Path(

            model_path

        )

        if not path.exists():

            raise FileNotFoundError(

                model_path

            )

        return {

            "name":

                path.name,

            "path":

                str(

                    path.resolve()

                ),

            "extension":

                path.suffix.lower(),

            "size_bytes":

                path.stat().st_size,

            "cached":

                str(

                    path.resolve()

                )

                in

                self._cache

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Model Loader",

            "status":

                "Healthy",

            "cached_models":

                len(

                    self._cache

                ),

            "supported_formats":

                [

                    ".joblib",

                    ".pkl"

                ]

        }

    def __repr__(
        self
    ) -> str:

        return (

            "ModelLoader("

            "Enterprise Version)"

        )


model_loader = ModelLoader()