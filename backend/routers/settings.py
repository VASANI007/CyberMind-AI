"""
CyberMind AI - Settings API Router
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import APIRouter
from backend.schemas import SettingsUpdate, APIResponse
from backend.db_service import db_service

router = APIRouter(prefix="/api/settings", tags=["Settings"])

API_KEYS = [
    "GOOGLE_SAFE_BROWSING_API_KEY",
    "VIRUSTOTAL_API_KEY",
    "URLSCAN_API_KEY",
    "IPINFO_API_KEY",
    "ABUSEIPDB_API_KEY",
    "NUMVERIFY_API_KEY",
    "VERIPHONE_API_KEY",
    "ABSTRACT_IP_API_KEY",
    "ABSTRACT_PHONE_API_KEY",
    "IPQS_API_KEY",
    "GROQ_API_KEY",
]


@router.get("")
def get_settings():
    db_settings = db_service.get_settings()

    # Masked API status
    api_status = {}
    for key in API_KEYS:
        val = os.environ.get(key, "").strip()
        if val:
            # Mask key: show only first 4 and last 3 chars
            masked = val[:4] + "..." + val[-3:] if len(val) > 8 else "Configured"
            api_status[key] = {
                "configured": True,
                "masked": masked,
            }
        else:
            api_status[key] = {
                "configured": False,
                "masked": "",
            }

    return {
        "preferences": {
            "language": db_settings.get("language", "English"),
            "dark_mode": db_settings.get("dark_mode", "True") == "True",
            "animations": db_settings.get("animations", "True") == "True",
            "sound_alerts": db_settings.get("sound_alerts", "False") == "True",
            "auto_save": db_settings.get("auto_save", "True") == "True",
            "offline_mode": db_settings.get("offline_mode", "False") == "True",
            "export_format": db_settings.get("report_format", "PDF"),
        },
        "api_services": api_status,
        "database_version": db_settings.get("database_version", "1.0.0"),
    }


@router.post("", response_model=APIResponse)
def update_settings(update: SettingsUpdate):
    if update.language is not None:
        db_service.update_setting("language", update.language)
    if update.dark_mode is not None:
        db_service.update_setting("dark_mode", str(update.dark_mode))
    if update.animations is not None:
        db_service.update_setting("animations", str(update.animations))
    if update.sound_alerts is not None:
        db_service.update_setting("sound_alerts", str(update.sound_alerts))
    if update.auto_save is not None:
        db_service.update_setting("auto_save", str(update.auto_save))
    if update.offline_mode is not None:
        db_service.update_setting("offline_mode", str(update.offline_mode))
        from core.offline_mode import offline_mode
        if update.offline_mode:
            offline_mode.enable()
        else:
            offline_mode.disable()
    if update.export_format is not None:
        db_service.update_setting("report_format", update.export_format)

    # API keys update (runtime environment update)
    if update.api_keys:
        for k, v in update.api_keys.items():
            if k in API_KEYS and v:
                os.environ[k] = v.strip()

    return APIResponse(success=True, message="Settings updated successfully.")
