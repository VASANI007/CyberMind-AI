"""
Mission Configuration & Payload Loader
Vulnerability: CWE-22 (Path Traversal / Arbitrary File Read)
"""
import os
import sys

def load_mission_config(config_filename: str) -> str:
    base_dir = "/var/log/mission_configs"
    # VULNERABLE: Direct concatenation allowing directory traversal sequences like ../../../../etc/passwd
    target_file = f"{base_dir}/{config_filename}"
    
    try:
        with open(target_file, "r") as f:
            return f.read()
    except Exception as e:
        return f"Config Read Error: {e}"

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "default.json"
    print(load_mission_config(target))
