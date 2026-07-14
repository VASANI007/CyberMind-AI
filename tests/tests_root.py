"""
CyberMind AI
Tests Root Manager
Enterprise Production Version
"""

from __future__ import annotations


import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import io
import pathlib
import sys
import pytest

# Add project root to path for direct execution support
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pathlib import Path
from typing import Any
from core.logger import logger


class TestsRoot:
    """
    Tests Root Manager.
    """

    VERSION = "2.0"

    def __init__(self) -> None:
        self.test_dir = Path(__file__).parent
        self.test_files = sorted(list(self.test_dir.glob("test_*.py")))

    def initialize(self) -> None:
        """
        Initialize tests layer.
        """
        logger.info("Initializing Tests...")
        logger.info(f"Discovered {len(self.test_files)} test files.")

    def run_tests(self, quiet: bool = True) -> int:
        """
        Run all tests using pytest.
        """
        logger.info("Running CyberMind AI test suite...")
        args = [str(self.test_dir)]
        if quiet:
            args.append("-q")
        
        # Invoke pytest
        exit_code = pytest.main(args)
        if exit_code == 0:
            logger.info("✔ All tests passed successfully!")
        else:
            logger.error(f"❌ Test suite failed with exit code: {exit_code}")
        return exit_code

    def health_check(self) -> dict[str, Any]:
        """
        Tests module health check.
        """
        return {
            "service": "Tests",
            "status": "Healthy" if len(self.test_files) > 0 else "Unhealthy",
            "test_files_count": len(self.test_files)
        }

    def status(self) -> dict[str, Any]:
        """
        Tests status.
        """
        return {
            "version": self.VERSION,
            "test_files": [f.name for f in self.test_files]
        }

    def list_tests(self) -> list[str]:
        """
        List all discovered test files.
        """
        return [f.name for f in self.test_files]

    def reload(self) -> None:
        """
        Reload test file discovery.
        """
        self.test_files = sorted(list(self.test_dir.glob("test_*.py")))

    def shutdown(self) -> None:
        """
        Shutdown tests.
        """
        logger.info("Tests manager shutdown.")

    def __len__(self) -> int:
        return len(self.test_files)

    def __repr__(self) -> str:
        return (
            f"TestsRoot("
            f"files={len(self.test_files)}, "
            f"version='{self.VERSION}')"
        )


tests_root = TestsRoot()

if __name__ == "__main__":
    # Configure stdout and stderr to support UTF-8 characters (emojis) on Windows terminals
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    sys.exit(tests_root.run_tests(quiet=False))
