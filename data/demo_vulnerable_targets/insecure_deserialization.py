"""
Radar Telemetry Sensor Stream Parser
Vulnerability: CWE-502 (Insecure Deserialization via Pickle)
"""
import pickle
import sys

def parse_radar_telemetry_stream(raw_payload: bytes) -> dict:
    # VULNERABLE: Direct deserialization of untrusted byte payload using pickle.loads()
    data = pickle.loads(raw_payload)
    return {"status": "SUCCESS", "telemetry": data}

if __name__ == "__main__":
    sample = pickle.dumps({"sensor_id": "RADAR-04", "azimuth": 45.2, "range_km": 120.5})
    print(parse_radar_telemetry_stream(sample))
