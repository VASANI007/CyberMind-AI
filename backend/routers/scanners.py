"""
CyberMind AI - Scanner API Router
Endpoints for all 10 CyberMind cybersecurity scanners.
"""

from __future__ import annotations

import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.config import TEMP_DIR
from backend.schemas import (
    URLScanRequest,
    WebsiteScanRequest,
    DomainScanRequest,
    EmailScanRequest,
    IPScanRequest,
    PhoneScanRequest,
    UniversalScanRequest,
    QRTextScanRequest,
    DeviceScanRequest,
    ScanResult,
)
from backend.db_service import db_service
from core.logger import logger

router = APIRouter(prefix="/api/scanners", tags=["Scanners"])


def _extract_score_and_level(raw: dict) -> tuple[float, str]:
    risk = raw.get("risk") or {}
    score = risk.get("risk_score") if risk.get("risk_score") is not None else risk.get("score")
    level = risk.get("risk_level") if risk.get("risk_level") is not None else risk.get("level")

    if score is None:
        score = raw.get("risk_score") or raw.get("fraud_score") or 0.0
    if level is None:
        level = raw.get("risk_level") or raw.get("scam_risk") or "Safe"

    try:
        score = float(score)
    except Exception:
        score = 0.0

    level_str = str(level).capitalize()
    if level_str in ("Malicious", "Danger"):
        level_str = "Critical"
    elif level_str in ("Suspicious", "Warn"):
        level_str = "Medium"
    elif level_str not in ("Safe", "Low", "Medium", "High", "Critical"):
        level_str = "Low"

    return score, level_str


def _standardize_result(
    scanner_key: str,
    target: str,
    raw: dict,
    start_time: float,
    geo: Optional[dict] = None,
) -> ScanResult:
    duration_sec = time.time() - start_time
    duration_str = f"{duration_sec:.2f} sec"
    timestamp_str = datetime.now().strftime("%H:%M:%S")

    score, level = _extract_score_and_level(raw)

    if geo is None:
        geo = db_service.resolve_geo(scanner_key, target)

    scan_id = db_service.record_scan(
        scanner_key=scanner_key,
        target=target,
        risk_level=level,
        risk_score=score,
        geo=geo,
        raw_analysis=raw.get("analysis"),
    )

    return ScanResult(
        success=bool(raw.get("success", True)),
        scanner=scanner_key,
        target=target,
        risk_score=score,
        risk_level=level,
        duration=duration_str,
        time=timestamp_str,
        analysis=raw.get("analysis") or {},
        ml_prediction=raw.get("ml_prediction") or {},
        risk=raw.get("risk") or {},
        recommendation=raw.get("recommendation") or {},
        explain_ai=raw.get("explain_ai") or {},
        mitre_attack=raw.get("mitre_attack"),
        geo=geo,
        simulated=bool(raw.get("simulated", False)),
        scan_id=scan_id,
        error=raw.get("message") if not raw.get("success", True) else None,
    )


# 1. URL & Phishing Scanner
@router.post("/url", response_model=ScanResult)
def scan_url(req: URLScanRequest):
    start_time = time.time()
    from modules.url_scanner import URLScanner
    scanner = URLScanner()
    raw = scanner.analyze(req.url.strip())
    return _standardize_result("URL Scanner", req.url.strip(), raw, start_time)


# 2. Website Security Analyzer
@router.post("/website", response_model=ScanResult)
def scan_website(req: WebsiteScanRequest):
    start_time = time.time()
    from modules.website_scanner import WebsiteScanner
    scanner = WebsiteScanner()
    raw = scanner.analyze(req.url.strip())
    return _standardize_result("Website Scanner", req.url.strip(), raw, start_time)


# 3. Domain & WHOIS Scanner
@router.post("/domain", response_model=ScanResult)
def scan_domain(req: DomainScanRequest):
    start_time = time.time()
    from modules.domain_scanner import DomainScanner
    scanner = DomainScanner()
    raw = scanner.analyze(req.domain.strip())
    return _standardize_result("Domain Scanner", req.domain.strip(), raw, start_time)


