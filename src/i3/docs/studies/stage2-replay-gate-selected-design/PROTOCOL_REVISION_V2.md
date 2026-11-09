# Stage 2.1: revised inferential design candidate v2 (NO World authorization)

**2026-11-09. STATUS: SOFTWARE-ONLY DRAFT, NOT A FROZEN PREREGISTRATION, NOT OWNER APPROVED.**
Baseline `main` `1be9764bf156c9eaf86ec7e4a3b202181925133f`. This is a *separate revision proposal*, not an edit of the original candidate [PROTOCOL.md](PROTOCOL.md) or original [inference audit](INFERENCE_POWER_AUDIT.md). Retain P1.3 funded-v2 and the frozen Stage-2.1 Mind unchanged. Historical DEVELOPMENT 80/81 is consumed without retry.

## Target and scientific distinction

The intended primary survival estimand is the **equally weighted mean of eight independent population-specific fixed-horizon survival contrasts**: `GATE_on_GATE_selected` minus `FIXED_on_FIXED_selected`. Each population independently selects 5 of 40 G0 founders for each architecture using complete selection receipts, then evaluates the chosen five on its six unexposed validation worlds at 400 steps. Each population contrast is the fraction surviving among its 30 assigned GATE lives minus that among its 30 assigned FIXED lives. Thus `d_p` lies in [-1,+1], with `p=0..7`. The *architecture-plus-selection pipeline* is the target, not same-genome causal replay effects. The alternative `FIXED_on_GATE_selected` arm isolates a same-genome comparison descriptively only. The eight populations, not the 240 lives, are the proposed statistical units.

The original **seven-out-of-eight directional sign criterion is NOT a mean non-inferiority test**, and may remain an exploratory sign report only. Four historical co-primary sign thresholds in [PROTOCOL.md](PROTOCOL.md) are not accepted as a mean-survival gate. Do not silently replace them for any executed experiment.

## Candidate confidence procedure, not yet validated

A transparent and conservative **one-sided Hoeffding** lower-bound calculation is implemented in `i3.lab.stage2_mean_survival_sensitivity.mean_survival_lower_bound`. Under *independent* population contrasts, each bounded [-1,+1], its lower confidence bound for the expected equally weighted population contrast at nominal one-sided alpha 0.05 is

`L = max(-1, mean(d_p) - sqrt(2*ln(1/0.05)/n))`, with `n = 8`.

For eight populations the radius is approximately **0.8654** (86.54 percentage points). At an *unreviewed* illustrative margin of -0.05, `L > -0.05` requires an observed mean above about **0.8154**. Thus the method is almost incapable of certifying a practically meaningful 5 percentage-point survival non-inferiority margin at realistic effects. This is a useful software proof of **design insufficiency**, not a replacement accepted test or an argument for relaxing the error bound.

To bound the same [-1,+1] population contrast with Hoeffding radius 0.05 at alpha 0.05 would require at least **2397 independent populations**, not merely additional correlated lives. This is a conservative *precision* calculation, not required sample size, joint four-endpoint power, or an assertion that 2397 populations should be produced. If populations share identical ecological environments, assumptions can fail and even this bound lacks coverage. Fixed deterministic seed allocation does not itself prove iid or independent sampling from a meaningful target population.

## Required operational estimand details

1. Define the target population-distribution and source of genuine population independence; justify generalization beyond the finite fixed G0/ecology family. F0 uses three **known** families (stable, depletion, pulse), only new seeds, so it does not test novel mechanisms or whole-family transfer.
2. Specify full original-receipt population denominators (30 assigned per arm), mortality/censoring on step 400 (death is never censoring), structural failures and blank receipts (NO_VERDICT), independent selection on 40 complete founder trials per arm, paired six-world exposure without leaks and unaltered treatment assignment. Never drop a death, deficient founder or unfavorable population.
3. Specify the acceptable survival-loss margin **scientifically** before exposure and choose a justified method with confidence coverage and simulation/power sensitivity over plausible heterogeneity and ecology dependence. The five-per-population selected genomes are not independent populations.
4. Preserve all physical cognitive energy/vigilance per assigned life and per actually lived step, costs conditional on survival, inactivity, deaths, full family strata and reasons for any outcome. Higher efficiency with earlier mortality must remain adverse.
5. Continue to report the frozen RANDOM-EQUAL-MEAN schedule `5532/867` versus actual funded replay receipts (nominal, eligible and paid), not claim equality of executed work. GATE versus RANDOM and ZERO-PERCEIVED-COST are **secondary descriptive** unless explicitly separately powered and allocated alpha before exposure.
6. The exact directional-sign code and the confidence-sensitivity helper are pure math: they cannot authenticate source SHA, independence, complete originals, selection integrity or grant a scientific verdict. There is no runner in this proposal.
7. An eventual intersection-union confirmatory gate requires **each** primary endpoint to use a valid estimand-matched test at alpha 0.05, plus joint power over correlated survival, energy, vigilance and inactivity. The original sign-test composite is not acceptable. No post hoc endpoint promotion or threshold adjustment.

## Decision / handoff

**NO_GO for the current eight-population mean-survival non-inferiority claim.** Keep eight F0 founder populations as a software-only design candidate; do **not** inflate to thousands of populations automatically. Scientific owner and genuinely independent statistical review must first arbitrate between (A) a practically meaningful but properly powered mean-survival non-inferiority experiment; (B) an explicitly weaker directional population-median hypothesis without a non-inferiority claim; or (C) stopping Stage 2.1 as underpowered. Independently justify the margin and target ecology/population. Avoid shifting to Stage 2.2 until a separately recorded Stage-2.1 closure decision.

No selection, validation, reserve, development or other new World is authorized. Before any future scientific exposure a new index-scoped claim, new locked source, full-scale G/R rehearsal, scientific registration and separate owner authorizations for selection then validation are mandatory. No historical code or evidence is rewritten by this proposal.
