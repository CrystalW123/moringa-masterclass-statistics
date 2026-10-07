"""Credit Risk & Inference Lab: an interactive companion to the masterclass notebook.

Run locally:   streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import streamlit as st
from matplotlib.ticker import PercentFormatter
from scipy import stats
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.proportion import proportion_confint

from credit_risk.data import add_features, clean, load_credit_data, looks_official, read_raw

BLUE, RED, GREY = "#2a6f97", "#c0392b", "#8a8f98"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})

st.set_page_config(page_title="Credit Risk & Inference Lab", page_icon="📊", layout="wide")


# ----------------------------------------------------------------------------- data
@st.cache_data(show_spinner="Loading data...")
def get_data():
    return load_credit_data(allow_synthetic=True)


@st.cache_data(show_spinner="Reading uploaded file...")
def get_uploaded(file_bytes: bytes, name: str):
    import io

    buffer = io.BytesIO(file_bytes)
    return add_features(clean(read_raw(buffer, suffix=Path(name).suffix)))


def fmt_p(p):
    if p is None or np.isnan(p):
        return "n/a"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def show(fig):
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


# ----------------------------------------------------------------------------- pages
def page_home(df, source):
    st.title("Credit Risk & Inference Lab")
    st.markdown(
        "Move from **describing** data to **concluding** from it. "
        "Every page is a live version of a section from the masterclass notebook: "
        "change a slider, watch what happens to the uncertainty and the decision."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", f"{len(df):,}")
    c2.metric("Default rate", f"{df['default'].mean():.1%}")
    c3.metric("Average credit limit", f"{df['limit_k'].mean():,.0f}k")
    st.markdown(
        """
**The question behind every page:** *a lender has records of past credit-card customers. Who should it approve, and how sure can it be?*

