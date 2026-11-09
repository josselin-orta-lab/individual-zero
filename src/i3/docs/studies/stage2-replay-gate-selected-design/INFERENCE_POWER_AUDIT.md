# Stage 2.1 selected-gate inference and power audit (software-only)

**Date:** 2026-11-09. **Review status:** METHODOLOGICAL DEFECT IDENTIFIED; `REVISE` proposed. **Not independent external review, not accepted preregistration, not a World-opening authorization.**

## Immutable context

- Current reference: P1.3 funded-v2; I3 unregistered.
- Exact main baseline for this audit: `06f7f928eef928f000aebe19afe520ba87ba6ce0` (merged PR #1225). Proposed plan: [PROTOCOL.md](PROTOCOL.md), code [stage2_gate_design.py](../../../../lab/stage2_gate_design.py); original DEVELOPMENT results [80/81](../stage2-replay-gate-development-80-81/RESULTS.md). The canonical R0-R4 result is unchanged. The old 80/81 authorization is exhausted.
- All arithmetic below uses **hypothetical values**, no new genomes, Worlds, scientific lives, or observed outcomes. No old held-out life is reclassified.

## Defect: a population sign test is not mean-survival non-inferiority

The candidate four-endpoint test aggregates GATE-minus-FIXED survival proportions per population, declares a *positive sign* if the difference is greater than -0.05, then uses a one-sided exact sign test. Seven positive signs out of eight non-tied populations yield `9/256 = 0.03515625`, which passes the proposed alpha of 0.05 **for a directional median-population hypothesis**. It does not bound the mean difference, its uncertainty, or the worst-case family effect.

**Discrete counterexample compatible with 30 assigned validation lives per arm in each population:** seven populations have GATE-minus-FIXED survival `-1/30` (one fewer survivor), while the eighth has `-30/30` (all thirty fewer). Every one of the seven mild negative differences exceeds the proposed -0.05 margin and yields a favorable sign. The exact sign-test p value is 9/256, but the equally population-weighted mean difference is

`(7 * (-1/30) + (-30/30)) / 8 = -37/240 = -0.1541666667`.

This is a **15.42 percentage-point mean survival loss**, despite passing the proposed directional survival sign gate. It is an adversarial mathematical example, not I3 evidence. The `directional_gate` function remains unchanged because it is labeled arithmetic-only; it must not be used to claim mean non-inferiority.

The four co-primary conditions require **all** endpoints to pass, but that intersection-union structure does not repair the fact that the survival component tests the wrong estimand. Passing a sign-test composite would not prove mean survival non-inferiority. The five-per-population selected-genome set and world pairing cannot be counted as 1,200 independent genetic populations; there are eight population-level units.

## Exact power of ONE proposed one-sided sign test

The pure helper `i3.lab.stage2_gate_design.exact_sign_test_power(q, tie_probability=t)` enumerates the exact multinomial distribution of eight assumed independent signs (positive `(1-t)q`, negative `(1-t)(1-q)`, tie `t`), excludes ties from the test and sums rejections at alpha 0.05. It uses exact rational arithmetic, not Monte Carlo or a World, and makes no claim that population effects really are identically distributed. All q and t values here are **assumptions**, not fitted probabilities.

| Assumed favorable-sign probability q given non-tie | No ties (t=0) | 10% ties (t=0.1) |
| ---: | ---: | ---: |
| 0.50 (directional null) | 0.03515625 | below 0.05 (conservative) |
| 0.60 | 0.10637568 | 0.06601654 |
| 0.70 | 0.25529833 | 0.16447363 |
| 0.80 | 0.50331648 | 0.34674962 |
| 0.90 | 0.81310473 | 0.63163553 |

With eight units and no ties, **at least seven favorable signs are required**. Even q=0.8 produces only ~50.3% power for one endpoint, or ~34.7% if 10% ties occur. Four co-primary endpoints require their *joint* success; marginal powers cannot simply be multiplied because the endpoints share lives and are correlated. The smallest endpoint power is an upper bound on joint power. This sensitivity table neither powers a mean non-inferiority claim nor justifies any specific sample size.

## Estimands and limits needing independent review

1. **Primary scientific estimand not settled.** The currently drafted primary architecture contrast is `GATE_on_GATE_selected` versus `FIXED_on_FIXED_selected`, independently selected within each population. It asks whether two *selected architecture pipelines* differ; it is not a same-genome mechanistic replay-gate effect. The separate `FIXED_on_GATE_selected` comparator is useful descriptively to isolate the mechanism under GATE-selected genetics. The choice of target must be frozen before exposure and cannot be reversed after viewing outcomes.
2. **Survival:** fixed-horizon survival should be recorded as assigned 400-step censoring vs death before horizon. Death on step 400 is not censoring. A missing or structurally failed life is not a death or a zero and blocks a verdict until the existing blind repair process applies. Confirm denominators and original receipts per arm/family/population.
3. **Cost:** report physically paid cognitive energy and vigilance both **per assigned life** and **per lived step**. The latter is exposure-time conditional and can improve simply because a life ends earlier. A cost-only improvement paired with harmful survival remains adverse; do not use it to certify efficient survival.
4. **Heterogeneity:** the three F0 ecology families are repeated in both phases, with different seeds, not a truly held-out ecological mechanism or whole-family transfer. Show family-specific survival, deaths, activity and costs without selecting the most favorable family. Family disparities remain visible, including a single catastrophic subgroup.
5. **RANDOM:** the frozen `5532/867` mean is *scheduled nominal replay opportunity*, not guaranteed physically executed work. Report scheduled, eligible, actually paid counts and lives that never reached/funded sleep. Keep GATE vs RANDOM and ZERO-PERCEIVED-COST secondary descriptive until a separate multiplicity and power plan exists.
6. **Selection and uncertainty:** preselect population weighting (equal-population vs other), confidence-bound method for the actual mean-survival margin, population/family dependence model, margin interpretation, power under plausible heterogeneity and ties, sample ceiling, and stopping policy. The 5-point margin is a scientific proposal, not justified by arithmetic alone. A design may need more independent populations; simply adding correlated lives is not a replacement.
7. **Custody:** if revised, create a new candidate protocol and exact-source lock. Preserve this original proposal and all historical results. Selection, validation and reserve remain inaccessible without fresh collision checks, irreversible index-scoped pre-exposure claim, full-size G/R rehearsal and separate owner decisions, first for selection, subsequently for validation.

## Recommendation and falsifier

**REVISE / NO SCIENTIFIC OPENING.** An independent scientific-statistical review must select the estimand and justify a valid one-sided confidence bound (or other prespecified method) for mean survival loss, or explicitly narrow the scientific question to the directional population-median property rather than calling it mean non-inferiority. Justify the practical survival margin, demonstrate power for *all* primary requirements under realistic variability, and preregister the family-heterogeneity and missingness response. A favorable directional sign result alone **must not** authorize a scientific GO.

This is a bounded scientific-validity correction, not a new survival policy, designer rescue reward, physical change, retuned replay gate, or Stage 2.2 promotion. Research owner approval and genuinely independent review remain outstanding.
