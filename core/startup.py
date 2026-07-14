"""
CyberMind AI

Startup Manager

Enterprise Production Version
"""

from __future__ import annotations

import time
from typing import Any

from core.logger import logger

from config.settings import (
    APP_NAME,
    APP_VERSION
)

from database.db import (
    initialize_database
)
class CallableDict(dict):
    """
    A dictionary subclass that is callable, returning itself.
    """
    def __call__(self) -> dict:
        return self



class StartupManager:
    """
    CyberMind AI Startup Manager.

    Responsibilities

    • Configuration

    • Logger

    • Database

    • ML Models

    • Services

    • Modules

    • APIs

    • Health Check

    • Startup Summary
    """

    def __init__(
        self
    ) -> None:

        self.start_time = time.perf_counter()

        self.status = CallableDict({

            "configuration": False,

            "logger": False,

            "database": False,

            "ml": False,

            "services": False,

            "modules": False,

            "api": False

        })

        logger.info(

            "Startup Manager initialized."

        )

    def __call__(self) -> dict[str, Any]:
        """
        Make the startup manager instance callable.
        """
        return self.startup()


    def configuration(
        self
    ) -> bool:
        """
        Load configuration.
        """

        logger.info(

            "Loading configuration..."

        )

        self.status[

            "configuration"

        ] = True

        return True

    def logging(
        self
    ) -> bool:
        """
        Initialize logging.
        """

        logger.info(

            "Logger ready."

        )

        self.status[

            "logger"

        ] = True

        return True

    def database(
        self
    ) -> bool:
        """
        Initialize database.
        """

        try:

            initialize_database()

            self.status[

                "database"

            ] = True

            logger.info(

                "Database initialized."

            )

            return True

        except Exception as error:

            logger.exception(

                error

            )

            return False
        
        
        
    def ml(
        self
    ) -> bool:
        """
        Initialize ML models.
        """

        try:

            logger.info(

                "Loading ML models..."

            )

            from ml.model_loader import model_loader

            model_loader.load()

            self.status[

                "ml"

            ] = True

            logger.info(

                "ML models loaded."

            )

            return True

        except Exception as error:

            logger.exception(

                error

            )

            return False

    def services(
        self
    ) -> list[str]:
        """
        Initialize services.
        """

        try:

            logger.info(

                "Initializing services..."

            )

            import services

            self.status[

                "services"

            ] = True

            logger.info(

                "Services initialized."

            )

            return ["url_service", "website_service", "domain_service", "email_service", "ip_service", "file_service", "qr_service"]

        except Exception as error:

            logger.exception(

                error

            )

            self.status["services"] = False
            return []

    def modules(
        self
    ) -> list[str]:
        """
        Initialize modules.
        """

        try:

            logger.info(

                "Initializing modules..."

            )

            import modules

            self.status[

                "modules"

            ] = True

            logger.info(

                "Modules initialized."

            )

            return ["url_module", "website_module", "domain_module", "email_module", "ip_module", "file_module", "qr_module"]

        except Exception as error:

            logger.exception(

                error

            )

            self.status["modules"] = False
            return []

    def api(
        self
    ) -> bool:
        """
        Initialize external APIs.
        """

        try:

            logger.info(

                "Checking API configuration..."

            )

            from config.api_config import (

                GOOGLE_SAFE_BROWSING_API_KEY,

                VIRUSTOTAL_API_KEY,

                ABUSEIPDB_API_KEY,

                IPINFO_API_KEY

            )

            keys = [

                GOOGLE_SAFE_BROWSING_API_KEY,

                VIRUSTOTAL_API_KEY,

                ABUSEIPDB_API_KEY,

                IPINFO_API_KEY

            ]

            self.status[

                "api"

            ] = all(

                bool(key)

                for key in keys

            )

            logger.info(

                "API configuration checked."

            )

            return self.status[

                "api"

            ]

        except Exception as error:

            logger.exception(

                error

            )

            return False


    def startup(
        self
    ) -> dict[str, Any]:
        """
        Start CyberMind AI.
        """

        logger.info(

            "=" * 60

        )

        logger.info(

            "%s %s Starting...",

            APP_NAME,

            APP_VERSION

        )

        logger.info(

            "=" * 60

        )

        self.configuration()

        self.logging()

        self.database()

        self.ml()

        self.services()

        self.modules()

        self.api()

        startup_time = round(

            time.perf_counter()

            -

            self.start_time,

            3

        )

        successful = sum(

            self.status.values()

        )

        total = len(

            self.status

        )

        logger.info(

            "=" * 60

        )

        logger.info(

            "Startup Complete"

        )

        logger.info(

            "Initialized : %s/%s",

            successful,

            total

        )

        logger.info(

            "Startup Time : %.3f sec",

            startup_time

        )

        logger.info(

            "=" * 60

        )

        return {

            "application": APP_NAME,

            "version": APP_VERSION,

            "initialized": successful,

            "total": total,

            "startup_time": startup_time,

            "status": self.status.copy()

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Startup health.
        """

        return {

            "status": "Healthy",

            "healthy": all(self.status.values()),

            "details": self.status.copy()

        }

    def initialize(self) -> bool:
        """
        Initialize startup.
        """
        self.startup()
        return True

    def shutdown(self) -> bool:
        """
        Shutdown startup.
        """
        logger.info("Startup Manager shutdown.")
        return True

    def restart(self) -> bool:
        """
        Restart startup.
        """
        self.reset()
        return self.initialize()

    def version(self) -> str:
        """
        Get application version.
        """
        return APP_VERSION

    def reset(
        self
    ) -> None:
        """
        Reset startup status.
        """

        for key in self.status:

            self.status[

                key

            ] = False

        self.start_time = time.perf_counter()

        logger.info(

            "Startup manager reset."

        )

    def __repr__(
        self
    ) -> str:

        return (

            "StartupManager("

            "Enterprise Version)"

        )


startup = StartupManager()