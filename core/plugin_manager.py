"""
CyberMind AI
Plugin Manager
Enterprise Production Version

Auto-discovers and registers plugins from modules/plugins/ and services/.
"""

from __future__ import annotations

import importlib
import os
import pkgutil
from pathlib import Path
from typing import Any

from core.logger import logger


class PluginManager:
    """
    Manages plugin discovery, registration, and retrieval.
    """

    VERSION = "1.0"

    def __init__(self) -> None:
        self._plugins: dict[str, Any] = {}
        logger.info("Plugin Manager initialized.")

    def register_plugin(self, name: str, plugin: Any) -> None:
        """Register a plugin by name."""
        self._plugins[name] = plugin
        logger.info("Plugin registered: %s", name)

    def get_plugin(self, name: str) -> Any | None:
        """Get a registered plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        """List all registered plugin names."""
        return sorted(self._plugins.keys())

    def discover_plugins(self, package_path: str, package_name: str) -> int:
        """
        Auto-discover plugins in a Python package directory.

        Scans all .py files in the given path, imports them,
        and registers any object that has a 'name' and 'analyze'
        attribute (i.e. implements the BasePlugin interface).

        Returns the number of newly discovered plugins.
        """
        discovered = 0
        pkg_dir = Path(package_path)

        if not pkg_dir.is_dir():
            return 0

        for finder, module_name, is_pkg in pkgutil.iter_modules([str(pkg_dir)]):
            if module_name.startswith("_") or module_name == "base_plugin":
                continue

            full_module = f"{package_name}.{module_name}"
            try:
                mod = importlib.import_module(full_module)

                # Look for singleton instances (e.g. foo_service = FooService())
                for attr_name in dir(mod):
                    if attr_name.startswith("_"):
                        continue
                    obj = getattr(mod, attr_name)
                    if (
                        hasattr(obj, "name")
                        and hasattr(obj, "analyze")
                        and not isinstance(obj, type)
                    ):
                        plugin_name = getattr(obj, "name", attr_name)
                        if plugin_name not in self._plugins:
                            self.register_plugin(plugin_name, obj)
                            discovered += 1

            except Exception as exc:
                logger.warning(
                    "Plugin discovery skipped %s: %s", full_module, exc
                )

        return discovered

    def health_check(self) -> dict[str, Any]:
        """Plugin manager health check."""
        plugin_health = {}
        for name, plugin in self._plugins.items():
            try:
                if hasattr(plugin, "health_check"):
                    plugin_health[name] = plugin.health_check()
                else:
                    plugin_health[name] = {"status": "Healthy"}
            except Exception as exc:
                plugin_health[name] = {
                    "status": "Unhealthy",
                    "error": str(exc),
                }

        healthy = all(
            v.get("status") == "Healthy" for v in plugin_health.values()
        )

        return {
            "service": "Plugin Manager",
            "status": "Healthy" if healthy else "Unhealthy",
            "total_plugins": len(self._plugins),
            "plugins": plugin_health,
        }

    def __len__(self) -> int:
        return len(self._plugins)

    def __repr__(self) -> str:
        return (
            f"PluginManager("
            f"plugins={len(self._plugins)}, "
            f"version='{self.VERSION}')"
        )


plugin_manager = PluginManager()
