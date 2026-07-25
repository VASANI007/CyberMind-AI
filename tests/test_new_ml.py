"""
Tests for Anomaly & Malware Family Models (Phase 1G)
"""

import pytest
from ml.anomaly_model import anomaly_model
from ml.ransomware_model import ransomware_model
from ml.spyware_model import spyware_model
from ml.trojan_model import trojan_model
from ml.rootkit_model import rootkit_model
from ml.worm_model import worm_model
from ml.zero_day_risk_model import zero_day_risk_model


def test_anomaly_model():
    features = [1.0, 2.5, 0.3, 15.0, 80.0]
    res = anomaly_model.detect_anomaly(features)
    assert "is_anomaly" in res
    assert "anomaly_score" in res


def test_malware_family_models():
    sample_features = {
        "entropy": 7.8,
        "vba_macros_suspicious": True,
        "brand_impersonation": True,
        "redirect_hops": 4,
        "subdomains_count": 45,
        "anomaly_score": 0.85
    }

    rw = ransomware_model.predict(sample_features)
    assert rw["family"] == "Ransomware"
    assert rw["is_threat"] is True

    sp = spyware_model.predict(sample_features)
    assert sp["family"] == "Spyware"

    tr = trojan_model.predict(sample_features)
    assert tr["family"] == "Trojan"
    assert tr["is_threat"] is True

    rk = rootkit_model.predict(sample_features)
    assert rk["family"] == "Rootkit"

    wm = worm_model.predict(sample_features)
    assert wm["family"] == "Worm"
    assert wm["is_threat"] is True

    zd = zero_day_risk_model.predict(sample_features)
    assert zd["is_elevated"] is True
