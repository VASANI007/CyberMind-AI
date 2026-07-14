"""
CyberMind AI

Metadata Service
"""

from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class MetadataService:

    def get_file_metadata(
        self,
        file_path: str | Path
    ) -> dict:
        """
        Return file metadata.
        """

        file = Path(file_path)

        if not file.exists():

            raise FileNotFoundError(
                f"File not found: {file}"
            )

        stat = file.stat()

        mime_type, _ = mimetypes.guess_type(file)

        return {

            "name": file.name,

            "stem": file.stem,

            "extension": file.suffix.lower(),

            "mime_type": mime_type or "application/octet-stream",

            "size": stat.st_size,

            "created_at": datetime.fromtimestamp(
                stat.st_ctime
            ),

            "modified_at": datetime.fromtimestamp(
                stat.st_mtime
            ),

            "absolute_path": str(
                file.resolve()
            )

        }

    def get_url_metadata(
        self,
        url: str
    ) -> dict:
        """
        Return URL metadata.
        """

        parsed = urlparse(url)

        return {

            "url": url,

            "scheme": parsed.scheme,

            "hostname": parsed.hostname,

            "port": parsed.port,

            "path": parsed.path,

            "query": parsed.query,

            "fragment": parsed.fragment,

            "username": parsed.username,

            "password": parsed.password,

            "netloc": parsed.netloc

        }

    def get_domain_metadata(
        self,
        domain: str
    ) -> dict:
        """
        Return domain metadata.
        """

        parsed = urlparse(

            f"https://{domain}"

        )

        labels = [

            label

            for label in parsed.hostname.split(".")

            if label

        ]

        return {

            "domain": parsed.hostname,

            "subdomain_count": max(
                len(labels) - 2,
                0
            ),

            "label_count": len(labels),

            "length": len(parsed.hostname),

            "tld": labels[-1] if labels else "",

            "is_https": True

        }

    def extract(self, target: str | Path) -> dict:
        """
        Extract metadata from target (URL, file, or domain).
        """
        target_str = str(target)
        if target_str.startswith(("http://", "https://")):
            return self.get_url_metadata(target_str)
        elif Path(target_str).exists():
            return self.get_file_metadata(target)
        else:
            return self.get_domain_metadata(target_str)


metadata_service = MetadataService()