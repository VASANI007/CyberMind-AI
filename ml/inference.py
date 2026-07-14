"""
CyberMind AI — ML Inference Module
===================================
Single entry-point for running predictions through the 4 trained
RandomForestClassifier models:

  1. phishing_url_model.pkl   — binary: phishing vs. legitimate (50 PhiUSIIL features)
  2. online_valid_model.pkl   — multi-class: brand impersonation (18 lexical features)
  3. breaches_model.pkl       — multi-class: industry sector (6 features)
  4. file_signatures_model.pkl — multi-class: risk level Low/Medium/High (9 features)

Encoder Consistency
-------------------
Models 3 & 4 were trained with an OrdinalEncoder applied to one text column
each (method_clean for breaches, category_clean for file signatures).
Because the training script did NOT save the fitted encoder alongside the
model, we re-fit OrdinalEncoder on the same original CSVs at startup.
sklearn's OrdinalEncoder sorts categories alphabetically (deterministic),
so fitting on the same data produces the same integer-to-category mapping
as training time.

# TECH DEBT (TD-001):
# The proper fix is to retrain with:
#   joblib.dump({"model": clf, "encoder": oe, "imputer": imp, "feature_cols": [...]}, path)
# and update predict_* functions to use bundle["encoder"].transform() instead of
# the re-fit approach below.  Until retrained, unknown categories are handled
# by OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1).
"""

from __future__ import annotations

import re
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder

from ml.model_loader import model_loader
from core.logger import logger

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE = Path(__file__).resolve().parent.parent
_MODEL_DIR = _BASE / "ml" / "models"
_DATA_DIR = _BASE / "data" / "datasets"

PHISHING_URL_MODEL_PATH = str(_MODEL_DIR / "phishing_url_model.pkl")
ONLINE_VALID_MODEL_PATH = str(_MODEL_DIR / "online_valid_model.pkl")
BREACHES_MODEL_PATH = str(_MODEL_DIR / "breaches_model.pkl")
FILE_SIG_MODEL_PATH = str(_MODEL_DIR / "file_signatures_model.pkl")

# ---------------------------------------------------------------------------
# PhiUSIIL feature columns (50 columns, in the exact order after dropping
# FILENAME, URL, Domain, TLD, Title, label from the raw CSV)
# ---------------------------------------------------------------------------
PHISHING_URL_FEATURE_COLS: list[str] = [
    "URLLength", "DomainLength", "IsDomainIP", "URLSimilarityIndex",
    "CharContinuationRate", "TLDLegitimateProb", "URLCharProb", "TLDLength",
    "NoOfSubDomain", "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
    "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL", "DegitRatioInURL",
    "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS",
    "LineOfCode", "LargestLineLength", "HasTitle", "DomainTitleMatchScore",
    "URLTitleMatchScore", "HasFavicon", "Robots", "IsResponsive",
    "NoOfURLRedirect", "NoOfSelfRedirect", "HasDescription", "NoOfPopup",
    "NoOfiFrame", "HasExternalFormSubmit", "HasSocialNet", "HasSubmitButton",
    "HasHiddenFields", "HasPasswordField", "Bank", "Pay", "Crypto",
    "HasCopyrightInfo", "NoOfImage", "NoOfCSS", "NoOfJS", "NoOfSelfRef",
    "NoOfEmptyRef", "NoOfExternalRef",
]

# ---------------------------------------------------------------------------
# Lexical feature columns for online_valid_model (18 features, pure numeric)
# ---------------------------------------------------------------------------
ONLINE_VALID_FEATURE_COLS: list[str] = [
    "url_len", "has_https", "num_dots", "num_slashes", "num_hyphens",
    "num_digits", "num_at", "num_equals", "num_ampersand", "num_special",
    "has_ip", "path_depth", "query_len", "domain_len",
    "dot_slash_ratio", "special_ratio", "digit_ratio", "hyphen_ratio",
]

# ---------------------------------------------------------------------------
# Breaches model feature columns (6 features, 1 text: method_clean)
# ---------------------------------------------------------------------------
BREACH_FEATURE_COLS: list[str] = [
    "records_log", "sensitivity", "year_norm",
    "org_len", "has_story", "method_clean",
]

# ---------------------------------------------------------------------------
# File signatures model feature columns (9 features, 1 text: category_clean)
# ---------------------------------------------------------------------------
FILE_SIG_FEATURE_COLS: list[str] = [
    "category_clean", "hex_len", "hex_spaces", "hex_bytes",
    "hex_unique", "has_wild", "ext_len", "desc_len", "offset_val",
]


