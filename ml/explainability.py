"""
CyberMind AI
Explainability Engine
Enterprise Production Version
Supports SHAP (TreeExplainer) and LIME as fallbacks for model interpretability.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

from core.logger import logger
from ml.prediction_engine import prediction_engine


class Explainability:
    """
    Enterprise Explainability Engine.

    Capabilities:
    - SHAP (TreeExplainer for tree models)
    - LIME (Local Interpretable Model-agnostic Explanations fallback)
    - Feature Importance fallback
    - Confidence & Human-readable summaries
    """

    def __init__(self) -> None:
        logger.info("Explainability Engine initialized.")

    def explain_shap(self, model: Any, features_df: pd.DataFrame) -> dict[str, float]:
        """
        Explain a single prediction using SHAP (TreeExplainer).
        Returns a dict mapping feature_name -> shap_value.
        """
        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features_df)
            
            # Binary classification or multi-class handling
            if isinstance(shap_values, list):
                # Take index 1 for positive/malicious class if available
                vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
            elif len(shap_values.shape) == 3:
                vals = shap_values[0, :, 1]
            else:
                vals = shap_values[0]

            feature_names = features_df.columns.tolist()
            return dict(zip(feature_names, [float(v) for v in vals]))
        except Exception as exc:
            logger.warning("SHAP explanation failed, falling back to LIME/feature importance: %s", exc)
            return self.explain_lime_or_fallback(model, features_df)

    def explain_lime_or_fallback(self, model: Any, features_df: pd.DataFrame) -> dict[str, float]:
        """
        LIME / Feature Importance fallback for model interpretation.
        """
        feature_names = features_df.columns.tolist()
        
        try:
            from lime import lime_tabular
            explainer = lime_tabular.LimeTabularExplainer(
                training_data=np.zeros((10, len(feature_names))),
                feature_names=feature_names,
                mode="classification"
            )
            exp = explainer.explain_instance(
                data_row=features_df.iloc[0].values,
                predict_fn=model.predict_proba
            )
            return {feature: float(weight) for feature, weight in exp.as_list()}
        except Exception as exc:
            logger.warning("LIME explanation failed, falling back to static feature importances: %s", exc)
            return self.feature_importance(model, feature_names)

    def explain(
        self,
        model_path: str,
        dataframe: pd.DataFrame,
        feature_names: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Explain prediction.
        """
        result = prediction_engine.predict_with_confidence(
            model_path,
            dataframe
        )

        explanation = {
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "model": result["model"],
            "rows": result["rows"],
            "summary": self.summary(result)
        }

        if feature_names:
            explanation["features"] = feature_names

        return explanation

    def summary(self, prediction: dict[str, Any]) -> str:
        """Human readable explanation."""
        confidence = prediction.get("confidence", 0)
        if confidence >= 90:
            return "Very High Confidence"
        if confidence >= 75:
            return "High Confidence"
        if confidence >= 50:
            return "Medium Confidence"
        return "Low Confidence"

    def feature_importance(self, model: Any, feature_names: list[str]) -> dict[str, float]:
        """Feature importance."""
        if not hasattr(model, "feature_importances_"):
            return {}
        importance = model.feature_importances_
        return dict(zip(feature_names, [float(x) for x in importance]))

    def top_features(self, importance: dict[str, float], top_n: int = 10) -> dict[str, float]:
        """Top important features."""
        return dict(sorted(importance.items(), key=lambda item: item[1], reverse=True)[:top_n])

    def prediction_report(
        self,
        model_path: str,
        dataframe: pd.DataFrame,
        feature_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate prediction report."""
        report = self.explain(model_path, dataframe, feature_names)
        report["status"] = "Success" if report["confidence"] >= 50 else "Low Confidence"
        return report

    def supported_methods(self) -> list[str]:
        return ["SHAP TreeExplainer", "LIME", "Feature Importance", "Confidence Score", "Prediction Report"]

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Explainability Engine",
            "status": "Healthy",
            "supported_methods": self.supported_methods(),
            "version": "3.0"
        }


explainability = Explainability()