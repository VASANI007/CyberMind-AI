"""
CyberMind AI - Feedback API Router
"""

from __future__ import annotations

from fastapi import APIRouter
from backend.schemas import FeedbackRequest, APIResponse
from backend.db_service import db_service

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=APIResponse)
def submit_feedback(req: FeedbackRequest):
    db_service.save_feedback(
        scanner_key=req.scanner_key,
        target=req.target,
        risk_score=req.risk_score,
        is_helpful=req.is_helpful,
        comment=req.comment or "",
    )
    return APIResponse(success=True, message="Feedback submitted successfully. Thank you!")
