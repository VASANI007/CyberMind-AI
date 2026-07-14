"""
CyberMind AI

Website Service

Enterprise Production Version
"""

from __future__ import annotations
from bs4 import BeautifulSoup
import time

from typing import Any

import requests

from core.logger import logger

from services.url_service import (
    url_service
)

from services.dns_service import (
    dns_service
)

from services.whois_service import (
    whois_service
)

from services.ssl_service import (
    ssl_service
)

from services.security_headers_service import (
    security_headers_service
)

from services.geo_service import (
    geo_service
)

from services.reputation_service import (
    reputation_service
)


class WebsiteService:
    """
    Enterprise Website Analysis Service.

    Responsibilities

    • Website Validation

    • HTTP Connection

    • Website Information

    • URL Analysis

    • DNS Analysis

    • WHOIS Analysis

    • SSL Analysis

    • Security Headers

    • Geo Location

    • Reputation

    • Final Website Report
    """

    DEFAULT_TIMEOUT = 10

    DEFAULT_USER_AGENT = (

        "CyberMind-AI/1.0"

    )

    def __init__(
        self
    ) -> None:

        logger.info(

            "Website Service initialized."

        )

        self.session = requests.Session()

        self.session.headers.update(

            {

                "User-Agent":

                    self.DEFAULT_USER_AGENT

            }

        )

    def normalize(self, website: str) -> str:
        """
        Normalize website URL.
        """
        return self._normalize_url(website)

    def validate(self, website: str) -> bool:
        """
        Validate website using url_service.
        """
        return url_service.validate(website)

    def _normalize_url(
        self,
        url: str
    ) -> str:
        """
        Normalize website URL.
        """

        url = url.strip()

        if not url.startswith(

            (

                "http://",

                "https://"

            )

        ):

            url = (

                "https://"

                +

                url

            )

        return url

    def _request(
        self,
        url: str
    ):
        """
        Send HTTP request.
        """

        return self.session.get(

            self._normalize_url(

                url

            ),

            timeout=self.DEFAULT_TIMEOUT,

            allow_redirects=True

        )

    def _empty_response(
        self,
        url: str,
        message: str
    ) -> dict[str, Any]:
        """
        Standard error response.
        """

        return {

            "success": False,

            "url": url,

            "message": message

        }

    def _success_response(
        self
    ) -> dict[str, Any]:
        """
        Standard response.
        """

        return {

            "success": True,

            "url": "",

            "status_code": None,

            "response_time": 0.0,

            "final_url": "",

            "redirected": False,

            "redirect_count": 0,

            "server": "",

            "content_type": "",

            "content_length": 0,

            "website": {},

            "url_analysis": {},

            "dns": {},

            "whois": {},

            "ssl": {},

            "security_headers": {},

            "geo": {},

            "reputation": {}

        }
        
    def connect(
        self,
        url: str
    ):
        """
        Connect to website.
        """

        start_time = time.perf_counter()

        response = self._request(

            url

        )

        response_time = round(

            time.perf_counter()

            -

            start_time,

            3

        )

        return (

            response,

            response_time

        )

    def website_information(
        self,
        response
    ) -> dict[str, Any]:
        """
        Extract website information.
        """

        headers = response.headers

        return {

            "status_code":

                response.status_code,

            "final_url":

                response.url,

            "redirected":

                len(

                    response.history

                ) > 0,

            "redirect_count":

                len(

                    response.history

                ),

            "server":

                headers.get(

                    "Server",

                    ""

                ),

            "content_type":

                headers.get(

                    "Content-Type",

                    ""

                ),

            "content_length":

                headers.get(

                    "Content-Length",

                    0

                ),

            "encoding":

                response.encoding,

            "reason":

                response.reason

        }

    def html(
        self,
        response
    ) -> str:
        """
        Return HTML source.
        """

        return response.text

    def headers(
        self,
        response
    ) -> dict[str, str]:
        """
        Return HTTP headers.
        """

        return dict(

            response.headers

        )

    def cookies(
        self,
        response
    ) -> dict[str, str]:
        """
        Return cookies.
        """

        return response.cookies.get_dict()

    def title(
        self,
        response
    ) -> str:
        """
        Extract page title.
        """

        html = response.text

        start = html.lower().find(

            "<title>"

        )

        end = html.lower().find(

            "</title>"

        )

        if start == -1 or end == -1:

            return ""

        return html[

            start + 7 :

            end

        ].strip()

    def online(
        self,
        url: str
    ) -> bool:
        """
        Website availability.
        """

        try:

            response, _ = self.connect(

                url

            )

            return (

                response.status_code

                <

                500

            )

        except Exception:

            return False


    def soup(
        self,
        response
    ) -> BeautifulSoup:
        """
        Return BeautifulSoup object.
        """

        return BeautifulSoup(

            response.text,

            "html.parser"

        )

    def title(
        self,
        response
    ) -> str:
        """
        Website title.
        """

        soup = self.soup(

            response

        )

        if soup.title:

            return soup.title.get_text(

                strip=True

            )

        return ""

    def meta_tags(
        self,
        response
    ) -> dict[str, str]:
        """
        Extract meta tags.
        """

        soup = self.soup(

            response

        )

        metadata = {}

        for tag in soup.find_all(

            "meta"

        ):

            key = (

                tag.get(

                    "name"

                )

                or

                tag.get(

                    "property"

                )

            )

            value = tag.get(

                "content"

            )

            if key and value:

                metadata[

                    key

                ] = value

        return metadata

    def forms(
        self,
        response
    ) -> list[dict[str, Any]]:
        """
        Extract HTML forms.
        """

        soup = self.soup(

            response

        )

        forms = []

        for form in soup.find_all(

            "form"

        ):

            forms.append(

                {

                    "action":

                        form.get(

                            "action",

                            ""

                        ),

                    "method":

                        form.get(

                            "method",

                            "GET"

                        ).upper()

                }

            )

        return forms

    def links(
        self,
        response
    ) -> list[str]:
        """
        Extract hyperlinks.
        """

        soup = self.soup(

            response

        )

        urls = []

        for link in soup.find_all(

            "a",

            href=True

        ):

            urls.append(

                link["href"]

            )

        return urls

    def scripts(
        self,
        response
    ) -> list[str]:
        """
        Extract JavaScript files.
        """

        soup = self.soup(

            response

        )

        files = []

        for script in soup.find_all(

            "script",

            src=True

        ):

            files.append(

                script["src"]

            )

        return files

    def images(
        self,
        response
    ) -> list[str]:
        """
        Extract image sources.
        """

        soup = self.soup(

            response

        )

        files = []

        for image in soup.find_all(

            "img",

            src=True

        ):

            files.append(

                image["src"]

            )

        return files

    def html_information(
        self,
        response
    ) -> dict[str, Any]:
        """
        HTML summary.
        """

        return {

            "title":

                self.title(

                    response

                ),

            "meta_tags":

                self.meta_tags(

                    response

                ),

            "forms":

                self.forms(

                    response

                ),

            "links":

                self.links(

                    response

                ),

            "scripts":

                self.scripts(

                    response

                ),

            "images":

                self.images(

                    response

                )

        }
        
        
    def login_forms(
        self,
        response
    ) -> list[dict[str, Any]]:
        """
        Detect login forms.
        """

        soup = self.soup(

            response

        )

        forms = []

        for form in soup.find_all(

            "form"

        ):

            password = form.find(

                "input",

                {

                    "type": "password"

                }

            )

            if password:

                forms.append(

                    {

                        "action":

                            form.get(

                                "action",

                                ""

                            ),

                        "method":

                            form.get(

                                "method",

                                "GET"

                            ).upper()

                    }

                )

        return forms

    def iframes(
        self,
        response
    ) -> list[str]:
        """
        Extract iframe sources.
        """

        soup = self.soup(

            response

        )

        return [

            iframe.get(

                "src",

                ""

            )

            for iframe in soup.find_all(

                "iframe"

            )

        ]

    def hidden_inputs(
        self,
        response
    ) -> int:
        """
        Count hidden input fields.
        """

        soup = self.soup(

            response

        )

        return len(

            soup.find_all(

                "input",

                {

                    "type": "hidden"

                }

            )

        )

    def external_scripts(
        self,
        response
    ) -> list[str]:
        """
        Detect external JavaScript.
        """

        scripts = self.scripts(

            response

        )

        return [

            script

            for script in scripts

            if script.startswith(

                (

                    "http://",

                    "https://",

                    "//"

                )

            )

        ]

    def external_images(
        self,
        response
    ) -> list[str]:
        """
        Detect external images.
        """

        images = self.images(

            response

        )

        return [

            image

            for image in images

            if image.startswith(

                (

                    "http://",

                    "https://",

                    "//"

                )

            )

        ]

    def favicon(
        self,
        response
    ) -> str:
        """
        Detect favicon.
        """

        soup = self.soup(

            response

        )

        icon = soup.find(

            "link",

            rel=lambda value:

                value

                and

                "icon"

                in

                str(

                    value

                ).lower()

        )

        if icon:

            return icon.get(

                "href",

                ""

            )

        return ""

    def html_security(
        self,
        response
    ) -> dict[str, Any]:
        """
        HTML security summary.
        """

        return {

            "login_forms":

                self.login_forms(

                    response

                ),

            "iframe_count":

                len(

                    self.iframes(

                        response

                    )

                ),

            "hidden_inputs":

                self.hidden_inputs(

                    response

                ),

            "external_scripts":

                len(

                    self.external_scripts(

                        response

                    )

                ),

            "external_images":

                len(

                    self.external_images(

                        response

                    )

                ),

            "favicon":

                self.favicon(

                    response

                )

        }
        
        
    def analyze(
        self,
        url: str
    ) -> dict[str, Any]:
        """
        Analyze website.
        """

        try:

            url = self._normalize_url(

                url

            )

            response, response_time = (

                self.connect(

                    url

                )

            )

        except Exception as error:

            logger.exception(

                error

            )

            return self._empty_response(

                url,

                str(

                    error

                )

            )

        report = self._success_response()

        report["url"] = url

        report["response_time"] = response_time

        information = self.website_information(

            response

        )

        report.update(

            information

        )

        report["website"] = {

            **self.html_information(

                response

            ),

            **self.html_security(

                response

            )

        }

        report["url_analysis"] = (

            url_service.analyze(

                url

            )

        )

        report["dns"] = dns_service.analyze(

            url_service.hostname(

                url

            )

        )

        report["whois"] = whois_service.analyze(

            url_service.hostname(

                url

            )

        )

        report["ssl"] = ssl_service.analyze(

            url_service.hostname(

                url

            )

        )

        report["security_headers"] = (

            security_headers_service.analyze(

                url

            )

        )

        report["geo"] = geo_service.analyze(

            url_service.hostname(

                url

            )

        )

        report["reputation"] = (

            reputation_service.analyze(

                report

            )

        )

        logger.info(

            "Website analysis completed."

        )

        return report

    def analyze_batch(
        self,
        urls: list[str]
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple websites.
        """

        return [

            self.analyze(

                url

            )

            for url

            in urls

        ]

    def health_check(
        self
    ) -> dict[str, Any]:
        """
        Service health.
        """

        return {

            "service":

                "Website Service",

            "status":

                "Healthy",

            "version":

                "2.0"

        }

    def __repr__(
        self
    ) -> str:

        return (

            "WebsiteService("

            "Enterprise Version)"

        )


website_service = WebsiteService()