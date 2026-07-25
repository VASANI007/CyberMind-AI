"""
CyberMind AI — Standalone Local Security Agent
Runs genuine OS-level security checks on the user's local workstation
(this script must be downloaded and run ON YOUR OWN MACHINE — it cannot
be run by the web server, since only your own PC can see your own
firewall, antivirus, processes, and startup apps).

Usage:
    python cybermind_local_scanner.py

Output:
    - A human-readable summary printed to the terminal
    - A JSON report saved as cybermind_local_report.json (same folder)
"""

import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone

# psutil is optional but strongly recommended — enables CPU/RAM/process/
# startup checks. The script still runs without it, just with fewer checks.
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

OS_NAME = platform.system()  # "Windows", "Darwin" (macOS), or "Linux"


# ---------------------------------------------------------------------------
# 1. OS Info
# ---------------------------------------------------------------------------
def get_os_info() -> dict:
    return {
        "system": OS_NAME,
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "hostname": socket.gethostname(),
        "python_version": sys.version.split()[0],
    }


# ---------------------------------------------------------------------------
# 2. Hosts File Check — smarter than a raw line count
# ---------------------------------------------------------------------------
# A clean Windows/macOS/Linux hosts file normally has ~2-10 lines
# (localhost/loopback entries + comments). Rather than flagging "too many
# lines" (which false-positives on developers, Docker, and ad-blocker users
# who legitimately have 50+ entries), we instead look for the much more
# specific and reliable signal: well-known, high-value domains being
# redirected to a DIFFERENT IP than they should resolve to. That pattern —
# not line count — is what real hosts-file-hijacking malware does.
WATCHED_DOMAINS = [
    "google.com", "facebook.com", "microsoft.com", "apple.com",
    "paypal.com", "amazon.com", "bankofamerica.com", "chase.com",
    "windowsupdate.com", "update.microsoft.com",
]


def get_hosts_file_status() -> dict:
    hosts_path = (
        r"C:\Windows\System32\drivers\etc\hosts"
        if OS_NAME == "Windows"
        else "/etc/hosts"
    )
    if not os.path.exists(hosts_path):
        return {"status": "Missing", "tampered": True, "reason": "hosts file not found", "entries_count": 0}

    try:
        with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]

        suspicious_redirects = []
        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                continue
            ip, hostnames = parts[0], parts[1:]
            for host in hostnames:
                host_lower = host.lower()
                if any(watched in host_lower for watched in WATCHED_DOMAINS):
                    # A watched high-value domain is being redirected somewhere
                    # other than a loopback address — that's the real red flag.
                    if not (ip.startswith("127.") or ip == "::1"):
                        suspicious_redirects.append({"domain": host, "redirected_to": ip})

        return {
            "path": hosts_path,
            "status": "Intact",
            "entries_count": len(lines),
            "tampered": len(suspicious_redirects) > 0,
            "suspicious_redirects": suspicious_redirects,
            "sample_entries": lines[:10],
        }
    except Exception as e:
        return {"status": f"Error reading hosts file: {e}", "tampered": False, "entries_count": 0}


# ---------------------------------------------------------------------------
# 3. Network Ports — checks both loopback-only and externally-exposed binds
# ---------------------------------------------------------------------------
RISKY_PORTS = {
    21: "FTP", 23: "Telnet", 135: "RPC", 139: "NetBIOS",
    445: "SMB", 1433: "MSSQL", 3306: "MySQL", 3389: "RDP",
}
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 8080]


def get_network_ports() -> dict:
    open_local_ports = []
    for port in COMMON_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        try:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                open_local_ports.append(port)
        finally:
            sock.close()

    externally_exposed = []
    if HAS_PSUTIL:
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == psutil.CONN_LISTEN and conn.laddr:
                    bind_ip = conn.laddr.ip
                    port = conn.laddr.port
                    # 0.0.0.0 / :: means the service listens on ALL interfaces,
                    # not just localhost — a materially higher risk than a
                    # loopback-only bind, and psutil is the only reliable way
                    # to tell the difference (a raw connect_ex to 127.0.0.1
                    # can't distinguish "bound to localhost" from "bound to all").
                    if bind_ip in ("0.0.0.0", "::"):
                        externally_exposed.append(port)
        except (psutil.AccessDenied, PermissionError):
            pass  # some OSes require elevated privileges to list all sockets

    risky_open = [p for p in open_local_ports if p in RISKY_PORTS]
    risky_exposed = [p for p in externally_exposed if p in RISKY_PORTS]

    if risky_exposed:
        risk = "Critical"
    elif risky_open:
        risk = "High"
    elif externally_exposed:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "open_local_ports": open_local_ports,
        "externally_exposed_ports": externally_exposed,
        "risky_ports_found": [f"{p} ({RISKY_PORTS[p]})" for p in set(risky_open + risky_exposed)],
        "risk": risk,
    }


