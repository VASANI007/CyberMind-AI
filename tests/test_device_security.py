"""
CyberMind AI
Device Security Service and Module Tests
"""

from __future__ import annotations

import pytest
from services.device_security_service import device_security_service
from modules.device_security_module import device_security_module

def test_device_security_service_instance():
    assert device_security_service is not None

def test_device_security_module_instance():
    assert device_security_module is not None

def test_get_os_info():
    os_info = device_security_service.get_os_info()
    assert isinstance(os_info, dict)
    assert "os_name" in os_info
    assert "version" in os_info
    assert "architecture" in os_info
    assert "hostname" in os_info
    assert "boot_time" in os_info
    assert "ai_analysis" in os_info

def test_get_firewall_status():
    fw = device_security_service.get_firewall_status()
    assert isinstance(fw, dict)
    assert "enabled" in fw
    assert "status" in fw
    assert "details" in fw
    assert "risk" in fw

def test_get_antivirus_status():
    av = device_security_service.get_antivirus_status()
    assert isinstance(av, dict)
    assert "found" in av
    assert "names" in av
    assert "details" in av
    assert "risk" in av

def test_get_windows_updates():
    up = device_security_service.get_windows_updates()
    assert isinstance(up, dict)
    assert "pending_count" in up
    assert "status" in up
    assert "risk" in up

def test_get_cpu_usage():
    cpu = device_security_service.get_cpu_usage()
    assert isinstance(cpu, dict)
    assert "usage_percent" in cpu
    assert "risk" in cpu
    assert 0 <= cpu["usage_percent"] <= 100

def test_get_ram_usage():
    ram = device_security_service.get_ram_usage()
    assert isinstance(ram, dict)
    assert "usage_percent" in ram
    assert "total_gb" in ram
    assert "used_gb" in ram
    assert "available_gb" in ram
    assert 0 <= ram["usage_percent"] <= 100

def test_get_disk_health():
    disk = device_security_service.get_disk_health()
    assert isinstance(disk, dict)
    assert "partitions" in disk
    assert "risk" in disk
    for partition in disk["partitions"]:
        assert "drive" in partition
        assert "usage_percent" in partition
        assert 0 <= partition["usage_percent"] <= 100

def test_get_running_processes():
    proc = device_security_service.get_running_processes()
    assert isinstance(proc, dict)
    assert "processes" in proc
    assert "unknown_count" in proc
    assert "risk" in proc
    for p in proc["processes"]:
        assert "pid" in p
        assert "name" in p
        assert "cpu" in p
        assert "mem" in p
        assert "status" in p

def test_get_startup_applications():
    startup = device_security_service.get_startup_applications()
    assert isinstance(startup, dict)
    assert "apps" in startup
    for app in startup["apps"]:
        assert "name" in app
        assert "command" in app
        assert "status" in app

def test_get_open_ports():
    ports = device_security_service.get_open_ports()
    assert isinstance(ports, dict)
    assert "ports" in ports
    assert "open_count" in ports
    assert "risk" in ports
    for p in ports["ports"]:
        assert "port" in p
        assert "service" in p
        assert "status" in p

def test_get_network_info():
    net = device_security_service.get_network_info()
    assert isinstance(net, dict)
    assert "local_ip" in net
    assert "mac_address" in net
    assert "connection_type" in net
    assert "dns_provider" in net

def test_get_internet_security():
    internet = device_security_service.get_internet_security()
    assert isinstance(internet, dict)
    assert "https_status" in internet
    assert "dns_status" in internet
    assert "connectivity" in internet
    assert "risk" in internet

def test_get_browser_security():
    browser = device_security_service.get_browser_security()
    assert isinstance(browser, dict)
    assert "browsers" in browser
    for b in browser["browsers"]:
        assert "name" in b
        assert "status" in b

def test_get_suspicious_file_extensions():
    susp = device_security_service.get_suspicious_file_extensions()
    assert isinstance(susp, dict)
    assert "files" in susp
    assert "count" in susp
    for f in susp["files"]:
        assert "filename" in f
        assert "extension" in f
        assert "size_kb" in f

def test_check_email_security():
    res = device_security_service.check_email_security("test@google.com")
    assert isinstance(res, dict)
    assert res["valid"] is True
    assert res["email"] == "test@google.com"
    assert "disposable" in res
    assert "breach_found" in res
    assert "risk_level" in res

def test_module_analyze():
    # Test overall analysis calculation
    res = device_security_module.analyze()
    assert isinstance(res, dict)
    assert res["success"] is True
    assert "scanner" in res
    assert "risk_score" in res
    assert "risk_level" in res
    assert "status" in res
    assert "security_score" in res
    assert "problems_found" in res
    assert "recommendation" in res
    assert "explain_ai" in res
    
    # Verify score logic
    assert 0 <= res["security_score"] <= 100
    assert res["risk_score"] == 100 - res["security_score"]
