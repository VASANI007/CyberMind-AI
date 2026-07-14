"""
CyberMind AI
Core Root Manager
Enterprise Production Version
"""

from __future__ import annotations

import sys
import os
import logging

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Suppress Streamlit "missing ScriptRunContext" warnings when run outside of `streamlit run`
class _SuppressStreamlitBareMode(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "ScriptRunContext" not in record.getMessage() and \
               "Session state does not function" not in record.getMessage()

for _st_logger_name in (
    "streamlit.runtime.scriptrunner_utils.script_run_context",
    "streamlit.runtime.state.session_state_proxy",
):
    logging.getLogger(_st_logger_name).addFilter(_SuppressStreamlitBareMode())

from typing import Any

from core.logger import logger
from core.startup import startup
from core.navigation import navigation
from core.session import session

import core.cache as cache
import core.helpers as helpers
import core.security as security
import core.validator as validator
import core.exceptions as exceptions
import core.constants as constants


class CoreRoot:
    """
    Core Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.components = {

            "logger": logger,
            "startup": startup,
            "navigation": navigation,
            "session": session,
            "cache": cache,
            "helpers": helpers,
            "security": security,
            "validator": validator,
            "exceptions": exceptions,
            "constants": constants

        }

    def initialize(self) -> None:
        """
        Initialize core.
        """

        logger.info(
            "Initializing Core..."
        )

        session.initialize()

        logger.info(
            "Session initialized."
        )

        logger.info(
            "Navigation initialized."
        )

        logger.info(
            "Core initialized successfully."
        )

    def health_check(self) -> dict[str, Any]:
        """
        Core health.
        """

        healthy = all(
            component is not None
            for component in self.components.values()
        )

        return {

            "service": "Core",

            "status": (
                "Healthy"
                if healthy
                else "Unhealthy"
            ),

            "components": len(
                self.components
            )

        }

    def status(self) -> dict[str, Any]:
        """
        Core status.
        """

        return {

            "version": self.VERSION,

            "components": len(
                self.components
            ),

            "startup": startup.health_check()

        }

    def reload(self) -> None:
        """
        Reload core.
        """

        logger.info(
            "Reloading Core..."
        )

        session.initialize()

    def shutdown(self) -> None:
        """
        Shutdown core.
        """

        logger.info(
            "Core shutdown."
        )

    def list_components(self) -> list[str]:
        """
        List all components.
        """

        return list(
            self.components.keys()
        )

    def __len__(self) -> int:

        return len(
            self.components
        )

    def __repr__(self) -> str:

        return (

            f"CoreRoot("
            f"components={len(self.components)}, "
            f"version='{self.VERSION}')"

        )


core_root = CoreRoot()