# ---------------------------------------------------------------------------
# 4. Firewall Status — real, OS-specific check (this is what device_security_
#    service.py's server-side version could never actually see for a visitor)
# ---------------------------------------------------------------------------
def get_firewall_status() -> dict:
    try:
        if OS_NAME == "Windows":
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True, text=True, timeout=5,
            )
            output = result.stdout
            enabled = "State                                 ON" in output or "ON" in output
            return {"enabled": enabled, "details": output.strip()[:400], "checked": True}

        elif OS_NAME == "Darwin":
            result = subprocess.run(
                ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
                capture_output=True, text=True, timeout=5,
            )
            enabled = "enabled" in result.stdout.lower()
            return {"enabled": enabled, "details": result.stdout.strip(), "checked": True}

        elif OS_NAME == "Linux":
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
            enabled = "active" in result.stdout.lower()
            return {"enabled": enabled, "details": result.stdout.strip(), "checked": True}

    except FileNotFoundError:
        return {"enabled": None, "details": "Firewall tool not found (ufw not installed?)", "checked": False}
    except Exception as e:
        return {"enabled": None, "details": f"Could not check: {e}", "checked": False}

    return {"enabled": None, "details": "Unsupported OS", "checked": False}


# ---------------------------------------------------------------------------
# 5. Antivirus Status (Windows-only reliable API; other OSes marked N/A
#    rather than guessed, since there's no universal cross-platform signal)
# ---------------------------------------------------------------------------
def get_antivirus_status() -> dict:
    if OS_NAME != "Windows":
        return {"checked": False, "details": "No universal AV-detection API on this OS — not guessed."}
    try:
        result = subprocess.run(
            ["wmic", "/namespace:\\\\root\\SecurityCenter2", "path", "AntiVirusProduct", "get", "displayName"],
            capture_output=True, text=True, timeout=5,
        )
        names = [ln.strip() for ln in result.stdout.splitlines() if ln.strip() and "displayName" not in ln]
        return {"checked": True, "products_found": names, "protected": len(names) > 0}
    except Exception as e:
        return {"checked": False, "details": f"Could not check: {e}"}


# ---------------------------------------------------------------------------
# 6. Top Processes (by CPU/RAM) — requires psutil
# ---------------------------------------------------------------------------
def get_top_processes(limit: int = 5) -> dict:
    if not HAS_PSUTIL:
        return {"checked": False, "details": "psutil not installed — run: pip install psutil"}
    try:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        by_cpu = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:limit]
        return {"checked": True, "top_by_cpu": by_cpu}
    except Exception as e:
        return {"checked": False, "details": f"Could not check: {e}"}


# ---------------------------------------------------------------------------
# 7. Startup Applications (best-effort, per-OS)
# ---------------------------------------------------------------------------
def get_startup_apps() -> dict:
    try:
        if OS_NAME == "Windows":
            import winreg
            apps = []
            for hive, path in [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]:
                try:
                    with winreg.OpenKey(hive, path) as key:
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                apps.append({"name": name, "command": value})
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue
            return {"checked": True, "count": len(apps), "apps": apps}

        elif OS_NAME == "Darwin":
            path = os.path.expanduser("~/Library/LaunchAgents")
            apps = os.listdir(path) if os.path.isdir(path) else []
            return {"checked": True, "count": len(apps), "apps": apps}

        elif OS_NAME == "Linux":
            path = os.path.expanduser("~/.config/autostart")
            apps = os.listdir(path) if os.path.isdir(path) else []
            return {"checked": True, "count": len(apps), "apps": apps}

    except Exception as e:
        return {"checked": False, "details": f"Could not check: {e}"}

    return {"checked": False, "details": "Unsupported OS"}


