"""Synthetic stand-in for the UCI credit default data (same columns, similar shape).

Purpose: lets you test the notebook/app and practise offline. It is NOT real data;
never present results from it as real findings.

    python -m credit_risk.synthetic --out data/synthetic_credit_default.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


def make_synthetic(n: int = 30_000, seed: int = 42, target_rate: float = 0.2212) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = np.clip(np.round(21 + rng.gamma(2.6, 5.2, n)), 21, 75).astype(int)
    sex = np.where(rng.random(n) < 0.604, 2, 1)
    p_edu = np.array([0.353, 0.468, 0.164, 0.004, 0.009, 0.0017, 0.0005])
    edu = rng.choice([1, 2, 3, 4, 5, 6, 0], size=n, p=p_edu / p_edu.sum())
    marriage = rng.choice([1, 2, 3, 0], size=n, p=[0.455, 0.532, 0.011, 0.002])

    r = rng.normal(0, 1, n)  # hidden "riskiness" of each customer
    log_limit = (np.log(105_000) + 0.35 * (edu == 1) + 0.15 * (edu == 2)
                 + 0.008 * (age - 35) - 0.25 * r + rng.normal(0, 0.8, n))
    limit = np.clip(np.round(np.exp(log_limit), -4), 10_000, 800_000)

    cats = np.array([-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8])
    cum = [0.09, 0.28, 0.77, 0.885, 0.975, 0.99, 0.995, 0.998, 0.999, 0.9995]

    def draw_status(u):
        cuts = np.quantile(u, cum)
        return cats[np.searchsorted(cuts, u)]

    pay = [draw_status(r + rng.normal(0, 0.6, n))]
    for _ in range(5):
        fresh = draw_status(r + rng.normal(0, 0.8, n))
        pay.append(np.where(rng.random(n) < 0.75, pay[-1], fresh))

    util = np.clip(rng.beta(1.2, 2.2, n) * (1 + 0.25 * np.clip(pay[0], 0, 3)), 0, 1.4)
    bills = [limit * util]
    for _ in range(5):
        nxt = bills[-1] * rng.normal(0.95, 0.12, n) + rng.normal(0, 0.01, n) * limit
        nxt -= np.where(rng.random(n) < 0.02, rng.uniform(0, 0.1, n) * limit, 0)
        bills.append(nxt)
    bills = [np.round(b) for b in bills]

    pay_amts = []
    for k in range(6):
        prior_bill = np.clip(bills[k + 1] if k < 5 else bills[5], 0, None)
        frac = np.where(pay[k] <= -1, rng.beta(6, 1, n), rng.beta(0.8, 4, n))
        pay_amts.append(np.round(prior_bill * frac))

    paid_ratio = np.clip(pay_amts[0] / np.where(bills[0] > 0, bills[0], np.nan), 0, 1)
    paid_ratio = np.nan_to_num(paid_ratio, nan=1.0)
    z = (0.60 * np.clip(pay[0], 0, 6) + 0.20 * np.clip(pay[1], 0, 6) + 0.35 * (util - 0.4)
         - 0.30 * np.log(limit / 1e5) + 0.20 * (edu == 3) - 0.12 * (sex == 2)
         + 0.006 * (age - 35) - 0.5 * paid_ratio + 0.30 * r + rng.normal(0, 0.4, n))
    lo, hi = -15.0, 15.0
    for _ in range(60):  # bisect the intercept so the default rate hits the target
        mid = (lo + hi) / 2
        if _sigmoid(z + mid).mean() > target_rate:
            hi = mid
        else:
            lo = mid
    default = (rng.random(n) < _sigmoid(z + (lo + hi) / 2)).astype(int)

    out = {"ID": np.arange(1, n + 1), "LIMIT_BAL": limit.astype(int), "SEX": sex,
           "EDUCATION": edu, "MARRIAGE": marriage, "AGE": age}
    for name, values in zip(["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"], pay):
        out[name] = values
    for i, b in enumerate(bills, 1):
        out[f"BILL_AMT{i}"] = b.astype(int)
    for i, p in enumerate(pay_amts, 1):
        out[f"PAY_AMT{i}"] = p.astype(int)
    out["default.payment.next.month"] = default
    return pd.DataFrame(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/synthetic_credit_default.csv")
    ap.add_argument("--n", type=int, default=30_000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    make_synthetic(args.n, args.seed).to_csv(args.out, index=False)
    print(f"Wrote {args.n:,} SYNTHETIC rows to {args.out}")
