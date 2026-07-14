"""
CyberMind AI

Custom Exceptions
"""


class CyberMindError(Exception):
    """
    Base Exception
    """

    pass


class ValidationError(CyberMindError):
    """
    Validation Error
    """

    pass


class DatabaseError(CyberMindError):
    """
    Database Error
    """

    pass


class APIError(CyberMindError):
    """
    API Error
    """

    pass


class DatasetError(CyberMindError):
    """
    Dataset Error
    """

    pass


class ConfigurationError(CyberMindError):
    """
    Configuration Error
    """

    pass


class FileError(CyberMindError):
    """
    File Error
    """

    pass


class ScanError(CyberMindError):
    """
    Scan Error
    """

    pass


class URLScanError(ScanError):
    """
    URL Scan Error
    """

    pass


class WebsiteScanError(ScanError):
    """
    Website Scan Error
    """

    pass


class DomainScanError(ScanError):
    """
    Domain Scan Error
    """

    pass


class EmailScanError(ScanError):
    """
    Email Scan Error
    """

    pass


class IPScanError(ScanError):
    """
    IP Scan Error
    """

    pass


class QRScanError(ScanError):
    """
    QR Scan Error
    """

    pass


class FileScanError(ScanError):
    """
    File Scan Error
    """

    pass


class AuthenticationError(CyberMindError):
    """
    Authentication Error
    """

    pass


class PermissionDeniedError(CyberMindError):
    """
    Permission Denied Error
    """

    pass


class CacheError(CyberMindError):
    """
    Cache Error
    """

    pass


class ReportError(CyberMindError):
    """
    Report Error
    """

    pass


class ModelError(CyberMindError):
    """
    Machine Learning Model Error
    """

    pass