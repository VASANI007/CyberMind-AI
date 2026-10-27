"""
CyberMind AI - Database Service & History Persistence
"""

from __future__ import annotations

import sqlite3
import socket
from urllib.parse import urlparse
from typing import Any, Optional
from datetime import datetime
from backend.config import DATABASE_PATH
from core.logger import logger
from services.geo_service import geo_service


class DBService:
    def __init__(self) -> None:
        self.db_path = DATABASE_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def resolve_geo(self, scanner_key: str, target: str) -> dict[str, Any]:
        """Resolves IP and geographic coordinates for a given target where applicable."""
        geo_result = {
            "country": None,
            "country_code": None,
            "latitude": None,
            "longitude": None,
        }

        if scanner_key in ("Email Scanner", "QR Code Scanner", "File Scanner", "Device Security Check"):
            return geo_result

        try:
            target_str = str(target).strip()
            is_ip = False
            try:
                socket.inet_aton(target_str)
                is_ip = True
            except Exception:
                pass

            ip = None
            if is_ip:
                ip = target_str
            else:
                hostname = target_str
                if "://" in target_str or scanner_key in ("Website Scanner", "URL Scanner", "Universal Scan"):
                    try:
                        parsed = urlparse(target_str)
                        hostname = parsed.hostname or target_str
                    except Exception:
                        pass
                try:
                    ip = socket.gethostbyname(hostname)
                except Exception:
                    pass

            if ip:
                info = geo_service.lookup(ip)
                if info:
                    geo_result["country"] = info.get("country")
                    geo_result["country_code"] = info.get("country_code")
                    geo_result["latitude"] = info.get("latitude")
                    geo_result["longitude"] = info.get("longitude")
        except Exception as e:
            logger.debug("Geo resolution failed for %s: %s", target, e)

        return geo_result

    def record_scan(
        self,
        scanner_key: str,
        target: str,
        risk_level: str,
        risk_score: float,
        geo: Optional[dict[str, Any]] = None,
        raw_analysis: Optional[dict[str, Any]] = None,
    ) -> int:
        """Records a scan into scan_history and its specific scan sub-table."""
        db_level = risk_level
        if db_level == "Malicious":
            db_level = "Critical"
        elif db_level == "Suspicious":
            db_level = "Medium"
        elif db_level == "Unverified":
            db_level = "Low"
        elif db_level not in ("Safe", "Low", "Medium", "High", "Critical"):
            db_level = "Low"

        if geo is None:
            geo = self.resolve_geo(scanner_key, target)

        country = geo.get("country")
        country_code = geo.get("country_code")
        latitude = geo.get("latitude")
        longitude = geo.get("longitude")

        scan_id = -1
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scan_history (scan_type, target, risk_level, risk_score, status, country, country_code, latitude, longitude)
                VALUES (?, ?, ?, ?, 'Completed', ?, ?, ?, ?)
                """,
                (scanner_key, target, db_level, float(risk_score), country, country_code, latitude, longitude),
            )
            scan_id = cursor.lastrowid or -1
            conn.commit()

            # Optional child table insertion for backward compatibility
            try:
                analysis = raw_analysis or {}
                if scanner_key == "URL Scanner":
                    cursor.execute(
                        """
                        INSERT INTO url_scans (scan_id, url, domain, https, status_code, risk_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (scan_id, target, analysis.get("domain", {}).get("domain", ""), 1 if "https" in target.lower() else 0, 200, float(risk_score)),
                    )
                elif scanner_key == "Website Scanner":
                    cursor.execute(
                        """
                        INSERT INTO website_scans (scan_id, url, risk_score)
                        VALUES (?, ?, ?)
                        """,
                        (scan_id, target, float(risk_score)),
                    )
                elif scanner_key == "Domain Scanner":
                    cursor.execute(
                        """
                        INSERT INTO domain_scans (scan_id, domain, risk_score)
                        VALUES (?, ?, ?)
                        """,
                        (scan_id, target, float(risk_score)),
                    )
                elif scanner_key == "Email Scanner":
                    cursor.execute(
                        """
                        INSERT INTO email_scans (scan_id, email, risk_score)
                        VALUES (?, ?, ?)
                        """,
                        (scan_id, target, float(risk_score)),
                    )
                elif scanner_key == "IP Scanner":
                    cursor.execute(
                        """
                        INSERT INTO ip_scans (scan_id, ip, country, latitude, longitude, risk_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (scan_id, target, country, latitude, longitude, float(risk_score)),
                    )
                conn.commit()
            except Exception as sub_err:
                logger.debug("Child table insert skipped: %s", sub_err)

        return scan_id

    def get_history(
        self,
        scanner_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[int, list[dict[str, Any]]]:
        """Fetches filtered scan history records with pagination."""
        conditions = []
        params: list[Any] = []

        if scanner_type and scanner_type != "All":
            conditions.append("scan_type = ?")
            params.append(scanner_type)

        if risk_level and risk_level != "All":
            conditions.append("risk_level = ?")
            params.append(risk_level)

        if search:
            conditions.append("(target LIKE ? OR scan_type LIKE ?)")
            term = f"%{search.strip()}%"
            params.extend([term, term])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cursor = conn.cursor()
            count_query = f"SELECT COUNT(*) as cnt FROM scan_history {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()["cnt"]

            query = f"""
                SELECT scan_id, scan_type, target, risk_level, risk_score, status, scan_time, country, country_code, latitude, longitude
                FROM scan_history
                {where_clause}
                ORDER BY scan_id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [limit, offset])
            rows = [dict(r) for r in cursor.fetchall()]

        return total, rows

    def get_scan_by_id(self, scan_id: int) -> Optional[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_history WHERE scan_id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_scan(self, scan_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history WHERE scan_id = ?", (scan_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all_history(self) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history")
            cursor.execute("DELETE FROM url_scans")
            cursor.execute("DELETE FROM website_scans")
            cursor.execute("DELETE FROM domain_scans")
            cursor.execute("DELETE FROM email_scans")
            cursor.execute("DELETE FROM ip_scans")
            cursor.execute("DELETE FROM file_scans")
            cursor.execute("DELETE FROM qr_scans")
            conn.commit()
            return True

    def get_analytics(self) -> dict[str, Any]:
        """Calculates aggregated metrics, risk distribution, scanner counts, and recent activity."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total
            cursor.execute("SELECT COUNT(*) as cnt, AVG(risk_score) as avg_score FROM scan_history")
            tot_row = cursor.fetchone()
            total_scans = tot_row["cnt"] if tot_row else 0
            avg_risk_score = round(tot_row["avg_score"] or 0.0, 1)

            # Levels
            cursor.execute("""
                SELECT risk_level, COUNT(*) as cnt
                FROM scan_history
                GROUP BY risk_level
            """)
            level_counts = {r["risk_level"]: r["cnt"] for r in cursor.fetchall()}

            safe_count = level_counts.get("Safe", 0)
            low_count = level_counts.get("Low", 0)
            medium_count = level_counts.get("Medium", 0)
            high_count = level_counts.get("High", 0)
            critical_count = level_counts.get("Critical", 0)

            threats_detected = high_count + critical_count
            risky_items = low_count + medium_count
            safe_items = safe_count

            # Scanner distribution
            cursor.execute("""
                SELECT scan_type, COUNT(*) as cnt
                FROM scan_history
                GROUP BY scan_type
                ORDER BY cnt DESC
            """)
            scanners_distribution = {r["scan_type"]: r["cnt"] for r in cursor.fetchall()}

            # Recent scans
            cursor.execute("""
                SELECT scan_id, scan_type, target, risk_level, risk_score, scan_time
                FROM scan_history
                ORDER BY scan_id DESC
                LIMIT 10
            """)
            recent_activity = [dict(r) for r in cursor.fetchall()]

            return {
                "total_scans": total_scans,
                "threats_detected": threats_detected,
                "risky_items": risky_items,
                "safe_items": safe_items,
                "critical_count": critical_count,
                "high_count": high_count,
                "medium_count": medium_count,
                "low_count": low_count,
                "safe_count": safe_count,
                "avg_risk_score": avg_risk_score,
                "scanners_distribution": scanners_distribution,
                "recent_activity": recent_activity,
            }

    def get_geo_threats(self) -> list[dict[str, Any]]:
        """Returns geographic coordinates grouped by country with threat counts and average score."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    country,
                    country_code,
                    AVG(latitude) as lat,
                    AVG(longitude) as lng,
                    COUNT(*) as threat_count,
                    AVG(risk_score) as avg_score,
                    MAX(target) as latest_target,
                    CASE
                        WHEN AVG(risk_score) >= 75 THEN 'Critical'
                        WHEN AVG(risk_score) >= 50 THEN 'High'
                        WHEN AVG(risk_score) >= 25 THEN 'Medium'
                        ELSE 'Safe'
                    END as risk_level
                FROM scan_history
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND country IS NOT NULL
                GROUP BY country, country_code
                ORDER BY threat_count DESC
            """)
            rows = cursor.fetchall()

            results = []
            for r in rows:
                results.append({
                    "country": r["country"],
                    "country_code": r["country_code"],
                    "latitude": round(r["lat"], 4),
                    "longitude": round(r["lng"], 4),
                    "threat_count": r["threat_count"],
                    "avg_score": round(r["avg_score"], 1),
                    "latest_target": r["latest_target"],
                    "risk_level": r["risk_level"],
                })

            return results

    def save_feedback(self, scanner_key: str, target: str, risk_score: float, is_helpful: bool, comment: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback (scanner_key, target, risk_score, is_helpful, comment)
                VALUES (?, ?, ?, ?, ?)
                """,
                (scanner_key, target, float(risk_score), 1 if is_helpful else 0, comment or ""),
            )
            conn.commit()
            return True

    def get_settings(self) -> dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {r["key"]: r["value"] for r in cursor.fetchall()}

    def update_setting(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()


db_service = DBService()