# ---------------------------------------------------------------------------
# Health Score — computed from what was ACTUALLY checked, never hardcoded.
# A check that couldn't run is excluded from scoring, not assumed safe.
# ---------------------------------------------------------------------------
def compute_health_score(report: dict) -> dict:
    max_points = 0
    earned_points = 0
    checks_run = 0
    checks_total = 0
    warnings = []

    # Hosts file (20 pts)
    checks_total += 1
    hosts = report["hosts_check"]
    if "tampered" in hosts and hosts.get("status") not in (None,) and "Error" not in str(hosts.get("status", "")):
        checks_run += 1
        max_points += 20
        if hosts["tampered"]:
            warnings.append("Hosts file has suspicious redirects for known domains.")
        else:
            earned_points += 20

    # Network ports (25 pts)
    checks_total += 1
    net = report["network"]
    checks_run += 1
    max_points += 25
    risk_penalty = {"Low": 0, "Medium": 8, "High": 16, "Critical": 25}
    earned_points += 25 - risk_penalty.get(net["risk"], 12)
    if net["risk"] != "Low":
        warnings.append(f"Network exposure risk: {net['risk']} — {net.get('risky_ports_found')}")

    # Firewall (25 pts)
    checks_total += 1
    fw = report["firewall"]
    if fw.get("checked"):
        checks_run += 1
        max_points += 25
        if fw["enabled"]:
            earned_points += 25
        else:
            warnings.append("Firewall is disabled.")
    else:
        warnings.append("Firewall status could not be verified on this OS.")

    # Antivirus (20 pts)
    checks_total += 1
    av = report["antivirus"]
    if av.get("checked"):
        checks_run += 1
        max_points += 20
        if av.get("protected"):
            earned_points += 20
        else:
            warnings.append("No antivirus product detected.")
    else:
        warnings.append("Antivirus status could not be verified on this OS (no universal API).")

    # Startup apps (10 pts) — informational; large counts get a soft flag only
    checks_total += 1
    startup = report["startup_apps"]
    if startup.get("checked"):
        checks_run += 1
        max_points += 10
        earned_points += 10 if startup.get("count", 0) <= 15 else 6
        if startup.get("count", 0) > 15:
            warnings.append(f"Unusually high number of startup apps ({startup['count']}) — review for unwanted entries.")

    data_completeness = round((checks_run / checks_total) * 100, 1) if checks_total else 0.0
    score = round((earned_points / max_points) * 100) if max_points else None

    return {
        "score": score,
        "data_completeness_percent": data_completeness,
        "checks_run": checks_run,
        "checks_total": checks_total,
        "warnings": warnings,
        "note": (
            "Score reflects only checks that could actually run on this OS. "
            "Checks that could not be verified are excluded from scoring, not assumed safe — "
            "see 'warnings' and each section's 'checked' flag for what's missing."
        ),
    }


# ---------------------------------------------------------------------------
# Run everything
# ---------------------------------------------------------------------------
def run_audit() -> dict:
    print("Running CyberMind AI Local Security Audit...\n")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "os": get_os_info(),
        "hosts_check": get_hosts_file_status(),
        "network": get_network_ports(),
        "firewall": get_firewall_status(),
        "antivirus": get_antivirus_status(),
        "top_processes": get_top_processes(),
        "startup_apps": get_startup_apps(),
    }
    report["health"] = compute_health_score(report)

    # Human-readable console summary
    print(f"OS:           {report['os']['system']} {report['os']['release']}")
    print(f"Hostname:     {report['os']['hostname']}")
    hc = report["hosts_check"]
    print(f"Hosts file:   {'⚠️  Suspicious redirects found' if hc.get('tampered') else '✅ Looks normal'}")
    net = report["network"]
    print(f"Network risk: {net['risk']}  (open: {net['open_local_ports']}, externally exposed: {net['externally_exposed_ports']})")
    fw = report["firewall"]
    print(f"Firewall:     {'✅ Enabled' if fw.get('enabled') else ('❌ Disabled' if fw.get('checked') else '❔ Could not verify')}")
    av = report["antivirus"]
    print(f"Antivirus:    {'✅ ' + ', '.join(av.get('products_found', [])) if av.get('protected') else ('❌ None detected' if av.get('checked') else '❔ Could not verify on this OS')}")
    sa = report["startup_apps"]
    print(f"Startup apps: {sa.get('count', '?')} found" if sa.get("checked") else "Startup apps: could not verify")
    h = report["health"]
    print(f"\nHealth Score: {h['score']}/100  (based on {h['checks_run']}/{h['checks_total']} checks — {h['data_completeness_percent']}% data completeness)")
    if h["warnings"]:
        print("Warnings:")
        for w in h["warnings"]:
            print(f"  - {w}")

    out_file = "cybermind_local_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull report saved to {out_file}")

    return report


if __name__ == "__main__":
    run_audit()