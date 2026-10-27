"""
CyberMind AI - Reports API Router
"""

from __future__ import annotations

import re
from fastapi import APIRouter, Response, HTTPException
from backend.schemas import GenerateReportRequest
from backend.report_generator import generate_pdf_report, generate_json_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/generate")
def generate_report(req: GenerateReportRequest):
    fmt = req.format.lower().strip()
    target = req.scan_result.get("target") or req.scan_result.get("value") or "scan"
    safe_target = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', str(target))[:30]

    if fmt == "pdf":
        try:
            pdf_bytes = generate_pdf_report(req.scan_result)
            filename = f"cybermind_report_{safe_target}.pdf"
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Type": "application/pdf",
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")

    elif fmt == "json":
        try:
            json_str = generate_json_report(req.scan_result)
            filename = f"cybermind_report_{safe_target}.json"
            return Response(
                content=json_str,
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Type": "application/json",
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate JSON report: {e}")

    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats: pdf, json")


@router.get("/pdf/{scan_id}")
def download_pdf_by_id(scan_id: int):
    from backend.db_service import db_service
    item = db_service.get_scan_by_id(scan_id)
    if not item:
        raise HTTPException(status_code=404, detail="Scan record not found")
    safe_target = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', str(item.get("target") or "scan"))[:30]
    scan_result = {
        "scanner": item.get("scan_type"),
        "target": item.get("target"),
        "risk_score": item.get("risk_score"),
        "risk_level": item.get("risk_level"),
        "time": item.get("scan_time"),
        "analysis": {"status": item.get("status")},
        "geo": {
            "country": item.get("country"),
            "country_code": item.get("country_code"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        },
    }
    pdf_bytes = generate_pdf_report(scan_result)
    filename = f"cybermind_report_{safe_target}_{scan_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@router.get("/json/{scan_id}")
def download_json_by_id(scan_id: int):
    from backend.db_service import db_service
    item = db_service.get_scan_by_id(scan_id)
    if not item:
        raise HTTPException(status_code=404, detail="Scan record not found")
    safe_target = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', str(item.get("target") or "scan"))[:30]
    scan_result = {
        "scanner": item.get("scan_type"),
        "target": item.get("target"),
        "risk_score": item.get("risk_score"),
        "risk_level": item.get("risk_level"),
        "time": item.get("scan_time"),
        "analysis": {"status": item.get("status")},
        "geo": {
            "country": item.get("country"),
            "country_code": item.get("country_code"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        },
    }
    json_str = generate_json_report(scan_result)
    filename = f"cybermind_report_{safe_target}_{scan_id}.json"
    return Response(
        content=json_str,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/json",
        },
    )

