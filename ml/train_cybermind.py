"""
CyberMind AI - Multi-Dataset Model Training Script

Trains one RandomForestClassifier per dataset, using a genuine label
column from each source (no synthetic/derived targets, no leaked
features). Evaluated with 5-fold Stratified Cross-Validation using
standard classification metrics: Accuracy, Precision, Recall, F1-Score,
ROC-AUC and a Confusion Matrix.

Why classification metrics (not MAE/RMSE/R²)?
All four target columns used here are categorical (binary or multi-class
labels), not continuous numbers -- so this is a classification problem
end to end, and Accuracy/Precision/Recall/F1/ROC-AUC are the correct,
standard evaluation metrics for that. MAE/RMSE/R² are regression
metrics and are not used anywhere in this script because none of the
four tasks is genuinely a regression problem.

Run: python -m ml.train_cybermind
"""

from __future__ import annotations

import io
import json
import sys
import warnings

if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer

from sklearn.metrics import confusion_matrix as sk_confusion_matrix

from ml.metrics import metrics as metrics_engine

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

METRICS_PATH = MODEL_DIR / "cybermind_metrics.json"


# ── Model factory ────────────────────────────────────────────────────────
def make_clf(**kw) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=kw.get("n_estimators", 200),
        max_depth=kw.get("max_depth", None),
        min_samples_leaf=kw.get("min_samples_leaf", 2),
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )


# ── Generic preprocessor ────────────────────────────────────────────────
def encode_features(df: pd.DataFrame) -> np.ndarray:
    """
    Ordinal-encode any text columns, cast booleans to int,
    impute missing numeric values with the column mean.

    Builds the numeric matrix directly (rather than writing encoded
    values back into the DataFrame) to avoid pandas silently keeping
    a text dtype on the reassigned column, which would drop it from
    the final numeric feature matrix.
    """
    df = df.copy()

    text_cols = [
        c for c in df.columns
        if df[c].dtype == object or pd.api.types.is_string_dtype(df[c])
    ]
    other_cols = [c for c in df.columns if c not in text_cols]

    parts = []

    if text_cols:
        oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        encoded = oe.fit_transform(df[text_cols].astype(str))
        parts.append(np.asarray(encoded, dtype=float))

    if other_cols:
        rest = df[other_cols].copy()
        for c in rest.select_dtypes("bool").columns:
            rest[c] = rest[c].astype(int)
        parts.append(np.asarray(rest, dtype=float))

    X = np.hstack(parts) if len(parts) > 1 else parts[0]
    return np.asarray(SimpleImputer(strategy="mean").fit_transform(X))


# ── Cross-validated classification evaluation ───────────────────────────
def cv_classification(
    X: np.ndarray,
    y: np.ndarray,
    n_splits: int = 5,
    **kw,
) -> dict[str, Any]:
    """
    Stratified k-fold CV. Returns averaged Accuracy / Precision /
    Recall / F1 / ROC-AUC, plus a confusion matrix summed across folds.
    """
    classes = np.unique(y)
    is_binary = len(classes) == 2

    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    accs, precs, recs, f1s, aucs = [], [], [], [], []
    confusion_total = np.zeros((len(classes), len(classes)), dtype=int)

    for train_idx, test_idx in kf.split(X, y):
        model = make_clf(**kw)
        model.fit(X[train_idx], y[train_idx])

        y_pred = model.predict(X[test_idx])
        y_true = y[test_idx]

        proba = model.predict_proba(X[test_idx])
        y_score = proba[:, 1] if is_binary else proba

        accs.append(metrics_engine.accuracy(y_true, y_pred))
        precs.append(metrics_engine.precision(y_true, y_pred))
        recs.append(metrics_engine.recall(y_true, y_pred))
        f1s.append(metrics_engine.f1(y_true, y_pred))

        auc = metrics_engine.roc_auc(y_true, y_score)
        if auc is not None:
            aucs.append(auc)

        confusion_total += sk_confusion_matrix(y_true, y_pred, labels=classes)

    return {
        "accuracy": round(float(np.mean(accs)), 4),
        "precision": round(float(np.mean(precs)), 4),
        "recall": round(float(np.mean(recs)), 4),
        "f1_score": round(float(np.mean(f1s)), 4),
        "roc_auc": round(float(np.mean(aucs)), 4) if aucs else None,
        "accuracy_std": round(float(np.std(accs)), 4),
        "confusion_matrix": confusion_total.tolist(),
        "classes": [str(c) for c in classes],
    }


