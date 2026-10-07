# Speaker guide

Everything you need to run the session: timing, what to click, what to say, audience prompts, likely questions and a fallback plan.

> **Assumption:** the session is about **90 minutes** including questions. The brief did not state a length, so a 60-minute cut is included below. Adjust the times to your slot.

## The one-sentence storyline

*Describe what happened → quantify how wrong you might be → test whether patterns are real → explain drivers → predict a yes/no → recommend an action.*

Keep one running question on screen throughout: **"Should this lender approve this customer, and how sure can it be?"**

---

## Before the session

**A week before**
- [ ] Download the dataset ([dataset guide](01_dataset_guide.md)); confirm the notebook prints `Official UCI data? True`.
- [ ] Run the notebook top to bottom once. Note the actual numbers (odds ratio for `late_1`, AUC, best cut-off). You'll quote them.
- [ ] Deploy the app on Streamlit Community Cloud ([README](../README.md)); test the URL on your phone.
- [ ] Put the repo and app link on the last slide. Replace the `<your-username>` placeholders in the README.
- [ ] Send participants the requirements: laptop with Python + pandas + statsmodels or scikit-learn, **or** a free Google Colab account.

**The day before**
- [ ] Open the app to wake it up (free apps sleep).
- [ ] Restart the notebook kernel and run all; keep the run *with outputs* as a backup copy (`File → Save a copy`).
- [ ] Export the slides to PDF as a backup.
- [ ] Take screenshots of the key charts (CI coverage plot, permutation plot, ROC, cost curve) in case the internet fails.

**An hour before**
- [ ] Increase font size in the notebook (browser zoom 125%+).
- [ ] Close notifications. Have the app open in a second tab.
- [ ] Test the projector with the notebook, not only the slides.

---

## Run of show (90 minutes)

| Time | Segment | Where | Key message | Audience interaction |
|---|---|---|---|---|
| 0-7 | **Hook and roadmap** | Slides | "Data analysis has two jobs: describe and decide." | Poll: *A 200-customer pilot shows 18% defaults vs 22% average. Launch?* (Park the answer until 25 min.) |
| 7-17 | **Descriptive vs inferential** | Notebook §1-2 | Tables tell you what happened; they can't tell you what to expect. | Ask: "Is the drop from 22% to 18% real?" |
| 17-32 | **Sampling and confidence intervals** | Notebook §3, App page 1 | Every estimate wobbles; intervals measure the wobble; 4× data halves it. | Predict-then-reveal: "What happens to the interval if we go from n=100 to n=400?" Return to the hook poll: at n=200 the margin is about ±5 points, so the pilot proves nothing. |
| 32-50 | **Hypothesis testing** | Notebook §4, App page 2 | p-value = surprise meter; effect size = does it matter; big data makes everything significant. | Everyone runs the "sample size vs p-value" demo in the app and shouts out when the result flips. |
| 50-52 | *Stretch break / questions* | | | |
| 52-67 | **Linear regression** | Notebook §5, App page 3 | Coefficients = "holding others equal"; check residuals; logs fix fans. | "Which is the most important predictor?" (Trick question: units differ.) |
| 67-85 | **Logistic regression and the decision** | Notebook §6, App pages 4-5 | Odds ratios, AUC, deciles; the cut-off is a business decision. | Let the audience set the cost of a bad loan and find the best cut-off. Score an applicant live. |
| 85-90 | **From output to recommendation** | Notebook §7, Slides | Finding → Evidence → Uncertainty → Recommendation → Caveat. | Ask two people to re-word a p-value in plain English. |
| 90+ | Wrap and next steps | Slides | Exercises, repo, app link | |

---

## Segment notes and demo cues

### Hook (0-7)
- Start with the story, not the syllabus: *"A lender has 30,000 records and a new applicant at the counter."*
- The pilot poll (18% vs 22% on 200 customers) sets up the whole session. Take a show of hands; most people say "launch". You'll show at ~25 minutes that the data can't support that.

### Descriptive vs inferential (7-17)
- Run the setup cells beforehand; show the "Official UCI data?" line.
- Show the `groupby` table and the default-rate-by-months-late bar chart. Say: *"Everything on this screen is true, and none of it is a conclusion yet."*
- Land the match-report vs transfer-decision analogy.

### Sampling and CIs (17-32)
- Notebook §3.1: the four histograms. Ask: "Which n would you trust?" Then show the observed spread matches the formula.
- §3.3 coverage table: point at the 95% row. *"The method is right 95% of the time. We never know if this particular interval is one of the 5%."*
- **App page 1:** slide the sample size; watch red (missed) intervals appear. Push confidence to 99%: intervals widen and misses vanish, but usefulness drops.
- If coverage on screen shows something like 89% at 95% confidence with few analysts, that is a **teaching moment**: raise "Number of analysts" to 200 and it settles near 95%.
- Return to the hook poll (see table).

