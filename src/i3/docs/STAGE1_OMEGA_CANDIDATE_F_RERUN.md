# Stage 1 — ω falsifier rerun with Candidate F

Issue #1111. Baseline:
`806119a5181364a2916b556dd2a0f5b84d3d1a41`.

**FROZEN BEFORE EXECUTION. SOFTWARE ONLY.**

## Why this rerun exists

The original ω software falsifier returned `CAPACITY_SHOWN`, but its absolute
plan comparisons were contaminated by the P1.3 projection-length bias.

That blocker is now resolved for a future candidate path:

- #1117 established an unbiased end-to-end comparison oracle;
- #1118 validated canonical event boundaries;
- #1120 showed Candidate F meets the frozen accuracy/cost gate;
- #1121 integrated Candidate F into Mind with exact laboratory parity;
- #1122 established complete common forecast ceilings for Candidate F.

This rerun asks the original capacity question again with Candidate F.

## Frozen substrate

Unchanged from the original falsifier:

- the exact #1101 grid:
  - each body channel separately at 20, 30, 40 or 50;
  - all other channels at 80;
  - horizons 4, 6, 8 or 12;
  - total 80 states;
- exact realistic personal memory;
- exact explorer prefix;
- exact single stop-after-prefix continuation;
- ω arms:
  `{-1, -0.5, 0, 0.25, 0.5, 1}`;
- same uniform, need-agnostic ω shift of the unsupported-effect prior;
- same water-one-future-opportunity kernel;
- no World, life or study index.

Every model uses:

- `simulation_mode="candidate_f"`;
- `projection_accounting="event_local_quadratic4"`.

## Metrics

Per ω:

- states evaluated/unfunded;
- TRIAL among best choices;
- epistemic TRIAL;
- declined;
- positive water revelation count;
- maximum water revelation advantage;
- maximum trial information value;
- best/worst trial advantage;
- actual work;
- common forecast-work ceiling.

Also report the largest statewise range of actual simulated-step work across ω.

## Prospective rules

### R0F — Candidate-F defect guard

All 80 states must be evaluated in every arm.

#1121 exact Mind parity and #1122 complete forecast ceiling are prerequisites
already frozen outside this rerun. This rule checks they remain operational
under all six ω arms.

The old R0 identity to #1101 is intentionally not reused. #1101 measured the
projection semantics that Candidate F was created to replace.

### R1F — Cost fairness under dynamic sparse work

For each state:

- `forecast_work_ceiling` must be identical across all ω arms;
- every actual work component must be <= that ceiling.

Actual work itself is **not required to be identical**. Under Candidate F, ω
changes predicted bodies, which can change event/block counts and therefore the
number of physically paid sparse reward evaluations.

This adaptation is frozen before the rerun. It preserves a common perceived
forecast body while reporting real computation honestly.

### R2 — Direction

As ω increases, both:

- TRIAL selection count;
- positive water-revelation count

must be nondecreasing.

### R3 — Capacity

At least one ω > 0 must create a strictly positive water-revelation advantage
in a state where ω = 0 has none.

If yes, ω can make pre-contact water seeking worth its predicted cost under the
Candidate-F evaluator. This is a software capacity, not a survival claim.

## Verdict

- if R0F or R1F fails: `DEFECT_STOP`;
- otherwise, if R3 holds:
  `CAPACITY_SHOWN_WITH_CANDIDATE_F`;
- otherwise:
  `NO_CAPACITY_THROUGH_CANDIDATE_F`.

R2 is reported and must not be silently tuned around.

## Not authorized here

- genome schema change;
- live ω integration;
- Competition change;
- World/life execution;
- reference cognition adoption;
- ADR-0015 selection/validation exposure.

Any architecture adoption remains a separate preregistered ADR-0015 gate.