def build_result(
    name: str,
    pkl_path: Path,
    cv_result: dict[str, Any],
    n_samples: int,
    n_features: int,
    n_classes: int,
) -> dict[str, Any]:
    result = {
        "dataset": name,
        "model_file": pkl_path.name,
        "model_type": "RandomForestClassifier",
        "task": "Binary Classification" if n_classes == 2 else "Multi-Class Classification",
        "accuracy": cv_result["accuracy"],
        "precision": cv_result["precision"],
        "recall": cv_result["recall"],
        "f1_score": cv_result["f1_score"],
        "roc_auc": cv_result["roc_auc"],
        "samples": int(n_samples),
        "feature_count": int(n_features),
        "class_count": int(n_classes),
    }
    auc_txt = f"{cv_result['roc_auc']:.4f}" if cv_result["roc_auc"] is not None else "n/a"
    print(
        f"  Accuracy={result['accuracy']*100:.2f}%  "
        f"Precision={result['precision']:.4f}  "
        f"Recall={result['recall']:.4f}  "
        f"F1={result['f1_score']:.4f}  "
        f"ROC-AUC={auc_txt}  "
        f"-> saved: {pkl_path.name}"
    )
    return result


# ══════════════════════════════════════════════════════════════════════════
# DATASET 1 - PhiUSIIL Phishing URL  (binary: label 0/1)
# Model: phishing_url_model.pkl
# ══════════════════════════════════════════════════════════════════════════
def train_phishing_url() -> dict:
    path = BASE_DIR / "data/datasets/url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
    pkl = MODEL_DIR / "phishing_url_model.pkl"
    print(f"\n[1] PhiUSIIL Phishing URL Dataset -> {pkl.name}")

    df = pd.read_csv(path, low_memory=False)
    y = np.asarray(df["label"].astype(str))
    # Drop identifier/free-text columns that would leak the source URL
    # itself rather than teach generalizable phishing patterns.
    drop_cols = ["FILENAME", "URL", "Domain", "TLD", "Title", "label"]
    X = encode_features(df.drop(columns=[c for c in drop_cols if c in df.columns]))

    cv_result = cv_classification(X, y, n_estimators=200, max_depth=20, min_samples_leaf=2)

    final_model = make_clf(n_estimators=200, max_depth=20, min_samples_leaf=2)
    final_model.fit(X, y)
    joblib.dump(final_model, pkl)

    return build_result("PhiUSIIL Phishing URL", pkl, cv_result, len(y), X.shape[1], len(np.unique(y)))


