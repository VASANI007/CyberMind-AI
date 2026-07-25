"""
CyberMind AI
Offline Mode Controller
Enterprise Production Version

Provides global feature flags and fallback logic when offline mode is enabled.
"""

from __future__ import annotations

from typing import Any, Callable
import streamlit as st
from core.logger import logger


class OfflineMode:
    """
    Offline Mode Manager.
    Controls offline state and handles API fallback decorators.
    """

    @property
    def is_enabled(self) -> bool:
        """Check if offline mode toggle is turned on in session_state or env."""
        if hasattr(st, "session_state"):
            try:
                if st.session_state.get("settings_offline_mode", False):
                    return True
            except Exception:
                pass
        import os
        return os.environ.get("OFFLINE_MODE", "").lower() in ("true", "1", "yes")

    def toggle(self, state: bool) -> None:
        """Set offline mode state."""
        import os
        os.environ["OFFLINE_MODE"] = "true" if state else "false"
        if hasattr(st, "session_state"):
            try:
                st.session_state["settings_offline_mode"] = state
                st.session_state["widget_offline_mode"] = state
            except Exception:
                pass
        logger.info("Offline mode set to: %s", state)

    def health_check(self) -> dict[str, Any]:
        return {
            "service": "Offline Mode Controller",
            "status": "Healthy",
            "offline_mode_active": self.is_enabled
        }


offline_mode = OfflineMode()


def offline_fallback(fallback_value: Any = None) -> Callable:
    """
    Decorator to bypass online API calls when offline_mode is active.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if offline_mode.is_enabled:
                logger.info("Offline mode active: skipping API call in %s", func.__name__)
                return fallback_value
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.warning("API call %s failed, using offline fallback: %s", func.__name__, exc)
                return fallback_value
        return wrapper
    return decorator
