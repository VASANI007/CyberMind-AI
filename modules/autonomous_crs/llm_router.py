from __future__ import annotations

import os
import json
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)


class LLMRouter:
    """
    Intelligent Multi-LLM Provider Router & Fallback Manager.
    Dynamically routes tasks between Google Gemini, NVIDIA NIM, and Groq based on task specialization.
    
    Specialization Matrix:
    - NVIDIA NIM: Deep Coding, Cyber Reasoning, Root Cause Analysis, Patch Generation.
    - Google Gemini: Static Code Understanding, Architecture Analysis, Regression Test Synthesis.
    - Groq: Low-Latency Fuzz Target Generation, Fix Verification, Interactive Assistant.
    """

    PROVIDER_CONFIGS = {
        "GROQ": {
            "name": "Groq LPU",
            "env_key": ["GROQ_API_KEY"],
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "default_model": "groq/compound",
            "timeout": 3
        },
        "GEMINI": {
            "name": "Google Gemini",
            "env_key": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
            "default_model": "gemini-3.6-flash",
            "timeout": 3
        },
        "NVIDIA_NIM": {
            "name": "NVIDIA NIM",
            "env_key": ["NVIDIA_API_KEY", "NIM_API_KEY"],
            "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
            "default_model": "ai21labs/jamba-1.5-large-instruct",
            "timeout": 2
        }
    }

    # Ultra-Fast High-Throughput Routing Policy (Groq LPU & Gemini Flash first)
    AGENT_ROUTING_POLICY = {
        "orchestrator": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "reasoning": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "patch_engineer": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "static_analysis": ["GEMINI", "GROQ", "NVIDIA_NIM"],
        "regression": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "fuzzing": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "verification": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "assistant": ["GROQ", "GEMINI", "NVIDIA_NIM"],
        "default": ["GROQ", "GEMINI", "NVIDIA_NIM"]
    }

    def __init__(self):
        self.reload_keys()

    def reload_keys(self):
        load_dotenv(ENV_FILE, override=True)

    def get_api_key(self, provider: str) -> Optional[str]:
        self.reload_keys()
        cfg = self.PROVIDER_CONFIGS.get(provider, {})
        for env_var in cfg.get("env_key", []):
            val = os.environ.get(env_var, "").strip()
            if val:
                return val
        return None

    def get_active_providers(self) -> Dict[str, bool]:
        """Returns availability status for all 3 LLM providers."""
        return {
            p: bool(self.get_api_key(p))
            for p in self.PROVIDER_CONFIGS
        }

    def query(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "default",
        temperature: float = 0.4,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Executes query via task-specific primary provider with automatic multi-provider fallback.
        """
        providers_order = self.AGENT_ROUTING_POLICY.get(task_type.lower(), self.AGENT_ROUTING_POLICY["default"])
        attempted_providers = []

        for provider in providers_order:
            api_key = self.get_api_key(provider)
            attempted_providers.append(provider)

            if not api_key:
                continue

            try:
                if provider == "NVIDIA_NIM":
                    res = self._call_nvidia_nim(api_key, messages, temperature, max_tokens)
                elif provider == "GEMINI":
                    res = self._call_gemini(api_key, messages, temperature, max_tokens)
                elif provider == "GROQ":
                    res = self._call_groq(api_key, messages, temperature, max_tokens)
                else:
                    continue

                if res and not res.startswith("Error"):
                    return {
                        "success": True,
                        "content": res,
                        "provider_used": provider,
                        "provider_name": self.PROVIDER_CONFIGS[provider]["name"],
                        "task_type": task_type,
                        "fallback_path": attempted_providers
                    }
            except Exception as e:
                # Log error and continue to next provider in fallback hierarchy
                continue

        # If all API providers failed or had no keys configured
        return {
            "success": False,
            "content": f"Error: All LLM providers ({', '.join(providers_order)}) failed or are missing API keys.",
            "provider_used": "NONE",
            "provider_name": "Offline Engine",
            "task_type": task_type,
            "fallback_path": attempted_providers
        }

    def _call_groq(self, api_key: str, messages: List[Dict[str, str]], temp: float, tokens: int) -> str:
        url = self.PROVIDER_CONFIGS["GROQ"]["endpoint"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.PROVIDER_CONFIGS["GROQ"]["default_model"],
            "messages": messages,
            "temperature": temp,
            "max_tokens": tokens
        }
        res = requests.post(url, headers=headers, json=payload, timeout=self.PROVIDER_CONFIGS["GROQ"]["timeout"])
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        return f"Error: Groq HTTP {res.status_code} - {res.text}"

    def _call_nvidia_nim(self, api_key: str, messages: List[Dict[str, str]], temp: float, tokens: int) -> str:
        url = self.PROVIDER_CONFIGS["NVIDIA_NIM"]["endpoint"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.PROVIDER_CONFIGS["NVIDIA_NIM"]["default_model"],
            "messages": messages,
            "temperature": temp,
            "max_tokens": tokens
        }
        res = requests.post(url, headers=headers, json=payload, timeout=self.PROVIDER_CONFIGS["NVIDIA_NIM"]["timeout"])
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        return f"Error: NVIDIA NIM HTTP {res.status_code} - {res.text}"

    def _call_gemini(self, api_key: str, messages: List[Dict[str, str]], temp: float, tokens: int) -> str:
        url = f"{self.PROVIDER_CONFIGS['GEMINI']['endpoint']}?key={api_key}"
        
        combined_text_parts = []
        for m in messages:
            content = m.get("content", "")
            if m.get("role") == "system":
                combined_text_parts.append(f"[SYSTEM INSTRUCTION]\n{content}\n")
            else:
                combined_text_parts.append(content)

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": "\n\n".join(combined_text_parts)}]
            }],
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max(tokens, 800)
            }
        }
        res = requests.post(url, json=payload, timeout=self.PROVIDER_CONFIGS["GEMINI"]["timeout"])
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            return "Error: Gemini returned empty content structure."
        return f"Error: Gemini HTTP {res.status_code} - {res.text}"


# Singleton instance
llm_router = LLMRouter()
