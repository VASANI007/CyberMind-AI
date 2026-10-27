"""
CyberMind AI - Profile & System Overview API Router
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import uuid
import psutil
from datetime import datetime
from typing import Any
from fastapi import APIRouter
from backend.schemas import ProfileResponse
from backend.db_service import db_service

router = APIRouter(prefix="/api/profile", tags=["Profile"])

_cached_gpu_name: str | None = None
_cached_gateway: str | None = None
_cached_mac_address: str | None = None


def get_gpu_name() -> str:
    global _cached_gpu_name
    if _cached_gpu_name is not None:
        return _cached_gpu_name

    gpu_name = "N/A"
    try:
        import subprocess
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController).Name"],
            capture_output=True, text=True, timeout=4
        )
        lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        if lines:
            gpu_name = " / ".join(lines)
    except Exception:
        pass

    if gpu_name == "N/A":
        try:
            import subprocess
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, timeout=3
            )
            lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip() and l.strip().lower() != "name"]
            if lines:
                gpu_name = " / ".join(lines)
        except Exception:
            pass

    _cached_gpu_name = gpu_name
    return _cached_gpu_name


def get_gateway() -> str:
    global _cached_gateway
    if _cached_gateway is not None:
        return _cached_gateway
    gateway = "N/A"
    try:
        import subprocess
        res = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            if "Default Gateway" in line:
                parts = line.split(":")
                if len(parts) > 1 and parts[1].strip():
                    gateway = parts[1].strip()
                    break
    except Exception:
        pass
    _cached_gateway = gateway
    return gateway


def get_mac_address() -> str:
    global _cached_mac_address
    if _cached_mac_address is not None:
        return _cached_mac_address
    mac_address = "N/A"
    try:
        mac_int = uuid.getnode()
        mac_address = ":".join(f"{(mac_int >> i) & 0xFF:02X}" for i in range(40, -1, -8))
    except Exception:
        pass
    _cached_mac_address = mac_address
    return mac_address


@router.get("", response_model=ProfileResponse)
@router.get("/", response_model=ProfileResponse)
def get_profile():
    # 1. OS & CPU
    try:
        os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"
    except Exception:
        os_name = platform.platform()

    try:
        cpu_name = platform.processor() or "Unknown"
    except Exception:
        cpu_name = "Unknown"

    gpu_name = get_gpu_name()

    # 2. Memory
    try:
        mem = psutil.virtual_memory()
        mem_used_gb = round(mem.used / (1024 ** 3), 2)
        mem_avail_gb = round(mem.available / (1024 ** 3), 2)
        mem_total_gb = round(mem.total / (1024 ** 3), 2)
        mem_pct = round(mem.percent, 1)
    except Exception:
        mem_used_gb, mem_avail_gb, mem_total_gb, mem_pct = 0, 0, 0, 0

    # 3. Storage
    try:
        disk = shutil.disk_usage("/")
        disk_used_gb = round(disk.used / (1024 ** 3), 1)
        disk_free_gb = round(disk.free / (1024 ** 3), 1)
        disk_total_gb = round(disk.total / (1024 ** 3), 1)
        disk_pct = round((disk.used / disk.total) * 100, 1) if disk.total else 0
    except Exception:
        disk_used_gb, disk_free_gb, disk_total_gb, disk_pct = 0, 0, 0, 0

    # 4. Identity & Boot Time
    comp_name = platform.node() or os.environ.get("COMPUTERNAME", "Unknown")
    user_name = os.environ.get("USERNAME", os.environ.get("USER", "Unknown"))

    boot_time_str = "N/A"
    try:
        bt = datetime.fromtimestamp(psutil.boot_time())
        boot_time_str = bt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        pass

    # 5. Network
    local_ip = "N/A"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            pass

    mac_address = get_mac_address()
    gateway = get_gateway()

    # 6. Database Stats
    total_scans = 0
    threats_found = 0
    try:
        with db_service._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM scan_history")
            row = cursor.fetchone()
            if row:
                total_scans = row["cnt"]

            cursor.execute(
                "SELECT COUNT(*) as cnt FROM scan_history WHERE risk_level IN ('High', 'Critical')"
            )
            t_row = cursor.fetchone()
            if t_row:
                threats_found = t_row["cnt"]
    except Exception:
        pass

    return ProfileResponse(
        user_name=user_name,
        comp_name=comp_name,
        os_name=os_name,
        cpu_name=cpu_name,
        gpu_name=gpu_name,
        python_version=platform.python_version(),
        platform_name=platform.system(),
        architecture=platform.machine(),
        boot_time=boot_time_str,
        memory={
            "used_gb": mem_used_gb,
            "available_gb": mem_avail_gb,
            "total_gb": mem_total_gb,
            "percent": mem_pct,
        },
        storage={
            "used_gb": disk_used_gb,
            "free_gb": disk_free_gb,
            "total_gb": disk_total_gb,
            "percent": disk_pct,
        },
        network={
            "ip_address": local_ip,
            "hostname": platform.node() or comp_name,
            "gateway": gateway,
            "dns_server": "8.8.8.8, 1.1.1.1",
            "mac_address": mac_address,
        },
        stats={
            "total_scans": total_scans,
            "threats_found": threats_found,
            "account_status": "Active",
        },
    )
