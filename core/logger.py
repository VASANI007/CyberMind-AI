"""
CyberMind AI

Logger
"""

import logging
import warnings
from pathlib import Path

from config.settings import LOG_PATH

# Silence benign Streamlit background thread context warnings
for _name in (
    "streamlit.runtime.scriptrunner.script_run_context",
    "streamlit.runtime.scriptrunner_utils.script_run_context",
    "streamlit.runtime.scriptrunner",
):
    _l = logging.getLogger(_name)
    _l.setLevel(logging.ERROR)
    _l.addFilter(lambda r: "ScriptRunContext" not in r.getMessage())

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")


LOG_PATH.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = LOG_PATH / "cybermind.log"


class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except (ValueError, OSError):
            pass

    def flush(self):
        try:
            super().flush()
        except (ValueError, OSError):
            pass


def get_logger(name: str) -> logging.Logger:
    """
    Return logger instance.
    """

    logger = logging.getLogger(name)

    if logger.hasHandlers():

        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = SafeStreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger


logger = get_logger("CyberMind AI")