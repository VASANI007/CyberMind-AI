"""
CyberMind AI - FastAPI Backend Test Suite
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Healthy"
    assert data["app"] == "CyberMind AI"
    assert "version" in data


def test_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "threats_detected" in data
    assert "critical_count" in data
    assert "scanners_distribution" in data


def test_analytics_geo():
    response = client.get("/api/analytics/geo")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_history_endpoint():
    response = client.get("/api/history?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_settings_endpoint():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "preferences" in data
    assert "api_services" in data
    # Ensure sensitive credentials are never leaked
    for key, info in data["api_services"].items():
        assert "masked" in info
        masked_val = info["masked"]
        # Masked value should never be full raw key if longer than 8 chars
        if len(masked_val) > 8:
            assert "..." in masked_val


def test_ai_chat_endpoint():
    response = client.post(
        "/api/ai/chat",
        json={
            "messages": [
                {"role": "user", "content": "How do I recognize a phishing email?"}
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10


def test_ai_explain_endpoint():
    response = client.post(
        "/api/ai/explain",
        json={
            "scan_result": {
                "target": "example.com",
                "scanner": "URL Scanner",
                "risk_score": 15.0,
                "risk_level": "Safe",
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "recommendations" in data


def test_report_generation_json():
    response = client.post(
        "/api/reports/generate",
        json={
            "scan_result": {
                "target": "test-domain.com",
                "scanner": "Domain Scanner",
                "risk_score": 10.0,
                "risk_level": "Safe",
            },
            "format": "json",
        },
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_report_generation_pdf():
    response = client.post(
        "/api/reports/generate",
        json={
            "scan_result": {
                "target": "test-domain.com",
                "scanner": "Domain Scanner",
                "risk_score": 10.0,
                "risk_level": "Safe",
            },
            "format": "pdf",
        },
    )
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert len(response.content) > 1000


def test_feedback_endpoint():
    response = client.post(
        "/api/feedback",
        json={
            "scanner_key": "URL Scanner",
            "target": "https://example.com",
            "risk_score": 10.0,
            "is_helpful": True,
            "comment": "Very accurate scan",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_validation_error_handling():
    # Sending missing required target field
    response = client.post("/api/scanners/url", json={})
    assert response.status_code == 422
