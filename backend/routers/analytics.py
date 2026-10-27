"""
CyberMind AI - Analytics API Router
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter
from backend.schemas import AnalyticsSummary, GeoThreatPoint
from backend.db_service import db_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsSummary)
def get_analytics_overview():
    data = db_service.get_analytics()
    return AnalyticsSummary(**data)


@router.get("/geo", response_model=List[GeoThreatPoint])
def get_geo_threats():
    points = db_service.get_geo_threats()
    return [GeoThreatPoint(**p) for p in points]
