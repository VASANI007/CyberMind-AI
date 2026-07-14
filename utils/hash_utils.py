"""
CyberMind AI

Hash Utilities

Enterprise Production Version
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.logger import logger


class HashUtils:
    """
    Enterprise Hash Utility.

    Responsibilities

    • Text Hash

    • File Hash

    • Verify Hash

    • Compare Hash

    • Fingerprint
    """

    DEFAULT_ALGORITHM = "sha256"

    SUPPORTED_ALGORITHMS = (

        "md5",

        "sha1",

        "sha224",

        "sha256",

        "sha384",

        "sha512",

        "sha3_256",

        "sha3_512",

        "blake2b",

        "blake2s"

    )

    def __init__(
        self
    ) -> None:

        logger.info(

            "Hash Utils initialized."

        )

    def available_algorithms(
        self
    ) -> list[str]:
        """
        Supported algorithms.
        """

        return list(

            self.SUPPORTED_ALGORITHMS

        )

    def _hash(
        self,
        data: bytes,
        algorithm: str
    ) -> str:
        """
        Internal hash function.
        """

        algorithm = algorithm.lower()

        if algorithm not in self.SUPPORTED_ALGORITHMS:

            raise ValueError(

                f"Unsupported algorithm: {algorithm}"

            )

        hasher = hashlib.new(

            algorithm

        )

        hasher.update(

            data

        )

        return hasher.hexdigest()

    def hash_text(
        self,
        text: str,
        algorithm: str = DEFAULT_ALGORITHM
    ) -> str:
        """
        Hash text.
        """

        return self._hash(

            text.encode(

                "utf-8"

            ),

            algorithm

        )

    def hash_file(
        self,
        file_path: str,
        algorithm: str = DEFAULT_ALGORITHM,
        chunk_size: int = 8192
    ) -> str:
        """
        Hash file.
        """

        path = Path(

            file_path

        )

        if not path.is_file():

            raise FileNotFoundError(

                file_path

            )

        hasher = hashlib.new(

            algorithm

        )

        with path.open(

            "rb"

        ) as file:

            while True:

                chunk = file.read(

                    chunk_size

                )

                if not chunk:

                    break

                hasher.update(

                    chunk

                )

        return hasher.hexdigest()

    def md5(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "md5"

        )

    def sha1(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "sha1"

        )

    def sha224(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "sha224"

        )

    def sha256(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "sha256"

        )

    def sha384(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "sha384"

        )

    def sha512(
        self,
        text: str
    ) -> str:

        return self.hash_text(

            text,

            "sha512"

        )
        
        
        
    def sha3_256(
        self,
        text: str
    ) -> str:
        """
        SHA3-256 hash.
        """

        return self.hash_text(

            text,

            "sha3_256"

        )

    def sha3_512(
        self,
        text: str
    ) -> str:
        """
        SHA3-512 hash.
        """

        return self.hash_text(

            text,

            "sha3_512"

        )

    def blake2b(
        self,
        text: str
    ) -> str:
        """
        BLAKE2b hash.
        """

        return self.hash_text(

            text,

            "blake2b"

        )

    def blake2s(
        self,
        text: str
    ) -> str:
        """
        BLAKE2s hash.
        """

        return self.hash_text(

            text,

            "blake2s"

        )

    def verify(
        self,
        text: str,
        expected_hash: str,
        algorithm: str = DEFAULT_ALGORITHM
    ) -> bool:
        """
        Verify hash.
        """

        return (

            self.hash_text(

                text,

                algorithm

            )

            ==

            expected_hash.lower()

        )

    def compare(
        self,
        hash1: str,
        hash2: str
    ) -> bool:
        """
        Compare hashes.
        """

        return (

            hash1.lower()

            ==

            hash2.lower()

        )

    def fingerprint(
        self,
        text: str
    ) -> str:
        """
        Generate short fingerprint.
        """

        digest = self.sha256(

            text

        )

        return (

            digest[:8]

            +

            "-"

            +

            digest[-8:]

        )

    def hash_information(
        self,
        algorithm: str = DEFAULT_ALGORITHM
    ) -> dict[str, Any]:
        """
        Algorithm information.
        """

        algorithm = algorithm.lower()

        if algorithm not in self.SUPPORTED_ALGORITHMS:

            raise ValueError(

                f"Unsupported algorithm: {algorithm}"

            )

        digest_size = hashlib.new(

            algorithm

        ).digest_size

        block_size = hashlib.new(

            algorithm

        ).block_size

        return {

            "algorithm":

                algorithm,

            "digest_size":

                digest_size,

            "block_size":

                block_size,

            "available":

                True

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "Hash Utils",

            "status":

                "Healthy",

            "default_algorithm":

                self.DEFAULT_ALGORITHM,

            "supported_algorithms":

                len(

                    self.SUPPORTED_ALGORITHMS

                )

        }

    def __repr__(
        self
    ) -> str:

        return (

            "HashUtils("

            "Enterprise Version)"

        )


hash_utils = HashUtils()