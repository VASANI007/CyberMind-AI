"""
CyberMind AI
Modules Tests
Enterprise Production Version
"""

from __future__ import annotations

from modules.url_module import url_module
from modules.website_module import website_module
from modules.domain_module import domain_module
from modules.email_module import email_module
from modules.ip_module import ip_module
from modules.file_module import file_module
from modules.qr_module import qr_module


def test_url_module():
    """URL module instance."""

    assert url_module is not None


def test_website_module():
    """Website module instance."""

    assert website_module is not None


def test_domain_module():
    """Domain module instance."""

    assert domain_module is not None


def test_email_module():
    """Email module instance."""

    assert email_module is not None


def test_ip_module():
    """IP module instance."""

    assert ip_module is not None


def test_file_module():
    """File module instance."""

    assert file_module is not None


def test_qr_module():
    """QR module instance."""

    assert qr_module is not None


def test_url_module_health():
    """URL module health."""

    health = url_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_website_module_health():
    """Website module health."""

    health = website_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_domain_module_health():
    """Domain module health."""

    health = domain_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_email_module_health():
    """Email module health."""

    health = email_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_ip_module_health():
    """IP module health."""

    health = ip_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_file_module_health():
    """File module health."""

    health = file_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_qr_module_health():
    """QR module health."""

    health = qr_module.health_check()

    assert isinstance(health, dict)
    assert health["status"] == "Healthy"


def test_module_repr():
    """Module representation."""

    assert "Module" in repr(url_module)
    assert "Module" in repr(website_module)
    assert "Module" in repr(domain_module)
    assert "Module" in repr(email_module)
    assert "Module" in repr(ip_module)
    assert "Module" in repr(file_module)
    assert "Module" in repr(qr_module)


def test_all_modules_loaded():
    """All modules loaded."""

    modules = [
        url_module,
        website_module,
        domain_module,
        email_module,
        ip_module,
        file_module,
        qr_module
    ]

    assert all(module is not None for module in modules)


def test_ai_assistant_offline_fallback(monkeypatch):
    """Verify fallback when GROQ_API_KEY is not set."""
    import os
    import dotenv
    from modules.ai_assistant import get_chat_response
    
    # Prevent reloading of the real .env file during testing
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: None)
    
    original_key = os.environ.get("GROQ_API_KEY")
    if "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
        
    try:
        response = get_chat_response("password")
        assert "GROQ_API_KEY is not configured" in response
    finally:
        if original_key is not None:
            os.environ["GROQ_API_KEY"] = original_key




def test_ai_assistant_groq_api_mock(monkeypatch):
    """Verify Groq API query when key is set using mocks."""
    import os
    import streamlit as st
    from modules.ai_assistant import get_chat_response
    
    # Mock streamlit session state variables
    st.session_state.active_page = "AI Security Assistant"
    st.session_state.ai_page_chat_history = []
    
    class MockResponse:
        status_code = 200
        text = "OK"
        def json(self):
            return {"choices": [{"message": {"content": "This is a mock Groq response on passwords."}}]}
            
    import requests
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse())
    
    original_key = os.environ.get("GROQ_API_KEY")
    os.environ["GROQ_API_KEY"] = "mock_key_value"
    
    try:
        response = get_chat_response("What is the best way to choose a password?")
        assert response == "This is a mock Groq response on passwords."
    finally:
        if original_key is not None:
            os.environ["GROQ_API_KEY"] = original_key
        else:
            del os.environ["GROQ_API_KEY"]