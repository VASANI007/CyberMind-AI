"""
Application Constants
"""

# App Information
APP_NAME = "CyberMind AI"
APP_VERSION = "1.0.0"

# Risk Levels
SAFE = "Safe"
LOW = "Low Risk"
MEDIUM = "Medium Risk"
HIGH = "High Risk"
CRITICAL = "Critical"

# Risk Score Range
SAFE_SCORE = (0, 20)
LOW_SCORE = (21, 40)
MEDIUM_SCORE = (41, 60)
HIGH_SCORE = (61, 80)
CRITICAL_SCORE = (81, 100)

# Supported File Types
SUPPORTED_FILE_TYPES = [
    "pdf",
    "docx",
    "txt",
    "csv",
    "json",
    "zip",
    "exe",
    "apk"
]

# Export Formats
EXPORT_FORMATS = [
    "PDF",
    "Excel",
    "Word",
    "CSV",
    "JSON"
]

# Scan Types
SCAN_TYPES = [
    "URL",
    "Website",
    "Domain",
    "Email",
    "IP Address",
    "QR Code",
    "File"
]


class Constants:
    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION
    SAFE = SAFE
    LOW = LOW
    MEDIUM = MEDIUM
    HIGH = HIGH
    CRITICAL = CRITICAL
    SAFE_SCORE = SAFE_SCORE
    LOW_SCORE = LOW_SCORE
    MEDIUM_SCORE = MEDIUM_SCORE
    HIGH_SCORE = HIGH_SCORE
    CRITICAL_SCORE = CRITICAL_SCORE
    SUPPORTED_FILE_TYPES = SUPPORTED_FILE_TYPES
    EXPORT_FORMATS = EXPORT_FORMATS
    SCAN_TYPES = SCAN_TYPES