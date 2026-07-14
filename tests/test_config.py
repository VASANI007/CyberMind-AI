"""
CyberMind AI
Configuration Tests
Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path

from config.settings import settings
from config.constants import Constants


def test_project_name() -> None:
    """
    Test project name.
    """

    assert settings.PROJECT_NAME
    assert isinstance(
        settings.PROJECT_NAME,
        str
    )


def test_project_version() -> None:
    """
    Test version.
    """

    assert settings.VERSION
    assert isinstance(
        settings.VERSION,
        str
    )


def test_debug_mode() -> None:
    """
    Test debug mode.
    """

    assert isinstance(
        settings.DEBUG,
        bool
    )


def test_log_directory() -> None:
    """
    Test log directory.
    """

    assert isinstance(
        settings.LOG_DIR,
        (str, Path)
    )


def test_database_path() -> None:
    """
    Test database path.
    """

    assert settings.DATABASE_PATH


def test_model_directory() -> None:
    """
    Test model directory.
    """

    assert settings.MODEL_DIR


def test_report_directory() -> None:
    """
    Test report directory.
    """

    assert settings.REPORT_DIR


def test_constants() -> None:
    """
    Test constants class.
    """

    assert Constants is not None


def test_settings_instance() -> None:
    """
    Test settings instance.
    """

    assert settings is not None


def test_configuration_loaded() -> None:
    """
    Configuration successfully loaded.
    """

    assert settings.PROJECT_NAME != ""