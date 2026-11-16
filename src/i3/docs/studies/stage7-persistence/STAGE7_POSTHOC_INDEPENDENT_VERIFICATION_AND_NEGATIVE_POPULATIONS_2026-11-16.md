# Stage7 | Independent original-level verification and exploratory negative-population diagnostic

**Date:** 2026-11-16. **Post-exposure read-only work.** No new cohort, no changed original source, no refitted primary threshold.

## Provenance and independent verification

- Frozen Stage7 source: `06cfcf9cc9414e0f139b39a42d05177ddb813782`.
- [One-shot GitHub Actions run #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125): Python 3.11 rehearsal, Python 3.12 rehearsal and science all completed successfully.
- Pre-exposure scientific plan artifact 14213827437, ZIP SHA256 `8af2e4f4f9207997c6197c33e902f28672663d1e74de2a64e04fe568d4610ea3`.
- Scientific original lives artifact 14218795289, ZIP SHA256 `7391497d8664032c690b5d75cec3f98cabc8c589ea77fc946151d922d3a481b6`.
- Scientific report artifact 14217357887, ZIP SHA256 `a6e2b61208cbf65771ab8f8e101a3b7673552c4cdf656281dad38165f75e301c`.
- An **independently written read-only local Python reducer**, not importing the i3 motor, verified each of the 11,520 native gzip originals (2,304 G0; 4,608 G1; 4,608 G2), individual compressed and decompressed SHA256, identities, source pin, planned World/life seeds, paired worlds, paid cognitive accounting, exact body trace lengths, deaths, horizon censoring, per-population totals, the three generation seals and the nine-phase SHA256 chain. This is **not** a claim that the exact PR #1416 CLI was run.
- There are **18 recorded deaths on step 400**, distinct from administrative censures. The PR #1416 fix and regression tests preserve this distinction. The corrected PR has a successful software CI run [#43864009710](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43864009710).
- Final phase-chain tip: `7f48c4ba839fef47cb9f2a763f192c46feebc25ca302c6aa3512c24f4fcce0c5`.

**Independent reduction result:** `READ_ONLY_REPRODUCTION_OK`. G2 population differences selected-minus-random_parent = [-3.680556, +32.812500, +11.583333, +15.527778, +38.520833, -3.243056, +6.131944, +7.652778, +31.958333, +5.138889, +28.847222, -30.368056, +22.465278, +44.756944, +0.145833, -17.791667] lived steps. Strict positives 12, negatives 4, zero 0; average +11.9036458333. The **unmodified prospectively fixed requirement** is at least 13/16 strictly positive and a positive mean. Thus the pre-registered **scientific verdict stays `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`**.

## Exploratory G1 vs G2 contrasts

| Population | G1 Δ selected-random | G2 Δ selected-random | G2 horizon censored selected/random |
|---|---:|---:|---:|
| P00 | +6.2431 | -3.6806 | 35/35 |
| P05 | +6.6667 | -3.2431 | 59/52 |
| P11 | -4.6389 | -30.3681 | 44/51 |
| P15 | +4.2361 | -17.7917 | 47/51 |

The G1/G2 advantage change is descriptive across distinct generation environments, **not** proof of a genetic transmission mechanism.

## G2 ecological decomposition, 48 original lives per arm and family

| Population | stable Δ | depletion Δ | pulse Δ |
|---|---:|---:|---:|
| P00 | -11.8333 | +1.6875 | -0.8958 |
| P05 | -8.6458 | -1.3333 | +0.2500 |
| P11 | -23.8125 | -35.6667 | -31.6250 |
| P15 | -11.3333 | -6.7292 | -35.3125 |

### Diagnostic, hypotheses not verdicts

- **P00**: marginal population-wide disadvantage. Stable contributes most; equal G2 horizon censures (35/35) mean that total-step differences also reflect pre-horizon deaths.
- **P05**: very small negative mean but *more* censored selected lives (59 vs 52). This illustrates that a horizon-survival count and the preregistered mean lived-steps estimand can disagree. Investigate the full duration distributions, not just censored fractions.
- **P11**: strongest broad disadvantage, negative in stable, depletion and pulse. The G1 contrast is also negative; this is a useful robustness/failure-mode target but does not establish heritable causal harm.
- **P15**: the most adverse environment-specific difference is pulse (-35.3125). The G1-positive/G2-negative contrast change suggests a possible genotype–ecology interaction to test prospectively, not to proclaim retrospectively.

Deaths are overwhelmingly recorded with `zero_water` as cause in these original subgroups, with some `zero_food`. These are recorded terminal reasons, not evidence establishing why parent selection failed. Ecological subdivisions are **post hoc**, share population-level dependence and are not 48 independent replicates for inference; the 16 populations remain the prespecified primary units.

## Scope and boundaries

The comparison is **G2 selected vs random_parent within the same preallocated population/world opportunity**, not raw G0→G1→G2 means (ecologies change). The audit verifies recorded bytes and internal custody; it **does not** independently replay physical motor semantics, independently certify OS randomness, prove ecological independence, or provide external timestamp attestation. No new life was generated and no mutation, seed, frozen threshold, scientific record or I3 promotion was changed.

Follow-up: run the *exact* corrected PR #1416 CLI on the same three untouched artifacts and archive its console output; keep its separate review gate until then.
