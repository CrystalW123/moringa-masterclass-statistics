# Concepts in plain language

Everything you want to explain on the day, in simple words, with **an analogy** and **a real-world example** for each idea. Every section ends with a "say it on stage" line and the mistakes to warn people about.

**The running story (use it from the first minute):**
> A lender has records of 30,000 past credit customers. A new applicant walks in. *Should we lend to them, and how sure can we be?*

Every concept below answers one piece of that question.

| # | Concept | The question it answers | Analogy |
|---|---|---|---|
| 1 | Descriptive vs inferential | What happened vs what should we expect? | Match report vs transfer decision |
| 2 | Sampling | Can a small group speak for everyone? | Tasting the soup |
| 3 | Confidence intervals | How wrong could our number be? | Weather forecast range / a fishing net |
| 4 | Hypothesis testing | Is this pattern real or luck? | Courtroom, smoke alarm |
| 5 | Linear regression | What drives a number, holding others fixed? | Estate agent's rule of thumb |
| 6 | Logistic regression | How likely is a yes/no outcome? | A dimmer switch |
| 7 | Communicating results | What should the business do? | The doctor explaining a scan |

---

## 1. Descriptive vs inferential statistics

**In one sentence:** *Descriptive statistics summarise the data you have; inferential statistics use that data to draw conclusions about things you do not have.*

**Analogy: the match report vs the transfer decision.**
The match report ("58% possession, 4 shots on target") is 100% accurate about the game that was played. That is descriptive. A scout deciding whether to sign the player asks something different: *"Based on these ten matches, how will he perform next season?"* That is inferential. It goes beyond the data, so it needs honesty about uncertainty.

**Real-world example (lending).**
- *Descriptive:* "Of the 30,000 customers in our file, 22% defaulted. Average credit limit was 167k."
- *Inferential:* "Of next quarter's 5,000 new applicants, roughly how many will default? Is the difference between graduates and non-graduates real, or just noise in this file?"

**Vocabulary that makes the rest easy**

| Word | Plain meaning | Example |
|---|---|---|
| Population | Everyone you want to know about | All customers the lender will ever serve |
| Sample | The subset you actually observe | The 30,000 customers in the file |
| Parameter | A true value about the population (unknown) | The real default rate for all customers |
| Statistic | The same number computed on the sample (known) | 22% in our file |
| Inference | Using statistics to say something about parameters | "The true default rate is probably between 21.5% and 22.7%" |

**Say it on stage:** *"Descriptive statistics tell you what happened. Inferential statistics tell you what you can safely conclude, and how wrong you might be."*

**Watch out:** people often stop at descriptive because it feels safe. A bar chart showing "group A defaults more than group B" is not a conclusion until you ask whether the gap could be luck.

---

## 2. Sampling and sampling variation

**In one sentence:** *A well-chosen sample can tell you about a population, but different samples give slightly different answers, and that wobble is what we have to measure.*

**Analogy: tasting the soup.**
You don't drink the whole pot to check the salt: you stir well and taste one spoonful. If the pot is well mixed, the spoonful represents the pot. But two spoonfuls never taste *exactly* the same. That difference is **sampling variation**. The key phrase is *"stir well"*: a spoonful skimmed off the top is a biased sample.

**Real-world examples**
- A digital lender wants to know its repayment rate; it can't wait for all 2 million loans to mature, so it looks at a random 2,000.
- **Bias trap:** a lender only sees repayment results for customers it *approved*. A model built only on approved customers can't learn about the people it rejected. (Called *reject inference* in credit risk.) A great "why sampling is more than maths" point.
- **Bias trap:** surveying only customers who use the mobile app misses the ones who don't.

**Three ideas to show live (notebook Section 3, app page 1)**
1. **1,000 analysts, 1,000 different answers.** Each draws their own sample and reports a default rate. Plot them: a bell-shaped pile centred on the truth. That pile is the *sampling distribution*.
2. **Standard error** is simply the spread of that pile. For a proportion: √(p(1−p)/n).
3. **The square-root law:** to cut the wobble in half you need **four times** the data, not twice. Each extra customer helps less than the last.

**The Central Limit Theorem, without the scary name:** *"Average enough independent things and the result forms a bell curve, even if the individual things look nothing like a bell."* This is why so much of statistics works with one simple set of tools.

**Say it on stage:** *"Every number from a sample carries wobble. Our job is not to remove it (we can't) but to measure it."*

