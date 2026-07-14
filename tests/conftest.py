"""
CyberMind AI
Pytest Configuration
Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Project root directory.
    """
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def sample_url() -> str:
    """
    Sample URL.
    """
    return "https://example.com"


@pytest.fixture(scope="session")
def sample_domain() -> str:
    """
    Sample domain.
    """
    return "example.com"


@pytest.fixture(scope="session")
def sample_email() -> str:
    """
    Sample email.
    """
    return "admin@example.com"


@pytest.fixture(scope="session")
def sample_ip() -> str:
    """
    Sample IP.
    """
    return "8.8.8.8"


@pytest.fixture(scope="session")
def sample_file() -> dict:
    """
    Sample file information.
    """
    return {
        "filename": "sample.pdf",
        "extension": ".pdf",
        "size": 1024,
        "mime_type": "application/pdf"
    }


@pytest.fixture(scope="session")
def sample_qr() -> dict:
    """
    Sample QR data.
    """
    return {
        "decoded_text": "https://example.com",
        "contains_url": True,
        "content_type": "URL"
    }


@pytest.fixture(scope="session")
def sample_dataframe() -> pd.DataFrame:
    """
    Sample ML dataframe.
    """
    return pd.DataFrame({
        "url": [
            "https://example.com",
            "http://test.com"
        ],
        "hostname": [
            "example.com",
            "test.com"
        ]
    })


@pytest.fixture(scope="session")
def sample_classification_dataset() -> pd.DataFrame:
    """
    Sample classification dataset.
    """
    return pd.DataFrame({
        "url_length": [25, 35, 50, 18, 60],
        "digit_count": [1, 2, 5, 0, 8],
        "special_character_count": [2, 3, 6, 1, 7],
        "target": [0, 0, 1, 0, 1]
    })


@pytest.fixture(scope="session")
def sample_prediction() -> dict:
    """
    Sample prediction.
    """
    return {
        "prediction": [0],
        "probability": [[0.95, 0.05]],
        "confidence": 95.0
    }


@pytest.fixture(scope="session")
def sample_report() -> dict:
    """
    Sample report.
    """
    return {
        "success": True,
        "scanner": "url",
        "risk": "Low",
        "score": 95
    }


@pytest.fixture(scope="session")
def sample_metadata() -> dict:
    """
    Sample metadata.
    """
    return {
        "version": "2.0.0",
        "author": "CyberMind AI"
    }