# ===========================================================================
# Generic encoder (mirrors encode_features() in train_cybermind.py but uses
# .transform() instead of .fit_transform() for text columns)
# ===========================================================================

def _encode_features_with_fitted_oe(
    df: pd.DataFrame,
    fitted_oe: OrdinalEncoder | None,
    text_cols: list[str],
) -> np.ndarray:
    """
    Apply a pre-fitted OrdinalEncoder to text_cols, then impute all columns.
    Mirrors the training-time encode_features() logic exactly:
      final_matrix = [text-encoded cols] + [other cols]
    """
    df = df.copy()
    other_cols = [c for c in df.columns if c not in text_cols]
    parts: list[np.ndarray] = []

    if text_cols and fitted_oe is not None:
        encoded = fitted_oe.transform(df[text_cols].astype(str))
        parts.append(np.asarray(encoded, dtype=float))

    if other_cols:
        rest = df[other_cols].copy()
        for c in rest.select_dtypes("bool").columns:
            rest[c] = rest[c].astype(int)
        parts.append(np.asarray(rest, dtype=float))

    X = np.hstack(parts) if len(parts) > 1 else (parts[0] if parts else np.empty((len(df), 0)))
    return np.asarray(SimpleImputer(strategy="mean").fit_transform(X))


# ===========================================================================
# Lazy-loaded, cached encoders for models 3 & 4
# (re-fitted on the original CSVs to reproduce training-time category mapping)
# ===========================================================================

@lru_cache(maxsize=1)
def _load_breach_encoder() -> OrdinalEncoder | None:
    """
    Fit OrdinalEncoder on the method column of the breaches CSV.
    Using the same data as training → same alphabetical sort → same mapping.
    TECH DEBT (TD-001): Replace with saved encoder once models are retrained.
    """
    csv_path = _DATA_DIR / "website" / "raw" / "worlds_biggest_breaches_cleaned.csv"
    if not csv_path.exists():
        logger.warning("Breach CSV not found; encoder unavailable: %s", csv_path)
        return None
    try:
        df = pd.read_csv(csv_path)
        df["method_clean"] = df["method"].fillna("unknown").str.split(",").str[0].str.strip()
        oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        oe.fit(df[["method_clean"]].astype(str))
        logger.info("Breach OrdinalEncoder fitted successfully.")
        return oe
    except Exception as exc:
        logger.exception("Failed to fit breach encoder: %s", exc)
        return None


@lru_cache(maxsize=1)
def _load_file_sig_encoder() -> OrdinalEncoder | None:
    """
    Fit OrdinalEncoder on the Category column of the file signatures CSV.
    TECH DEBT (TD-001): Replace with saved encoder once models are retrained.
    """
    csv_path = _DATA_DIR / "file" / "raw" / "file_signatures.csv"
    if not csv_path.exists():
        logger.warning("File signatures CSV not found; encoder unavailable: %s", csv_path)
        return None
    try:
        df = pd.read_csv(csv_path)
        df["category_clean"] = df["Category"].fillna("Unknown")
        oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        oe.fit(df[["category_clean"]].astype(str))
        logger.info("File signatures OrdinalEncoder fitted successfully.")
        return oe
    except Exception as exc:
        logger.exception("Failed to fit file sig encoder: %s", exc)
        return None


# ===========================================================================
# Feature extraction helpers
# ===========================================================================

def extract_url_lexical_features(url: str) -> dict[str, float]:
    """
    Extract the 18 lexical features used to train online_valid_model.
    All features are derived purely from the raw URL string.
    Matches exactly the computation in train_cybermind.py::train_online_valid().
    """
    url = str(url)
    url_len = len(url)
    num_slashes = url.count("/")
    num_digits = sum(c.isdigit() for c in url)
    num_special = len(re.findall(r"[^a-zA-Z0-9./:-]", url))

    # domain_len: length of the 3rd slash-separated segment (index 2)
    parts = url.split("/")
    domain_len = len(parts[2]) if len(parts) > 2 else 0

    return {
        "url_len":       float(url_len),
        "has_https":     float(url.startswith("https")),
        "num_dots":      float(url.count(".")),
        "num_slashes":   float(num_slashes),
        "num_hyphens":   float(url.count("-")),
        "num_digits":    float(num_digits),
        "num_at":        float(url.count("@")),
        "num_equals":    float(url.count("=")),
        "num_ampersand": float(url.count("&")),
        "num_special":   float(num_special),
        "has_ip":        float(bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url))),
        "path_depth":    float(min(num_slashes, 10)),
        "query_len":     float(len(url.split("?", 1)[1]) if "?" in url else 0),
        "domain_len":    float(domain_len),
        "dot_slash_ratio":  float(url.count(".")) / max(float(num_slashes), 1.0),
        "special_ratio":    float(num_special) / max(float(url_len), 1.0),
        "digit_ratio":      float(num_digits) / max(float(url_len), 1.0),
        "hyphen_ratio":     float(url.count("-")) / max(float(url_len), 1.0),
    }


