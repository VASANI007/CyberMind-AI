"""
Tests for Plugin System (Phase 0)
"""

import pytest
from core.plugin_manager import plugin_manager, PluginManager
from modules.plugins.base_plugin import BasePlugin


class MockPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "mock_plugin"

    def analyze(self, *args, **kwargs):
        return {"status": "ok"}


def test_plugin_registration():
    pm = PluginManager()
    plugin = MockPlugin()
    pm.register_plugin("mock_plugin", plugin)

    assert "mock_plugin" in pm.list_plugins()
    assert pm.get_plugin("mock_plugin") is plugin
    assert pm.health_check()["status"] == "Healthy"


def test_base_plugin_defaults():
    plugin = MockPlugin()
    assert plugin.version == "1.0"
    assert plugin.plugin_type == "service"
    assert plugin.health_check()["status"] == "Healthy"
