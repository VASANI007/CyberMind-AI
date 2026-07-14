"""
CyberMind AI

Feature Engineering

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from core.logger import logger


class FeatureEngineering:
    """
    Enterprise Feature Engineering.

    Responsibilities

    • Feature Creation

    • Feature Selection

    • Feature Validation

    • Derived Features

    • Dataset Optimization
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Feature Engineering initialized."

        )

    def url_length(
        self,
        url: str
    ) -> int:
        """
        URL length.
        """

        return len(

            url

        )

    def hostname_length(
        self,
        hostname: str
    ) -> int:
        """
        Hostname length.
        """

        return len(

            hostname

        )

    def count_digits(
        self,
        text: str
    ) -> int:
        """
        Digit count.
        """

        return sum(

            character.isdigit()

            for character

            in text

        )

    def count_letters(
        self,
        text: str
    ) -> int:
        """
        Letter count.
        """

        return sum(

            character.isalpha()

            for character

            in text

        )

    def count_special_characters(
        self,
        text: str
    ) -> int:
        """
        Special character count.
        """

        return sum(

            not character.isalnum()

            for character

            in text

        )

    def count_subdomains(
        self,
        hostname: str
    ) -> int:
        """
        Subdomain count.
        """

        if not hostname:

            return 0

        return max(

            hostname.count("."),

            0

        )

    def create_basic_features(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate basic features.
        """

        dataframe = dataframe.copy()

        if "url" in dataframe.columns:

            dataframe["url_length"] = (

                dataframe["url"]

                .astype(str)

                .apply(

                    self.url_length

                )

            )

            dataframe["digit_count"] = (

                dataframe["url"]

                .astype(str)

                .apply(

                    self.count_digits

                )

            )

            dataframe["letter_count"] = (

                dataframe["url"]

                .astype(str)

                .apply(

                    self.count_letters

                )

            )

            dataframe["special_character_count"] = (

                dataframe["url"]

                .astype(str)

                .apply(

                    self.count_special_characters

                )

            )

        if "hostname" in dataframe.columns:

            dataframe["hostname_length"] = (

                dataframe["hostname"]

                .astype(str)

                .apply(

                    self.hostname_length

                )

            )

            dataframe["subdomain_count"] = (

                dataframe["hostname"]

                .astype(str)

                .apply(

                    self.count_subdomains

                )

            )

        return dataframe
    
    
    
    def select_features(
        self,
        dataframe: pd.DataFrame,
        columns: list[str]
    ) -> pd.DataFrame:
        """
        Select required features.
        """

        return dataframe[

            columns

        ].copy()

    def validate(
        self,
        dataframe: pd.DataFrame
    ) -> bool:
        """
        Validate feature dataset.
        """

        if dataframe.empty:

            return False

        if dataframe.shape[1] == 0:

            return False

        return True

    def statistics(
        self,
        dataframe: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Feature statistics.
        """

        return {

            "rows":

                len(

                    dataframe

                ),

            "columns":

                len(

                    dataframe.columns

                ),

            "feature_names":

                list(

                    dataframe.columns

                ),

            "missing_values":

                int(

                    dataframe.isna()

                    .sum()

                    .sum()

                )

        }

    def pipeline(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Complete feature engineering pipeline.
        """

        if not self.validate(

            dataframe

        ):

            raise ValueError(

                "Invalid dataframe."

            )

        dataframe = self.create_basic_features(

            dataframe

        )

        logger.info(

            "Feature engineering completed."

        )

        return dataframe

    def reset(
        self
    ) -> None:
        """
        Reset feature engineering.
        """

        logger.info(

            "Feature engineering reset."

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """
        return {
            "service":
                "Feature Engineering",
            "status":
                "Healthy",
            "version":
                "2.0"
        }

    def __repr__(
        self
    ) -> str:

        return (

            "FeatureEngineering("

            "Enterprise Version)"

        )


feature_engineering = FeatureEngineering()