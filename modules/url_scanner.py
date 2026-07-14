"""
CyberMind AI

URL Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from core.logger import logger

from services.url_service import (
    url_service
)


class URLScanner:
    """
    Enterprise URL Scanner.

    Responsibilities

    • URL Validation

    • URL Analysis

    • ML Prediction

    • Risk Engine

    • Recommendation

    • Explain AI

    • Final Response
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "URL Scanner initialized."

        )

    def validate(
        self,
        url: str
    ) -> bool:
        """
        Validate URL.
        """

        return url_service.validate(

            url

        )

    def normalize(
        self,
        url: str
    ) -> str:
        """
        Normalize URL.
        """

        return url_service.normalize(

            url

        )

    def _empty_response(
        self,
        url: str,
        message: str
    ) -> dict[str, Any]:
        """
        Standard error response.
        """

        return {

            "success": False,

            "scanner": "url",

            "url": url,

            "message": message

        }

    def _success_response(
        self
    ) -> dict[str, Any]:
        """
        Standard response.
        """

        return {

            "success": True,

            "scanner": "url",

            "url": "",

            "analysis": {},

            "ml_prediction": {},

            "risk": {},

            "recommendation": {},

            "explain_ai": {}

        }
        
        
        
    def analyze(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Analyze URL.
        """

        url = self.normalize(

            url

        )

        if not self.validate(

            url

        ):

            logger.warning(

                "Invalid URL : %s",

                url

            )

            return self._empty_response(

                url,

                "Invalid URL."

            )

        logger.info(

            "Starting URL scan : %s",

            url

        )

        report = self._success_response()

        report["url"] = url

        try:

            report["analysis"] = (

                url_service.analyze(

                    url

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return self._empty_response(

                url,

                str(error)

            )

        report["ml_prediction"] = self.ml_prediction(

            report

        )

        report["risk"] = self.risk(

            report

        )

        report["recommendation"] = (

            self.recommendation(

                report

            )

        )

        report["explain_ai"] = (

            self.explain_ai(

                report

            )

        )

        # Add result to analytics engine
        from modules.analytics_engine import analytics_engine
        analytics_engine.add(report)

        logger.info(

            "URL scan completed."

        )

        return report

    def ml_prediction(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Perform ML prediction for URL using trained RandomForest models.

        Primary signal  : phishing_url_model (binary: Phishing vs Legitimate)
                          uses 50 PhiUSIIL structured features.
        Secondary signal: online_valid_model (multi-class: brand impersonation)
                          uses 18 lexical features derived from the raw URL.

        Falls back to the original heuristic logic if the models are not
        available or any inference error occurs.
        """
        analysis = report.get("analysis", {})
        url = report.get("url", "")

        # ── Attempt ML inference ──────────────────────────────────────────
        try:
            from ml.inference import predict_phishing_url, predict_brand_impersonation

            # Build the PhiUSIIL feature dict from whatever the URL service
            # was able to extract.  Any missing key defaults to 0 inside
            # build_phishing_url_feature_row(), which is conservative but safe.
            features = analysis.get("features", {}) or {}
            lexical = analysis.get("lexical", {}) or {}

            phishing_features = {
                # Direct lexical features
                "URLLength":                 lexical.get("length", len(str(url))),
                "IsHTTPS":                   int("https" in str(url).lower()),
                "NoOfSubDomain":             lexical.get("subdomains", str(url).count(".") - 1),
                "NoOfDegitsInURL":           lexical.get("digits", sum(c.isdigit() for c in str(url))),
                "NoOfEqualsInURL":           str(url).count("="),
                "NoOfAmpersandInURL":        str(url).count("&"),
                "NoOfOtherSpecialCharsInURL": lexical.get("special_characters", 0),
                "IsDomainIP":                int(lexical.get("ip_based", False)),
                # From URL service features dict
                **{k: v for k, v in features.items() if isinstance(v, (int, float, bool))},
            }

            phishing_result = predict_phishing_url(phishing_features)
            brand_result = predict_brand_impersonation(url)

            if phishing_result.get("available"):
                label = phishing_result["label"]
                confidence = phishing_result["confidence"]
                # Map confidence to a 0-100 probability for the UI
                prob = round(confidence * 100, 1) if label == "Phishing" else round((1 - confidence) * 100, 1)

                result = {
                    "prediction":    label,
                    "probability":   prob,
                    "confidence":    round(confidence, 4),
                    "model":         "phishing_url_model (RandomForest)",
                    "ml_available":  True,
                }

                if brand_result.get("available"):
                    result["brand_impersonation"] = brand_result["brand"]
                    result["brand_confidence"]    = round(brand_result["confidence"], 4)
                    result["brand_probabilities"] = brand_result.get("probabilities", {})

                return result

        except Exception as exc:
            logger.warning("ML inference failed for URL scanner, using heuristic: %s", exc)

        # ── Original heuristic fallback ───────────────────────────────────
        features = analysis.get("features", {})
        prob = 0.05
        if features:
            url_len = features.get("url_length", 0)
            special_chars = features.get("special_character_count", 0)
            subdomain_count = features.get("subdomain_count", 0)
            if url_len > 80:
                prob += 0.2
            if special_chars > 10:
                prob += 0.25
            if subdomain_count > 3:
                prob += 0.15

        rep_score = analysis.get("reputation", {}).get("score", 100)
        if rep_score < 50:
            prob += 0.4

        is_malicious = analysis.get("google_safe_browsing", {}).get("malicious", False)
        if is_malicious:
            prob = 0.98

        prob = min(max(prob, 0.0), 1.0)
        prediction = "Phishing" if prob > 0.5 else "Safe"
        return {
            "prediction":   prediction,
            "probability":  prob,
            "ml_available": False,
        }

    def risk(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculate risk.
        """
        from modules.risk_engine import risk_engine
        return risk_engine.calculate(report.get("analysis", {}))

    def recommendation(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate recommendations.
        """
        from modules.recommendation import recommendation_engine
        return recommendation_engine.generate(report.get("analysis", {}))

    def explain_ai(
        self,
        report: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate explanation.
        """
        from modules.explain_ai import explain_ai
        analysis = report.get("analysis", {}).copy()
        analysis["risk"] = report.get("risk", {})
        return explain_ai.explain(analysis)

    def analyze_batch(
        self,
        urls: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple URLs.
        """

        return [

            self.analyze(

                url

            )

            for url

            in urls

        ]
        
        
        
    def statistics(
        self
    ) -> dict[str, Any]:
        """
        Scanner statistics.
        """

        return {

            "scanner":

                "URL Scanner",

            "service":

                "URL Service",

            "version":

                "2.0"

        }

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "URL Validation",

            "URL Analysis",

            "Metadata",

            "Feature Extraction",

            "DNS",

            "WHOIS",

            "SSL",

            "Security Headers",

            "Blacklist",

            "Google Safe Browsing",

            "VirusTotal",

            "Reputation",

            "Batch Analysis"

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Scanner health.
        """

        try:

            service = (

                url_service.health_check()

                if hasattr(

                    url_service,

                    "health_check"

                )

                else {

                    "status":

                        "Unknown"

                }

            )

            return {

                "scanner":

                    "URL Scanner",

                "status":

                    "Healthy",

                "service":

                    service

            }

        except Exception as error:

            logger.exception(

                error

            )

            return {

                "scanner":

                    "URL Scanner",

                "status":

                    "Failed",

                "message":

                    str(error)

            }

    def __repr__(
        self
    ) -> str:

        return (

            "URLScanner("

            "Enterprise Version)"

        )


url_scanner = URLScanner()