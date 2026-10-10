# I0-vNext Stage 11: descriptive prospective prediction from lived observations

**Classification:** software development, not scientific acceptance. **Stage 9 remains scientific NO-GO.**

## Motivation

The public, non-held-out 18-step hydration diagnostic exposed an actual gap:
Stage-11 Exploration made a causal-test action eligible and it was physically
applied, but frozen E-v1 Equipment returned `equipment_input_unseen`.
Consequently Stage-9 Planning stored an empty numerical prediction in
`PlanStep`; P-47 AgencyComparator correctly produced no comparison, and the
canonical Causal Model could not publish a P-35 intervention.

The missing comparison must not be "fixed" by assuming the world effect,
using hidden WorldBody or the Lab, relaxing the comparator's evidence gate,
or promoting the episode itself as causal intervention.

## Narrow opt-in development mechanism

`src/i0/modules/lived_prediction.py` implements a **stateless descriptive
one-step forecaster** based strictly on prior *individually experienced* drinking
actions that the canonical Causal Model already holds with:

1. an actual command and transition, each with a distinct physical event ID;
2. an independently Memory-closed physical episode, and next-step Perception water observation;
3. an earlier emission/observation world step, never the present action or later data;
4. the same observed water-source site, without duplicated episode, transition or time;
5. enough versioned independent observations and sufficiently consistent numeric deltas.

The prospective expected water level equals the current accessible
Perception water plus the arithmetic mean of the previously witnessed
one-step changes, clipped to the observable range. The precision bound is
declared before the observation; inconsistent data produce **no prediction**.

A `stage11_prospective_prediction_frozen` journal record carries the prior
physical transitions, Memory episodes, steps, predicted value, precision and
predictor version. It is appended **before Action Control dispatch**. The
actual command's `PreparedCommand` carries the result to the unchanged P-47
comparator. A later independently observed disagreement is allowed and cannot
be relabelled retroactively as confirmation.

This source is NOT an E-v1/E-v2/E-v3 Equipment prediction, `E_a^sim`,
`Q`, evidence of causal establishment, or a correction in the Simulator.
Equipment remains frozen, and only the canonical owner can publish
`testee_par_intervention` / `etablie` after its usual Memory and P-47 joins.

## Explicit opt-in and bounds

`Stage11Config.prospective_water=None` (default) fully disables the adapter.
The public fixture accepts `build_stage11_reference_runtime(
enable_lived_prediction=True)` with the **development-only** values:

- `min_distinct_episodes=1`
- `maximum_spread=0.5`
- `precision_floor=0.0`
- `max_precision=1.0`

These values are not preregistered scientific P-47 calibration; one prior
observed action does not establish a causal relation. The zero-precision
single-sample case is an exact descriptive forecast to be evaluated honestly,
not a claim of a certain outcome.

The new option in the public diagnostic is:
`run_public_hydration_funnel(seed=41, world="small_water_gain",
steps=18, enable_lived_prediction=True)`.
The no-predictor control retains the same ordinary reference configuration.
The protocol and digest schema are incremented to
`stage11-public-hydration-funnel-dev-v3`.

## Failure modes and outstanding gates

- Not all real drinks have a Memory-closed *causal-action* numeric witness.
  Earlier goal-driven observations may be qualitative only; this forecaster
  intentionally declines to use an invented numeric value.
- A short run or habituation may finish before any **subsequent** eligible
  test action, so even a valid prior sample need not produce a new comparator
  report. Zero forecasts is a permissible negative outcome.
- A conforming P-47 report is descriptive agency evidence only.
  A real Memory-closed current physical episode and independent n2 contexts
  are still required before causal establishment.
- Compare longer public worlds, matched null controls, reproducible schedules,
  count forecast accuracy separately from causal status, and test rollback,
  replay and snapshot restoration before any acceptance claim.
- No Stage-9 held-out materials, independent science review, Stage-9 Golden,
  INV-25 result or retrospective threshold tuning are authorized by this code.

**Status: Stage 11 development in progress; scientific verdict = none.**
