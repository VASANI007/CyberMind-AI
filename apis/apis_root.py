"""
CyberMind AI
APIs Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from typing import Any

from core.logger import logger

from apis.url_api import url_api
from apis.website_api import website_api
from apis.domain_api import domain_api
from apis.email_api import email_api
from apis.ip_api import ip_api
from apis.file_api import file_api
from apis.qr_api import qr_api


class APIsRoot:
    """
    APIs Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.apis = [

            url_api,

            website_api,

            domain_api,

            email_api,

            ip_api,

            file_api,

            qr_api

        ]

    def initialize(self) -> None:
        """
        Initialize all APIs.
        """

        logger.info(
            "Initializing APIs..."
        )

        for api in self.apis:

            logger.info(
                "%s initialized.",
                api.__class__.__name__
            )

        logger.info(
            "All APIs initialized successfully."
        )

    def health_check(self) -> dict[str, Any]:
        """
        Health check.
        """

        results = {}

        healthy = True

        for api in self.apis:

            status = api.health_check()

            results[
                api.__class__.__name__
            ] = status

            if status.get("status") != "Healthy":

                healthy = False

        return {

            "service": "APIs",

            "status": "Healthy" if healthy else "Unhealthy",

            "apis": results

        }

    def reload(self) -> None:
        """
        Reload APIs.
        """

        logger.info(
            "Reloading APIs..."
        )

        self.initialize()

    def shutdown(self) -> None:
        """
        Shutdown APIs.
        """

        logger.info(
            "Shutting down APIs..."
        )

    def status(self) -> dict[str, Any]:
        """
        APIs status.
        """

        return {

            "version": self.VERSION,

            "total_apis": len(self.apis),

            "health": self.health_check()

        }

    def list_apis(self) -> list[str]:
        """
        List all APIs.
        """

        return [

            api.__class__.__name__

            for api

            in self.apis

        ]

    def __len__(self) -> int:

        return len(
            self.apis
        )

    def __repr__(self) -> str:

        return (

            f"APIsRoot("
            f"apis={len(self.apis)}, "
            f"version='{self.VERSION}')"

        )


apis_root = APIsRoot()