**Watch out:** a huge but biased sample is worse than a small random one. Size cannot fix bias.

---

## 3. Confidence intervals

**In one sentence:** *A confidence interval is a range of plausible values for the true number, built by a method that captures the truth a stated percentage of the time.*

**Analogy 1: the weather forecast.** "Tomorrow: 24°C" pretends to a precision nobody has. "Between 21 and 27°C" is honest and more useful.

**Analogy 2: the fishing net.** The true value is a fish that doesn't move. Each analyst throws a net (their interval). A "95% net" is one that catches the fish 95 times out of 100 throws. Once a net is thrown, it either caught the fish or it didn't. You just never know which.

**Real-world example.**
A lender pilots a new product on **200** customers. 18% default, versus 22% for the whole portfolio. Is the product better?

The 95% margin of error at n = 200 is about ±5 points, so the interval runs from roughly 13% to 24%. It comfortably *includes* 22%. **The pilot can't tell the difference: it needs a bigger sample**. That is the practical power of an interval: it stops you launching (or cancelling) on noise.

**Reading it correctly**

| Say this | Not this |
|---|---|
| "The method captures the true value 95% of the time." | "There's a 95% chance the truth is in this interval." |
| "We're fairly confident the rate is between 13% and 24%." | "The rate is 18%." |
| "An interval that includes 22% means we can't rule 22% out." | "It's 18%, so it's better than 22%." |

**Three knobs that change the width**
- **More data → narrower** (square-root law).
- **Higher confidence → wider.** A 99.9% interval is nearly always right and nearly useless.
- **More variable data → wider.**

**Bootstrap (when no formula exists).** Re-sample your own sample, with replacement, thousands of times, and look at the spread of the statistic. **Analogy:** photocopy your handful of marbles and draw from the photocopies to see how much handfuls vary. Great for medians, ratios, AUC.

**Say it on stage:** *"An estimate without an interval is a guess with confidence issues."*

**Watch out:** the interval only covers *sampling* uncertainty. It does not protect you against biased data, data errors or a changing world.

---

## 4. Hypothesis testing

**In one sentence:** *A hypothesis test asks whether a pattern in your sample is strong enough that pure chance is an unconvincing explanation.*

**Analogy: the courtroom.** The defendant (the **null hypothesis, H0**: "nothing is going on") is presumed innocent. The prosecutor (**alternative, H1**) must show evidence so unlikely under innocence that we're willing to convict. "Not guilty" doesn't mean "innocent"; it means *not enough evidence*.

**The p-value, plainly.**
> *If nothing were really going on, how often would luck alone produce a gap at least this big?*

p = 0.003 → about 3 times in 1,000. That's a surprising result under H0, so we doubt H0.

**What a p-value is NOT:** the probability that H0 is true; the probability you're wrong; the size or importance of the effect. Ask an audience of 30 what a p-value is: most get it wrong, which is normal.

**The 5-step routine**
1. State H0 and H1 (e.g. defaulters and non-defaulters have the same average limit / they differ).
2. Choose alpha (usually 0.05) *before* looking.
3. Pick the test that fits the data (table below).
4. Get the p-value.
5. Decide **and report the effect size and a CI**, never just "p < 0.05".

**Which test when**

| Question | Data | Test |
|---|---|---|
| Do two groups differ on an average? | number vs 2 groups | Welch t-test (Mann-Whitney if very skewed) |
| Do two groups differ on a rate? | yes/no vs 2 groups | Two-proportion z-test |
| Is a category related to a yes/no outcome? | category vs yes/no | Chi-square test |
| Are two numbers related? | number vs number | Correlation / regression |

**Two ways to be wrong: the smoke alarm**
- **Type I error (false alarm):** the alarm rings, there's no fire. You declare an effect that isn't real. Alpha = 0.05 means you accept this risk 5% of the time when nothing is going on.
- **Type II error (missed fire):** there's a fire, the alarm stays silent. A real effect goes undetected, usually because the sample was too small. **Power** = the chance of catching a real fire.
- *Lending example:* Type I = "the new SMS reminder lowers defaults" when it doesn't (money wasted on a useless feature). Type II = missing a reminder that really would have cut defaults.