def build_phishing_url_feature_row(features: dict[str, Any]) -> np.ndarray:
    """
    Build the 50-column PhiUSIIL feature row from a dict of URL features.
    Missing keys are filled with 0. All columns are numeric — no encoder needed.
    The dict can come from url_service.analyze() fields or be built manually.
    """
    row = {col: float(features.get(col, 0)) for col in PHISHING_URL_FEATURE_COLS}
    df = pd.DataFrame([row])[PHISHING_URL_FEATURE_COLS]
    return SimpleImputer(strategy="mean").fit_transform(df.values.astype(float))


def build_breach_feature_row(
    records_log: float,
    sensitivity: float,
    year_norm: float,
    org_len: int,
    has_story: int,
    method_clean: str,
) -> np.ndarray | None:
    """
    Build the 6-feature row for breaches_model.
    Feature order matches BREACH_FEATURE_COLS exactly.
    method_clean is the text column → requires OrdinalEncoder.
    """
    oe = _load_breach_encoder()
    if oe is None:
        return None

    row = pd.DataFrame([{
        "records_log":  float(records_log),
        "sensitivity":  float(sensitivity),
        "year_norm":    float(year_norm),
        "org_len":      float(org_len),
        "has_story":    float(has_story),
        "method_clean": str(method_clean),
    }])

    # Training encode_features order: text cols first, then numeric
    text_cols = ["method_clean"]
    return _encode_features_with_fitted_oe(row[BREACH_FEATURE_COLS], oe, text_cols)


def build_file_sig_feature_row(
    hex_sig: str,
    extension: str,
    description: str,
    category: str,
    offset: float = 0.0,
) -> np.ndarray | None:
    """
    Build the 9-feature row for file_signatures_model from raw file attributes.
    Mirrors train_cybermind.py::train_file_signatures() feature derivation.
    """
    oe = _load_file_sig_encoder()
    if oe is None:
        return None

    hex_sig = str(hex_sig) if hex_sig else ""
    ext = str(extension) if extension else ""
    desc = str(description) if description else ""
    cat = str(category) if category else "Unknown"

    hex_spaces = hex_sig.count(" ")
    hex_bytes = hex_spaces + 1 if hex_sig.strip() else 0
    hex_unique = len(set(hex_sig.replace(" ", "")))
    has_wild = int(bool(re.search(r"\?|xx", hex_sig, re.IGNORECASE)))

    row = pd.DataFrame([{
        "category_clean": cat,
        "hex_len":        float(len(hex_sig)),
        "hex_spaces":     float(hex_spaces),
        "hex_bytes":      float(hex_bytes),
        "hex_unique":     float(hex_unique),
        "has_wild":       float(has_wild),
        "ext_len":        float(len(ext)),
        "desc_len":       float(len(desc)),
        "offset_val":     float(offset),
    }])

    text_cols = ["category_clean"]
    return _encode_features_with_fitted_oe(row[FILE_SIG_FEATURE_COLS], oe, text_cols)


# ===========================================================================
# High-level prediction functions
# ===========================================================================

def _fmt_proba(classes: list[str], proba: np.ndarray) -> dict[str, float]:
    """Return {class_name: probability} sorted descending."""
    return dict(sorted(
        zip(classes, proba.flatten().tolist()),
        key=lambda x: x[1], reverse=True
    ))