| Page | Try this |
|---|---|
| **1 · Sampling & CIs** | Raise the sample size. What happens to the width of the intervals? Raise the confidence level. What's the trade-off? |
| **2 · Hypothesis tests** | Shrink the sample size and watch a real difference lose its "significance". |
| **3 · Linear regression** | Predict monthly bills. Add and remove predictors, then check the residual plot. |
| **4 · Logistic regression** | Move the cut-off and the cost of a bad loan. Where does total cost bottom out? |
| **5 · Score an applicant** | Change one input at a time and see which factors move the risk. |
"""
    )
    st.caption(
        "Data: Yeh & Lien (2009), UCI Machine Learning Repository, 'Default of Credit Card Clients' (Taiwan, 2005). "
        "Educational demo only, not a real credit-decision tool."
    )


def page_sampling(df):
    st.header("1 · Sampling, confidence intervals and uncertainty")
    st.markdown(
        "**Analogy:** tasting soup. One spoonful tells you about the pot, but every spoonful tastes slightly different. "
        "Here the whole portfolio is the pot, and each 'analyst' tastes one spoonful (a random sample) and reports a "
        "confidence interval. The dashed line is the truth that, in real life, nobody gets to see."
    )
    metric = st.radio("What are we estimating?", ["Default rate", "Average credit limit (k)"], horizontal=True)
    c1, c2, c3, c4 = st.columns(4)
    n = c1.slider("Sample size (n)", 20, 5000, 200, step=10)
    conf = c2.slider("Confidence level", 0.80, 0.99, 0.95, 0.01)
    reps = c3.select_slider("Number of analysts", [20, 50, 100, 200], value=100)
    seed = c4.number_input("Random seed (change to redraw)", 0, 10_000, 3)

    is_rate = metric == "Default rate"
    values = df["default"].to_numpy() if is_rate else df["limit_k"].to_numpy()
    truth = values.mean()
    rng = np.random.default_rng(int(seed))

    rows = []
    for _ in range(reps):
        s = rng.choice(values, n, replace=False)
        if is_rate:
            lo, hi = proportion_confint(int(s.sum()), n, alpha=1 - conf, method="wilson")
        else:
            lo, hi = stats.t.interval(conf, n - 1, loc=s.mean(), scale=stats.sem(s))
        rows.append((s.mean(), lo, hi))
    res = pd.DataFrame(rows, columns=["estimate", "low", "high"])
    res["caught"] = (res["low"] <= truth) & (truth <= res["high"])

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, r in res.iterrows():
        color = BLUE if r["caught"] else RED
        ax.plot([r["low"], r["high"]], [i, i], color=color, lw=1.8 if reps <= 100 else 1.1)
        ax.plot(r["estimate"], i, "o", ms=2.5, color=color)
    ax.axvline(truth, color="black", ls="--", label="true value")
    ax.set_yticks([])
    ax.set_xlabel(metric)
    if is_rate:
        ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_title(f"{reps} analysts, each with n = {n}: red intervals missed the truth")
    ax.legend(loc="upper right")
    show(fig)

    m1, m2, m3 = st.columns(3)
    m1.metric("Intervals that caught the truth", f"{res['caught'].mean():.0%}", help="Should be close to the confidence level. It bounces around when there are few analysts, so try 200.")
    m2.metric("Average interval width", f"{(res['high'] - res['low']).mean():.3f}" if is_rate else f"{(res['high'] - res['low']).mean():.1f}k")
    first = res.iloc[0]
    fmt = (lambda v: f"{v:.1%}") if is_rate else (lambda v: f"{v:.1f}k")
    m3.metric("Truth", fmt(truth))
    st.info(
        f"**In real life you get just one sample.** Analyst #1 would report {fmt(first['estimate'])} "
        f"with a {conf:.0%} interval of {fmt(first['low'])} to {fmt(first['high'])}. "
        f"The method captures the truth about {conf:.0%} of the time, but you never know if *this* interval is one of the misses."
    )
    st.caption("Try: n from 100 to 400 roughly halves the width (square-root law). Confidence 80% -> 99% widens intervals but misses less often.")


NUMERIC_VARS = {
    "Credit limit (k)": "limit_k",
    "Age": "AGE",
    "Credit utilization (bill / limit)": "utilization",
    "Share of latest bill paid": "paid_ratio",
    "Average monthly bill (k)": "avg_bill",
    "Months late on latest bill": "late_1",
}
CATEGORICAL_VARS = {"Sex": "sex_label", "Education": "edu_label", "Marital status": "marriage_label"}


def effect_label(value, kind):
    v = abs(value)
    cuts = (0.2, 0.5, 0.8) if kind == "d" else (0.1, 0.3, 0.5)
    return ["negligible", "small", "medium", "large"][int(np.searchsorted(cuts, v, side="right"))]


def run_test(s: pd.DataFrame, kind: str, col: str) -> dict:
    """Compare defaulters and non-defaulters on one variable."""
    if kind == "numeric":
        g1, g0 = s.loc[s["default"] == 1, col], s.loc[s["default"] == 0, col]
        if len(g1) < 3 or len(g0) < 3:
            return {"p": np.nan}
        _, p = stats.ttest_ind(g1, g0, equal_var=False)
        diff = g1.mean() - g0.mean()
        se = np.sqrt(g1.var(ddof=1) / len(g1) + g0.var(ddof=1) / len(g0))
        pooled = np.sqrt(((len(g1) - 1) * g1.var(ddof=1) + (len(g0) - 1) * g0.var(ddof=1)) / (len(g1) + len(g0) - 2))
        d = diff / pooled if pooled > 0 else np.nan
        return {"p": p, "diff": diff, "ci": (diff - 1.96 * se, diff + 1.96 * se), "effect": d, "effect_kind": "d",
                "means": (g0.mean(), g1.mean()), "test": "Welch t-test"}
    ct = pd.crosstab(s[col], s["default"])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"p": np.nan}
    chi2, p, _, _ = stats.chi2_contingency(ct, correction=False)
    v = np.sqrt(chi2 / (len(s) * (min(ct.shape) - 1)))
    rates = ct[1] / ct.sum(axis=1)
    return {"p": p, "effect": v, "effect_kind": "V", "table": ct, "rates": rates, "test": "Chi-square test of independence"}


def page_tests(df):
    st.header("2 · Hypothesis testing: is it real, or just luck?")
    st.markdown(
        "**Analogy:** a courtroom. The 'defendant' (H0) is *there is no difference*. We reject it only if the evidence would be very "
        "surprising under H0. **p-value** = how surprising. **Effect size** = how big the difference is. You need both."
    )
    c1, c2 = st.columns(2)
    kind_label = c1.radio("Compare defaulters and non-defaulters on a...", ["Number", "Category"], horizontal=True)
    if kind_label == "Number":
        name = c2.selectbox("Variable", list(NUMERIC_VARS))
        col, kind = NUMERIC_VARS[name], "numeric"
    else:
        name = c2.selectbox("Variable", list(CATEGORICAL_VARS))
        col, kind = CATEGORICAL_VARS[name], "categorical"

    c3, c4, c5 = st.columns(3)
    n = c3.slider("Pretend you only had this many customers", 100, len(df), min(2000, len(df)), step=100)
    alpha = c4.select_slider("Significance level (alpha)", [0.01, 0.05, 0.10], value=0.05)
    seed = c5.number_input("Random seed", 0, 10_000, 7)
    s = df.sample(n, random_state=int(seed))
    out = run_test(s, kind, col)
    if np.isnan(out["p"]):
        st.warning("Not enough data in one of the groups. Increase the sample size.")
        return

    a, b, c = st.columns(3)
    a.metric("p-value", fmt_p(out["p"]))
    b.metric(f"Verdict at alpha = {alpha}", "Significant" if out["p"] < alpha else "Not significant")
    c.metric("Effect size" + (" (Cohen's d)" if out["effect_kind"] == "d" else " (Cramer's V)"),
             f"{out['effect']:.2f}", help=effect_label(out["effect"], out["effect_kind"]))
    st.caption(f"Test used: {out['test']}. Effect is **{effect_label(out['effect'], out['effect_kind'])}**.")

    left, right = st.columns(2)
    with left:
        if kind == "numeric":
            fig, ax = plt.subplots(figsize=(6, 3.6))
            lim = s[col].quantile([0.005, 0.995]).to_numpy()
            bins = np.linspace(lim[0], lim[1], 30)
            ax.hist(s.loc[s["default"] == 0, col], bins=bins, alpha=0.6, density=True, color=BLUE, label="repaid")
            ax.hist(s.loc[s["default"] == 1, col], bins=bins, alpha=0.6, density=True, color=RED, label="defaulted")
            ax.set_xlabel(name); ax.set_yticks([]); ax.legend()
            show(fig)
            lo, hi = out["ci"]
            st.write(f"Average **defaulted - repaid** = **{out['diff']:.3g}** (95% CI {lo:.3g} to {hi:.3g}). "
                     f"{'The interval excludes 0.' if lo > 0 or hi < 0 else 'The interval includes 0, so we cannot rule out no difference.'}")
        else:
            rates, ct = out["rates"], out["table"]
            lo_hi = [proportion_confint(ct.loc[i, 1], ct.loc[i].sum(), method="wilson") for i in ct.index]
            fig, ax = plt.subplots(figsize=(6, 3.6))
            pos = np.arange(len(rates))
            err = np.array([[r - l for r, (l, h) in zip(rates, lo_hi)], [h - r for r, (l, h) in zip(rates, lo_hi)]])
            ax.bar(pos, rates, color=BLUE, yerr=err, capsize=4)
            ax.set_xticks(pos); ax.set_xticklabels(rates.index, rotation=15)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0)); ax.set_ylabel("default rate")
            ax.set_title("Default rate with 95% CI")
            show(fig)
    with right:
        if kind == "categorical":
            st.dataframe(out["table"].rename(columns={0: "repaid", 1: "defaulted"}).assign(default_rate=out["rates"].round(3)))
        st.markdown(
            "**Reading it**\n\n"
            "- Small p-value -> *unlikely to be luck alone*.\n"
            "- Small effect size -> *may not matter in practice*, even if 'significant'.\n"
            "- Large p-value -> *not convincing evidence*, **not** proof of no difference."
        )

    st.divider()
    st.subheader("The big-data trap: how does the p-value change with sample size?")
    if st.checkbox("Show it (runs 30 random samples at each size)"):
        sizes = [s_ for s_ in [200, 500, 1000, 2000, 5000, 10000, len(df)] if s_ <= len(df)]
        rng = np.random.default_rng(int(seed))
        medians, share = [], []
        with st.spinner("Simulating..."):
            for size in sizes:
                reps = 1 if size == len(df) else 30
                ps = [run_test(df.sample(size, random_state=int(rng.integers(1e9))), kind, col)["p"] for _ in range(reps)]
                ps = np.array([p for p in ps if not np.isnan(p)])
                medians.append(np.median(ps) if len(ps) else np.nan)
                share.append((ps < alpha).mean() if len(ps) else np.nan)
        fig, ax = plt.subplots(figsize=(8, 3.6))
        ax.plot(sizes, medians, "o-", color=BLUE, label="median p-value")
        ax.axhline(alpha, color=RED, ls="--", label=f"alpha = {alpha}")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("sample size"); ax.set_ylabel("p-value"); ax.legend()
        show(fig)
        st.caption("The underlying effect never changed. Only the amount of data did. "
                   "With very large samples almost anything becomes 'significant', so always ask *how big* the effect is.")


REG_OUTCOMES = {"Average monthly bill (k)": "avg_bill", "Average monthly payment (k)": "avg_payment", "Credit limit (k)": "limit_k"}
REG_NUMERIC = {"Credit limit (k)": "limit_k", "Age": "AGE", "Months late (latest bill)": "late_1",
               "Credit utilization": "utilization", "Share of latest bill paid": "paid_ratio",
               "Average monthly payment (k)": "avg_payment", "Average monthly bill (k)": "avg_bill"}
REG_CATEGORICAL = {"Education": "C(edu_label)", "Marital status": "C(marriage_label)"}


def page_linear(df):
    st.header("3 · Linear regression: explaining a number")
    st.markdown(
        "**Analogy:** an estate agent's rule of thumb: *each extra bedroom adds X, each kilometre from town subtracts Y*. "
        "Regression learns those rules from data, **holding the other factors fixed**."
    )
    c1, c2 = st.columns(2)
    out_name = c1.selectbox("What do we want to explain?", list(REG_OUTCOMES))
    outcome = REG_OUTCOMES[out_name]
    options = [k for k, v in REG_NUMERIC.items() if v != outcome] + list(REG_CATEGORICAL)
    default = [o for o in ["Credit limit (k)", "Age", "Months late (latest bill)"] if o in options]
    chosen = c2.multiselect("Predictors", options, default=default)
    c3, c4 = st.columns(2)
    use_log = c3.checkbox("Model the log of the outcome (percentage effects; uses positive values only)")
    robust = c4.checkbox("Robust standard errors (HC3)")
    if not chosen:
        st.info("Pick at least one predictor.")
        return

    terms = [REG_NUMERIC.get(c) or REG_CATEGORICAL[c] for c in chosen]
    data = df[df[outcome] > 0] if use_log else df
    lhs = f"np.log({outcome})" if use_log else outcome
    model = smf.ols(f"{lhs} ~ " + " + ".join(terms), data=data).fit(cov_type="HC3" if robust else "nonrobust")

    m1, m2, m3 = st.columns(3)
    m1.metric("R-squared", f"{model.rsquared:.3f}", help="Share of the variation explained")
    m2.metric("Adjusted R-squared", f"{model.rsquared_adj:.3f}", help="Penalises useless predictors")
    m3.metric("Customers used", f"{int(model.nobs):,}")

    ci = model.conf_int()
    table = pd.DataFrame({"coef": model.params, "ci_low": ci[0], "ci_high": ci[1], "p_value": model.pvalues}).round(4)
    if use_log:
        table["pct_effect"] = ((np.exp(table["coef"]) - 1) * 100).round(2)
    st.subheader("Coefficients")
    st.dataframe(table.drop(index="Intercept"))

    first_num = next((REG_NUMERIC[c] for c in chosen if c in REG_NUMERIC), None)
    if first_num:
        b, (lo, hi), p = model.params[first_num], ci.loc[first_num], model.pvalues[first_num]
        if use_log:
            sentence = f"each extra unit of `{first_num}` goes with a **{(np.exp(b) - 1) * 100:.1f}%** change in {out_name.lower()}"
        else:
            sentence = f"each extra unit of `{first_num}` goes with a **{b:.3g}** change in {out_name.lower()} (95% CI {lo:.3g} to {hi:.3g})"
        st.success(f"**In plain English:** holding the other predictors fixed, {sentence} (p {fmt_p(p) if p < 0.001 else '= ' + fmt_p(p)}). "
                   "This is an association, not proof of cause.")

    st.subheader("Check the model before trusting it")
    left, right = st.columns(2)
    sample_idx = np.random.default_rng(0).choice(len(model.resid), size=min(4000, len(model.resid)), replace=False)
    with left:
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        ax.scatter(np.asarray(model.fittedvalues)[sample_idx], np.asarray(model.resid)[sample_idx], s=5, alpha=0.3, color=BLUE)
        ax.axhline(0, color=RED)
        ax.set_xlabel("fitted value"); ax.set_ylabel("residual"); ax.set_title("Want: a shapeless cloud, not a fan")
        show(fig)
    with right:
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        sm.qqplot(np.asarray(model.resid)[sample_idx], line="s", ax=ax, markersize=2)
        ax.set_title("Want: points on the line")
        show(fig)

    numeric_terms = [t for t in terms if not t.startswith("C(")]
    if len(numeric_terms) >= 2:
        X = sm.add_constant(data[numeric_terms])
        vif = pd.Series([variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])], index=numeric_terms, name="VIF").round(2)
        with st.expander("Multicollinearity check (VIF; above ~5-10 is a warning)"):
            st.dataframe(vif.to_frame())


LOGIT_NUMERIC = {"Credit limit (per 100k)": "limit_100k", "Age": "AGE", "Months late (latest bill)": "late_1",
                 "Credit utilization": "utilization", "Share of latest bill paid": "paid_ratio"}
LOGIT_CATEGORICAL = {"Education": "C(edu_label)", "Marital status": "C(marriage_label)", "Sex (see fairness note)": "C(sex_label)"}


def fit_logit(train, feature_names):
    terms = [LOGIT_NUMERIC.get(f) or LOGIT_CATEGORICAL[f] for f in feature_names]
    return smf.logit("default ~ " + " + ".join(terms), data=train).fit(disp=False)


def page_logistic(df):
    st.header("4 · Logistic regression: predicting a yes/no, then making a decision")
    st.markdown(
        "**Analogy:** a dimmer switch, not a light switch. The output is a *probability of default* that rises smoothly as risk factors add up. "
        "The model gives the probability; **the cut-off is a business decision** that depends on what each kind of mistake costs."
    )
    c1, c2 = st.columns([3, 1])
    default_feats = ["Credit limit (per 100k)", "Age", "Months late (latest bill)", "Credit utilization", "Share of latest bill paid", "Education", "Marital status"]
    feats = c1.multiselect("Model features", list(LOGIT_NUMERIC) + list(LOGIT_CATEGORICAL), default=default_feats)
    test_size = c2.slider("Held-out test share", 0.1, 0.4, 0.25, 0.05)
    if "Sex (see fairness note)" in feats:
        st.warning("**Fairness note:** using sex to approve or price credit is unlawful in many jurisdictions. "
                   "Add it to see how little it may change the model, then take it out again and discuss why.")
    if not feats:
        st.info("Pick at least one feature.")
        return

    train, test = train_test_split(df, test_size=test_size, stratify=df["default"], random_state=42)
    try:
        model = fit_logit(train, feats)
    except Exception as exc:  # e.g. perfect separation or a singular matrix
        st.error(f"Model could not be fitted ({type(exc).__name__}). Try removing a feature.")
        return
    p_test, y_test = model.predict(test).to_numpy(), test["default"].to_numpy()
    auc = roc_auc_score(y_test, p_test)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Odds ratios")
        ci = model.conf_int()
        tbl = pd.DataFrame({"odds_ratio": np.exp(model.params), "ci_low": np.exp(ci[0]), "ci_high": np.exp(ci[1]), "p_value": model.pvalues}).round(3)
        st.dataframe(tbl.drop(index="Intercept"))
        st.caption("Odds ratio 1.5 = odds of default 50% higher per unit; 0.8 = 20% lower. A CI that crosses 1 means 'cannot rule out no effect'.")
    with right:
        st.subheader("How good is it on unseen customers?")
        fpr, tpr, _ = roc_curve(y_test, p_test)
        fig, ax = plt.subplots(figsize=(4.6, 3.6))
        ax.plot(fpr, tpr, color=BLUE, lw=2.5, label=f"model, AUC = {auc:.2f}")
        ax.plot([0, 1], [0, 1], "k--", label="coin flip")
        ax.set_xlabel("good customers wrongly flagged"); ax.set_ylabel("defaulters caught"); ax.legend(loc="lower right")
        show(fig)

    st.divider()
    st.subheader("From probability to decision")
    k1, k2, k3 = st.columns(3)
    cost_fn = k1.slider("Cost of approving someone who defaults", 1, 20, 5, help="Money lost on the loan (in arbitrary units)")
    cost_fp = k2.slider("Cost of declining someone who would have repaid", 1, 20, 1, help="Profit you didn't make")
    thresholds = np.linspace(0.02, 0.98, 97)

    def evaluate(t):
        decline = p_test >= t
        fn = int((~decline & (y_test == 1)).sum())
        fp = int((decline & (y_test == 0)).sum())
        return decline, fn, fp, cost_fn * fn + cost_fp * fp

    costs = np.array([evaluate(t)[3] for t in thresholds])
    best_t = float(thresholds[costs.argmin()])
    use_best = k3.checkbox(f"Use the cost-optimal cut-off ({best_t:.2f})", value=False)
    t = best_t if use_best else st.slider("Decline if predicted probability of default is at least...", 0.02, 0.98, 0.50, 0.01)
    decline, fn, fp, cost = evaluate(t)
    approve_all = cost_fn * int((y_test == 1).sum())

    a, b, c, d = st.columns(4)
    a.metric("Approval rate", f"{1 - decline.mean():.0%}")
    b.metric("Defaulters caught", f"{(decline & (y_test == 1)).sum() / max((y_test == 1).sum(), 1):.0%}")
    c.metric("Total cost", f"{cost:,}")
    d.metric("Cost if we approve everyone", f"{approve_all:,}", delta=f"{cost - approve_all:,}", delta_color="inverse")

    l2, r2 = st.columns(2)
    with l2:
        cm = pd.DataFrame({"Approve": [int((~decline & (y_test == 0)).sum()), fn], "Decline": [fp, int((decline & (y_test == 1)).sum())]},
                          index=["Actually repaid", "Actually defaulted"])
        st.caption("Confusion matrix on the test set")
        st.dataframe(cm)
    with r2:
        fig, ax = plt.subplots(figsize=(5.5, 3.2))
        ax.plot(thresholds, costs, color=BLUE, lw=2)
        ax.axvline(best_t, color=GREY, ls="--", label=f"best = {best_t:.2f}")
        ax.axvline(t, color=RED, label=f"yours = {t:.2f}")
        ax.set_xlabel("cut-off"); ax.set_ylabel("total cost"); ax.legend()
        show(fig)
    st.caption("Make a default 10x as costly as a lost customer and watch the best cut-off fall: the lender becomes stricter. "
               "The cut-off is a business choice, not a statistical fact.")

    with st.expander("Risk deciles: does the model rank customers well, and are the probabilities honest?"):
        view = pd.DataFrame({"p": p_test, "y": y_test})
        view["risk_decile (10 = riskiest)"] = pd.qcut(view["p"].rank(method="first"), 10, labels=False) + 1
        st.dataframe(view.groupby("risk_decile (10 = riskiest)").agg(customers=("y", "size"), avg_predicted=("p", "mean"),
                                                                     actual_default_rate=("y", "mean")).round(3))


SCORER_FEATURES = ["Credit limit (per 100k)", "Age", "Months late (latest bill)", "Credit utilization",
                   "Share of latest bill paid", "Education", "Marital status"]


@st.cache_resource(show_spinner="Fitting the scoring model...")
def get_scorer(_df, source):
    return fit_logit(_df, SCORER_FEATURES)


def page_scorer(df, source):
    st.header("5 · Score an applicant")
    st.markdown("Describe a hypothetical applicant. The model returns a **probability of default**, and shows *what is driving it*.")
    model = get_scorer(df, source)
    edu_options = ["Graduate school", "University", "High school", "Other"]
    mar_options = ["Married", "Single", "Other"]

    c1, c2 = st.columns(2)
    with c1:
        limit = st.slider("Credit limit (k)", 10, 1000, 150, step=10)
        age = st.slider("Age", 21, 70, 35)
        late = st.slider("Months late on the latest bill", 0, 8, 0)
        util = st.slider("Credit utilization (latest bill / limit)", 0.0, 1.5, 0.40, 0.05)
    with c2:
        paid = st.slider("Share of the latest bill that was paid", 0.0, 1.0, 0.30, 0.05)
        edu = st.selectbox("Education", edu_options, index=1)
        mar = st.selectbox("Marital status", mar_options, index=1)
        cutoff = st.slider("Decline if probability of default is at least...", 0.05, 0.95, 0.30, 0.01)

    applicant = pd.DataFrame([{"limit_100k": limit / 100, "AGE": age, "late_1": late, "utilization": util, "paid_ratio": paid,
                               "edu_label": edu, "marriage_label": mar}])
    prob = float(model.predict(applicant).iloc[0])
    baseline = float(df["default"].mean())

    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted probability of default", f"{prob:.1%}", delta=f"{prob - baseline:+.1%} vs portfolio average", delta_color="inverse")
    m2.metric("Decision at your cut-off", "Decline" if prob >= cutoff else "Approve")
    m3.metric("Portfolio average default rate", f"{baseline:.1%}")
    st.progress(min(prob, 1.0))

    reference = {"limit_100k": df["limit_100k"].median(), "AGE": df["AGE"].median(), "late_1": 0, "utilization": df["utilization"].median(),
                 "paid_ratio": df["paid_ratio"].median(), "edu_label": df["edu_label"].mode()[0], "marriage_label": df["marriage_label"].mode()[0]}
    names = {"limit_100k": "Credit limit", "AGE": "Age", "late_1": "Months late", "utilization": "Utilization",
             "paid_ratio": "Share paid", "edu_label": "Education", "marriage_label": "Marital status"}
    deltas = {}
    for key in reference:
        alt = applicant.copy()
        alt[key] = reference[key]
        deltas[names[key]] = prob - float(model.predict(alt).iloc[0])
    drivers = pd.Series(deltas).sort_values()
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.barh(drivers.index, drivers.values * 100, color=[RED if v > 0 else BLUE for v in drivers.values])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Change in default probability vs. a typical value (percentage points)")
    ax.set_title("What is driving this applicant's risk? (red = pushes risk up)")
    show(fig)

    st.subheader("What-if: more months late")
    grid = pd.concat([applicant.assign(late_1=m) for m in range(0, 7)], ignore_index=True)
    grid["probability"] = model.predict(grid).values
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.plot(grid["late_1"], grid["probability"] * 100, "o-", color=RED)
    ax.set_xlabel("months late"); ax.set_ylabel("default probability (%)")
    show(fig)
    st.caption("Educational demo trained on public 2005 Taiwan data. It is **not** a real credit-decision tool. "
               "Real lending needs local data, regulatory review and fairness testing.")


# ----------------------------------------------------------------------------- main
def main():
    st.sidebar.title("Credit Risk & Inference Lab")
    upload = st.sidebar.file_uploader("Optional: upload the UCI file (.xls / .xlsx / .csv)", type=["xls", "xlsx", "csv"])
    try:
        if upload is not None:
            df, source = get_uploaded(upload.getvalue(), upload.name), f"uploaded: {upload.name}"
        else:
            df, source = get_data()
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        st.stop()

    if source.startswith("SYNTHETIC"):
        st.sidebar.warning("**Practice mode:** synthetic data, not the real UCI dataset. Results are not real findings. "
                           "Add the UCI file to `data/` or upload it above.")
    elif looks_official(df):
        st.sidebar.success(f"Official UCI data ({source})")
    else:
        st.sidebar.info(f"Data loaded ({source}). Row count or default rate differs from the published dataset.")

    page = st.sidebar.radio("Go to", ["Start here", "1 · Sampling & CIs", "2 · Hypothesis tests", "3 · Linear regression",
                                      "4 · Logistic regression", "5 · Score an applicant"])
    if page == "Start here":
        page_home(df, source)
    elif page.startswith("1"):
        page_sampling(df)
    elif page.startswith("2"):
        page_tests(df)
    elif page.startswith("3"):
        page_linear(df)
    elif page.startswith("4"):
        page_logistic(df)
    else:
        page_scorer(df, source)


main()
