"""
CyberMind AI - AI Assistant & Explanation Router
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import APIRouter
from backend.schemas import (
    AIChatRequest,
    AIChatResponse,
    AIExplainRequest,
    AIExplainResponse,
)
from modules.ai_assistant import (
    query_groq_api,
    get_offline_response,
    FALLBACK_RESPONSE,
)
from modules.ai_summary_module import ai_summary_module
from modules.explain_ai import explain_ai
from modules.recommendation import recommendation_engine

router = APIRouter(prefix="/api/ai", tags=["AI"])

SYSTEM_PROMPT = """You are CyberMind AI, an elite cybersecurity and threat intelligence AI assistant.
You possess deep expertise in:
- Phishing detection, brand impersonation, and homograph attacks.
- Network forensics, IP reputation, ASN tracking, and DNS inspection.
- SSL/TLS cryptographic verification and HTTP security headers.
- File entropy analysis, PE header inspection, and malware signatures.
- Practical mitigation strategies and cybersecurity hygiene.

Provide clear, professional, markdown-formatted guidance. Maintain high accuracy and concise, actionable recommendations.
"""


@router.post("/chat", response_model=AIChatResponse)
def chat_with_assistant(req: AIChatRequest):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    user_msg = req.messages[-1].content if req.messages else ""

    # If scanner context is supplied, enrich the conversation
    context_prefix = ""
    if req.scanner_context:
        ctx = req.scanner_context
        context_prefix = f"[Recent Scan Context: Target='{ctx.get('target')}', Scanner='{ctx.get('scanner')}', Risk={ctx.get('risk_score')}/100 ({ctx.get('risk_level')})]\n"

    # Attempt online Groq generation if key exists
    if api_key:
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in req.messages:
            content = m.content
            if m == req.messages[-1] and context_prefix:
                content = context_prefix + content
            api_messages.append({"role": m.role, "content": content})

        reply = query_groq_api(api_messages)
        if not reply.startswith("Error:"):
            return AIChatResponse(reply=reply, source="groq")

    # Offline rule-based fallback
    offline_reply = get_offline_response(user_msg)
    if not offline_reply:
        offline_reply = FALLBACK_RESPONSE

    return AIChatResponse(reply=offline_reply, source="rule_based")


@router.post("/explain", response_model=AIExplainResponse)
def explain_scan(req: AIExplainRequest):
    scan_result = req.scan_result
    risk = scan_result.get("risk") or {
        "risk_score": scan_result.get("risk_score", 0),
        "risk_level": scan_result.get("risk_level", "Safe"),
    }

    # Generate summary via ai_summary_module or explain_ai
    summary = ""
    try:
        summary = ai_summary_module.generate_summary(scan_result)
    except Exception:
        pass

    if not summary:
        exp = explain_ai.explain(risk)
        summary = exp.get("summary") or "Automated cyber risk scan completed across available intelligence sources."

    recs = recommendation_engine.generate(risk)
    rec_list = recs.get("recommendations", [])

    return AIExplainResponse(summary=summary, recommendations=rec_list)
