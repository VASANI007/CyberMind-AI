"""
CyberMind AI

Breach Intelligence Service

Enterprise Production Version
"""

from __future__ import annotations
import pandas as pd
import re
from typing import Any
from core.logger import logger

class BreachIntelligenceService:
    """
    Enterprise Website Breach Intelligence Service.
    """

    def __init__(self) -> None:
        self.dataset_path = "data/datasets/website/raw/worlds_biggest_breaches_cleaned.csv"
        self._df = None
        logger.info("Breach Intelligence Service initialized.")

    def load_dataset(self) -> pd.DataFrame:
        if self._df is None:
            try:
                self._df = pd.read_csv(self.dataset_path)
                logger.info(f"Breach dataset loaded successfully with {len(self._df)} rows.")
            except Exception as e:
                logger.error(f"Error loading breach dataset: {e}")
                self._df = pd.DataFrame()
        return self._df

    def clean_domain_to_org(self, domain_or_url: str) -> str:
        s = domain_or_url.lower()
        if "://" in s:
            s = s.split("://")[1]
        s = s.split("/")[0]
        if s.startswith("www."):
            s = s[4:]
        parts = s.split(".")
        if len(parts) >= 2:
            tlds = {"com", "co", "org", "net", "edu", "gov", "ac", "mil", "in", "uk", "us", "ca", "de", "jp", "fr", "au"}
            if len(parts) >= 3 and parts[-2] in tlds:
                return parts[-3]
            return parts[-2]
        return parts[0]

    def get_breach_report(self, domain_or_url: str) -> dict[str, Any] | None:
        df = self.load_dataset()
        if df.empty:
            return None

        org_name = self.clean_domain_to_org(domain_or_url)
        if not org_name:
            return None

        # Filter the dataframe for matched organisation or alternative name
        # We do case-insensitive substring search for high compatibility
        matches = df[
            (df["organisation"].astype(str).str.lower().str.contains(org_name, na=False)) |
            (df["alternative name"].astype(str).str.lower().str.contains(org_name, na=False))
        ]

        if matches.empty:
            return None

        # Merge multiple breach reports
        breach_count = len(matches)
        
        # Sort matches by year to construct the timeline
        matches_sorted = matches.sort_values(by="year")
        
        # Aggregate metrics
        first_row = matches.iloc[0]
        company_name = str(first_row.get("organisation", org_name.capitalize()))
        sector = str(first_row.get("sector", "Technology")).capitalize()
        
        try:
            total_records = int(matches["records lost"].sum())
        except Exception:
            total_records = 0
            
        try:
            first_year = int(matches["year"].min())
            latest_year = int(matches["year"].max())
        except Exception:
            first_year = "N/A"
            latest_year = "N/A"

        # Unique attack methods
        attack_methods = matches["method"].dropna().unique().tolist()
        attack_methods = [str(m).capitalize() for m in attack_methods]

        # Overall risk level and logic
        if total_records > 10000000 or breach_count >= 3:
            risk_level = "Critical"
        elif total_records > 1000000 or breach_count >= 2:
            risk_level = "High"
        elif total_records > 100000:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Sensitive Data Analysis
        sensitive_data = []
        combined_stories = " ".join(matches["story"].astype(str).str.lower().tolist())
        
        if any(w in combined_stories for w in ["password", "credential", "login", "hash"]):
            sensitive_data.append("Passwords")
        if any(w in combined_stories for w in ["email", "address", "mailbox"]):
            sensitive_data.append("Emails")
        if any(w in combined_stories for w in ["phone", "mobile", "number"]):
            sensitive_data.append("Phone Numbers")
        if any(w in combined_stories for w in ["name", "profile", "first name", "last name", "user"]):
            sensitive_data.append("Names")
        if any(w in combined_stories for w in ["credit card", "card number", "payment", "cvv"]):
            sensitive_data.append("Credit Cards")
        if any(w in combined_stories for w in ["financial", "bank", "routing", "account", "tax"]):
            sensitive_data.append("Financial Data")
        if any(w in combined_stories for w in ["medical", "health", "patient", "ssn", "social security"]):
            sensitive_data.append("Medical Records")

        # Fallback to general user details if empty
        if not sensitive_data:
            sensitive_data = ["Names", "Emails"]

        # Attack stats for summary
        largest_single_breach = int(matches["records lost"].max()) if not matches["records lost"].empty else 0
        avg_records_per_breach = int(matches["records lost"].mean()) if not matches["records lost"].empty else 0

        # AI Summary Generation
        methods_str = ", ".join(attack_methods[:3]) if attack_methods else "external hacking"
        ai_summary = (
            f"This organization has experienced {breach_count} publicly reported security incident(s) "
            f"exposing a total of {total_records:,} customer records. "
            f"Most attacks were related to {methods_str}. "
            f"Overall cyber risk is flagged as {risk_level.upper()} due to the volume of exposed data."
        )

        # Security recommendations
        recommendations = ["Enable Multi-Factor Authentication (MFA) across all endpoints"]
        if "Passwords" in sensitive_data:
            recommendations.append("Enforce global password reset and update credentials policies")
        if "Credit Cards" in sensitive_data or "Financial Data" in sensitive_data:
            recommendations.append("Reset financial access tokens and review payment gateways security")
        recommendations.extend([
            "Implement real-time breach monitoring and dark web tracking",
            "Improve security policies regarding database access control",
            "Perform regular penetration testing and vulnerability assessments"
        ])

        # Timeline entries
        timeline = []
        for _, row in matches_sorted.iterrows():
            timeline.append({
                "year": str(row.get("year", "N/A")),
                "method": str(row.get("method", "Unknown Incident")).capitalize(),
                "records": int(row.get("records lost", 0))
            })

        # History records for table
        history = []
        for _, row in matches_sorted.iterrows():
            history.append({
                "year": str(row.get("year", "N/A")),
                "date": str(row.get("date", "N/A")),
                "method": str(row.get("method", "N/A")).capitalize(),
                "records": int(row.get("records lost", 0)),
                "sensitivity": str(row.get("data sensitivity", "N/A")),
                "source_name": str(row.get("source name", "N/A")),
                "link_1": str(row.get("1st source link", "")),
                "link_2": str(row.get("2nd source link", "")),
                "story": str(row.get("story", "No story recorded."))
            })

        # ── ML Sector Prediction (breaches_model) ────────────────────────
        # Predict industry sector from breach characteristics.
        # NOTE: This model has ~36% accuracy (515 training samples) — labeled
        # as "Experimental" in the UI.  See ml/inference.py TD-001 for the
        # encoder consistency note.
        ml_sector: dict = {"available": False}
        try:
            from ml.inference import predict_breach_sector
            import numpy as np

            row0 = first_row
            records_val = pd.to_numeric(row0.get("records lost", 0), errors="coerce")
            records_log = float(np.log1p(records_val if not pd.isna(records_val) else 0))
            sensitivity = float(pd.to_numeric(row0.get("data sensitivity", 2.0), errors="coerce") or 2.0)
            year_raw = pd.to_numeric(row0.get("year", 2010), errors="coerce")
            year_norm = float(((year_raw if not pd.isna(year_raw) else 2010) - 2004) / 18)
            org_len = int(len(str(row0.get("organisation", ""))))
            has_story = int(pd.notna(row0.get("interesting story", None)))
            method_clean = str(row0.get("method", "unknown")).split(",")[0].strip() or "unknown"

            ml_sector = predict_breach_sector(
                records_log=records_log,
                sensitivity=sensitivity,
                year_norm=year_norm,
                org_len=org_len,
                has_story=has_story,
                method_clean=method_clean,
            )
        except Exception as exc:
            logger.warning("Breach ML sector prediction failed: %s", exc)
        # ─────────────────────────────────────────────────────────────────

        return {
            "company_name": company_name,
            "sector": sector,
            "total_breaches": breach_count,
            "first_year": first_year,
            "latest_year": latest_year,
            "risk_level": risk_level,
            "total_records": total_records,
            "attack_methods": attack_methods,
            "sensitive_data": sensitive_data,
            "largest_single_breach": largest_single_breach,
            "avg_records_per_breach": avg_records_per_breach,
            "ai_summary": ai_summary,
            "recommendations": recommendations,
            "timeline": timeline,
            "history": history,
            "raw_df": matches_sorted,
            "ml_sector_prediction": ml_sector,
        }

breach_intelligence_service = BreachIntelligenceService()