# ══════════════════════════════════════════════════════════════════════════
# DATASET 2 - Online-Valid Phishing URLs  (multi-class: impersonated brand)
# Target: `target` column (which real-world brand a phishing URL mimics),
# collapsed to the 9 most frequent brands + "Other".
# Model: online_valid_model.pkl
# ══════════════════════════════════════════════════════════════════════════
def train_online_valid() -> dict:
    path = BASE_DIR / "data/datasets/url/raw/online-valid.csv"
    pkl = MODEL_DIR / "online_valid_model.pkl"
    print(f"\n[2] Online-Valid Phishing URLs Dataset -> {pkl.name}")

    df = pd.read_csv(path)
    df = df.dropna(subset=["url", "target"])

    top_brands = df["target"].value_counts().nlargest(9).index
    df["brand_class"] = df["target"].where(df["target"].isin(top_brands), "Other")

    # Purely lexical URL features -- nothing derived from the label.
    url = df["url"].astype(str)
    df["url_len"] = url.str.len()
    df["has_https"] = url.str.startswith("https").astype(int)
    df["num_dots"] = url.str.count(r"\.")
    df["num_slashes"] = url.str.count("/")
    df["num_hyphens"] = url.str.count("-")
    df["num_digits"] = url.str.count(r"\d")
    df["num_at"] = url.str.count("@")
    df["num_equals"] = url.str.count("=")
    df["num_ampersand"] = url.str.count("&")
    df["num_special"] = url.str.count(r"[^a-zA-Z0-9./:-]")
    df["has_ip"] = url.str.contains(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}").astype(int)
    df["path_depth"] = url.str.count("/").clip(0, 10)
    df["query_len"] = url.apply(lambda u: len(u.split("?", 1)[1]) if "?" in u else 0)
    df["domain_len"] = url.apply(lambda u: len(u.split("/")[2]) if len(u.split("/")) > 2 else 0)
    df["dot_slash_ratio"] = df["num_dots"] / df["num_slashes"].clip(lower=1)
    df["special_ratio"] = df["num_special"] / df["url_len"].clip(lower=1)
    df["digit_ratio"] = df["num_digits"] / df["url_len"].clip(lower=1)
    df["hyphen_ratio"] = df["num_hyphens"] / df["url_len"].clip(lower=1)

    feature_cols = [
        "url_len", "has_https", "num_dots", "num_slashes", "num_hyphens",
        "num_digits", "num_at", "num_equals", "num_ampersand", "num_special",
        "has_ip", "path_depth", "query_len", "domain_len",
        "dot_slash_ratio", "special_ratio", "digit_ratio", "hyphen_ratio",
    ]
    X = encode_features(df[feature_cols])
    y = np.asarray(df["brand_class"].astype(str))

    cv_result = cv_classification(X, y, n_estimators=200, max_depth=15, min_samples_leaf=2)

    final_model = make_clf(n_estimators=200, max_depth=15, min_samples_leaf=2)
    final_model.fit(X, y)
    joblib.dump(final_model, pkl)

    return build_result("Online-Valid Phishing URLs", pkl, cv_result, len(y), X.shape[1], len(np.unique(y)))


# ══════════════════════════════════════════════════════════════════════════
# DATASET 3 - World's Biggest Data Breaches  (multi-class: industry sector)
# Target: `sector` column, cleaned to its primary category, rare
# sectors (<15 samples, e.g. "military") dropped to keep CV stable.
# Model: breaches_model.pkl
# ══════════════════════════════════════════════════════════════════════════
def train_breaches() -> dict:
    path = BASE_DIR / "data/datasets/website/raw/worlds_biggest_breaches_cleaned.csv"
    pkl = MODEL_DIR / "breaches_model.pkl"
    print(f"\n[3] World's Biggest Data Breaches Dataset -> {pkl.name}")

    df = pd.read_csv(path)
    df["sector_clean"] = df["sector"].fillna("unknown").str.split(",").str[0].str.strip()

    counts = df["sector_clean"].value_counts()
    keep_sectors = counts[counts >= 15].index
    df = df[df["sector_clean"].isin(keep_sectors)].copy()

    df["records_log"] = np.log1p(pd.to_numeric(df["records lost"], errors="coerce").fillna(0))
    df["sensitivity"] = pd.to_numeric(df["data sensitivity"], errors="coerce").fillna(2.0)
    df["year_norm"] = (pd.to_numeric(df["year"], errors="coerce").fillna(2010) - 2004) / 18
    df["org_len"] = df["organisation"].fillna("").str.len()
    df["has_story"] = df["interesting story"].notna().astype(int)
    df["method_clean"] = df["method"].fillna("unknown").str.split(",").str[0].str.strip()

    feature_cols = ["records_log", "sensitivity", "year_norm", "org_len", "has_story", "method_clean"]
    X = encode_features(df[feature_cols])
    y = np.asarray(df["sector_clean"].astype(str))

    cv_result = cv_classification(X, y, n_estimators=200, max_depth=10, min_samples_leaf=2)

    final_model = make_clf(n_estimators=200, max_depth=10, min_samples_leaf=2)
    final_model.fit(X, y)
    joblib.dump(final_model, pkl)

    return build_result("World's Biggest Data Breaches", pkl, cv_result, len(y), X.shape[1], len(np.unique(y)))


