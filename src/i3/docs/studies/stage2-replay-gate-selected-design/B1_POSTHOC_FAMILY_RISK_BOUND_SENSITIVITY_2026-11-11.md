# I3 Stage 2.1: B1 family-level conditional survival-bound stress test (read-only, post hoc)

**Date:** 11 November 2026. **Baseline:** main `79f517d1fd57ad602316a7b068f5b331c5b94acd`. **Nature:** transparent **POST-HOC arithmetic sensitivity** on already published, consumed B1 DEVELOPMENT counts; no preregistered scientific hypothesis, independent methods review, newly verified original bytes, World, life or new cohort. **Verdict:** `NO_CONFIRMATORY_NI`, Stage 2 still `NOT_ISSUED`.

## Purpose and immutable inputs

The [B1 original report](B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md) records 96 matched development pairs across three **known F0** families (stable, depletion, pulse). [Post-E3 methods audit](POST_E3_INFERENCE_DECISION_ENVELOPE_RESULTS_2026-11-11.md) correctly labels the pooled conditional iid one-sided 95% lower survival-difference bound `-0.04325164695153383` as an **unapproved numerical sensitivity**, *not* biological mean survival non-inferiority. The question here is more restrictive: **does a seemingly favorable aggregate even provide a numerical family-by-family non-inferiority witness under the same hypothetical iid mathematics?**

Only the previously published B1 stratum discordance counts are input. No new outcome, outcome selection, sample modification or cross-study pooling occurs.

| F0 family | Assigned pairs | GATE-only horizon survivors | FIXED-only horizon survivors | Observed GATE - FIXED difference |
| --- | ---: | ---: | ---: | ---: |
| stable | 35 | 4 | 1 | +3/35 = +8.57 pp |
| depletion | 31 | 5 | 4 | +1/31 = +3.23 pp |
| pulse | 30 | 4 | 0 | +4/30 = +13.33 pp |
| **B1 pooled (descriptive only)** | **96** | **13** | **5** | **+8/96 = +8.33 pp** |

These are **matched-pair discordances**, not two statistically independent samples; the same WorldSpec and newborn source are paired within each unit.

## Exact conditional method and independent arithmetic cross-check

For one putative iid paired stratum with `n` pairs, `g` GATE-only and `f` FIXED-only survivors, let `p_g=P(GATE only)` and `p_f=P(FIXED only)`, so the mean paired risk difference is `p_g-p_f`. Use a one-sided lower Clopper-Pearson bound for `p_g` with tail probability `alpha/2`, minus a one-sided upper Clopper-Pearson bound for `p_f` with tail probability `alpha/2`. Bonferroni gives a conservative total one-sided `1-alpha` lower bound **only conditional on an actually iid paired sampling model**. Independence of the two outcomes *within* a pair is not assumed.

The calculations below were independently evaluated outside the repository with (a) direct binomial-tail bisection using `math.comb` and (b) `scipy.stats.beta.ppf` (SciPy 1.17.0); both agreed to better than `1e-12`. The pooled result agrees with the repository's previously published method to better than `1e-12`. **No repository tests or old-original re-reduction were executed in this addendum.**

| Family | One-sided lower, nominal alpha=0.05, **if iid** | One-sided lower, Bonferroni across 3 families (alpha=0.05/3), **if iid** |
| --- | ---: | ---: |
| stable | **-11.7141 pp** | **-15.7055 pp** |
| depletion | **-24.3812 pp** | **-29.5490 pp** |
| pulse | **-7.8150 pp** | **-12.0480 pp** |
| B1 pooled (for orientation, *not* an extra family test) | **-4.3252 pp** | Not part of the three-family family-wise design |

In the **illustrative, unapproved** absolute survival-loss margin `delta=0.05`, the aggregate bound `-4.3252 pp > -5 pp` crosses the *numerical* inequality, while **none of the three family-level lower bounds exceeds `-5 pp`**, even before adjusting for three simultaneous claims. This does **not** establish a harmful effect or statistically significant family differences; it simply means these old counts cannot numerically certify a *uniform, family-by-family* 5 pp non-inferiority property with this bound.

A common **mean-over-specified-F0-mixture** estimand and a **worst-family/minimum-over-families** estimand answer different questions. One can never silently substitute the first for the second after observing positive pooled counts. The old F0 family labels are not independent ecological mechanisms and do not establish transfer to a held-out novel family.

## Reproduction on an available source checkout

The existing, unchanged [pure library function](../../../lab/stage2_exact_paired_survival.py) is sufficient; no new research-policy code or runtime is needed:

```python
from i3.lab.stage2_exact_paired_survival import exact_paired_lower_bound

families = (("stable", 35, 4, 1),
            ("depletion", 31, 5, 4),
            ("pulse", 30, 4, 0))
for label, n, gate_only, fixed_only in families:
    nominal = exact_paired_lower_bound(
        pairs=n, gate_only=gate_only, fixed_only=fixed_only, alpha=0.05)
    simultaneous = exact_paired_lower_bound(
        pairs=n, gate_only=gate_only, fixed_only=fixed_only, alpha=0.05 / 3)
    print(label,
          nominal["simultaneous_one_sided_lower_bound"],
          simultaneous["simultaneous_one_sided_lower_bound"])
```

**Important:** Running the above pure arithmetic does *not* verify source-world independence or reproduce a birth. It makes no valid ecological confidence claim. The family-level values are post-hoc sensitivity, not retrospectively preregistered inference.

## Costs and possible counterinterpretations

The primary [B1 report](B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md) records higher GATE paid vigilance per assigned life overall (167.59388 FIXED -> 171.60702 GATE), despite lower mean paid energy. Within **pulse**, GATE uses **more energy** (107.23264 -> 115.53113) **and vigilance** (131.93407 -> 148.39940) while observed survival is higher. This is not a free cognitive efficiency gain and cannot isolate replay information benefit from changed action, lifetime or sleep.

A positive historical point estimate in each F0 stratum is consistent with both potentially useful and potentially harmful target-population effects under these limited data. As before, additional action-relevant first-person information, equal *executed* computation between visibility/discard arms, genuinely delivered future motor mediation, post-paid-learning bodily outcomes, a new independent source sampling frame and justified margin remain absent. The result does not reopen old B1 indices or resolve the E3 motor negative.

## Research decision and dependencies

1. **Reject the new shortcut:** pooled B1 conditional arithmetic does not imply **family-uniform** survival non-inferiority, even granting hypothetical iid; it certainly cannot certify generalization beyond known F0. This is a methods caution, not a claim that the family-average estimand itself is mathematically invalid.
2. **Preserve all exact original studies and the current scientific state:** B1 DEVELOPMENT permanently consumed; E3 exact software candidate `CLOSED_NEGATIVE`; full Stage 2 `NOT_ISSUED`, P1.3 funded-v2 retained, I3 unregistered, and no new scientific World/owner-index authority.
3. **Next minimum step:** hand this distinct estimand sensitivity to an **independent scoped methods/futility review** under [#1226](https://github.com/josselin-orta-lab/individual-zero/issues/1226) and [#1239](https://github.com/josselin-orta-lab/individual-zero/issues/1239), rather than launch a powered NI cohort or retune E3. Any future primary target must declare **mean over which ecology** vs **uniform family safety**, source independence, power, cost dimensions and tolerated loss *before* exposure.

**Work accounting for this analysis:** 0 new scientific births, 0 new Worlds, 0 reused original traces, 0 source-policy mutations. Independent arithmetic cross-check: PASS. Repository CI: NOT_RUN on this documentation-only result; do not infer a biological GO.
