# I3 Stage 2.1: confirmatory survival study, statistical launch (candidate B1)

**9 November 2026. STATUS: POWER/SAMPLING STUDY LAUNCHED, SCIENTIFIC WORLD EXECUTION BLOCKED.**
**Study type:** proposed prospective independent-cluster survival non-inferiority trial.
**Evidence so far:** software-only power grid with declared hypothetical assumptions; no new scientific lives, allocations, executions, or non-inferiority verdict.

This is the second phase of the [archived evidence campaign](ANALYSIS_CAMPAIGN_2026-11-09.md) and a *separate* inferential branch from the [v3 720-life descriptive candidate](MECHANISM_FIRST_CANDIDATE_V3.md), [original selected-genome pipeline](PROTOCOL.md), and [v2 inference correction](PROTOCOL_REVISION_V2.md). None of the frozen source, DEVELOPMENT 80/81, genotype selection rule, P1.3 funded-v2 or replay-gate mechanism is modified.

## 1. Target, hypotheses and planned primary outcome

**Scientific question:** Over a prospectively defined, independently sampled distribution of **newborn G0 genome/world pairs** drawn from the known F0 ecology mixture, is the expected probability of surviving the full 400-step horizon under GATE no more than a defensible, predeclared absolute margin below FIXED, while preserving actual physical cognitive-cost results?

A paired unit would hold the **same newborn G0 genome, WorldSpec and life seed** fixed while executing exactly two full-policy arms: FIXED/P1.3 and physically funded GATE. Outcomes of a unit are (GATE horizon survivor, FIXED horizon survivor). Define the independent **cluster** outcome `D_i = I(GATE censored at 400) - I(FIXED censored at 400)` in `{-1,0,+1}`. The primary estimand is `mu = E[D_i]` over the **prespecified target population distribution of paired world/genome units**. The protocol must specify whether this is a finite F0 mixture, a source-generator superpopulation, or something else. No whole-family transfer to unseen ecological mechanisms is claimed from F0 alone.

**Non-inferiority hypothesis** for a *scientifically justified and still undecided* margin `delta > 0`: `H0: mu <= -delta` vs `H1: mu > -delta`. Death **at step 400** is death, not horizon survival. A structurally failed or missing life yields `NO_VERDICT`, never a death, fabricated survivor or postmortem replacement. Retain all assigned lives, adverse ecological strata and per-life physical funding costs. No favorable sequential stopping, adaptive reseeding, post-outcome family dropping or retrospective margin selection.

Illustrative planning uses **one-sided alpha 0.05** and **power 0.80**. The previously drafted five-percentage-point margin `delta=0.05` is **not approved**: its scientific acceptability must be justified independently before any study registration. Costs, restricted lived time, inactivity, family harms and GATE−RANDOM contrasts are **secondary descriptive only**, without automatic superiority claims or multiplicity laundering. This is about fixed-G0 **full policy contrast**, not an evolved architecture or causal attribution to replay selection alone.

## 2. Independent-cluster power study now running as software

The pure module `i3.lab.stage2_confirmatory_survival_power` gives two deliberately separated planning models, never a scientific verdict:

**Conservative, distribution-free.** For truly independent bounded paired cluster differences in `[-1,1]`, the one-sided Hoeffding lower bound `L = mean(D) - sqrt(2*ln(1/alpha)/n)` covers the average expected cluster difference conditionally on independence. With target power at least `1-beta` under a hypothetical true mean `mu_alt > -delta`, a **sufficient, conservative** fixed size for that bound is

`n >= 2*(sqrt(ln(1/alpha)) + sqrt(ln(1/beta)))^2 / (mu_alt + delta)^2`.

This is a *power guarantee for that method under assumptions*, not an information-theoretic minimum, the true sample size required by an efficient paired test, or permission to create so many Worlds. Generalization to a population distribution further requires a defensible random sampling/exchangeability model.

| Hypothetical acceptable absolute loss margin | Assumed true GATE−FIXED survival difference 0 pp | Assumed true difference +2 pp | Assumed true difference +5 pp |
| --- | ---: | ---: | ---: |
| 2 percentage points | 44,984 independent paired units | 11,246 | 3,673 |
| 5 percentage points | **7,198** independent paired units | 3,673 | 1,800 |
| 10 percentage points | 1,800 independent paired units | 1,250 | 800 |

All cells assume the *same conditional* alpha=0.05, power≥0.80 and independent units. **Margins and alternatives are hypothetical**. Choosing the 10-point margin only to reduce cost would be scientifically invalid.

For the provisional 5-point/zero-effect example, **7,198 distinct independent paired units** would require 14,396 two-arm lives and up to **5,758,400 horizon steps**, *if* a defensible source/world sampling frame and enough new legal indices existed. Neither is established. The existing F0 validation candidate provides 48 known family world identifiers and 240 matched founder/world blocks that share genetics and world slots. It cannot be silently counted as 240 independent cluster draws, cannot provide 7,198 new independent ecological units, and its fixed 8 population labels cannot be upgraded to thousands of independently sampled populations.

