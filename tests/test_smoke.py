"""Smoke tests: data pipeline + every Streamlit page renders without errors.

Run from the repo root:  pytest -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from credit_risk.data import add_features, clean, load_credit_data  # noqa: E402
from credit_risk.synthetic import make_synthetic  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return add_features(clean(make_synthetic(n=6000, seed=1)))


def test_clean_fixes_undocumented_codes(df):
    assert set(df["EDUCATION"].unique()) <= {1, 2, 3, 4}
    assert set(df["MARRIAGE"].unique()) <= {1, 2, 3}
    assert set(df["default"].unique()) == {0, 1}


def test_engineered_features_are_sane(df):
    assert (df["late_1"] >= 0).all()
    assert df["utilization"].between(0, 1.5).all()
    assert df["paid_ratio"].between(0, 1).all()
    assert np.allclose(df["limit_100k"] * 100, df["limit_k"])


def test_loader_raises_helpful_error_when_no_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import credit_risk.data as data

    monkeypatch.setattr(data, "_find_file", lambda *_: None)
    with pytest.raises(FileNotFoundError, match="archive.ics.uci.edu"):
        load_credit_data(allow_download=False)


PAGES = ["Start here", "1 · Sampling & CIs", "2 · Hypothesis tests", "3 · Linear regression",
         "4 · Logistic regression", "5 · Score an applicant"]


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders(page):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=120).run()
    assert not at.exception, at.exception
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, at.exception


def test_interactive_branches():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=180).run()
    # Hypothesis page: categorical branch + the p-value-vs-sample-size curve
    at.sidebar.radio[0].set_value("2 · Hypothesis tests").run()
    at.radio[0].set_value("Category").run()
    assert not at.exception, at.exception
    at.checkbox[0].check().run()
    assert not at.exception, at.exception
    # Linear regression: log outcome + robust SE
    at.sidebar.radio[0].set_value("3 · Linear regression").run()
    at.checkbox[0].check().run()
    at.checkbox[1].check().run()
    assert not at.exception, at.exception
    # Logistic: cost-optimal cut-off
    at.sidebar.radio[0].set_value("4 · Logistic regression").run()
    at.checkbox[0].check().run()
    assert not at.exception, at.exception
