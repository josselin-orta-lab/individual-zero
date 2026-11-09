# I3 Stage 2.1 / Survival B1: autonomous campaign launch

**9 November 2026. Campaign state: COMPUTATIONAL STUDY ACTIVE + ENGINEERING SMOKE LAUNCHED. SCIENTIFIC EXPOSURE STILL LOCKED.**

The research owner requested autonomous definition and launch after [Phase B statistical planning](CONFIRMATORY_SURVIVAL_POWER_STUDY.md) and [decision-gate issue #1239](https://github.com/josselin-orta-lab/individual-zero/issues/1239). This grants operational discretion to pursue a defensible study; it does **not** imply that an independent reviewer has assessed assumptions, that an unscoped authorization can reopen old indices, or that source/World provenance is attested. P1.3 remains the reference, and I3 is unregistered. All original DEVELOPMENT 80/81 evidence remains untouched.

## 1. Chosen scientific objective and boundary

**Primary objective:** test non-inferiority of physically funded GATE versus FIXED/P1.3 on the 400-step binary survival outcome using *matched newborn G0/world pairs*. Both policies must run on the same G0 genome, frozen WorldSpec and life seed; death at step 400 is a **death**. The target is the equal-family-weight mixture of the three **known F0 families** stable, depletion and pulse, with each family producing independently sampled newborn-genome/world pairs under a prospectively frozen random-source protocol.

This is a proposed **superpopulation of generated known-F0 mechanisms**, **not** transfer to a new ecological family, not evolution under separate genetic selection, not a causal decomposition of replay selection, and not the 720-life descriptive v3 study. Correlation between GATE and FIXED **within a pair is expected**; reusing one world across multiple founder seeds does not create independently sampled world draws. A separate future scientific transport must produce every proposed independent pair from its own reserved seed/world allocation before any World exposure.

Primary estimand: `mu = P(GATE-only survives 400) - P(FIXED-only survives 400)`. These two disjoint events define each matched pair's +1/-1 outcomes. For proposed biological margin `delta`, null `H0: mu <= -delta`, alternative `H1: mu > -delta`. **No survival-loss margin has yet been independently justified or approved.** An illustrative 5 percentage point margin and one-sided alpha 0.05 are used only for numerical sensitivity. Favorable stopping, retry, attrition removal and outcome-dependent new sampling are forbidden.

## 2. A finite-sample exact lower confidence procedure

The new pure arithmetic `i3.lab.stage2_exact_paired_survival` uses a **conservative simultaneous** one-sided lower confidence limit for the paired risk difference. For `n` genuinely independent identically distributed matched pairs, let `X` count GATE-only survivors and `Y` count FIXED-only survivors, `X+Y <= n`. Marginally, `X ~ Binomial(n,p+)` and `Y ~ Binomial(n,p-)`. No assumption of independence of `X` and `Y` is needed.

- Compute the **exact one-sided Clopper-Pearson lower bound** `L_plus` for `p+` at tail probability `alpha/2`.
- Compute the **exact one-sided Clopper-Pearson upper bound** `U_minus` for `p-` at tail probability `alpha/2`.
- Return `L = L_plus - U_minus`. The union bound ensures coverage **at least 1-alpha** for `mu=p+ - p-` under iid pairs; finite-sample conservative (not a claim of optimal power).
- For a future *fully approved* prospective study only, the statistical non-inferiority rule would be `L > -delta`. The software itself **never issues a scientific verdict** and cannot approve `delta`, independence or admissions.

Complete pair denominators are mandatory. A missing or structurally failed original is **NO_VERDICT**, never a zero difference, death or censored case. Fixed and GATE survival disagreements, all family strata, actual paid energy/vigilance **per assigned life**, survival-time distribution and adverse discordances remain visible regardless of the primary result. Secondary cognition or family effects are **descriptive**, with no hidden multiple testing.

### Computational campaign launched

GitHub workflow `.github/workflows/i3-proposal-checks.yml` runs a deterministic **synthetic**, iid paired survival simulation grid (240, 500, 1,000 and 1,500 pairs; discordance probabilities 10%/10%, 15%/15%, 30%/30%, and adverse 5%/10%), 256 trials each. It reports only a model-conditional observed rejection frequency and Monte Carlo uncertainty, **not** new biological observations or guaranteed real-world power. Unit tests independently enumerate every trinomial count configuration for small n to check coverage against known null populations.

The completed [Phase B Hoeffding sensitivity](CONFIRMATORY_SURVIVAL_POWER_STUDY.md) remains a conservative, distribution-free alternative: 7,198 independent paired units for an illustrative 5-point margin, 80% target power and assumed zero true effect. The exact paired CP calculation may be more efficient if the prespecified iid model and realistic discordance assumptions hold; power depends strongly on ecological heterogeneity and cannot be inferred from the 12 old correlated blocks. **No final sample size is authorized by these simulations.**

## 3. The launched live-engineering transport check

The [frozen engineering-only plan](ENGINEERING_B1_PLAN.json) deliberately has **zero scientific indices**. The dedicated two-version GitHub workflow uses the existing hard-closed `stage2_panel.rehearse` transport and the existing `engineering` admission path to generate **24 temporary, non-evidentiary full-horizon lives** (3 F0 families × 4 disjoint engineering World indices × 1 G0 birth seed × FIXED/GATE). The same G/R original sealing and validation code is executed as the historical transport. It verifies 24/24 generated/reduced and all structural funding/admission invariants.

Only an allowlisted **structural** PASS/FAIL/count/fingerprint/mean-step-time receipt and the **synthetic** statistical power grid may be uploaded. Engineering lives, food, deaths, survival, behavior, routes, policy decisions or full original life records **must not** be published or used as evidence, and their temporary originals are destroyed when the rehearsal finishes. Running a software-engineering rehearsal is not a 24-life scientific study.

This is a **transport smoke**, not the required full-scale rehearsal on the exact SHA of the future independent-world scientific runner. It does not establish an independent sampling frame or authorize a new World. The existing scientific runner remains deliberately hard-closed even if old ADR-0017 lift text is present.

## 4. Concrete path to new scientific lives, in priority order

1. **Sampling/world namespace decision:** independently review a new disjoint World/index domain capable of independent paired draws from the three fixed known-F0 generators. Specify random entropy and deterministic auditability, unit-level genome/world/life seeds, family weights and independence assumptions. The existing P2 F0 validation indices are not a substitute and the P2 reserve must remain sealed.
2. **Scientific non-inferiority margin and sample-size decision:** obtain independent methodological review of the exact CP one-sided procedure (including small-sample coverage, multiple outcomes, target superpopulation and heterogeneity) and justify a meaningful margin. Determine the fixed upper n under plausible worst-case discordance and compute limits/resources before exposure. Do not inflate the sample by recounting correlated lives.
3. **Implement an entirely separate prospective source-locked scientific admission and irreversible index claim**, tested fail-closed, preserving the old permanently exhausted 80/81 runner. Protect the design from post-outcome edits.
4. **Rehearse full exact-transport scale on non-evidentiary engineering** with identical pipeline, shape and horizon, both supported Python versions, and no outcome disclosure.
5. **Independent attestation and owner-scoped release:** externally witness the source SHA/World generator/manifest, register the complete protocol prospectively, then record an explicit new index/transport authorization. Only then open new science Worlds once under G/R, retain failures and negatives, and perform a read-only final analysis.

**Current execution decision:** engineering and numerical study **RUN**; scientific cohort **LOCKED_PENDING_REVIEW**. This is a deliberate stop at the boundary, not an assertion that the requested research is scientifically complete. Neither owner delegation nor software CI can manufacture an external independent review.
