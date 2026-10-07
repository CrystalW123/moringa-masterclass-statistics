# Dataset guide

## Which dataset and why

**Default of Credit Card Clients** (UCI Machine Learning Repository, dataset id 350)

- 30,000 credit-card customers at a bank in Taiwan, April to September 2005
- Target: did the customer **default on the next month's payment?** (22.12% did)
- Open dataset, free to download, no sign-up
- Small enough to run on any laptop or in Colab (~2.7 MB), big enough for real inference
- Contains everything the session needs: a yes/no outcome (logistic regression), continuous outcomes such as bill amounts (linear regression), groups to compare (hypothesis tests), and a population large enough to demonstrate sampling

It was chosen over Home Credit / Give Me Some Credit because it is a single tidy table, needs no joins, and its columns are easy to explain to a mixed audience.

> **Be upfront with the audience:** this is 2005 Taiwan card data. The *methods* transfer directly to digital lending, SACCO loans or buy-now-pay-later in Kenya; the *numbers* do not.

## Download (2 minutes)

1. Open <https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients>
2. Click **Download** (zip). Unzip it.
3. Copy `default of credit card clients.xls` into this repo's `data/` folder. Keep the file name.

**Alternatives**
- **Kaggle copy** (`UCI_Credit_Card.csv`): same data, CSV format. Drop it in `data/`; the loader accepts it.
- **Colab:** upload the file via the Files panel (left sidebar), or just run the notebook; it tries to download via the `ucimlrepo` package when the file isn't found. (That download path could not be tested from the environment this repo was built in, so keep the manual file as your backup.)
- **Streamlit app:** use the "upload" box in the sidebar if the file isn't in `data/`.

## Licence and citation

UCI lists this dataset under a Creative Commons Attribution licence (CC BY 4.0). Double-check on the dataset page before redistributing, and always cite:

> Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. *Expert Systems with Applications*, 36(2), 2473-2480.

## How to know you have the right file

The notebook and app print **"Official UCI data? True"** when the file has exactly **30,000 rows and a 22.12% default rate**. If it says `False`, you probably have a modified copy; results will differ slightly from the docs.

## Data dictionary

| Original column | Renamed to | Meaning |
|---|---|---|
| `LIMIT_BAL` | `LIMIT_BAL` | Credit limit in NT$ (New Taiwan dollars) |
| `SEX` | `SEX` | 1 = male, 2 = female |
| `EDUCATION` | `EDUCATION` | 1 = graduate school, 2 = university, 3 = high school, 4 = other |
| `MARRIAGE` | `MARRIAGE` | 1 = married, 2 = single, 3 = other |
| `AGE` | `AGE` | Age in years |
| `PAY_0`, `PAY_2` to `PAY_6` | `PAY_1` to `PAY_6` | Repayment status, Sept back to April. -2 = no consumption, -1 = paid in full, 0 = revolving credit paid minimum, 1 = one month late, 2 = two months late, ... 9 |
| `BILL_AMT1` to `BILL_AMT6` | same | Bill statement amount, Sept back to April |
| `PAY_AMT1` to `PAY_AMT6` | same | Amount paid, Sept back to April |
| `default payment next month` | `default` | **Target.** 1 = defaulted, 0 = did not |

The original file calls the September status `PAY_0` and skips `PAY_1`. The loader renames it to `PAY_1` so the six columns are numbered 1 to 6 (1 = most recent).

### Columns the repo adds

| Column | Definition | Why |
|---|---|---|
| `limit_k`, `limit_100k` | Credit limit in thousands / hundred-thousands | Readable coefficients and odds ratios |
| `late_1` | `PAY_1` with negatives set to 0 (months late on the latest bill) | Simple "how late" measure |
| `max_late`, `n_late_months` | Worst delay in six months; number of late months | Extra exercise features |
| `utilization` | Latest bill / credit limit, clipped to 0-1.5 | "How maxed out is this customer?" |
| `paid_ratio` | Latest payment / latest bill, clipped to 0-1 (1 if nothing owed) | Repayment behaviour |
| `avg_bill`, `avg_payment` | Six-month averages, in thousands | Outcomes for the linear regression |
| `sex_label`, `edu_label`, `marriage_label`, `female` | Readable labels / indicator | Tables and formulas |

## Known quirks (great teaching moments)

1. **Undocumented category codes.** `EDUCATION` contains 0, 5 and 6 and `MARRIAGE` contains 0, none of which appear in the data dictionary. The loader folds them into "Other". *Lesson: always compare the data to its documentation.*
2. **`PAY_x` mixes two ideas.** Values -2, -1 and 0 mean "not late" in different ways, while 1 to 9 count months late. Treating the column as one numeric scale is a simplification. The repo's `late_1` collapses the not-late values to 0. *Discussion: what information did we throw away?*
3. **Negative bill amounts** exist (credits/refunds). `utilization` is clipped at 0; `avg_bill` can be zero or negative, which is why the log-model in the notebook uses positive bills only.
4. **Selection bias.** The data only contains customers the bank *approved*. A real credit model must also worry about the applicants it rejected and never saw repay ("reject inference").
5. **Fairness.** `SEX`, `AGE` and `MARRIAGE` are sensitive. The repo tests differences on them but deliberately keeps `SEX` out of the predictive model. Use this to open a discussion on responsible credit scoring.
6. **A snapshot, not a time series.** Taiwan had a card-debt crisis in 2005-2006; defaults were unusually high. Do not present 22% as a normal default rate.

## Synthetic practice data

`src/credit_risk/synthetic.py` generates 30,000 fake customers with the same columns and roughly similar relationships, for testing and offline practice:

```bash
PYTHONPATH=src python -m credit_risk.synthetic --out data/synthetic_credit_default.csv
```

It is **not real**. Its numbers (for example the AUC, the odds ratios) will differ from the real dataset. Use it only to test the plumbing.
