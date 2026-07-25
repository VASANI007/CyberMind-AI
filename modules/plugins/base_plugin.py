"""
CyberMind AI
Base Plugin Interface
Enterprise Production Version
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """
    Abstract base class for all CyberMind AI plugins.

    Every new service or module should implement this interface
    so it can be auto-discovered by the PluginManager.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable plugin name."""
        ...

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0"

    @property
    def plugin_type(self) -> str:
        """Plugin type: 'service', 'module', 'ml_model', or 'engine'."""
        return "service"

    @abstractmethod
    def analyze(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Primary analysis method.
        Each plugin defines its own signature.
        """
        ...

    def health_check(self) -> dict[str, Any]:
        """Plugin health check."""
        return {
            "plugin": self.name,
            "status": "Healthy",
            "version": self.version,
            "type": self.plugin_type,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', v{self.version})"