def predict_phishing_url(features: dict[str, Any]) -> dict[str, Any]:
    """
    Run phishing_url_model on a feature dict.

    Parameters
    ----------
    features : dict mapping PHISHING_URL_FEATURE_COLS names to numeric values.
               Missing keys → 0.  Comes from the URL scanner's analysis dict.

    Returns
    -------
    {
        "label":       "Phishing" | "Legitimate",
        "confidence":  float (0–1),
        "raw_class":   "0" | "1",
        "probabilities": {"0": float, "1": float},
        "model":       "phishing_url_model",
        "available":   True | False
    }
    """
    try:
        model = model_loader.load(PHISHING_URL_MODEL_PATH)
        X = build_phishing_url_feature_row(features)
        pred = model.predict(X)[0]          # "0" or "1"
        proba = model.predict_proba(X)[0]   # shape (2,)
        classes = list(model.classes_)
        confidence = float(max(proba))
        label = "Phishing" if str(pred) == "1" else "Legitimate"
        return {
            "label":       label,
            "confidence":  confidence,
            "raw_class":   str(pred),
            "probabilities": _fmt_proba(classes, proba),
            "model":       "phishing_url_model",
            "available":   True,
        }
    except Exception as exc:
        logger.exception("predict_phishing_url failed: %s", exc)
        return {"available": False, "error": str(exc)}


def predict_brand_impersonation(url: str) -> dict[str, Any]:
    """
    Run online_valid_model on a raw URL string.
    Predicts which real-world brand (if any) a phishing URL is impersonating.

    Returns
    -------
    {
        "brand":        str  (e.g. "PayPal", "Other"),
        "confidence":   float (0–1),
        "probabilities": {brand: float, ...},
        "model":        "online_valid_model",
        "available":    True | False
    }
    """
    try:
        model = model_loader.load(ONLINE_VALID_MODEL_PATH)
        feat = extract_url_lexical_features(url)
        df = pd.DataFrame([feat])[ONLINE_VALID_FEATURE_COLS]
        X = SimpleImputer(strategy="mean").fit_transform(df.values.astype(float))
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        confidence = float(max(proba))
        return {
            "brand":         str(pred),
            "confidence":    confidence,
            "probabilities": _fmt_proba(classes, proba),
            "model":         "online_valid_model",
            "available":     True,
        }
    except Exception as exc:
        logger.exception("predict_brand_impersonation failed: %s", exc)
        return {"available": False, "error": str(exc)}


def predict_breach_sector(
    records_log: float,
    sensitivity: float,
    year_norm: float,
    org_len: int,
    has_story: int,
    method_clean: str,
) -> dict[str, Any]:
    """
    Run breaches_model to predict the industry sector for a breach record.

    Returns
    -------
    {
        "sector":       str  (e.g. "tech", "finance"),
        "confidence":   float (0–1),
        "probabilities": {sector: float, ...},
        "model":        "breaches_model",
        "available":    True | False,
        "experimental": True  (always True — model accuracy ~36%)
    }
    """
    try:
        model = model_loader.load(BREACHES_MODEL_PATH)
        X = build_breach_feature_row(
            records_log, sensitivity, year_norm, org_len, has_story, method_clean
        )
        if X is None:
            return {"available": False, "error": "Encoder not available"}
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        confidence = float(max(proba))
        return {
            "sector":        str(pred),
            "confidence":    confidence,
            "probabilities": _fmt_proba(classes, proba),
            "model":         "breaches_model",
            "available":     True,
            "experimental":  True,
        }
    except Exception as exc:
        logger.exception("predict_breach_sector failed: %s", exc)
        return {"available": False, "error": str(exc)}


def predict_file_risk(
    hex_sig: str = "",
    extension: str = "",
    description: str = "",
    category: str = "Unknown",
    offset: float = 0.0,
) -> dict[str, Any]:
    """
    Run file_signatures_model to predict the risk level of a file based on
    its hex signature / magic bytes, extension, description and category.

    Returns
    -------
    {
        "risk_level":   "Low" | "Medium" | "High",
        "confidence":   float (0–1),
        "probabilities": {"Low": float, "Medium": float, "High": float},
        "model":        "file_signatures_model",
        "available":    True | False
    }
    """
    try:
        model = model_loader.load(FILE_SIG_MODEL_PATH)
        X = build_file_sig_feature_row(hex_sig, extension, description, category, offset)
        if X is None:
            return {"available": False, "error": "Encoder not available"}
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        confidence = float(max(proba))
        return {
            "risk_level":    str(pred),
            "confidence":    confidence,
            "probabilities": _fmt_proba(classes, proba),
            "model":         "file_signatures_model",
            "available":     True,
        }
    except Exception as exc:
        logger.exception("predict_file_risk failed: %s", exc)
        return {"available": False, "error": str(exc)}
