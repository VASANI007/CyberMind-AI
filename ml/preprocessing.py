"""
CyberMind AI

Preprocessing

Enterprise Production Version
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    StandardScaler
)

from core.logger import logger


class Preprocessing:
    """
    Enterprise Preprocessing Pipeline.

    Responsibilities

    • Missing Values

    • Label Encoding

    • Feature Scaling

    • Data Cleaning

    • Data Validation
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "Preprocessing initialized."

        )

        self.standard_scaler = StandardScaler()

        self.minmax_scaler = MinMaxScaler()

        self.imputer = SimpleImputer(

            strategy="mean"

        )

        self.label_encoders: dict[

            str,

            LabelEncoder

        ] = {}

    def remove_duplicates(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Remove duplicate rows.
        """

        return dataframe.drop_duplicates()

    def fill_missing(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Fill numeric missing values.
        """

        numeric_columns = dataframe.select_dtypes(

            include=np.number

        ).columns

        if len(

            numeric_columns

        ):

            dataframe[

                numeric_columns

            ] = self.imputer.fit_transform(

                dataframe[

                    numeric_columns

                ]

            )

        return dataframe

    def encode_labels(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Encode categorical columns.
        """

        categorical = dataframe.select_dtypes(

            include="object"

        ).columns

        for column in categorical:

            encoder = LabelEncoder()

            dataframe[column] = encoder.fit_transform(

                dataframe[column].astype(

                    str

                )

            )

            self.label_encoders[

                column

            ] = encoder

        return dataframe

    def standard_scale(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Standard scaling.
        """

        numeric = dataframe.select_dtypes(

            include=np.number

        ).columns

        dataframe[

            numeric

        ] = self.standard_scaler.fit_transform(

            dataframe[

                numeric

            ]

        )

        return dataframe

    def minmax_scale(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Min-Max scaling.
        """

        numeric = dataframe.select_dtypes(

            include=np.number

        ).columns

        dataframe[

            numeric

        ] = self.minmax_scaler.fit_transform(

            dataframe[

                numeric

            ]

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
        Validate dataset.
        """

        if dataframe.empty:

            return False

        if dataframe.shape[

            1

        ] == 0:

            return False

        return True

    def pipeline(
        self,
        dataframe: pd.DataFrame,
        *,
        remove_duplicates: bool = True,
        fill_missing: bool = True,
        encode_labels: bool = True,
        scaling: str = "standard"
    ) -> pd.DataFrame:
        """
        Complete preprocessing pipeline.
        """

        dataframe = dataframe.copy()

        if not self.validate(

            dataframe

        ):

            raise ValueError(

                "Invalid dataframe."

            )

        if remove_duplicates:

            dataframe = self.remove_duplicates(

                dataframe

            )

        if fill_missing:

            dataframe = self.fill_missing(

                dataframe

            )

        if encode_labels:

            dataframe = self.encode_labels(

                dataframe

            )

        scaling = scaling.lower()

        if scaling == "standard":

            dataframe = self.standard_scale(

                dataframe

            )

        elif scaling == "minmax":

            dataframe = self.minmax_scale(

                dataframe

            )

        elif scaling == "none":

            pass

        else:

            raise ValueError(

                f"Unsupported scaling method: {scaling}"

            )

        return dataframe

    def reset(
        self
    ) -> None:
        """
        Reset preprocessing state.
        """

        self.label_encoders.clear()

        self.standard_scaler = StandardScaler()

        self.minmax_scaler = MinMaxScaler()

        self.imputer = SimpleImputer(

            strategy="mean"

        )

        logger.info(

            "Preprocessing reset."

        )

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Preprocessing",

            "status":

                "Healthy",

            "label_encoders":

                len(

                    self.label_encoders

                ),

            "scalers":

                [

                    "StandardScaler",

                    "MinMaxScaler"

                ]

        }

    def __repr__(
        self
    ) -> str:

        return (

            "Preprocessing("

            "Enterprise Version)"

        )


preprocessing = Preprocessing()