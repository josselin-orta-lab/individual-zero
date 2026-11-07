# Stage 1 omega falsifier: fresh Candidate-F rerun after dispatch repair

Issue #1111. Baseline:
`8aba9402c2dc43493023fb46fec2b98bb5ef612c`.

**FROZEN BEFORE EXECUTION. SOFTWARE ONLY.**

## Why a fresh rerun is required

#1123 executed the frozen Candidate-F omega falsifier once, but the result was
invalidated after a post-hoc audit showed that Candidate F bypassed the
`ObservedEffectView` exact branch delta.

#1124 repaired only that proxy dispatch.

The original raw `NO_CAPACITY_THROUGH_CANDIDATE_F` result remains archived as
invalid defect evidence and is not reinterpreted.

## Frozen falsifier identity

Reuse the existing module unchanged:

`src/i3/lab/stage1_omega_candidate_f_falsifier.py`

Frozen Git blob:

`3a5cb6003d4555e9a62c6b204cfffcdd06c5346f`.

A dedicated software test computes the Git blob from the checked-out source and
fails if this falsifier changes.

## Frozen substrate

Unchanged from #1123:

- exact #1101 80-state grid;
- omega arms:
  `{-1,-0.5,0,0.25,0.5,1}`;
- same realistic personal memory;
- same explorer prefix;
- same stop-after-prefix continuation;
- same uniform need-agnostic omega shift;
- same water-one-future-opportunity kernel;
- `simulation_mode="candidate_f"`;
- `projection_accounting="event_local_quadratic4"`;
- forecast ceilings from #1122.

The only changed prerequisite is the #1124 proxy-dispatch repair.

## Frozen rules

### R0F

All 80 states must be evaluated in every omega arm, with zero unfunded state.

### R1F

For each state:

- common `forecast_work_ceiling` is identical across omega;
- every actual work vector remains <= its ceiling.

Actual sparse work may vary with omega because changed predicted bodies may
change Candidate-F event/block counts.

### R2

Trial-selected and positive-revelation counts must be nondecreasing as omega
increases.

### R3

At least one positive omega must create positive water revelation in a state
where omega=0 has none.

## Frozen verdict

- R0F/R1F defect => `DEFECT_STOP`;
- guards pass + R3 => `CAPACITY_SHOWN_WITH_CANDIDATE_F`;
- guards pass + no R3 => `NO_CAPACITY_THROUGH_CANDIDATE_F`.

No tuning after execution.

## Boundaries

This rerun does not:

- change omega or add it to the genome;
- change Candidate F;
- change the water kernel;
- open World or life data;
- make a survival claim;
- authorize reference adoption.

A capacity result is only software evidence that a generic inherited expectation
parameter can affect first-contact decisions under the repaired, unbiased
Candidate-F simulation substrate.