# ══════════════════════════════════════════════════════════════════════════
# DATASET 4 - File Signatures  (multi-class: RiskLevel Low/Medium/High)
# Model: file_signatures_model.pkl
# ══════════════════════════════════════════════════════════════════════════
def train_file_signatures() -> dict:
    path = BASE_DIR / "data/datasets/file/raw/file_signatures.csv"
    pkl = MODEL_DIR / "file_signatures_model.pkl"
    print(f"\n[4] File Signatures Risk Dataset -> {pkl.name}")

    df = pd.read_csv(path)
    df = df.dropna(subset=["RiskLevel"])

    hexsig = df["HexSignature"].fillna("")
    df["hex_len"] = hexsig.str.len()
    df["hex_spaces"] = hexsig.str.count(" ")
    df["hex_bytes"] = df["hex_spaces"] + 1
    df["hex_unique"] = hexsig.apply(lambda h: len(set(h.replace(" ", ""))))
    df["has_wild"] = hexsig.str.contains(r"\?|xx", na=False).astype(int)
    df["ext_len"] = df["Extension"].fillna("").str.len()
    df["desc_len"] = df["Description"].fillna("").str.len()
    df["offset_val"] = pd.to_numeric(df["Offset"], errors="coerce").fillna(0)
    df["category_clean"] = df["Category"].fillna("Unknown")

    feature_cols = [
        "category_clean", "hex_len", "hex_spaces", "hex_bytes",
        "hex_unique", "has_wild", "ext_len", "desc_len", "offset_val",
    ]
    X = encode_features(df[feature_cols])
    y = np.asarray(df["RiskLevel"].astype(str))

    cv_result = cv_classification(X, y, n_estimators=200, max_depth=10, min_samples_leaf=2)

    final_model = make_clf(n_estimators=200, max_depth=10, min_samples_leaf=2)
    final_model.fit(X, y)
    joblib.dump(final_model, pkl)

    return build_result("File Signatures Risk", pkl, cv_result, len(y), X.shape[1], len(np.unique(y)))


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("  CyberMind AI - Multi-Dataset Training (Classification Metrics)")
    print("=" * 70)

    results = [
        train_phishing_url(),
        train_online_valid(),
        train_breaches(),
        train_file_signatures(),
    ]

    avg_acc = float(np.mean([r["accuracy"] for r in results]))
    avg_prec = float(np.mean([r["precision"] for r in results]))
    avg_rec = float(np.mean([r["recall"] for r in results]))
    avg_f1 = float(np.mean([r["f1_score"] for r in results]))
    aucs = [r["roc_auc"] for r in results if r["roc_auc"] is not None]
    avg_auc = float(np.mean(aucs)) if aucs else None

    print("\n" + "=" * 70)
    print("  AVERAGE METRICS  (4 datasets, 5-fold Stratified CV)")
    print("=" * 70)
    print(f"  Avg Accuracy  : {avg_acc*100:.2f}%")
    print(f"  Avg Precision : {avg_prec:.4f}")
    print(f"  Avg Recall    : {avg_rec:.4f}")
    print(f"  Avg F1-Score  : {avg_f1:.4f}")
    print(f"  Avg ROC-AUC   : {avg_auc:.4f}" if avg_auc is not None else "  Avg ROC-AUC   : n/a")

    metrics_out = {
        "accuracy": round(avg_acc, 4),
        "precision": round(avg_prec, 4),
        "recall": round(avg_rec, 4),
        "f1_score": round(avg_f1, 4),
        "roc_auc": round(avg_auc, 4) if avg_auc is not None else None,
        "model_type": "RandomForestClassifier",
        "evaluation": "5-fold Stratified Cross-Validation",
        "dataset": "Multi-Dataset (4 CSV sources)",
        "per_dataset": results,
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_out, f, indent=2)

    print(f"\n[OK] Metrics saved  -> {METRICS_PATH.name}")
    print("[OK] All done! Individual .pkl files saved:")
    for r in results:
        auc_txt = f"{r['roc_auc']:.4f}" if r["roc_auc"] is not None else "n/a"
        print(f"    {r['model_file']:30s}  Acc={r['accuracy']*100:6.2f}%  F1={r['f1_score']:.4f}  AUC={auc_txt}")

    return metrics_out


if __name__ == "__main__":
    main()