### Hypothesis testing (32-50)
- Walk through Test A (credit limits) fast; spend time on the **interpretation**, not the code: p-value, difference with CI, Cohen's d.
- Test B/C (gender, education): show that "significant" and "large" are different questions.
- §4.4 (the big-data trap) is the best demo of the session. Run it, then open **App page 2 → "Show it"** and let the audience watch the p-value fall as n grows while the effect stays constant.
- §4.5 permutation plot: 90 seconds. *"No formulas, just shuffling."*
- §4.6 noise test: 30 seconds. *"200 tests on pure noise, about 10 discoveries."*

### Linear regression (52-67)
- Start with the simple regression and the scatter, then the multiple regression table. Read one row aloud: *"Holding age, education and lateness the same, each extra 1k of limit goes with…"*
- Show the residual fan, then the log fix. Say plainly that it's better but not perfect.
- VIF: 60 seconds; the six bills tell the same story.
- **App page 3:** add/remove predictors; tick "log outcome".

### Logistic regression (67-85)
- Open with the linear-probability failure (§6.1): "probabilities" outside 0 to 1.
- Odds table: read *one* row in words, and show the probability curve for months late. Probabilities beat odds ratios for lay audiences.
- ROC/AUC: use the "pick one defaulter and one good customer" explanation.
- Decile table: *"This is how a risk team reads a model."*
- **App page 4:** set the cost of a bad loan; find the best cut-off; then let someone set it to 10× and predict what happens.
- **App page 5:** score an applicant; move "months late"; discuss the drivers chart. Optional: add `Sex` to the page-4 model, note it barely helps, and open the fairness discussion.

### Wrap (85-90)
- Read the auto-generated memo in §7 aloud. Then ask: *"What would you have to know before you signed this off?"* (Data age, fairness, cost assumptions.)
- Close on the take-home exercises and repo/app links.

---

## 60-minute version

Keep: hook, descriptive vs inferential (5 min), sampling + CI (10), hypothesis testing (12, skip permutation and multiple-testing), linear regression (10, skip VIF and train/test), logistic regression (15, skip scikit-learn comparison), wrap (5). Skip the app pages you don't have time for and point people to them afterwards.

---

## Likely questions and short answers

1. **"Is a p-value the probability that I'm wrong?"** No. It's the probability of a result this extreme *if nothing were going on*. It isn't the probability H0 is true.
2. **"Why 0.05?"** Convention (Fisher, 1920s). It's a policy choice: stricter when false alarms are costly, looser when misses are.
3. **"My p-value is 0.06. Is it real?"** Don't treat 0.05 as a cliff. Report the effect size and interval and say "suggestive, not conclusive".
4. **"When do I use a t-test vs Mann-Whitney?"** t-test compares means and is fine for large samples; Mann-Whitney compares ranks and is safer for heavy skew or outliers. Running both and seeing agreement is reassuring.
5. **"How large a sample do I need?"** It depends on the smallest effect you care about; do a power calculation (`statsmodels.stats.power`). Rule of thumb: halving the margin of error needs 4× the data.
6. **"Can I use R² to compare models?"** Only for the same outcome. Adjusted R², AIC/BIC or test-set performance are better. R² isn't comparable between a raw and a logged outcome.
7. **"Odds ratio vs risk ratio?"** They're close only when the outcome is rare. At a 22% default rate they diverge, so present probabilities to non-technical people.
8. **"Is 0.75 AUC good?"** It depends on the alternative. Real credit scorecards commonly sit around 0.7-0.85, but compare against what the business does today, and check calibration and fairness.
9. **"Should we use sex/age in credit models?"** Often prohibited or restricted. Test for differences, but exclude protected attributes from decisions, and check that other variables aren't proxies for them.
10. **"Why not just use XGBoost?"** Often more accurate, but harder to explain to regulators and customers. Logistic regression is the standard baseline and is interpretable. Always beat the baseline before adding complexity.
11. **"Does this apply to mobile lending in Kenya?"** The *methods* do. The *numbers* don't: this is 2005 Taiwan card data. Local data with mobile-money behaviour would change the features, the base rate and the model.
12. **"Doesn't significance testing have problems?"** Yes: p-hacking, multiple testing, and confusing significance with importance. That's exactly why this session pairs p-values with effect sizes and intervals.

---

## If something breaks

| Problem | Fix |
|---|---|
| Wi-Fi fails | Use the executed backup notebook, screenshots and PDF slides. Run the notebook locally (no internet needed once the data file is in `data/`). |
| Streamlit app is down | Run it locally: `streamlit run app/streamlit_app.py`, or walk through the notebook equivalent. |
| Notebook prints `Official UCI data? False` | You have a modified file. Re-download; numbers will differ from your notes. |
| Colab users can't install `statsmodels` | Restart the runtime after the first cell; it installs quietly. |
| Someone's numbers differ from yours | Random seeds are fixed; differences usually mean a different data file. Good chance to talk about reproducibility. |

---

## After the session

- Share: repo link, app link, slides PDF.
- Give the take-home exercises (end of the notebook).
- Suggested next reads: an introductory statistics text of your choice; the `statsmodels` documentation on regression; the UCI dataset page and the original paper.