**Statistical significance ≠ practical importance: the bathroom scale.**
A scale accurate to one gram will say, with overwhelming certainty, that you gained three grams. Detectable, real, irrelevant. With 30,000 rows almost everything is "significant", so **always ask how big the effect is**:
- Numeric gaps: Cohen's d (0.2 small, 0.5 medium, 0.8 large).
- Category associations: Cramér's V.
- Or simply the difference and its confidence interval, in real units.

In the notebook's Section 4.4 the *same* small gender gap looks unremarkable at n = 500 but becomes clearly "significant" by n = 15,000 (the exact p-values depend on your data). The effect never changed; only the sample did.

**The multiple-testing trap: the psychic.**
Flip coins until you get five heads in a row and announce you're psychic. Test 20 things at alpha = 0.05 and you *expect one false discovery*. The notebook tests 200 columns of pure noise and finds about 10 "significant" ones. Fixes: decide hypotheses in advance, be honest about how many things you tried, or use a stricter threshold (Bonferroni: alpha ÷ number of tests).

**Permutation test: a p-value with no formulas.** Shuffle the labels (defaulted/repaid) randomly thousands of times, each time recomputing the gap. The shuffled gaps show what luck produces; if the real gap sits far outside, luck is a poor explanation. It's the best way to make p-values *feel* real.

**Real-world example (A/B test in fintech).** A lender sends half its borrowers a new repayment reminder wording and half the old one. 4,000 each: 12.1% (new wording) vs 13.4% (old) default, purely illustrative numbers. Is the new wording working? A two-proportion z-test gives a p-value and a CI for the 1.3-point reduction. Here the CI runs from roughly −0.2 to 2.8 points, which includes zero: "promising, not proven; extend the test."

**Say it on stage:** *"A p-value tells you whether luck is a good explanation. The effect size tells you whether you should care."*

**Watch out:** "not significant" is **not** "no effect". It means "not convincing yet". Also: association, not cause. Lower limits go with default partly because lenders give risky customers lower limits.

---

## 5. Linear regression

**In one sentence:** *Linear regression finds the straight-line rule that best explains a number from other numbers, and tells you how much each factor matters while holding the others fixed.*

**Analogy: the estate agent's rule of thumb.**
"Each extra bedroom adds about KES 500,000; each 10 minutes closer to town adds KES 300,000." The agent learned these rules from hundreds of sales. Regression does the same, on purpose, with error bars.

**The equation, in words**
> outcome = baseline + (amount per unit of factor 1) × factor 1 + (amount per unit of factor 2) × factor 2 + … + leftover

**Real-world example (lending).** *What drives a customer's average monthly bill?* Useful for revenue forecasting and limit setting. The notebook uses credit limit, age, months late, education, and marital status.

**Reading the output: the 80% you need**

| Piece | Plain meaning |
|---|---|
| Intercept | The baseline when all factors are zero (often not meaningful on its own) |
| Coefficient | Change in the outcome for **one more unit** of that factor, **other factors held equal** |
| Standard error / CI | The wobble on that coefficient |
| p-value (per coefficient) | Test of "the true coefficient is zero" (no relationship) |
| R² | Share of the variation in the outcome the model explains (0 to 1) |
| Adjusted R² | R² with a penalty for adding useless factors |
| Residual | Actual − predicted; the part the model missed |

**"Holding everything else constant"** is the magic phrase. It compares two customers who are alike in every listed way except one.

**Categorical predictors** (education, marital status) get compared to a **reference group**. A coefficient of +3 means "3 more than the reference".

**Checking the model: the L-I-N-E memory aid**

| Letter | Assumption | Check with |
|---|---|---|
| **L** | The relationship is Linear | Residuals vs fitted: no curve |
| **I** | Observations are Independent | Think about how data was collected |
| **N** | Errors are roughly Normal | QQ plot: points near the line |
| **E** | Errors have Equal spread | Residuals vs fitted: no fan shape |

**Analogy for "E":** a bathroom scale that's reliable for light people but erratic for heavy ones. The *error* shouldn't depend on the size of what you measure. Money data usually violates this (bigger bills, bigger errors). **Fix:** model the **log** of the outcome. Coefficients become **percentage** effects: "each extra month late goes with about X% higher bills" (the notebook prints the actual X).

**Multicollinearity: two people telling the same story.** If two predictors carry almost the same information (six monthly bills that move together), the model can't split the credit between them. Coefficients swing wildly and even flip sign. Detect it with **VIF** (above 5 to 10 is a warning); fix it by dropping or combining predictors. The notebook computes VIFs for the six monthly bills; expect values far above the warning line.

