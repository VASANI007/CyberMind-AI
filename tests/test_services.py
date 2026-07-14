"""
CyberMind AI
Services Tests
Enterprise Production Version
"""

from __future__ import annotations

from services.url_service import url_service
from services.website_service import website_service
from services.domain_service import domain_service
from services.email_service import email_service
from services.ip_service import ip_service
from services.file_service import file_service
from services.qr_service import qr_service


def test_url_service():
    """URL service instance."""

    assert url_service is not None


def test_website_service():
    """Website service instance."""

    assert website_service is not None


def test_domain_service():
    """Domain service instance."""

    assert domain_service is not None


def test_email_service():
    """Email service instance."""

    assert email_service is not None


def test_ip_service():
    """IP service instance."""

    assert ip_service is not None


def test_file_service():
    """File service instance."""

    assert file_service is not None


def test_qr_service():
    """QR service instance."""

    assert qr_service is not None


def test_url_service_health():
    """URL service health."""

    health = url_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_website_service_health():
    """Website service health."""

    health = website_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_domain_service_health():
    """Domain service health."""

    health = domain_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_email_service_health():
    """Email service health."""

    health = email_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_ip_service_health():
    """IP service health."""

    health = ip_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_file_service_health():
    """File service health."""

    health = file_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_qr_service_health():
    """QR service health."""

    health = qr_service.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_service_repr():
    """Service string representation."""

    assert "Service" in repr(url_service)
    assert "Service" in repr(website_service)
    assert "Service" in repr(domain_service)
    assert "Service" in repr(email_service)
    assert "Service" in repr(ip_service)
    assert "Service" in repr(file_service)
    assert "Service" in repr(qr_service)


def test_all_services_loaded():
    """All services loaded."""

    services = [
        url_service,
        website_service,
        domain_service,
        email_service,
        ip_service,
        file_service,
        qr_service
    ]

    assert all(service is not None for service in services)


def test_reputation_fallback_and_keys():
    """Test reputation fallback and key compatibility."""
    from services.reputation_service import reputation_service

    # Test GSB 'malicious' key addition
    from services.google_safe_browsing_service import google_safe_browsing_service
    res = google_safe_browsing_service.scan("http://example.com")
    if res.get("success"):
        assert "malicious" in res

    # Test SSL service valid=False fallback
    from services.ssl_service import ssl_service
    ssl_res = ssl_service.analyze("nonexistent-domain-xyz.com")
    assert ssl_res.get("valid") is False

    # Test reputation nested fallback for website report
    test_report = {
        "url_analysis": {
            "features": {
                "contains_ip": True
            },
            "blacklist": {
                "blacklisted": True
            }
        }
    }
    rep_res = reputation_service.analyze(test_report)
    assert rep_res.get("risk_score") > 0
    assert rep_res.get("safe") is False