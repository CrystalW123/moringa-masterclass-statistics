# From Describing Data to Making Decisions
### Inferential statistics, regression and credit risk: a practical masterclass

A hands-on repo for a live session that moves aspiring data professionals **beyond describing data** to **testing assumptions, quantifying uncertainty and supporting decisions**, using one running example: *should a lender approve this credit customer?*

| You get | Where |
|---|---|
| Workshop notebook (78 cells, runs top to bottom in about 15 seconds) | [`notebooks/01_masterclass.ipynb`](notebooks/01_masterclass.ipynb) |
| Interactive Streamlit app for the audience to play with | [`app/streamlit_app.py`](app/streamlit_app.py) |
| Plain-language explanations, analogies and real-world examples | [`docs/02_concepts_in_plain_language.md`](docs/02_concepts_in_plain_language.md) |
| Dataset download guide and data dictionary | [`docs/01_dataset_guide.md`](docs/01_dataset_guide.md) |
| Speaker run-of-show, demo cues, Q&A prep, checklist | [`docs/03_speaker_guide.md`](docs/03_speaker_guide.md) |

## What the session covers

1. Descriptive vs inferential statistics
2. Sampling, confidence intervals and measuring uncertainty
3. Hypothesis testing: p-values, significance, effect sizes and traps
4. Linear regression: building, interpreting, checking
5. Logistic regression for yes/no decisions such as credit risk
6. Translating results into a recommendation stakeholders can act on

## Quick start (5 minutes)

**1. Get the data** (free, open, ~2.7 MB). See [`docs/01_dataset_guide.md`](docs/01_dataset_guide.md).

Download *Default of Credit Card Clients* from the UCI repository:
<https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients>
and place the file in `data/` (keep its original name, `default of credit card clients.xls`).

**2. Install**

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3a. Notebook**: `jupyter lab notebooks/01_masterclass.ipynb`, or upload it to [Google Colab](https://colab.research.google.com/) (the first cells install what's missing; upload the data file in Colab's file panel, or let the notebook try to download it).

**3b. App**: `streamlit run app/streamlit_app.py`

The first cell that loads data prints whether you have the **official** dataset (30,000 rows, 22.12% defaults). Check that before you present.

> **No data yet?** The **app** falls back to *synthetic* practice data (same columns, made-up rows) and shows a loud "practice mode" banner. The **notebook** needs the real file and will tell you where to get it. Never present synthetic results as real findings.

## Deploy the app so the audience can open it (Streamlit Community Cloud, free)

1. Push this repo to GitHub (commit `data/default of credit card clients.xls` too, so the deployed app has the real data; check the licence note in the dataset guide).
2. Go to <https://share.streamlit.io>, click **New app**, pick the repo, and set **Main file path** to `app/streamlit_app.py`.
3. Deploy, then share the URL on your last slide. Open it once beforehand: free apps go to sleep after inactivity and take a minute to wake.

Also update the "Open in Colab" link below with your GitHub username:
`https://colab.research.google.com/github/<your-username>/<repo-name>/blob/main/notebooks/01_masterclass.ipynb`

## Repo layout

```
├── app/streamlit_app.py            # 5-page interactive lab
├── notebooks/01_masterclass.ipynb  # the live-coding notebook (outputs cleared)
├── src/credit_risk/
│   ├── data.py                     # load + clean + feature engineering (shared by notebook and app)
│   └── synthetic.py                # synthetic stand-in data for offline practice/testing
├── docs/                           # dataset guide, concepts, speaker guide
├── data/                           # put the UCI file here
├── tests/test_smoke.py             # pytest: data pipeline + every app page renders
└── requirements.txt
```

## Testing

```bash
PYTHONPATH=src pytest -q
```

The tests check the data cleaning, the engineered features, and that every app page renders (including the interactive branches). The notebook was executed end-to-end during development.

## Credit and licence notes

- Data: Yeh, I. C., & Lien, C. H. (2009). *The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients.* Expert Systems with Applications, 36(2), 2473-2480. Distributed via the UCI Machine Learning Repository (dataset id 350).
- Add a `LICENSE` file for your own code before publishing (MIT is a common choice).
- This is an **educational** project. The models are not fit for real lending decisions.
