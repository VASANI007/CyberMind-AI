"""
CyberMind AI
Device Security Module
"""

from __future__ import annotations

import time
from typing import Any
from pathlib import Path
from datetime import datetime

from core.logger import logger
from services.device_security_service import device_security_service
from database.db import db

class DeviceSecurityModule:
    """
    Device Security Module acting as the AI Risk Engine for local system scan data.
    """

    def __init__(self) -> None:
        logger.info("Device Security Module initialized.")

    def analyze(self, email: str | None = None, url: str | None = None, qr_image_path: str | None = None, file_path: str | None = None) -> dict[str, Any]:
        """
        Runs all scanner checks, parses the results, evaluates overall risk score,
        generates recommendations and saves them to the scan history.
        """
        # Run raw device scan checks
        scan_data = device_security_service.run_all_checks(
            email=email, url=url, qr_image_path=qr_image_path, file_path=file_path
        )
        
        # Calculate risk and security score
        security_score = 100
        problems = []
        recs = []
        
        # 1. Firewall check
        fw_status = scan_data["firewall"]
        if not fw_status.get("enabled", True):
            security_score -= 14
            problems.append("Windows Firewall is Disabled")
            recs.append("Enable Windows Firewall immediately to protect your system from unauthorized network requests.")
            
        # 2. Antivirus check
        av_status = scan_data["antivirus"]
        if not av_status.get("found", True):
            security_score -= 25
            problems.append("No active Antivirus detected")
            recs.append("Install and run a trusted antivirus software (e.g. Windows Defender, Quick Heal, or Kaspersky).")
            
        # 3. Windows updates
        up_status = scan_data["updates"]
        pending_updates = up_status.get("pending_count", 0)
        if pending_updates > 0:
            deduction = min(pending_updates * 3, 15)
            security_score -= deduction
            problems.append(f"{pending_updates} Pending Security Updates found")
            recs.append("Install all pending system updates in Windows Update to patch critical vulnerabilities.")
            
        # 4. CPU usage
        cpu_usage = scan_data["cpu"].get("usage_percent", 0.0)
        if cpu_usage > 85:
            security_score -= 5
            problems.append("CPU usage is critically high")
            recs.append("Close high resource applications running in the background using Task Manager.")
            
        # 5. RAM usage
        ram_percent = scan_data["ram"].get("usage_percent", 0.0)
        if ram_percent > 90:
            security_score -= 5
            problems.append("RAM usage is critically high")
            recs.append("Close memory-hogging tasks or web browser tabs to free up RAM.")
            
        # 6. Disk usage
        disk_status = scan_data["disk"]
        disk_partitions = disk_status.get("partitions", [])
        full_drives = [d["drive"] for d in disk_partitions if d.get("usage_percent", 0) > 95]
        if full_drives:
            security_score -= 8
            problems.append(f"Disk space critically low on drive(s): {', '.join(full_drives)}")
            recs.append("Free at least 20 GB of space by clearing cache files or moving data to external storage.")
            
        # 7. Open Ports
        ports_status = scan_data["ports"]
        open_ports = [p["port"] for p in ports_status.get("ports", [])]
        if 445 in open_ports:
            security_score -= 10
            problems.append("Port 445 (SMB) is open to local networks")
            recs.append("Disable file sharing or block port 445 at the firewall level if you do not actively use local sharing.")
        
        risky_ports = [p for p in open_ports if p in (21, 23, 3389, 139)]
        if risky_ports:
            security_score -= min(len(risky_ports) * 5, 15)
            problems.append(f"Remote administration ports open: {', '.join(map(str, risky_ports))}")
            recs.append("Close remote administration services (like FTP/Telnet/RDP) if not in use.")
            
        # 8. Internet & Connectivity check
        int_status = scan_data["internet"]
        if int_status.get("connectivity", "") == "Disconnected":
            security_score -= 8
            problems.append("Internet connectivity check failed")
            recs.append("Verify network cables, Wi-Fi configuration, or consult your ISP.")
            
        # 9. Email security (if submitted)
        em_status = scan_data.get("email_check")
        if em_status:
            if em_status.get("disposable", False):
                problems.append("Submitted email domain is disposable")
                recs.append("Avoid registering critical accounts with temporary/disposable email addresses.")
            if em_status.get("breach_found", False):
                problems.append(f"Submitted email domain has experienced {em_status.get('breach_count', 0)} breaches")
                recs.append("Change passwords for accounts registered on compromised domains and enable MFA.")

        # Ensure security score is between 0 and 100
        security_score = max(0, min(100, security_score))
        
        # Risk levels mapping
        if security_score >= 85:
            risk_level = "Low"
            status = "Secure 🟢"
        elif security_score >= 60:
            risk_level = "Medium"
            status = "Warning 🟡"
        elif security_score >= 35:
            risk_level = "High"
            status = "High Risk 🔴"
        else:
            risk_level = "Critical"
            status = "Critical 🔴"

        # Overall risk score is 100 - security_score (higher risk score means more dangerous)
        risk_score = 100 - security_score

        # Generate AI explanation points
        explanation_details = [
            f"Overall Device Security Score: {security_score}/100",
            f"Risk Level: {risk_level.upper()}"
        ]
        
        if security_score >= 85:
            explanation_details.append("The system is highly secure. Basic security features like firewall and antivirus are running properly, and resource utilization is normal.")
        elif security_score >= 60:
            explanation_details.append("The system is moderately secure. We detected some configuration issues or resource constraints that should be resolved to prevent vulnerabilities.")
        else:
            explanation_details.append("The system has multiple critical security vulnerabilities. Crucial protection systems are disabled, updates are missing, or risky ports are open. Immediate corrective action is recommended.")

        for p in problems:
            explanation_details.append(f"Issue identified: {p}.")

        # Generate recommendations list
        final_recs = []
        if not fw_status.get("enabled", True):
            final_recs.append("Enable Windows Firewall")
        if not av_status.get("found", True):
            final_recs.append("Install a trusted Antivirus")
        if pending_updates > 0:
            final_recs.append("Install Pending Updates")
        if cpu_usage > 85 or ram_percent > 90:
            final_recs.append("Close background tasks to free resources")
        if full_drives:
            final_recs.append("Free disk space on low capacity drives")
        if 445 in open_ports:
            final_recs.append("Disable file sharing or block port 445")
        if risky_ports:
            final_recs.append("Secure remote administration ports")
        final_recs.extend([
            "Perform a Full Antivirus Scan",
            "Enable Multi-Factor Authentication (MFA)",
            "Keep Web Browsers Updated",
            "Restart the computer regularly to apply updates"
        ])

        os_info_target = scan_data["os_info"]["hostname"]

        # Prepare final report payload
        result = {
            "success": True,
            "scanner": "device_security",
            "value": os_info_target,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "status": status,
            "security_score": security_score,
            "problems_found": problems if problems else ["No critical vulnerabilities identified"],
            "recommendation": {
                "recommendations": final_recs
            },
            "explain_ai": {
                "summary": explanation_details[2] if len(explanation_details) > 2 else "System is healthy.",
                "details": explanation_details
            },
            "scan_details": scan_data
        }

        # Save to SQLite Database history (compatible with existing history logic)
        try:
            db_level = risk_level
            if db_level == "Safe":
                db_level = "Low"
            db.execute(
                """
                INSERT INTO scan_history (scan_type, target, risk_level, risk_score)
                VALUES (?, ?, ?, ?)
                """,
                ("Device Security Check", os_info_target, db_level, float(risk_score))
            )
        except Exception as e:
            logger.error(f"Failed to save device scan to history database: {e}")

        return result

device_security_module = DeviceSecurityModule()