# 4. Email Intelligence Scanner
@router.post("/email", response_model=ScanResult)
def scan_email(req: EmailScanRequest):
    start_time = time.time()
    from modules.email_scanner import EmailScanner
    scanner = EmailScanner()
    raw = scanner.analyze(req.email.strip())
    return _standardize_result("Email Scanner", req.email.strip(), raw, start_time)


# 5. IP Reputation Scanner
@router.post("/ip", response_model=ScanResult)
def scan_ip(req: IPScanRequest):
    start_time = time.time()
    from modules.ip_scanner import IPScanner
    scanner = IPScanner()
    raw = scanner.analyze(req.ip.strip())
    return _standardize_result("IP Scanner", req.ip.strip(), raw, start_time)


# 6. Phone Threat Intelligence
@router.post("/phone", response_model=ScanResult)
def scan_phone(req: PhoneScanRequest):
    start_time = time.time()
    from modules.phone_scanner import PhoneScanner
    scanner = PhoneScanner()
    phone = req.get_phone()
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")
    raw = scanner.analyze(phone)
    return _standardize_result("Phone Threat Intelligence", phone, raw, start_time)


# 7. File Analyzer (Upload)
@router.post("/file", response_model=ScanResult)
async def scan_file(file: UploadFile = File(...)):
    start_time = time.time()
    # Save safely to temp directory
    safe_filename = Path(file.filename or "uploaded_sample").name
    temp_path = TEMP_DIR / f"{int(time.time())}_{safe_filename}"

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        from modules.file_scanner import FileScanner
        scanner = FileScanner()
        raw = scanner.analyze(str(temp_path))

        # Replace local temp path with clean original filename in target and analysis
        if "file_path" in raw:
            raw["file_path"] = safe_filename

        return _standardize_result("File Scanner", safe_filename, raw, start_time)
    finally:
        # Secure cleanup
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


# 8. QR Code Scanner (Upload Image or Payload String)
@router.post("/qr", response_model=ScanResult)
async def scan_qr(
    file: Optional[UploadFile] = File(None),
    payload: Optional[str] = Form(None),
):
    start_time = time.time()
    from modules.qr_scanner import QRScanner
    scanner = QRScanner()

    if file is not None:
        safe_filename = Path(file.filename or "qr_code.png").name
        temp_path = TEMP_DIR / f"{int(time.time())}_{safe_filename}"
        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            raw = scanner.analyze(str(temp_path))
            target_name = safe_filename
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
    elif payload:
        # Direct payload analysis
        from services.qr_service import qr_service
        raw = qr_service.analyze(payload.strip())
        from modules.risk_engine import risk_engine
        from modules.recommendation import recommendation_engine
        from modules.explain_ai import explain_ai
        risk = risk_engine.calculate(raw)
        raw["risk"] = risk
        raw = {
            "success": True,
            "scanner": "qr",
            "image": payload.strip(),
            "analysis": raw,
            "risk": risk,
            "recommendation": recommendation_engine.generate(risk),
            "explain_ai": explain_ai.explain(risk),
        }
        target_name = payload.strip()
    else:
        raise HTTPException(status_code=400, detail="Must provide either QR image file or payload string.")

    return _standardize_result("QR Code Scanner", target_name, raw, start_time)


# 9. Device Security Check
@router.post("/device", response_model=ScanResult)
def scan_device(req: DeviceScanRequest = DeviceScanRequest()):
    start_time = time.time()
    from modules.device_security_module import DeviceSecurityModule
    module = DeviceSecurityModule()
    raw = module.analyze(email=req.email, url=req.url)

    target_name = "Local Host Machine"
    try:
        import platform
        target_name = f"{platform.node()} ({platform.system()} {platform.release()})"
    except Exception:
        pass

    return _standardize_result("Device Security Check", target_name, raw, start_time)


# 10. Universal Auto Scanner
@router.post("/universal", response_model=ScanResult)
def scan_universal(req: UniversalScanRequest):
    start_time = time.time()
    from modules.universal_scan_module import UniversalScanModule
    module = UniversalScanModule()
    raw = module.analyze(req.target.strip())
    return _standardize_result("Universal Scan", req.target.strip(), raw, start_time)
