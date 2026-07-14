"""
CyberMind AI

File Utilities

Enterprise Production Version
"""

from __future__ import annotations

from pathlib import Path

import shutil

from typing import Any

from core.logger import logger


class FileUtils:
    """
    Enterprise File Utility.

    Responsibilities

    • File Validation

    • File Information

    • Read

    • Write

    • Copy

    • Move

    • Delete

    • Directory Operations
    """

    def __init__(
        self
    ) -> None:

        logger.info(

            "File Utils initialized."

        )

    def exists(
        self,
        path: str
    ) -> bool:
        """
        File exists.
        """

        return Path(

            path

        ).exists()

    def is_file(
        self,
        path: str
    ) -> bool:
        """
        Is file.
        """

        return Path(

            path

        ).is_file()

    def is_directory(
        self,
        path: str
    ) -> bool:
        """
        Is directory.
        """

        return Path(

            path

        ).is_dir()

    def extension(
        self,
        path: str
    ) -> str:
        """
        File extension.
        """

        return Path(

            path

        ).suffix.lower()

    def filename(
        self,
        path: str
    ) -> str:
        """
        Filename.
        """

        return Path(

            path

        ).name

    def stem(
        self,
        path: str
    ) -> str:
        """
        Filename without extension.
        """

        return Path(

            path

        ).stem

    def size(
        self,
        path: str
    ) -> int:
        """
        File size.
        """

        return Path(

            path

        ).stat().st_size

    def read_text(
        self,
        path: str,
        encoding: str = "utf-8"
    ) -> str:
        """
        Read text file.
        """

        return Path(

            path

        ).read_text(

            encoding=encoding

        )

    def write_text(
        self,
        path: str,
        text: str,
        encoding: str = "utf-8"
    ) -> None:
        """
        Write text file.
        """

        Path(

            path

        ).write_text(

            text,

            encoding=encoding

        )

    def copy(
        self,
        source: str,
        destination: str
    ) -> None:
        """
        Copy file.
        """

        shutil.copy2(

            source,

            destination

        )

    def move(
        self,
        source: str,
        destination: str
    ) -> None:
        """
        Move file.
        """

        shutil.move(

            source,

            destination

        )

    def delete(
        self,
        path: str
    ) -> bool:
        """
        Delete file.
        """

        file = Path(

            path

        )

        if not file.exists():

            return False

        file.unlink()

        return True

    def create_directory(
        self,
        path: str
    ) -> None:
        """
        Create directory.
        """

        Path(

            path

        ).mkdir(

            parents=True,

            exist_ok=True

        )

    def list_files(
        self,
        directory: str
    ) -> list[str]:
        """
        List files.
        """

        folder = Path(

            directory

        )

        if not folder.exists():

            return []

        return [

            str(file)

            for file

            in folder.iterdir()

            if file.is_file()

        ]

    def information(
        self,
        path: str
    ) -> dict[str, Any]:
        """
        File information.
        """

        file = Path(

            path

        )

        return {

            "exists":

                file.exists(),

            "name":

                file.name,

            "stem":

                file.stem,

            "extension":

                file.suffix.lower(),

            "size":

                file.stat().st_size

                if file.exists()

                else 0,

            "is_file":

                file.is_file(),

            "is_directory":

                file.is_dir(),

            "parent":

                str(

                    file.parent

                )

        }

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Health check.
        """

        return {

            "service":

                "File Utils",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "FileUtils("

            "Enterprise Version)"

        )


file_utils = FileUtils()