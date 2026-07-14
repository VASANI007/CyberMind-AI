"""
CyberMind AI

Navigation Manager
"""

import streamlit as st

from core.session import session, _is_streamlit_running


PAGES = [

    "Dashboard",

    "URL Scanner",

    "Website Scanner",

    "Domain Scanner",

    "Email Scanner",

    "IP Scanner",

    "QR Scanner",

    "File Scanner",

    "Reports",

    "Settings"

]


ICONS = {

    "Dashboard": "🏠",

    "URL Scanner": "🌐",

    "Website Scanner": "🖥️",

    "Domain Scanner": "🌍",

    "Email Scanner": "📧",

    "IP Scanner": "📡",

    "QR Scanner": "🔳",

    "File Scanner": "📁",

    "Reports": "📊",

    "Settings": "⚙️"

}


class NavigationManager:

    def __init__(self):

        if _is_streamlit_running() and not session.exists("current_page"):

            session.set(

                "current_page",

                "Dashboard"

            )

    def sidebar(self):
        """
        Render sidebar navigation.
        """

        if not _is_streamlit_running():
            return "Dashboard"

        st.sidebar.title("CyberMind AI")

        selected = st.sidebar.radio(

            "Navigation",

            PAGES,

            index=PAGES.index(

                session.get("current_page") or "Dashboard"

            ),

            format_func=lambda page: (

                f"{ICONS[page]} {page}"

            )

        )

        session.set(

            "current_page",

            selected

        )

        return selected

    def current_page(self):
        """
        Return current page.
        """

        return session.get(

            "current_page"

        ) or "Dashboard"

    def change_page(

        self,

        page: str

    ):
        """
        Change page.
        """

        if page in PAGES:

            session.set(

                "current_page",

                page

            )

    def pages(self):
        """
        Return all pages.
        """

        return PAGES.copy()

    def reset(self):
        """
        Reset navigation.
        """

        session.set(

            "current_page",

            "Dashboard"

        )


navigation = NavigationManager()