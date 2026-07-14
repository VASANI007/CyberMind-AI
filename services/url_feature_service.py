"""
CyberMind AI

URL Feature Service

Production Version
"""

from __future__ import annotations

import math
import re
import string
from collections import Counter
from ipaddress import ip_address
from urllib.parse import (
    parse_qs,
    unquote,
    urlparse
)

import pandas as pd

from core.logger import logger

from services.blacklist_service import blacklist_service
from services.dns_service import dns_service
from services.entropy_service import entropy_service
from services.google_safe_browsing_service import (
    google_safe_browsing_service
)
from services.punycode_service import punycode_service
from services.shorturl_service import shorturl_service
from services.ssl_service import ssl_service
from services.tld_service import tld_service
from services.virustotal_service import virustotal_service
from services.whois_service import whois_service


class URLFeatureService:
    """
    Production URL Feature Extraction Engine.

    This class extracts machine-learning features
    from URLs for phishing detection.

    Designed for:

    • ML Models
    • Rule Engine
    • Reputation Engine
    • Reports
    """

    SUSPICIOUS_KEYWORDS = {

        "login",
        "signin",
        "verify",
        "verification",
        "secure",
        "account",
        "update",
        "password",
        "bank",
        "paypal",
        "wallet",
        "crypto",
        "gift",
        "bonus",
        "reward",
        "invoice",
        "confirm",
        "authentication",
        "admin",
        "security",
        "support",
        "office365",
        "microsoft",
        "apple",
        "google",
        "facebook"

    }

    SUSPICIOUS_EXTENSIONS = {

        ".exe",
        ".zip",
        ".rar",
        ".7z",
        ".apk",
        ".bat",
        ".cmd",
        ".scr",
        ".jar",
        ".dll",
        ".ps1"

    }

    SPECIAL_CHARACTERS = {

        "-",
        "_",
        "@",
        "?",
        "=",
        "&",
        "%",
        ".",
        "/",
        "#",
        ":",
        ";",
        "~",
        "+",
        ",",
        "$",
        "!",
        "*"

    }

    SAFE_PORTS = {

        80,
        443

    }

    DEFAULT_TIMEOUT = 5

    def __init__(self):

        logger.info(
            "URL Feature Service Initialized."
        )

    # ---------------------------------------------------

    def normalize_url(
        self,
        url: str
    ) -> str:
        """
        Normalize URL.
        """

        url = url.strip()

        if not url.startswith(

            (
                "http://",
                "https://"
            )

        ):

            url = "https://" + url

        return url

    # ---------------------------------------------------

    def parse_url(
        self,
        url: str
    ):
        """
        Parse URL.
        """

        return urlparse(

            self.normalize_url(url)

        )

    # ---------------------------------------------------

    def hostname(
        self,
        url: str
    ) -> str:

        return (

            self.parse_url(url).hostname

            or ""

        ).lower()

    # ---------------------------------------------------

    def path(
        self,
        url: str
    ) -> str:

        return self.parse_url(

            url

        ).path

    # ---------------------------------------------------

    def query(
        self,
        url: str
    ) -> str:

        return self.parse_url(

            url

        ).query

    # ---------------------------------------------------

    def fragment(
        self,
        url: str
    ) -> str:

        return self.parse_url(

            url

        ).fragment

    # ---------------------------------------------------

    def scheme(
        self,
        url: str
    ) -> str:

        return self.parse_url(

            url

        ).scheme

    # ---------------------------------------------------

    def port(
        self,
        url: str
    ):

        return self.parse_url(

            url

        ).port
        
    def url_length(
        self,
        url: str
    ) -> int:
        """
        Return total URL length.
        """

        return len(url)

    # ---------------------------------------------------

    def hostname_length(
        self,
        url: str
    ) -> int:
        """
        Return hostname length.
        """

        return len(
            self.hostname(url)
        )

    # ---------------------------------------------------

    def path_length(
        self,
        url: str
    ) -> int:
        """
        Return path length.
        """

        return len(
            self.path(url)
        )

    # ---------------------------------------------------

    def query_length(
        self,
        url: str
    ) -> int:
        """
        Return query string length.
        """

        return len(
            self.query(url)
        )

    # ---------------------------------------------------

    def fragment_length(
        self,
        url: str
    ) -> int:
        """
        Return fragment length.
        """

        return len(
            self.fragment(url)
        )

    # ---------------------------------------------------

    def domain_length(
        self,
        url: str
    ) -> int:
        """
        Alias for hostname length.
        """

        return self.hostname_length(
            url
        )

    # ---------------------------------------------------

    def url_depth(
        self,
        url: str
    ) -> int:
        """
        Count path depth.
        """

        path = self.path(url)

        return len(

            [

                part

                for part in path.split("/")

                if part

            ]

        )

    # ---------------------------------------------------

    def directory_count(
        self,
        url: str
    ) -> int:
        """
        Return directory count.
        """

        return self.url_depth(
            url
        )

    # ---------------------------------------------------

    def filename(
        self,
        url: str
    ) -> str:
        """
        Return filename.
        """

        path = self.path(url)

        if "/" not in path:

            return ""

        return path.split("/")[-1]

    # ---------------------------------------------------

    def extension(
        self,
        url: str
    ) -> str:
        """
        Return file extension.
        """

        filename = self.filename(
            url
        )

        if "." not in filename:

            return ""

        return "." + filename.split(".")[-1].lower()

    # ---------------------------------------------------

    def parameter_count(
        self,
        url: str
    ) -> int:
        """
        Number of query parameters.
        """

        return len(

            parse_qs(

                self.query(url)

            )

        )

    # ---------------------------------------------------

    def query_parameters(
        self,
        url: str
    ) -> dict:
        """
        Return parsed query parameters.
        """

        return parse_qs(

            self.query(url)

        )

    # ---------------------------------------------------

    def token_count(
        self,
        url: str
    ) -> int:
        """
        Count URL tokens.
        """

        tokens = re.split(

            r"[/:?&=._\-#]+",

            url

        )

        return len(

            [

                token

                for token in tokens

                if token

            ]

        )

    # ---------------------------------------------------

    def tokens(
        self,
        url: str
    ) -> list[str]:
        """
        Return URL tokens.
        """

        return [

            token

            for token in re.split(

                r"[/:?&=._\-#]+",

                url

            )

            if token

        ]

    # ---------------------------------------------------

    def longest_token(
        self,
        url: str
    ) -> int:
        """
        Length of longest token.
        """

        tokens = self.tokens(url)

        if not tokens:

            return 0

        return max(

            len(token)

            for token in tokens

        )

    # ---------------------------------------------------

    def average_token_length(
        self,
        url: str
    ) -> float:
        """
        Average token length.
        """

        tokens = self.tokens(url)

        if not tokens:

            return 0.0

        return round(

            sum(

                len(token)

                for token in tokens

            )

            /

            len(tokens),

            2

        )

    # ---------------------------------------------------

    def decoded_url(
        self,
        url: str
    ) -> str:
        """
        URL decoded text.
        """

        return unquote(
            url
        )

    # ---------------------------------------------------

    def encoded_character_count(
        self,
        url: str
    ) -> int:
        """
        Count URL encoded characters.
        """

        return len(

            re.findall(

                r"%[0-9A-Fa-f]{2}",

                url

            )

        )
        
    def uppercase_count(
        self,
        url: str
    ) -> int:
        """
        Count uppercase letters.
        """

        return sum(

            character.isupper()

            for character in url

        )

    def lowercase_count(
        self,
        url: str
    ) -> int:
        """
        Count lowercase letters.
        """

        return sum(

            character.islower()

            for character in url

        )

    def digit_count(
        self,
        url: str
    ) -> int:
        """
        Count digits.
        """

        return sum(

            character.isdigit()

            for character in url

        )

    def letter_count(
        self,
        url: str
    ) -> int:
        """
        Count alphabetic characters.
        """

        return sum(

            character.isalpha()

            for character in url

        )

    def special_character_count(
        self,
        url: str
    ) -> int:
        """
        Count special characters.
        """

        return sum(

            character in self.SPECIAL_CHARACTERS

            for character in url

        )

    def dot_count(
        self,
        url: str
    ) -> int:

        return url.count(".")

    def dash_count(
        self,
        url: str
    ) -> int:

        return url.count("-")

    def underscore_count(
        self,
        url: str
    ) -> int:

        return url.count("_")

    def slash_count(
        self,
        url: str
    ) -> int:

        return url.count("/")

    def colon_count(
        self,
        url: str
    ) -> int:

        return url.count(":")

    def semicolon_count(
        self,
        url: str
    ) -> int:

        return url.count(";")

    def equal_count(
        self,
        url: str
    ) -> int:

        return url.count("=")

    def ampersand_count(
        self,
        url: str
    ) -> int:

        return url.count("&")

    def at_count(
        self,
        url: str
    ) -> int:

        return url.count("@")

    def question_count(
        self,
        url: str
    ) -> int:

        return url.count("?")

    def hash_count(
        self,
        url: str
    ) -> int:

        return url.count("#")

    def percent_count(
        self,
        url: str
    ) -> int:

        return url.count("%")

    def plus_count(
        self,
        url: str
    ) -> int:

        return url.count("+")

    def comma_count(
        self,
        url: str
    ) -> int:

        return url.count(",")

    def exclamation_count(
        self,
        url: str
    ) -> int:

        return url.count("!")

    def ratio(
        self,
        value: int,
        total: int
    ) -> float:
        """
        Calculate ratio.
        """

        if total == 0:

            return 0.0

        return round(

            value / total,

            4

        )

    def digit_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.digit_count(url),

            len(url)

        )

    def letter_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.letter_count(url),

            len(url)

        )

    def uppercase_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.uppercase_count(url),

            len(url)

        )

    def lowercase_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.lowercase_count(url),

            len(url)

        )

    def special_character_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.special_character_count(url),

            len(url)

        )

    def repeated_character_count(
        self,
        url: str
    ) -> int:
        """
        Count repeated consecutive characters.
        """

        total = 0

        previous = ""

        for character in url:

            if character == previous:

                total += 1

            previous = character

        return total

    def unique_character_count(
        self,
        url: str
    ) -> int:
        """
        Count unique characters.
        """

        return len(

            set(url)

        )

    def character_diversity(
        self,
        url: str
    ) -> float:
        """
        Ratio of unique characters.
        """

        return self.ratio(

            self.unique_character_count(url),

            len(url)

        )

    def shannon_entropy(
        self,
        text: str
    ) -> float:
        """
        Calculate Shannon entropy.
        """

        if not text:

            return 0.0

        counts = Counter(text)

        entropy = 0.0

        length = len(text)

        for count in counts.values():

            probability = count / length

            entropy -= (

                probability *

                math.log2(

                    probability

                )

            )

        return round(

            entropy,

            4

        )

    def url_entropy(
        self,
        url: str
    ) -> float:

        return self.shannon_entropy(

            url

        )

    def hostname_entropy(
        self,
        url: str
    ) -> float:

        return self.shannon_entropy(

            self.hostname(url)

        )

    def path_entropy(
        self,
        url: str
    ) -> float:

        return self.shannon_entropy(

            self.path(url)

        )
    
    def contains_ip(
        self,
        url: str
    ) -> bool:
        """
        Check whether hostname is an IP address.
        """

        try:

            ip_address(

                self.hostname(url)

            )

            return True

        except ValueError:

            return False

    def is_https(
        self,
        url: str
    ) -> bool:
        """
        Check HTTPS.
        """

        return (

            self.scheme(url)

            ==

            "https"

        )

    def has_port(
        self,
        url: str
    ) -> bool:
        """
        Check custom port.
        """

        return self.port(url) is not None

    def is_default_port(
        self,
        url: str
    ) -> bool:
        """
        Check default HTTP/HTTPS port.
        """

        port = self.port(url)

        if port is None:

            return True

        return port in self.SAFE_PORTS

    def contains_punycode(
        self,
        url: str
    ) -> bool:
        """
        Check Punycode.
        """

        return punycode_service.is_punycode(

            self.hostname(url)

        )

    def contains_unicode(
        self,
        url: str
    ) -> bool:
        """
        Check Unicode hostname.
        """

        return punycode_service.contains_unicode(

            self.hostname(url)

        )

    def valid_tld(
        self,
        url: str
    ) -> bool:
        """
        Check TLD validity.
        """

        return tld_service.is_valid_tld(

            self.hostname(url)

        )

    def short_url(
        self,
        url: str
    ) -> bool:
        """
        Check URL shortener.
        """

        return shorturl_service.is_short_url(

            url

        )

    def suspicious_extension(
        self,
        url: str
    ) -> bool:
        """
        Check dangerous extension.
        """

        extension = self.extension(url)

        return (

            extension

            in

            self.SUSPICIOUS_EXTENSIONS

        )

    def keyword_count(
        self,
        url: str
    ) -> int:
        """
        Count suspicious keywords.
        """

        text = url.lower()

        return sum(

            keyword in text

            for keyword in self.SUSPICIOUS_KEYWORDS

        )

    def contains_keyword(
        self,
        url: str,
        keyword: str
    ) -> bool:
        """
        Check keyword.
        """

        return (

            keyword.lower()

            in

            url.lower()

        )

    def detected_keywords(
        self,
        url: str
    ) -> list[str]:
        """
        Return matched keywords.
        """

        text = url.lower()

        return [

            keyword

            for keyword

            in

            self.SUSPICIOUS_KEYWORDS

            if keyword in text

        ]

    def multiple_slashes(
        self,
        url: str
    ) -> bool:
        """
        Detect multiple slashes.
        """

        path = self.path(url)

        return "//" in path

    def multiple_dots(
        self,
        url: str
    ) -> bool:
        """
        Detect multiple dots.
        """

        return ".." in url

    def contains_hex_encoding(
        self,
        url: str
    ) -> bool:
        """
        Detect hexadecimal encoding.
        """

        return bool(

            re.search(

                r"%[0-9A-Fa-f]{2}",

                url

            )

        )

    def contains_base64(
        self,
        url: str
    ) -> bool:
        """
        Detect Base64-like strings.
        """

        pattern = (

            r"(?:[A-Za-z0-9+/]{20,}"

            r"={0,2})"

        )

        return bool(

            re.search(

                pattern,

                url

            )

        )

    def blacklist_detected(
        self,
        url: str
    ) -> bool:
        """
        Offline blacklist.
        """

        return blacklist_service.is_blacklisted(

            url

        )

    def ssl_available(
        self,
        url: str
    ) -> bool:
        """
        SSL available.
        """

        try:

            return ssl_service.is_valid(

                self.hostname(url)

            )

        except Exception:

            return False

    def dns_available(
        self,
        url: str
    ) -> bool:
        """
        DNS exists.
        """

        try:

            return bool(

                dns_service.a(

                    self.hostname(url)

                )

            )

        except Exception:

            return False

    def domain_exists(
        self,
        url: str
    ) -> bool:
        """
        WHOIS check.
        """

        try:

            return whois_service.exists(

                self.hostname(url)

            )

        except Exception:

            return False
        
    def subdomain_count(
        self,
        url: str
    ) -> int:
        """
        Count subdomains.
        """

        host = self.hostname(url)

        if not host:

            return 0

        parts = host.split(".")

        if len(parts) <= 2:

            return 0

        return len(parts) - 2

    # ---------------------------------------------------

    def host_token_count(
        self,
        url: str
    ) -> int:
        """
        Count hostname tokens.
        """

        host = self.hostname(url)

        tokens = re.split(

            r"[\.-]",

            host

        )

        return len(

            [

                token

                for token in tokens

                if token

            ]

        )

    # ---------------------------------------------------

    def longest_host_token(
        self,
        url: str
    ) -> int:
        """
        Longest hostname token.
        """

        host = self.hostname(url)

        tokens = [

            token

            for token

            in

            re.split(

                r"[\.-]",

                host

            )

            if token

        ]

        if not tokens:

            return 0

        return max(

            len(token)

            for token in tokens

        )

    # ---------------------------------------------------

    def average_host_token_length(
        self,
        url: str
    ) -> float:
        """
        Average hostname token length.
        """

        host = self.hostname(url)

        tokens = [

            token

            for token

            in

            re.split(

                r"[\.-]",

                host

            )

            if token

        ]

        if not tokens:

            return 0.0

        return round(

            sum(

                len(token)

                for token in tokens

            )

            /

            len(tokens),

            2

        )

    # ---------------------------------------------------

    def path_segment_count(
        self,
        url: str
    ) -> int:
        """
        Count path segments.
        """

        segments = [

            part

            for part

            in

            self.path(url).split("/")

            if part

        ]

        return len(

            segments

        )

    # ---------------------------------------------------

    def longest_path_segment(
        self,
        url: str
    ) -> int:
        """
        Longest path segment.
        """

        segments = [

            part

            for part

            in

            self.path(url).split("/")

            if part

        ]

        if not segments:

            return 0

        return max(

            len(segment)

            for segment in segments

        )

    # ---------------------------------------------------

    def average_path_segment_length(
        self,
        url: str
    ) -> float:
        """
        Average path segment length.
        """

        segments = [

            part

            for part

            in

            self.path(url).split("/")

            if part

        ]

        if not segments:

            return 0.0

        return round(

            sum(

                len(segment)

                for segment in segments

            )

            /

            len(segments),

            2

        )

    # ---------------------------------------------------

    def empty_query(
        self,
        url: str
    ) -> bool:
        """
        Query exists but empty.
        """

        parsed = self.parse_url(url)

        return (

            "?"

            in

            url

            and

            parsed.query == ""

        )

    # ---------------------------------------------------

    def fragment_exists(
        self,
        url: str
    ) -> bool:
        """
        Check fragment.
        """

        return bool(

            self.fragment(url)

        )

    # ---------------------------------------------------

    def suspicious_path(
        self,
        url: str
    ) -> bool:
        """
        Suspicious path keywords.
        """

        path = self.path(

            url

        ).lower()

        keywords = {

            "login",

            "verify",

            "secure",

            "signin",

            "admin",

            "password",

            "confirm",

            "auth"

        }

        return any(

            keyword in path

            for keyword in keywords

        )

    # ---------------------------------------------------

    def suspicious_filename(
        self,
        url: str
    ) -> bool:
        """
        Suspicious filename.
        """

        filename = self.filename(

            url

        ).lower()

        return any(

            keyword

            in

            filename

            for keyword in self.SUSPICIOUS_KEYWORDS

        )

    # ---------------------------------------------------

    def suspicious_parameter_names(
        self,
        url: str
    ) -> int:
        """
        Count suspicious query parameter names.
        """

        parameters = self.query_parameters(

            url

        )

        keywords = {

            "token",

            "session",

            "password",

            "auth",

            "redirect",

            "continue",

            "next",

            "login",

            "email"

        }

        total = 0

        for key in parameters:

            if key.lower() in keywords:

                total += 1

        return total

    # ---------------------------------------------------

    def parameter_value_count(
        self,
        url: str
    ) -> int:
        """
        Total query values.
        """

        parameters = self.query_parameters(

            url

        )

        total = 0

        for values in parameters.values():

            total += len(values)

        return total

    # ---------------------------------------------------

    def longest_parameter_value(
        self,
        url: str
    ) -> int:
        """
        Longest parameter value.
        """

        parameters = self.query_parameters(

            url

        )

        longest = 0

        for values in parameters.values():

            for value in values:

                longest = max(

                    longest,

                    len(value)

                )

        return longest

    # ---------------------------------------------------

    def parameter_entropy(
        self,
        url: str
    ) -> float:
        """
        Query entropy.
        """

        return self.shannon_entropy(

            self.query(url)

        )
    
    
    
    def repeated_token_count(
        self,
        url: str
    ) -> int:
        """
        Count repeated URL tokens.
        """

        tokens = [

            token.lower()

            for token in self.tokens(url)

        ]

        counter = Counter(tokens)

        return sum(

            count - 1

            for count in counter.values()

            if count > 1

        )

    # ---------------------------------------------------

    def lexical_diversity(
        self,
        url: str
    ) -> float:
        """
        Lexical diversity score.
        """

        tokens = [

            token.lower()

            for token in self.tokens(url)

        ]

        if not tokens:

            return 0.0

        return round(

            len(set(tokens))

            /

            len(tokens),

            4

        )

    # ---------------------------------------------------

    def vowel_count(
        self,
        url: str
    ) -> int:
        """
        Count vowels.
        """

        vowels = "aeiou"

        return sum(

            character.lower() in vowels

            for character in url

        )

    # ---------------------------------------------------

    def consonant_count(
        self,
        url: str
    ) -> int:
        """
        Count consonants.
        """

        vowels = "aeiou"

        return sum(

            character.isalpha()

            and

            character.lower() not in vowels

            for character in url

        )

    # ---------------------------------------------------

    def vowel_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.vowel_count(url),

            self.letter_count(url)

        )

    # ---------------------------------------------------

    def consonant_ratio(
        self,
        url: str
    ) -> float:

        return self.ratio(

            self.consonant_count(url),

            self.letter_count(url)

        )

    # ---------------------------------------------------

    def longest_digit_sequence(
        self,
        url: str
    ) -> int:
        """
        Longest numeric sequence.
        """

        matches = re.findall(

            r"\d+",

            url

        )

        if not matches:

            return 0

        return max(

            len(match)

            for match in matches

        )

    # ---------------------------------------------------

    def longest_letter_sequence(
        self,
        url: str
    ) -> int:
        """
        Longest alphabetic sequence.
        """

        matches = re.findall(

            r"[A-Za-z]+",

            url

        )

        if not matches:

            return 0

        return max(

            len(match)

            for match in matches

        )

    # ---------------------------------------------------

    def consecutive_special_characters(
        self,
        url: str
    ) -> int:
        """
        Longest special-character sequence.
        """

        matches = re.findall(

            r"[^A-Za-z0-9]+",

            url

        )

        if not matches:

            return 0

        return max(

            len(match)

            for match in matches

        )

    # ---------------------------------------------------

    def repeated_character_ratio(
        self,
        url: str
    ) -> float:
        """
        Ratio of repeated characters.
        """

        return self.ratio(

            self.repeated_character_count(url),

            len(url)

        )

    # ---------------------------------------------------

    def starts_with_digit(
        self,
        url: str
    ) -> bool:

        host = self.hostname(url)

        if not host:

            return False

        return host[0].isdigit()

    # ---------------------------------------------------

    def ends_with_digit(
        self,
        url: str
    ) -> bool:

        host = self.hostname(url)

        if not host:

            return False

        return host[-1].isdigit()

    # ---------------------------------------------------

    def contains_brand_name(
        self,
        url: str
    ) -> bool:
        """
        Detect common brands.
        """

        brands = {

            "google",

            "microsoft",

            "paypal",

            "amazon",

            "facebook",

            "instagram",

            "apple",

            "netflix",

            "dropbox",

            "github",

            "linkedin",

            "twitter",

            "whatsapp",

            "telegram",

            "adobe",

            "office365"

        }

        text = url.lower()

        return any(

            brand in text

            for brand in brands

        )

    # ---------------------------------------------------

    def brand_count(
        self,
        url: str
    ) -> int:
        """
        Count detected brands.
        """

        brands = {

            "google",

            "microsoft",

            "paypal",

            "amazon",

            "facebook",

            "instagram",

            "apple",

            "netflix",

            "dropbox",

            "github",

            "linkedin",

            "twitter",

            "whatsapp",

            "telegram",

            "adobe",

            "office365"

        }

        text = url.lower()

        return sum(

            brand in text

            for brand in brands

        )

    # ---------------------------------------------------

    def impersonation_score(
        self,
        url: str
    ) -> int:
        """
        Brand impersonation score.
        """

        score = 0

        if self.contains_brand_name(url):

            score += 25

        if self.contains_punycode(url):

            score += 25

        if self.short_url(url):

            score += 15

        if self.keyword_count(url) > 0:

            score += 15

        if self.contains_ip(url):

            score += 20

        return min(

            score,

            100

        )

    # ---------------------------------------------------

    def lexical_complexity(
        self,
        url: str
    ) -> float:
        """
        Overall lexical complexity.
        """

        score = (

            self.url_entropy(url)

            +

            self.character_diversity(url)

            +

            self.lexical_diversity(url)

        )

        return round(

            score,

            4

        )
        
    FEATURE_COLUMNS = [

        "url_length",
        "hostname_length",
        "domain_length",
        "path_length",
        "query_length",
        "fragment_length",

        "url_depth",
        "directory_count",

        "token_count",
        "longest_token",
        "average_token_length",

        "digit_count",
        "letter_count",
        "uppercase_count",
        "lowercase_count",

        "special_character_count",

        "dot_count",
        "dash_count",
        "underscore_count",
        "slash_count",
        "colon_count",
        "semicolon_count",
        "equal_count",
        "ampersand_count",
        "at_count",
        "question_count",
        "hash_count",
        "percent_count",
        "plus_count",
        "comma_count",
        "exclamation_count",

        "digit_ratio",
        "letter_ratio",
        "uppercase_ratio",
        "lowercase_ratio",
        "special_character_ratio",

        "unique_character_count",
        "character_diversity",

        "url_entropy",
        "hostname_entropy",
        "path_entropy",

        "contains_ip",
        "https",

        "contains_punycode",
        "contains_unicode",

        "valid_tld",

        "short_url",

        "subdomain_count",

        "host_token_count",
        "longest_host_token",
        "average_host_token_length",

        "path_segment_count",
        "longest_path_segment",
        "average_path_segment_length",

        "keyword_count",

        "contains_brand_name",

        "brand_count",

        "impersonation_score",

        "lexical_diversity",

        "lexical_complexity",

        "parameter_count",

        "parameter_value_count",

        "longest_parameter_value",

        "parameter_entropy",

        "repeated_character_count",

        "repeated_character_ratio",

        "repeated_token_count"

    ]

    def feature_names(
        self
    ) -> list[str]:
        """
        Return ordered feature names.
        """

        return self.FEATURE_COLUMNS.copy()

    def feature_count(
        self
    ) -> int:
        """
        Number of ML features.
        """

        return len(

            self.FEATURE_COLUMNS

        )
        
        
    def extract_features(
        self,
        url: str
    ) -> dict:
        """
        Extract all ML features.
        """

        url = self.normalize_url(url)

        features = {

            "url_length":
                self.url_length(url),

            "hostname_length":
                self.hostname_length(url),

            "domain_length":
                self.domain_length(url),

            "path_length":
                self.path_length(url),

            "query_length":
                self.query_length(url),

            "fragment_length":
                self.fragment_length(url),

            "url_depth":
                self.url_depth(url),

            "directory_count":
                self.directory_count(url),

            "token_count":
                self.token_count(url),

            "longest_token":
                self.longest_token(url),

            "average_token_length":
                self.average_token_length(url),

            "digit_count":
                self.digit_count(url),

            "letter_count":
                self.letter_count(url),

            "uppercase_count":
                self.uppercase_count(url),

            "lowercase_count":
                self.lowercase_count(url),

            "special_character_count":
                self.special_character_count(url),

            "dot_count":
                self.dot_count(url),

            "dash_count":
                self.dash_count(url),

            "underscore_count":
                self.underscore_count(url),

            "slash_count":
                self.slash_count(url),

            "colon_count":
                self.colon_count(url),

            "semicolon_count":
                self.semicolon_count(url),

            "equal_count":
                self.equal_count(url),

            "ampersand_count":
                self.ampersand_count(url),

            "at_count":
                self.at_count(url),

            "question_count":
                self.question_count(url),

            "hash_count":
                self.hash_count(url),

            "percent_count":
                self.percent_count(url),

            "plus_count":
                self.plus_count(url),

            "comma_count":
                self.comma_count(url),

            "exclamation_count":
                self.exclamation_count(url),

            "digit_ratio":
                self.digit_ratio(url),

            "letter_ratio":
                self.letter_ratio(url),

            "uppercase_ratio":
                self.uppercase_ratio(url),

            "lowercase_ratio":
                self.lowercase_ratio(url),

            "special_character_ratio":
                self.special_character_ratio(url),

            "unique_character_count":
                self.unique_character_count(url),

            "character_diversity":
                self.character_diversity(url),

            "url_entropy":
                self.url_entropy(url),

            "hostname_entropy":
                self.hostname_entropy(url),

            "path_entropy":
                self.path_entropy(url),

            "contains_ip":
                int(self.contains_ip(url)),

            "https":
                int(self.is_https(url)),

            "contains_punycode":
                int(self.contains_punycode(url)),

            "contains_unicode":
                int(self.contains_unicode(url)),

            "valid_tld":
                int(self.valid_tld(url)),

            "short_url":
                int(self.short_url(url)),

            "subdomain_count":
                self.subdomain_count(url),

            "host_token_count":
                self.host_token_count(url),

            "longest_host_token":
                self.longest_host_token(url),

            "average_host_token_length":
                self.average_host_token_length(url),

            "path_segment_count":
                self.path_segment_count(url),

            "longest_path_segment":
                self.longest_path_segment(url),

            "average_path_segment_length":
                self.average_path_segment_length(url),

            "keyword_count":
                self.keyword_count(url),

            "contains_brand_name":
                int(self.contains_brand_name(url)),

            "brand_count":
                self.brand_count(url),

            "impersonation_score":
                self.impersonation_score(url),

            "lexical_diversity":
                self.lexical_diversity(url),

            "lexical_complexity":
                self.lexical_complexity(url),

            "parameter_count":
                self.parameter_count(url),

            "parameter_value_count":
                self.parameter_value_count(url),

            "longest_parameter_value":
                self.longest_parameter_value(url),

            "parameter_entropy":
                self.parameter_entropy(url),

            "repeated_character_count":
                self.repeated_character_count(url),

            "repeated_character_ratio":
                self.repeated_character_ratio(url),

            "repeated_token_count":
                self.repeated_token_count(url)

        }

        return features


url_feature_service = URLFeatureService()