"""
CyberMind AI

File Scanner

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

from pathlib import Path

from core.logger import logger

from services.file_service import (
    file_service
)

from modules.risk_engine import (
    risk_engine
)

from modules.recommendation import (
    recommendation_engine
)

from modules.explain_ai import (
    explain_ai
)

from modules.analytics_engine import (
    analytics_engine
)


class FileScanner:
    """
    Enterprise File Scanner.

    Responsibilities

    • File Validation

    • File Analysis

    • Risk Analysis

    • Recommendation

    • Explain AI

    • Analytics
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "File Scanner initialized."

        )

    def validate(
        self,
        file_path: str
    ) -> bool:
        """
        Validate file.
        """

        return Path(

            file_path

        ).is_file()

    def analyze(
        self,
        file_path: str
    ) -> dict[str, Any]:
        """
        Analyze file.

        In addition to the existing service-based analysis (hashes, entropy,
        VirusTotal, reputation), this method now also runs the trained
        file_signatures_model to predict risk level (Low / Medium / High)
        based on the file's hex signature, extension, description and category.
        The ML result is stored under the 'ml_prediction' key.
        """

        if not self.validate(

            file_path

        ):

            return {

                "success": False,

                "scanner": "file",

                "message": "File not found."

            }

        logger.info(

            "File scan started : %s",

            file_path

        )

        analysis = file_service.analyze(

            file_path

        )

        risk = risk_engine.calculate(

            analysis

        )

        analysis["risk"] = risk

        # ── ML Risk Prediction (file_signatures_model) ────────────────────
        try:
            from ml.inference import predict_file_risk
            from pathlib import Path as _Path
            import mimetypes

            _p = _Path(file_path)
            ext = _p.suffix.lower()

            # Read first 32 bytes → convert to hex string (e.g. "FF D8 FF ...")
            hex_sig = ""
            try:
                with open(file_path, "rb") as _f:
                    raw = _f.read(32)
                hex_sig = " ".join(f"{b:02X}" for b in raw)
            except Exception:
                pass

            mime, _ = mimetypes.guess_type(file_path)
            mime = mime or "application/octet-stream"

            # Derive category from MIME type (mirrors dataset categories)
            mime_to_cat = {
                "image":       "Image",
                "audio":       "Audio",
                "video":       "Video",
                "text":        "Document",
                "application/pdf": "Document",
                "application/msword": "Document",
                "application/zip": "Archive",
                "application/x-rar": "Archive",
                "application/x-tar": "Archive",
                "application/x-executable": "Executable",
                "application/x-dosexec": "Executable",
            }
            category = "Unknown"
            for key, cat in mime_to_cat.items():
                if key in mime:
                    category = cat
                    break

            # Use extension as description fallback
            description = ext.lstrip(".").upper() + " file" if ext else "Unknown"

            ml_result = predict_file_risk(
                hex_sig=hex_sig,
                extension=ext,
                description=description,
                category=category,
                offset=0.0,
            )
            analysis["ml_prediction"] = ml_result
            logger.info(
                "File ML risk prediction: %s (confidence=%.2f)",
                ml_result.get("risk_level", "N/A"),
                ml_result.get("confidence", 0.0),
            )

        except Exception as exc:
            logger.warning("File ML inference skipped: %s", exc)
            analysis["ml_prediction"] = {"available": False}
        # ─────────────────────────────────────────────────────────────────

        recommendation = (

            recommendation_engine.generate(

                analysis

            )

        )

        explanation = (

            explain_ai.explain(

                analysis

            )

        )

        result = {

            "success": True,

            "scanner": "file",

            "file": file_path,

            "analysis": analysis,

            "risk": risk,

            "recommendation": recommendation,

            "explain_ai": explanation

        }

        analytics_engine.add(

            result

        )

        logger.info(

            "File scan completed."

        )

        return result

    def analyze_batch(
        self,
        files: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple files.
        """

        return [

            self.analyze(

                file

            )

            for file

            in files

        ]

    def supported_features(
        self
    ) -> list[str]:
        """
        Supported features.
        """

        return [

            "File Validation",

            "File Analysis",

            "Risk Analysis",

            "Recommendation",

            "Explain AI",

            "Analytics",

            "Batch Analysis"

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "File Scanner",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "FileScanner("

            "Enterprise Version)"

        )


file_scanner = FileScanner()