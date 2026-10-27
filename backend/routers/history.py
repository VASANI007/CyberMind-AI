"""
CyberMind AI - History API Router
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas import ScanHistoryListResponse, ScanHistoryItem, APIResponse
from backend.db_service import db_service

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=ScanHistoryListResponse)
def get_history(
    scanner_type: Optional[str] = Query(None, description="Filter by scanner type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    search: Optional[str] = Query(None, description="Search target keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    offset = (page - 1) * page_size
    total, rows = db_service.get_history(
        scanner_type=scanner_type,
        risk_level=risk_level,
        search=search,
        limit=page_size,
        offset=offset,
    )

    items = [ScanHistoryItem(**r) for r in rows]
    return ScanHistoryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get("/{scan_id}")
def get_scan_details(scan_id: int):
    scan = db_service.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return scan


@router.delete("/{scan_id}", response_model=APIResponse)
def delete_scan(scan_id: int):
    success = db_service.delete_scan(scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return APIResponse(success=True, message=f"Scan record {scan_id} deleted successfully.")


@router.delete("", response_model=APIResponse)
def clear_all_history():
    db_service.clear_all_history()
    return APIResponse(success=True, message="All scan history records have been cleared.")
