"""
CyberMind AI
AI Executive Summary Module
Generates a concise 3-4 sentence plain-language executive summary of scan results.
Uses Groq API when available, falls back to rule-based offline template.
"""

from __future__ import annotations
from typing import Any
import os
import requests
from core.logger import logger


class AISummaryModule:
    """
    Executive Summary Generator for scan reports.
    """

    @property
    def name(self) -> str:
        return "ai_summary_module"

    def generate_summary(self, scan_result: dict[str, Any]) -> str:
        """
        Generate executive summary for *scan_result*.
        """
        target = (
            scan_result.get("value")
            or scan_result.get("url")
            or scan_result.get("domain")
            or scan_result.get("ip")
            or scan_result.get("file")
            or scan_result.get("email")
            or scan_result.get("image")
            or "Target"
        )
        score = scan_result.get("risk_score")
        if score is None:
            score = scan_result.get("risk", {}).get("score")
        if score is None:
            score = (scan_result.get("raw") or {}).get("risk", {}).get("score", 0)

        level = (
            scan_result.get("risk_level")
            or scan_result.get("risk", {}).get("level")
            or (scan_result.get("raw") or {}).get("risk", {}).get("level", "Safe")
        )

        raw_risk = (scan_result.get("raw") or {}).get("risk", {})
        reasons = (
            scan_result.get("risk", {}).get("reasons")
            or (raw_risk.get("reasons") if isinstance(raw_risk, dict) else [])
            or (scan_result.get("reasons") if isinstance(scan_result.get("reasons"), list) else [])
            or []
        )

        # Try Groq API if key exists and not in offline mode
        from core.offline_mode import offline_mode
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if api_key and not offline_mode.is_enabled:
            try:
                summary = self._query_groq(target, score, level, reasons, scan_result, api_key)
                if summary:
                    return summary
            except Exception as exc:
                logger.warning("Groq executive summary failed: %s", exc)

        # Offline template fallback
        return self._offline_summary(target, score, level, reasons)

    def _query_groq(self, target: str, score: float, level: str, reasons: list[str], scan_result: dict, api_key: str) -> str | None:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        prompt = (
            f"Write a concise 3-sentence executive summary for a security scan on '{target}'. "
            f"Risk Score: {score}/100 ({level}). Key risk factors: {', '.join(reasons) if reasons else 'No major issues'}. "
            f"Provide actionable advice for non-technical managers."
        )
        payload = {
            "model": "groq/compound",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 200
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=8)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return None

    def _offline_summary(self, target: str, score: float, level: str, reasons: list[str]) -> str:
        if str(level).lower() == "unverified":
            status_desc = f"is in an **UNVERIFIED STATE** (Score: {score}/100)"
            action = "Low data completeness was available to confirm safety. Exercise caution."
        elif score >= 70:
            status_desc = f"has been flagged as **HIGH RISK** ({level}, Score: {score}/100)"
            action = "Immediate isolation or blocking of this asset is recommended."
        elif score >= 40:
            status_desc = f"exhibits **MODERATE RISK** ({level}, Score: {score}/100)"
            action = "Caution is advised when interacting with or visiting this asset."
        elif score >= 20:
            status_desc = f"exhibits **LOW RISK** ({level}, Score: {score}/100)"
            action = "Minor risk signals detected. Continue to monitor."
        else:
            status_desc = f"appears to be **SAFE** ({level}, Score: {score}/100)"
            action = "No immediate security threats were detected during automated analysis."

        factors_str = f" Key contributing factors include: {', '.join(reasons[:3])}." if reasons else ""
        return f"Analysis for `{target}` indicates that the target {status_desc}.{factors_str} {action}"

    def translate_summary(self, text: str, target_lang: str) -> str:
        """
        Translate summary text into target_lang (e.g. 'Hindi', 'Hinglish', 'Gujarati', 'Marathi', etc.).
        """
        if not text or target_lang in ("English", "en", "English 🇬🇧"):
            return text

        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        from core.offline_mode import offline_mode
        if api_key and not offline_mode.is_enabled:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                prompt = (
                    f"Translate the following security analysis executive summary into {target_lang}. "
                    f"Keep technical terms clear and easy to understand for non-technical users.\n\n"
                    f"Summary: {text}"
                )
                payload = {
                    "model": "groq/compound",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=6)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.warning("Groq translation failed: %s", e)

        # Fallback offline translations
        lang_lower = target_lang.lower()
        if "hindi" in lang_lower and "hinglish" not in lang_lower:
            return f"सुरक्षा विश्लेषण: {text.replace('Analysis for', '').replace('indicates that the target', 'यह दर्शाता है कि टारगेट')}"
        elif "hinglish" in lang_lower:
            return f"Security Analysis Update: {text} (Note: Kripya security action lein)."
        elif "gujarati" in lang_lower:
            return f"સુરક્ષા વિશ્લેષણ: {text}"
        elif "marathi" in lang_lower:
            return f"सुरक्षा विश्लेषण: {text}"
        elif "spanish" in lang_lower:
            return f"Análisis de seguridad: {text}"
        elif "french" in lang_lower:
            return f"Analyse de sécurité: {text}"
        elif "german" in lang_lower:
            return f"Sicherheitsanalyse: {text}"

        return text

    def analyze(self, scan_result: dict[str, Any]) -> str:
        """Plugin interface."""
        return self.generate_summary(scan_result)

    def health_check(self) -> dict[str, Any]:
        return {"module": "AI Summary Module", "status": "Healthy"}


ai_summary_module = AISummaryModule()
