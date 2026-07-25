"""
Tests for Brand Impersonation & MITRE Mapper Modules
"""

import pytest
from modules.brand_impersonation_module import brand_impersonation_module
from modules.mitre_mapper import mitre_mapper


def test_brand_impersonation_module():
    res = brand_impersonation_module.check("g00gle.com")
    assert "is_impersonation" in res


def test_mitre_mapper():
    scan_result = {
        "risk_score": 85,
        "risk_level": "High",
        "result": {
            "js_behavior": {"flags": [{"severity": "critical", "name": "eval()"}]},
            "homograph": {"is_homograph": True}
        }
    }
    res = mitre_mapper.map_findings(scan_result)
    assert res["count"] > 0
    assert len(res["techniques"]) > 0
