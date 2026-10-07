"""Load, clean and enrich the UCI "Default of Credit Card Clients" dataset.

Dataset: Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining
techniques for the predictive accuracy of probability of default of credit card
clients. Expert Systems with Applications, 36(2), 2473-2480.
UCI Machine Learning Repository, dataset id 350.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

TARGET = "default"

PAY_COLS = [f"PAY_{i}" for i in range(1, 7)]
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYAMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]
RAW_FEATURES = ["LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"] + PAY_COLS + BILL_COLS + PAYAMT_COLS

SEX_LABELS = {1: "Male", 2: "Female"}
EDU_LABELS = {1: "Graduate school", 2: "University", 3: "High school", 4: "Other"}
MARRIAGE_LABELS = {1: "Married", 2: "Single", 3: "Other"}

_FILE_PATTERNS = [
    "default of credit card clients*.xls*",
    "default_of_credit_card_clients*.xls*",
    "UCI_Credit_Card*.csv",
    "credit_default*.csv",
]

INSTRUCTIONS = """Could not find the credit card default dataset.

Download it (free, open licence) from the UCI repository:
  https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
and put the file in the data/ folder (or upload it to Colab's file panel).
Accepted names: 'default of credit card clients.xls' or 'UCI_Credit_Card.csv'.
"""


def _search_dirs(data_dir=None):
    here = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
    dirs = [Path(data_dir)] if data_dir else []
    dirs += [here / "data", Path.cwd() / "data", Path.cwd().parent / "data", Path.cwd()]
    return dirs


def _find_file(data_dir=None):
    for d in _search_dirs(data_dir):
        for pattern in _FILE_PATTERNS:
            hits = sorted(d.glob(pattern)) if d.exists() else []
            if hits:
                return hits[0]
    return None


def read_raw(source, suffix=None) -> pd.DataFrame:
    """Read the raw UCI file (.xls/.xlsx/.csv) from a path or an uploaded file object."""
    suffix = (suffix or Path(str(getattr(source, "name", source))).suffix).lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    # The UCI Excel file has a row of X1..X23 labels above the real header.
    df = pd.read_excel(source, header=1, engine="xlrd")
    if "LIMIT_BAL" not in df.columns:
        if hasattr(source, "seek"):
            source.seek(0)
        df = pd.read_excel(source, header=0, engine="xlrd")
    return df


def _from_ucimlrepo() -> pd.DataFrame:
    from ucimlrepo import fetch_ucirepo  # pip install ucimlrepo

    ds = fetch_ucirepo(id=350)
    X, y = ds.data.features.copy(), ds.data.targets.copy()
    if list(X.columns)[:2] == ["X1", "X2"]:
        X.columns = ["LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"] + [
            "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"
        ] + [f"BILL_AMT{i}" for i in range(1, 7)] + [f"PAY_AMT{i}" for i in range(1, 7)]
    X[TARGET] = y.iloc[:, 0].values
    return X


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Standardise column names and fix the undocumented category codes."""
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={
        "PAY_0": "PAY_1",
        "default payment next month": TARGET,
        "default.payment.next.month": TARGET,
    })
    df = df.drop(columns=[c for c in ["ID"] if c in df.columns])
    missing = set(RAW_FEATURES + [TARGET]) - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {sorted(missing)}")
    df = df[RAW_FEATURES + [TARGET]].astype(float).round().astype(int)
    # The data dictionary lists education 1-4 and marriage 1-3, but the file also
    # contains 0, 5, 6 (education) and 0 (marriage). Fold them into "Other".
    df["EDUCATION"] = df["EDUCATION"].replace({0: 4, 5: 4, 6: 4})
    df["MARRIAGE"] = df["MARRIAGE"].replace({0: 3})
    return df.reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add readable labels and a few analyst-friendly engineered columns."""
    df = df.copy()
    df["sex_label"] = df["SEX"].map(SEX_LABELS)
    df["edu_label"] = df["EDUCATION"].map(EDU_LABELS)
    df["marriage_label"] = df["MARRIAGE"].map(MARRIAGE_LABELS)
    df["female"] = (df["SEX"] == 2).astype(int)
    df["limit_k"] = df["LIMIT_BAL"] / 1000  # credit limit in thousands
    df["limit_100k"] = df["limit_k"] / 100  # per-100k scale keeps odds ratios readable
    # PAY_x codes: -2 no consumption, -1 paid in full, 0 revolving, 1..9 months late.
    df["late_1"] = df["PAY_1"].clip(lower=0)  # months late on the latest bill
    df["max_late"] = df[PAY_COLS].clip(lower=0).max(axis=1)
    df["n_late_months"] = (df[PAY_COLS] > 0).sum(axis=1)
    df["utilization"] = (df["BILL_AMT1"] / df["LIMIT_BAL"]).clip(0, 1.5)
    df["avg_bill"] = df[BILL_COLS].mean(axis=1) / 1000  # thousands
    df["avg_payment"] = df[PAYAMT_COLS].mean(axis=1) / 1000
    owed = df["BILL_AMT1"].where(df["BILL_AMT1"] > 0)
    df["paid_ratio"] = (df["PAY_AMT1"] / owed).clip(0, 1).fillna(1.0)
    return df


def looks_official(df: pd.DataFrame) -> bool:
    """True if the data matches the published dataset: 30,000 rows, 22.12% defaults."""
    return len(df) == 30_000 and abs(df[TARGET].mean() - 0.2212) < 0.001


def load_credit_data(data_dir=None, allow_download=True, allow_synthetic=False):
    """Return (dataframe, source_description).

    Order tried: local file in data/ -> download via `ucimlrepo` -> synthetic
    practice data (only if allow_synthetic=True).
    """
    path = _find_file(data_dir)
    if path is not None:
        return add_features(clean(read_raw(path))), f"local file: {path.name}"
    if allow_download:
        try:
            return add_features(clean(_from_ucimlrepo())), "UCI repository (via ucimlrepo)"
        except Exception as exc:  # no network, package missing, etc.
            reason = f"{type(exc).__name__}: {exc}"
    else:
        reason = "download disabled"
    if allow_synthetic:
        from .synthetic import make_synthetic

        return add_features(clean(make_synthetic())), "SYNTHETIC practice data (not real)"
    raise FileNotFoundError(INSTRUCTIONS + f"\n(Automatic download also failed: {reason})")
