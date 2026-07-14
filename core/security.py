"""
CyberMind AI

Security Utilities
"""

import hashlib
import hmac
import secrets
import string
from pathlib import Path


def generate_token(
    length: int = 32
) -> str:
    """
    Generate secure token.
    """

    return secrets.token_hex(length)


def generate_salt(
    length: int = 16
) -> str:
    """
    Generate random salt.
    """

    alphabet = (
        string.ascii_letters
        + string.digits
    )

    return "".join(

        secrets.choice(alphabet)

        for _ in range(length)

    )


def secure_compare(
    value1: str,
    value2: str
) -> bool:
    """
    Secure string comparison.
    """

    return hmac.compare_digest(
        value1,
        value2
    )


def md5(
    text: str
) -> str:
    """
    MD5 hash.
    """

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()


def sha1(
    text: str
) -> str:
    """
    SHA1 hash.
    """

    return hashlib.sha1(
        text.encode("utf-8")
    ).hexdigest()


def sha256(
    text: str
) -> str:
    """
    SHA256 hash.
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def file_sha256(
    file_path: str
) -> str:
    """
    SHA256 hash of file.
    """

    hash_object = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(8192)

            if not chunk:

                break

            hash_object.update(chunk)

    return hash_object.hexdigest()


def file_md5(
    file_path: str
) -> str:
    """
    MD5 hash of file.
    """

    hash_object = hashlib.md5()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(8192)

            if not chunk:

                break

            hash_object.update(chunk)

    return hash_object.hexdigest()


def file_sha1(
    file_path: str
) -> str:
    """
    SHA1 hash of file.
    """

    hash_object = hashlib.sha1()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(8192)

            if not chunk:

                break

            hash_object.update(chunk)

    return hash_object.hexdigest()


def secure_filename(
    filename: str
) -> str:
    """
    Return safe filename.
    """

    invalid = '<>:"/\\|?*'

    for char in invalid:

        filename = filename.replace(
            char,
            "_"
        )

    return Path(
        filename
    ).name


def random_string(
    length: int = 16
) -> str:
    """
    Generate random string.
    """

    alphabet = (

        string.ascii_letters

        + string.digits

    )

    return "".join(

        secrets.choice(alphabet)

        for _ in range(length)

    )