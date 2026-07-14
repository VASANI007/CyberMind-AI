"""
===========================================================
CyberMind AI
Global Constants
===========================================================
"""

from enum import Enum


# Application


APP_NAME = "CyberMind AI"

APP_VERSION = "1.0.0"

DEFAULT_LANGUAGE = "English"

DEFAULT_THEME = "Dark"

DEFAULT_ENCODING = "utf-8"


# Scan Types



class ScanType(Enum):

    URL = "URL"

    WEBSITE = "Website"

    DOMAIN = "Domain"

    EMAIL = "Email"

    IP = "IP"

    FILE = "File"

    QR = "QR"



# Risk Levels



class RiskLevel(Enum):

    SAFE = "Safe"

    LOW = "Low"

    MEDIUM = "Medium"

    HIGH = "High"

    CRITICAL = "Critical"



# Scan Status



class ScanStatus(Enum):

    PENDING = "Pending"

    RUNNING = "Running"

    COMPLETED = "Completed"

    FAILED = "Failed"



# Report Formats



class ReportFormat(Enum):

    PDF = "pdf"

    WORD = "docx"

    EXCEL = "xlsx"

    JSON = "json"

    CSV = "csv"



# Supported File Types


SUPPORTED_FILE_EXTENSIONS = {

    ".exe",

    ".dll",

    ".bat",

    ".cmd",

    ".ps1",

    ".vbs",

    ".jar",

    ".apk",

    ".zip",

    ".rar",

    ".7z",

    ".pdf",

    ".doc",

    ".docx",

    ".xls",

    ".xlsx",

    ".ppt",

    ".pptx",

    ".csv",

    ".json",

    ".xml",

    ".txt",

    ".png",

    ".jpg",

    ".jpeg",

    ".gif",

    ".bmp",

    ".mp3",

    ".wav",

    ".mp4",

    ".avi"

}


# Dangerous Extensions


DANGEROUS_EXTENSIONS = {

    ".exe",

    ".dll",

    ".bat",

    ".cmd",

    ".vbs",

    ".ps1",

    ".scr",

    ".com",

    ".jar",

    ".msi"

}


# Safe Extensions


SAFE_EXTENSIONS = {

    ".pdf",

    ".docx",

    ".xlsx",

    ".pptx",

    ".png",

    ".jpg",

    ".jpeg",

    ".gif",

    ".csv",

    ".txt",

    ".json",

    ".xml"

}


# Hash Algorithms


HASH_TYPES = (

    "MD5",

    "SHA1",

    "SHA256"

)


# URL Shorteners


URL_SHORTENERS = {

    "bit.ly",

    "tinyurl.com",

    "t.co",

    "goo.gl",

    "ow.ly",

    "buff.ly",

    "rebrand.ly",

    "is.gd",

    "cutt.ly",

    "shorturl.at"

}


# Disposable Email Providers


DISPOSABLE_EMAIL_KEYWORDS = {

    "10min",

    "temp",

    "mailinator",

    "guerrilla",

    "trash",

    "fake"

}


# DNS Record Types


DNS_RECORD_TYPES = (

    "A",

    "AAAA",

    "MX",

    "TXT",

    "NS",

    "CNAME",

    "PTR",

    "SOA",

    "CAA",

    "SRV"

)


# HTTP Methods


HTTP_METHODS = (

    "GET",

    "POST",

    "PUT",

    "DELETE",

    "PATCH",

    "HEAD",

    "OPTIONS"

)


# Security Headers


SECURITY_HEADERS = (

    "Content-Security-Policy",

    "Strict-Transport-Security",

    "X-Frame-Options",

    "X-Content-Type-Options",

    "Referrer-Policy",

    "Permissions-Policy"

)


# SSL/TLS


SUPPORTED_TLS = (

    "TLS 1.2",

    "TLS 1.3"

)

DEPRECATED_TLS = (

    "SSL 2.0",

    "SSL 3.0",

    "TLS 1.0",

    "TLS 1.1"

)


# QR Types


QR_TYPES = (

    "URL",

    "WiFi",

    "UPI",

    "Email",

    "Phone",

    "SMS",

    "Contact",

    "Location"

)


# API Timeout


API_TIMEOUT = 30

API_RETRY = 3


# Scan Limits


MAX_URL_LENGTH = 2048

MAX_DOMAIN_LENGTH = 253

MAX_EMAIL_LENGTH = 320

MAX_FILE_SIZE_MB = 100


# Risk Score


SAFE_SCORE = 0

LOW_SCORE = 25

MEDIUM_SCORE = 50

HIGH_SCORE = 75

CRITICAL_SCORE = 100


# Logging


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

LOG_LEVEL = "INFO"


# Cache


CACHE_EXPIRY = 3600


# Date Time


DATE_FORMAT = "%Y-%m-%d"

TIME_FORMAT = "%H:%M:%S"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"