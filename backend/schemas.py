"""
CyberMind AI - Pydantic Request & Response Schemas
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Generic Response ──────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


# ── Scanner Requests ─────────────────────────────────────────────────────────

class UniversalScanRequest(BaseModel):
    target: str = Field(..., description="Target input: URL, Domain, IP, Email, or File Hash")

class URLScanRequest(BaseModel):
    url: str = Field(..., description="URL to scan for phishing & malicious content")

class WebsiteScanRequest(BaseModel):
    url: str = Field(..., description="Website address to analyze")

class DomainScanRequest(BaseModel):
    domain: str = Field(..., description="Domain name (e.g. example.com)")

class EmailScanRequest(BaseModel):
    email: str = Field(..., description="Email address to verify and analyze")

class IPScanRequest(BaseModel):
    ip: str = Field(..., description="IPv4 or IPv6 address")

class PhoneScanRequest(BaseModel):
    phone_number: Optional[str] = Field(None, description="Phone number with country code")
    phone: Optional[str] = Field(None, description="Alias for phone_number")

    def get_phone(self) -> str:
        return (self.phone_number or self.phone or "").strip()


class QRTextScanRequest(BaseModel):
    payload: str = Field(..., description="Decoded QR payload or URL")

class DeviceScanRequest(BaseModel):
    email: Optional[str] = None
    url: Optional[str] = None


# ── Scanner Result Standard Schema ───────────────────────────────────────────

class ScanResult(BaseModel):
    success: bool
    scanner: str
    target: str
    risk_score: float
    risk_level: str
    duration: str
    time: str
    analysis: dict[str, Any] = Field(default_factory=dict)
    ml_prediction: dict[str, Any] = Field(default_factory=dict)
    risk: dict[str, Any] = Field(default_factory=dict)
    recommendation: dict[str, Any] = Field(default_factory=dict)
    explain_ai: dict[str, Any] = Field(default_factory=dict)
    mitre_attack: Optional[Any] = None
    geo: Optional[dict[str, Any]] = None
    simulated: bool = False
    scan_id: Optional[int] = None
    error: Optional[str] = None


# ── Scan History ─────────────────────────────────────────────────────────────

class ScanHistoryItem(BaseModel):
    scan_id: int
    scan_type: str
    target: str
    risk_level: str
    risk_score: float
    status: str
    scan_time: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ScanHistoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ScanHistoryItem]


# ── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_scans: int
    threats_detected: int
    risky_items: int
    safe_items: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    safe_count: int
    avg_risk_score: float
    scanners_distribution: dict[str, int]
    recent_activity: list[dict[str, Any]]

class GeoThreatPoint(BaseModel):
    country: str
    country_code: Optional[str] = None
    latitude: float
    longitude: float
    threat_count: int
    avg_score: float
    latest_target: Optional[str] = None
    risk_level: str


# ── AI Assistant ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant or system")
    content: str

class AIChatRequest(BaseModel):
    messages: list[ChatMessage]
    scanner_context: Optional[dict[str, Any]] = None

class AIChatResponse(BaseModel):
    reply: str
    source: str = Field("hybrid", description="groq or rule_based")

class AIExplainRequest(BaseModel):
    scan_result: dict[str, Any]

class AIExplainResponse(BaseModel):
    summary: str
    recommendations: list[str]


# ── Reports ──────────────────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    scan_result: dict[str, Any]
    format: str = Field("pdf", description="pdf or json")


# ── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    scanner_key: str
    target: str
    risk_score: float
    is_helpful: bool
    comment: Optional[str] = ""


# ── Settings ─────────────────────────────────────────────────────────────────

class SettingsUpdate(BaseModel):
    language: Optional[str] = None
    dark_mode: Optional[bool] = None
    animations: Optional[bool] = None
    sound_alerts: Optional[bool] = None
    auto_save: Optional[bool] = None
    offline_mode: Optional[bool] = None
    export_format: Optional[str] = None
    api_keys: Optional[dict[str, str]] = None


# ── Profile ──────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    user_name: str
    comp_name: str
    os_name: str
    cpu_name: str
    gpu_name: str
    python_version: str
    platform_name: str
    architecture: str
    boot_time: str
    memory: dict[str, Any]
    storage: dict[str, Any]
    network: dict[str, Any]
    stats: dict[str, Any]

