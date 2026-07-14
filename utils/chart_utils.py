"""
CyberMind AI

Chart Utilities

Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

from core.logger import logger


class ChartUtils:
    """
    Enterprise Chart Utility.

    Responsibilities

    • Bar Chart

    • Line Chart

    • Pie Chart

    • Histogram

    • Scatter Plot

    • Export Charts

    • Dashboard Support
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Chart Utils initialized."

        )

    def line_chart(
        self,
        dataframe: pd.DataFrame,
        x: str,
        y: str,
        title: str = ""
    ):
        """
        Plotly line chart.
        """

        return px.line(

            dataframe,

            x=x,

            y=y,

            title=title

        )

    def bar_chart(
        self,
        dataframe: pd.DataFrame,
        x: str,
        y: str,
        title: str = ""
    ):
        """
        Plotly bar chart.
        """

        return px.bar(

            dataframe,

            x=x,

            y=y,

            title=title

        )

    def pie_chart(
        self,
        dataframe: pd.DataFrame,
        names: str,
        values: str,
        title: str = ""
    ):
        """
        Plotly pie chart.
        """

        return px.pie(

            dataframe,

            names=names,

            values=values,

            title=title

        )

    def histogram(
        self,
        dataframe: pd.DataFrame,
        column: str,
        title: str = ""
    ):
        """
        Plotly histogram.
        """

        return px.histogram(

            dataframe,

            x=column,

            title=title

        )

    def scatter_chart(
        self,
        dataframe: pd.DataFrame,
        x: str,
        y: str,
        color: str | None = None,
        title: str = ""
    ):
        """
        Plotly scatter chart.
        """

        return px.scatter(

            dataframe,

            x=x,

            y=y,

            color=color,

            title=title

        )

    def save_matplotlib(
        self,
        path: str
    ) -> None:
        """
        Save matplotlib figure.
        """

        Path(

            path

        ).parent.mkdir(

            parents=True,

            exist_ok=True

        )

        plt.savefig(

            path,

            dpi=300,

            bbox_inches="tight"

        )

    def close(
        self
    ) -> None:
        """
        Close matplotlib figure.
        """

        plt.close()

    def supported_charts(
        self
    ) -> list[str]:
        """
        Supported chart types.
        """

        return [

            "Line Chart",

            "Bar Chart",

            "Pie Chart",

            "Histogram",

            "Scatter Chart"

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Chart Utils",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "ChartUtils("

            "Enterprise Version)"

        )


chart_utils = ChartUtils()