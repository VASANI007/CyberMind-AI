"""
===========================================================
CyberMind AI
Helper Utilities
===========================================================
"""

from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime
from pathlib import Path



# UUID


def generate_uuid() -> str:
    """
    Generate UUID4.
    """

    return str(uuid.uuid4())



# Secure Token


def generate_token(length: int = 32) -> str:
    """
    Generate secure random token.
    """

    return secrets.token_hex(length)



# Current Time


def current_datetime() -> datetime:
    """
    Return current datetime.
    """

    return datetime.now()


def current_timestamp() -> str:
    """
    Return formatted timestamp.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )



# File Size


def format_file_size(size: int) -> str:
    """
    Convert bytes to readable format.
    """

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    value = float(size)

    for unit in units:

        if value < 1024:

            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} PB"



# JSON


def load_json(file_path: str | Path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(data, file_path: str | Path):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )



# Hashing


def md5_hash(data: str) -> str:

    return hashlib.md5(
        data.encode()
    ).hexdigest()


def sha1_hash(data: str) -> str:

    return hashlib.sha1(
        data.encode()
    ).hexdigest()


def sha256_hash(data: str) -> str:

    return hashlib.sha256(
        data.encode()
    ).hexdigest()



# File Hash


def sha256_file(file_path: str | Path) -> str:
    """
    SHA256 of file.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(8192)

            if not chunk:

                break

            sha256.update(chunk)

    return sha256.hexdigest()



# Risk


def risk_level(score: float) -> str:
    """
    Convert score into risk level.
    """

    if score <= 20:

        return "Safe"

    if score <= 40:

        return "Low"

    if score <= 60:

        return "Medium"

    if score <= 80:

        return "High"

    return "Critical"



# Text


def clean_text(text: str) -> str:
    """
    Clean text.
    """

    return " ".join(
        text.strip().split()
    )



# Path


def create_directory(path: str | Path):
    """
    Create directory.
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )



# File


def file_exists(path: str | Path) -> bool:

    return Path(path).exists()



# Date


def current_date() -> str:

    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def current_time() -> str:

    return datetime.now().strftime(
        "%H:%M:%S"
    )



# Percentage


def percentage(
    value: float,
    total: float
) -> float:
    """
    Calculate percentage.
    """

    if total == 0:

        return 0

    return round(
        (value / total) * 100,
        2
    )


def load_css(file_path: str | Path):
    """
    Load CSS file into Streamlit.
    """
    try:
        import streamlit as st
        path = Path(file_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                st.markdown(
                    f"<style>{file.read()}</style>",
                    unsafe_allow_html=True
                )
    except Exception:
        pass