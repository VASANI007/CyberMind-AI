"""
CyberMind AI

Session Manager
"""

import streamlit as st


def _is_streamlit_running() -> bool:
    """Return True only when executed inside a real Streamlit server context."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


class SessionManager:

    def __init__(self):
        if _is_streamlit_running():
            self.initialize()

    def initialize(self):
        """
        Initialize session.
        """

        if not _is_streamlit_running():
            return

        defaults = {

            "user": None,

            "current_page": "Dashboard",

            "current_module": None,

            "theme": "Dark",

            "language": "English",

            "scan_result": None,

            "scan_history": [],

            "report_data": None,

            "uploaded_file": None,

            "api_cache": {},

            "settings": {},

            "sidebar_state": "expanded"

        }

        for key, value in defaults.items():

            if key not in st.session_state:

                st.session_state[key] = value

    def get(
        self,
        key,
        default=None
    ):
        """
        Get session value.
        """

        if not _is_streamlit_running():
            return default

        return st.session_state.get(
            key,
            default
        )

    def set(
        self,
        key,
        value
    ):
        """
        Set session value.
        """

        if not _is_streamlit_running():
            return

        st.session_state[key] = value

    def update(
        self,
        data: dict
    ):
        """
        Update multiple values.
        """

        if not _is_streamlit_running():
            return

        for key, value in data.items():

            st.session_state[key] = value

    def remove(
        self,
        key
    ):
        """
        Remove session key.
        """

        if not _is_streamlit_running():
            return

        if key in st.session_state:

            del st.session_state[key]

    def clear(self):
        """
        Clear session.
        """

        if not _is_streamlit_running():
            return

        st.session_state.clear()

    def exists(
        self,
        key
    ) -> bool:
        """
        Check session key.
        """

        if not _is_streamlit_running():
            return False

        return key in st.session_state

    def all(self):
        """
        Return all session values.
        """

        if not _is_streamlit_running():
            return {}

        return dict(st.session_state)


session = SessionManager()


def initialize_session():
    """
    Initialize application session.
    """
    session.initialize()