**Overfitting: the student who memorised last year's paper.** A model can fit its training data beautifully and fail on new customers. Always compare fit on held-back data.

**Association, not causation.** Age doesn't *cause* bills; it travels with life stage, income and habits.

**Say it on stage:** *"Regression is a fair way to split credit. Each coefficient answers: with everything else equal, what does one more unit of this do?"*

**Watch out:** R² is not "accuracy". A model can have low R² and still be very useful for understanding drivers (or high R² and useless for decisions). And never extrapolate far outside your data.

---

## 6. Logistic regression

**In one sentence:** *Logistic regression estimates the probability of a yes/no outcome from several factors, using an S-shaped curve so the answer stays between 0% and 100%.*

**Why not linear regression?** A straight line doesn't know probabilities live between 0 and 1. In the notebook a linear model of default produces "probabilities" below 0 or above 1 for a few hundred customers (the notebook counts them). The S-curve fixes this.

**Analogy: the dimmer switch.** Not on/off, but *how bright*: risk factors slide the probability smoothly up from near 0 towards near 1.

**Odds: the language of betting.**
- Probability 20% → odds of **1 to 4** (0.25).
- Probability 50% → odds 1 to 1.
- Odds = p ÷ (1 − p). Logistic regression is a straight-line model for the **log** of the odds.

**Odds ratio (OR): the number you'll report.** Exponentiate a coefficient.

| OR | Meaning |
|---|---|
| 1.0 | No effect |
| 1.5 | Odds of default are **50% higher** per unit increase |
| 0.8 | Odds of default are **20% lower** per unit increase |
| CI includes 1 | Can't rule out no effect (same as p > 0.05) |

**Careful:** an odds ratio is *not* "50% more likely". For rare outcomes the two are close; for common outcomes (like a 22% default rate) they diverge. For non-technical audiences, **show predicted probabilities** ("a customer with no late payments: 15% risk; three months late: 70%").

**Real-world example (credit risk).** A digital lender, SACCO or card issuer scores every applicant with a logistic model on features such as repayment history, utilisation, and limit. Its output is a probability that becomes a score, a risk band and a decision. Banks have used variants of this "scorecard" for decades because it's **interpretable**: a regulator or a customer can be told *why*.

**How good is it? The four views**

| View | Question | Plain meaning |
|---|---|---|
| **AUC** | Does it rank risky above safe? | Pick one defaulter and one good customer at random; AUC is the chance the model scores the defaulter higher. 0.5 = coin flip, 1.0 = perfect. (Banks often quote Gini = 2 × AUC − 1.) |
| **Confusion matrix** | What kinds of mistakes? | Approved-and-defaulted vs declined-but-would-have-repaid |
| **Precision / recall** | How clean / how complete? | Precision: of those we flagged, how many really defaulted? Recall: of all defaulters, how many did we catch? |
| **Deciles / calibration** | Are the probabilities honest? | Sort customers by predicted risk into ten groups. Default rate should climb steadily and predicted ≈ actual |

**From probability to decision: the cut-off is a business choice.**
The model outputs "38% chance of default". Someone must decide: approve or decline? The right line depends on what each mistake costs:
- **Approve a defaulter** → lose the principal.
- **Decline a good customer** → lose the profit.

If the first mistake costs five times the second, the best cut-off is far below 0.5 and the lender declines more people. This is a **business** decision informed by statistics, not a statistical fact. The app lets the audience move the two cost sliders and watch the best cut-off move.

**Train/test split: the exam with new questions.** Never grade a model on the customers it learned from.

**Fairness and responsibility.** Some inputs (sex, sometimes age, marital status, ethnicity, location proxies) are illegal or ethically risky in credit decisions. This repo *tests* a sex difference (Section 4) but *excludes* sex from the model. Ask: who could be harmed if this scores them wrongly? Is there an appeals route? Is the data representative of the people being scored?

**Say it on stage:** *"Logistic regression turns evidence into a probability. The business turns a probability into a decision."*

**Watch out:**
- Reading an odds ratio as a probability change.
- Judging a model on training data.
- Choosing 0.5 as the cut-off "because that's default".
- Leaving out late-payment information and being puzzled why the model is weak.

---

## 7. Communicating results to stakeholders

**In one sentence:** *Your analysis only matters if someone does something differently because of it.*

**Analogy: the doctor explaining a scan.** The doctor doesn't recite the imaging parameters. They say what they found, how sure they are, what it means for you, and what to do next.

