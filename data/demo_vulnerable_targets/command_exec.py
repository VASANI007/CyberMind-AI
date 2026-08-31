"""
Network Node Telemetry & Diagnostic Utility
Vulnerability: CWE-78 (Command Injection)
"""
import os
import sys

def ping_remote_node(target_host: str) -> int:
    # VULNERABLE: Direct string composition in os.system without argument tokenization or escaping
    command = f"ping -c 2 {target_host}"
    exit_code = os.system(command)
    return exit_code

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    res = ping_remote_node(host)
    print(f"Ping finished with status: {res}")
