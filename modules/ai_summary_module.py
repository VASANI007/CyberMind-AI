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
        reasons_text = ", ".join(reasons[:3]) if reasons else "Standard automated scan attributes analyzed"
        prompt = (
            f"You are CyberMind AI Executive Security Analyst. Write a concise, professional 2 to 3 sentence executive summary for target '{target}'.\n"
            f"- Verdict: {level} (Risk Score: {score}/100)\n"
            f"- Identified Indicators: {reasons_text}\n\n"
            f"Include:\n"
            f"1. Target identity and assigned verdict ({score}/100).\n"
            f"2. Primary contributing threat factors in plain words.\n"
            f"3. Concrete immediate recommended action.\n"
            f"Keep the summary strictly under 60 words in plain text with bold highlights for key terms. Do NOT use markdown tables or headers."
        )
        models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
        for model_name in models_to_try:
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 200
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=8)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.warning("Groq summary model %s failed: %s", model_name, e)
        return None

    def _offline_summary(self, target: str, score: float, level: str, reasons: list[str]) -> str:
        if str(level).lower() == "unverified":
            status_desc = f"is classified as **UNVERIFIED** (Score: {score}/100)"
            action = "Limited baseline intelligence was available. Exercise heightened caution before interacting."
        elif score >= 70:
            status_desc = f"has been flagged as **CRITICAL / HIGH RISK** ({level}, Score: {score}/100)"
            action = "Immediate network isolation and blocking of all communication with this asset is strongly recommended."
        elif score >= 40:
            status_desc = f"exhibits **MODERATE TO HIGH RISK** ({level}, Score: {score}/100)"
            action = "Caution is advised. Avoid entering credentials, submitting sensitive financial details, or downloading attachments."
        elif score >= 20:
            status_desc = f"exhibits **LOW RISK** ({level}, Score: {score}/100)"
            action = "Minor anomalous signals detected. Continue standard operational monitoring."
        else:
            status_desc = f"appears to be **BENIGN & SAFE** ({level}, Score: {score}/100)"
            action = "No active malware signatures or blacklist triggers were detected during telemetry inspection."

        factors_str = f" Key contributing factors include: {', '.join(reasons[:3])}." if reasons else ""
        return f"Automated inspection for `{target}` indicates that the target {status_desc}.{factors_str} {action}"

    def translate_summary(self, text: str, target_lang: str) -> str:
        """
        Translate summary text into target_lang (e.g. 'Hindi', 'Hinglish', 'Gujarati', 'Marathi', etc.).
        """
        if not text or target_lang in ("English", "en", "English 🇬🇧"):
            return text

        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        from core.offline_mode import offline_mode
        if api_key and not offline_mode.is_enabled:
            models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
            for model_name in models_to_try:
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    prompt = (
                        f"Translate the following cybersecurity executive summary into {target_lang}. "
                        f"Maintain technical formatting, headings, bullet points, and clear recommendations.\n\n"
                        f"Summary:\n{text}"
                    )
                    payload = {
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 900
                    }
                    resp = requests.post(url, json=payload, headers=headers, timeout=12)
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    logger.warning("Groq translation with %s failed: %s", model_name, e)

        # Fallback offline translations
        lang_lower = target_lang.lower()
        if "hindi" in lang_lower and "hinglish" not in lang_lower:
            return f"सुरक्षा विश्लेषण:\n\n{text.replace('Security Diagnosis & Verdict', 'सुरक्षा निदान व निर्णय').replace('Threat Vector Analysis', 'खतरे के वैक्टर का विश्लेषण').replace('Recommended Protective Actions', 'अनुशंसित सुरक्षात्मक कदम')}"
        elif "hinglish" in lang_lower:
            return f"Security Analysis Briefing:\n\n{text}\n\n*(CyberMind AI Alert: Kripya recommended security precautions follow karein)*"
        elif "gujarati" in lang_lower:
            return f"સુરક્ષા વિશ્લેષણ:\n\n{text.replace('Security Diagnosis & Verdict', 'સુરક્ષા નિદાન અને નિર્ણય').replace('Recommended Protective Actions', 'સૂચવેલ સુરક્ષા પગલાં')}"
        elif "marathi" in lang_lower:
            return f"सुरक्षा विश्लेषण:\n\n{text.replace('Security Diagnosis & Verdict', 'सुरक्षा निदान आणि निर्णय').replace('Recommended Protective Actions', 'शिफारस केलेल्या सुरक्षा उपाययोजना')}"
        elif "spanish" in lang_lower:
            return f"Análisis de Seguridad:\n\n{text}"
        elif "french" in lang_lower:
            return f"Analyse de Sécurité:\n\n{text}"
        elif "german" in lang_lower:
            return f"Sicherheitsanalyse:\n\n{text}"

        return text

    def generate_tts(self, text: str, lang: str = "English 🇬🇧") -> bytes | None:
        """
        Generate natural voice audio (MP3 bytes) for the given executive summary text.
        """
        if not text:
            return None
        try:
            import io
            from gtts import gTTS
            import re

            lang_lower = str(lang).lower()
            if "hindi" in lang_lower and "hinglish" not in lang_lower:
                lang_code = "hi"
            elif "gujarati" in lang_lower:
                lang_code = "gu"
            elif "marathi" in lang_lower:
                lang_code = "mr"
            elif "spanish" in lang_lower:
                lang_code = "es"
            elif "french" in lang_lower:
                lang_code = "fr"
            elif "german" in lang_lower:
                lang_code = "de"
            elif "hinglish" in lang_lower:
                lang_code = "hi"
            else:
                lang_code = "en"

            clean_text = re.sub(r'[*#`_>|\[\]\(\)]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if len(clean_text) > 700:
                clean_text = clean_text[:700] + "..."

            tts = gTTS(text=clean_text, lang=lang_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.getvalue()
        except Exception as exc:
            logger.warning("TTS audio generation failed: %s", exc)
            return None

    def analyze(self, scan_result: dict[str, Any]) -> str:
        """Plugin interface."""
        return self.generate_summary(scan_result)

    def health_check(self) -> dict[str, Any]:
        return {"module": "AI Summary Module", "status": "Healthy"}


ai_summary_module = AISummaryModule()