**Conditional paired normal-approximation sensitivity.** Hypothesize each independent pair has probabilities `p_plus` (only GATE survives), `p_minus` (only FIXED survives) and `1-p_plus-p_minus` (tie). Then `mu=p_plus-p_minus` and `Var(D)=p_plus+p_minus-mu^2`. An illustrative fixed-variance one-sided normal size is

`n ≈ ceil(Var(D)*(z_(1-alpha)+z_(power))^2/(mu+delta)^2)`.

For an *unapproved* 5-point margin and assumed:
- `p_plus=p_minus=0.10`: approximately **495 independent pairs**.
- `p_plus=p_minus=0.15`: approximately **742 independent pairs**.
- `p_plus=p_minus=0.30`: approximately **1,484 independent pairs**.
- `p_plus=0.11, p_minus=0.09`: approximately **252 independent pairs**.
- `p_plus=0.05, p_minus=0.10`: mean difference equals the null boundary; **no finite-power target separation**.

These are **asymptotic sensitivity calculations** that provide no exact type-I error or 80%-power guarantee, and the pilot's 12 correlated observations cannot legitimately validate their assumed probabilities. An independently designed, predeclared coverage/size procedure and plausible variance/heterogeneity model are needed before an efficient sample size may be selected. Never substitute these numbers for a confirmed experimental plan.

Methodological analogies (not rules legally governing an artificial individual): FDA's [2016 non-inferiority guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/non-inferiority-clinical-trials) emphasizes margin justification and interpretable comparisons. The [ICH E9(R1) estimand framework](https://www.ema.europa.eu/en/documents/scientific-guideline/ich-e9-r1-addendum-estimands-and-sensitivity-analysis-clinical-trials-guideline-statistical-principles-clinical-trials-step-5_en.pdf) motivates explicit target population, conditions, outcome, intercurrent events and summary measure.

## Follow-up: finite-sample paired bound and live engineering study (9 November 2026)

A separate [autonomous B1 launch](SURVIVAL_B1_LAUNCH.md)
now implements an **exact one-sided paired risk-difference lower
confidence bound** using Bonferroni-adjusted Clopper-Pearson marginal
limits on GATE-only versus FIXED-only horizon survivors. It gives
finite-sample conservative coverage if the prospective *pairs*
are genuinely iid; correlation between policies within a pair is
allowed. The paired numeric power scenarios are **hypothetical** and
cannot choose a final n or justify World opening by themselves.
An engineering-only two-version GitHub Actions check uses the existing
source-locked G/R transport to generate and reduce 24 temporary
non-evidentiary full-policy lives without publishing their outcomes.
This is a smoke test, not the required full-scale prospective
scientific-transport rehearsal. Independent review and new admission
remain blocked.

## 3. Why the requested scientific run cannot open Worlds yet

This user-requested study **launches its power-analysis and protocol-review stage now**. It does **not** implicitly reuse an owner lift for DEVELOPMENT 80/81 or grant a new lift under ADR-0017/0019. Before the first new scientific birth, the research owner and an independent method reviewer must settle:

1. **Target and scientific loss margin:** specify the actual F0 sampling population, ecological-family weights and biologically meaningful allowable absolute survival loss, rather than reverse-engineering the 80/81 pilot.
2. **Genuine units and coverage:** source-lock a new independent paired world/genome sampler or a justified independent population design; define dependence across shared genomes/worlds/families, confidence method and fixed-sample joint power, including adverse family effects. A seed value alone does not prove independence. No external-family transfer claim from F0.
3. **Resources and scope:** decide whether the conservative count is feasible; if a lower paired-model number is selected, justify and verify its inference calibration and statistical power *before exposure*. Record a fixed upper sample ceiling and no outcome-based stopping.
4. **Full study custody:** identify never-used index namespaces after collision review; freeze a versioned plan and exact source/World witnesses, independent approval, no-retry G/R pipeline, full-size exact-transport engineering rehearsal, and a **new** explicit index-scoped owner authorization. Never use the reserve or reuse consumed indices.
5. **Reproducible analysis:** prospective written handling of missingness, death at horizon, budget deficits, RANDOM scheduled versus paid replays if optional, all ecological strata and adverse/null cases. Confirm the archive verifier is not treated as an authority signature.

**No official scientific preregistration is claimed. The actual execution phase is BLOCKED pending these checks.** This is not a refusal to study survival: it is the first completed formal power-planning stage for a study strong enough to support or refute a meaningful survival claim, without inventing invalid independent units.

## 4. Reproducibility and next decision

```bash
PYTHONPATH=src python -m i3.lab.stage2_confirmatory_survival_power
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage2_confirmatory_survival_power.py'
```

The command prints the full margin/true-effect/discordance scenario grid, its explicit assumptions, F0 capacity discrepancy and `scientific_verdict=NOT_ISSUED`. It never runs a World, changes cognition or opens a cohort. Negative, underpowered and infeasible scenarios are valid outputs.

**Research recommendation:** `PROSPECTIVE_POWER_DESIGN_STARTED; NO_WORLD_UNTIL_INDEPENDENT_REVIEW`. If meaningful margins and adequate independent ecological replication cannot be demonstrated at reasonable cost, transparently declare the confirmatory study infeasible and retain the smaller descriptive v3 mechanism question as a separate option. Do not relabel the pilot or expand F0 solely to force a positive result.
