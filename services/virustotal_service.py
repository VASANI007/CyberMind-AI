"""
CyberMind AI

VirusTotal Service
"""

import base64
import hashlib
from pathlib import Path
import requests

from config.api_config import (
    VIRUSTOTAL_API_KEY,
    HEADERS
)

from core.constants import API_TIMEOUT


class VirusTotalService:

    BASE_URL = "https://www.virustotal.com/api/v3"

    def available(self) -> bool:
        """
        Check API key.
        """

        return bool(VIRUSTOTAL_API_KEY)

    def scan_url(
        self,
        url: str
    ) -> dict:
        """
        Scan URL.
        """

        if not self.available():

            return {
                "success": False,
                "error": "VirusTotal API key not configured.",
                "malicious": 0
            }

        try:
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            # Check existing report first
            report_res = self.get_url_report(url_id)
            if report_res.get("success"):
                attributes = report_res.get("data", {}).get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                if stats:
                    return {
                        "success": True,
                        "malicious": stats.get("malicious", 0),
                        "suspicious": stats.get("suspicious", 0),
                        "harmless": stats.get("harmless", 0),
                        "undetected": stats.get("undetected", 0),
                        "total": sum(stats.values())
                    }

            # Submit URL for scanning
            response = requests.post(

                f"{self.BASE_URL}/urls",

                headers={
                    "x-apikey": VIRUSTOTAL_API_KEY
                },

                data={
                    "url": url
                },

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            # Wait briefly and try fetching once
            import time
            time.sleep(1.0)
            report_res = self.get_url_report(url_id)
            if report_res.get("success"):
                attributes = report_res.get("data", {}).get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                if stats:
                    return {
                        "success": True,
                        "malicious": stats.get("malicious", 0),
                        "suspicious": stats.get("suspicious", 0),
                        "harmless": stats.get("harmless", 0),
                        "undetected": stats.get("undetected", 0),
                        "total": sum(stats.values())
                    }

            return {
                "success": True,
                "message": "Scan submitted. Analysis in progress.",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "total": 0
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
                "malicious": 0
            }

    def get_url_report(
        self,
        url_id: str
    ) -> dict:
        """
        Get URL report.
        """

        if not self.available():

            return {
                "success": False,
                "error": "VirusTotal API key not configured."
            }

        try:

            response = requests.get(

                f"{self.BASE_URL}/urls/{url_id}",

                headers={
                    "x-apikey": VIRUSTOTAL_API_KEY
                },

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except requests.RequestException as error:

            return {
                "success": False,
                "error": str(error)
            }

    def get_file_report(
        self,
        sha256: str
    ) -> dict:
        """
        Get file hash report.
        """

        if not self.available():

            return {
                "success": False,
                "error": "VirusTotal API key not configured."
            }

        try:

            response = requests.get(

                f"{self.BASE_URL}/files/{sha256}",

                headers={
                    "x-apikey": VIRUSTOTAL_API_KEY
                },

                timeout=API_TIMEOUT

            )

            response.raise_for_status()

            return {
                "success": True,
                "data": response.json()
            }

        except requests.RequestException as error:

            return {
                "success": False,
                "error": str(error)
            }


    def scan_file(
        self,
        file_path: str
    ) -> dict:
        """
        Scan file.
        """

        if not self.available():

            return {
                "success": False,
                "error": "VirusTotal API key not configured.",
                "malicious": 0
            }

        path = Path(file_path)
        if not path.is_file():
            return {
                "success": False,
                "error": "File not found.",
                "malicious": 0
            }

        try:
            # Calculate SHA256 of the file
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            sha256 = hasher.hexdigest()

            # Check existing report by hash first
            report_res = self.get_file_report(sha256)
            if report_res.get("success"):
                attributes = report_res.get("data", {}).get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                if stats:
                    return {
                        "success": True,
                        "malicious": stats.get("malicious", 0),
                        "suspicious": stats.get("suspicious", 0),
                        "harmless": stats.get("harmless", 0),
                        "undetected": stats.get("undetected", 0),
                        "total": sum(stats.values())
                    }

            # Fallback: upload file if < 32MB
            if path.stat().st_size < 32 * 1024 * 1024:
                with open(file_path, "rb") as f:
                    response = requests.post(
                        f"{self.BASE_URL}/files",
                        headers={
                            "x-apikey": VIRUSTOTAL_API_KEY
                        },
                        files={
                            "file": (path.name, f)
                        },
                        timeout=API_TIMEOUT
                    )
                response.raise_for_status()

                # Wait briefly and check by hash again
                import time
                time.sleep(1.0)
                report_res = self.get_file_report(sha256)
                if report_res.get("success"):
                    attributes = report_res.get("data", {}).get("data", {}).get("attributes", {})
                    stats = attributes.get("last_analysis_stats", {})
                    if stats:
                        return {
                            "success": True,
                            "malicious": stats.get("malicious", 0),
                            "suspicious": stats.get("suspicious", 0),
                            "harmless": stats.get("harmless", 0),
                            "undetected": stats.get("undetected", 0),
                            "total": sum(stats.values())
                        }

                return {
                    "success": True,
                    "message": "File uploaded. Analysis in progress.",
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                    "total": 0
                }
            else:
                return {
                    "success": False,
                    "error": "File too large to upload. No existing hash report found.",
                    "malicious": 0
                }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
                "malicious": 0
            }


virustotal_service = VirusTotalService()