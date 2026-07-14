"""
CyberMind AI

QR Service

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any
from pathlib import Path
from PIL import Image

from core.logger import logger
from core.validator import contains_url

from services.shorturl_service import shorturl_service
from services.reputation_service import reputation_service
from services.url_service import url_service


class QRService:
    """
    Enterprise QR Analysis Service.
    """

    def __init__(self) -> None:
        logger.info("QR Service initialized.")

    def decode_qr(self, image_path: str) -> str:
        """
        Decode QR code from image path.
        """
        # Try importing pyzbar and decoding
        try:
            from pyzbar.pyzbar import decode
            img = Image.open(image_path)
            decoded = decode(img)
            if decoded:
                return decoded[0].data.decode("utf-8")
        except Exception as e:
            logger.warning(f"pyzbar decoding failed: {e}")

        # Try OpenCV as a fallback
        try:
            import cv2
            img = cv2.imread(image_path)
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(img)
            if data:
                return data
        except Exception as e:
            logger.warning(f"OpenCV decoding failed: {e}")

        return ""

    def analyze(self, image_path: str) -> dict[str, Any]:
        """
        Analyze QR code from image path.
        """
        decoded_text = self.decode_qr(image_path)
        has_url = contains_url(decoded_text) if decoded_text else False
        
        is_short = False
        if has_url:
            is_short = shorturl_service.is_short_url(decoded_text)
            
        url_analysis = {}
        if has_url:
            try:
                url_analysis = url_service.analyze(decoded_text)
            except Exception as e:
                logger.error(f"Failed to scan QR URL: {e}")

        analysis = {
            "scanner": "qr",
            "image_path": image_path,
            "payload": decoded_text,
            "qr_type": "URL" if has_url else "Text",
            "decoded_text": decoded_text,
            "is_short_url": is_short,
            "contains_url": has_url,
            "url_analysis": url_analysis,
            "risk_score": 0.0,
            "reputation": {}
        }
        
        reputation = reputation_service.analyze(analysis) or {}
        analysis["reputation"] = reputation
        analysis["risk_score"] = reputation.get("risk_score") or 0.0
        
        return analysis

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """
        return {
            "service": "QR Service",
            "status": "Healthy"
        }

    def __repr__(self) -> str:
        return "QRService(Enterprise Version)"


qr_service = QRService()