**A five-part structure that works every time**

> **Finding → Evidence → Uncertainty → Recommendation → Caveat**

**Translation table: statistics → plain English**

| The output says | Say this instead |
|---|---|
| p = 0.003 | "If there were really no difference, we'd see a gap this big about 3 times in 1,000, so it's unlikely to be luck." |
| 95% CI: 4 to 9 points | "We're fairly confident the true gap is somewhere between 4 and 9 points." |
| Odds ratio 1.6 | "Each extra unit goes with about 60% higher odds of default." |
| R² = 0.30 | "The model explains roughly 30% of why bills differ. It's good for trends, not for forecasting one person." |
| AUC = 0.77 | "Given one defaulter and one good customer, the model ranks them correctly about 77% of the time." |
| p > 0.05 | "We haven't found convincing evidence of a difference," not "there's no difference." |

**Questions stakeholders always ask (have answers ready)**
1. *"How sure are you?"* → Give the interval, then say what would change your mind.
2. *"How much money is this worth?"* → Convert to the cost assumptions (with Finance).
3. *"What could go wrong?"* → Data age, bias, drift, fairness. Name them first.
4. *"Why did it decline this customer?"* → Show the drivers (app page 5).
5. *"What do you recommend?"* → One clear action, with the trade-off.

**The notebook's Section 7 builds a draft memo from the numbers you actually computed**, so the story updates whenever the data does.

**Say it on stage:** *"Lead with the decision, not the method. The method is there to be trusted, not to be admired."*

---

## Quick reference: analogies to keep handy

| Idea | Analogy in one line |
|---|---|
| Descriptive vs inferential | Match report vs deciding whether to sign the player |
| Sampling variation | Two spoonfuls of the same soup never taste exactly alike |
| Sampling bias | Tasting only the top of an unstirred pot |
| Square-root law | To halve the wobble, you need four times the data |
| Confidence interval | Weather-forecast range; a net that catches the fish 95 times in 100 |
| Bootstrap | Photocopy your handful of marbles and draw from the photocopies |
| Null hypothesis | Presumed innocent until proven guilty |
| p-value | A surprise meter: how strange would this be if nothing were going on? |
| Type I / Type II | False alarm vs missed fire |
| Significant vs important | A scale that detects three grams of weight gain |
| Multiple testing | Flip coins until five heads in a row, then claim you're psychic |
| Linear regression | The estate agent's rule of thumb, learned from data |
| Holding others constant | Compare two houses identical except for one bedroom |
| Heteroscedasticity | A scale that's accurate for light people and erratic for heavy ones |
| Multicollinearity | Two people telling you the same story |
| Overfitting | The student who memorised last year's exam |
| Logistic regression | A dimmer switch, not a light switch |
| Odds | Betting odds ("1 to 4") |
| Train/test split | An exam with questions you've never seen |
| Cut-off choice | Deciding how many false alarms you'll tolerate to catch real fires |

---

## Glossary

- **Alpha (α):** the p-value threshold for "significant" (commonly 0.05).
- **AUC:** area under the ROC curve; ranking quality from 0.5 (chance) to 1 (perfect).
- **Bias (sampling):** a sample that systematically misrepresents the population.
- **Bootstrap:** estimating uncertainty by re-sampling your own data.
- **Calibration:** whether predicted probabilities match observed frequencies.
- **Confidence interval (CI):** range of plausible values built by a method with a stated long-run success rate.
- **Confounder:** a hidden factor that influences both things you are comparing.
- **Effect size:** how big a difference or relationship is (Cohen's d, Cramér's V, odds ratio, or the raw difference).
- **Heteroscedasticity:** error spread that changes with the fitted value.
- **Null hypothesis (H0):** the "nothing going on" claim a test tries to reject.
- **Odds ratio:** how much the odds of the outcome multiply per one-unit increase.
- **Overfitting:** learning noise in the training data; performs worse on new data.
- **p-value:** probability of a result at least this extreme if H0 were true.
- **Power:** probability a test detects a real effect.
- **Residual:** actual minus predicted value.
- **Sampling distribution:** the pattern of a statistic across many hypothetical samples.
- **Standard error:** the standard deviation of a statistic across samples; the "wobble".
- **Type I / Type II error:** false alarm / missed detection.
- **VIF:** variance inflation factor, a measure of multicollinearity.
