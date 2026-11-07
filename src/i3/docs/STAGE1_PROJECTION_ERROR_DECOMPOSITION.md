# Stage 1 projection: event-segmentation error-source decomposition

Issue #1111. Baseline:
`3568d810346f15d544f44810660ee49cb390b65e`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE DIAGNOSTIC ONLY.**

## Why this diagnostic exists

Candidate C kept the reference geometric horizon, split projection at predicted
bodily regime events and used a start/mid/end quadratic inside each segment.
It cost 11-33 projection evaluations but retained a maximum decision bias of
0.0601516822 versus the 255-unit per-step truth.

Candidate D kept exactly the same event segmentation and replaced the quadratic
with fixed five-node degree <=4 interpolation. It improved maximum decision bias
to 0.0337292963 at 19-55 evaluations, but still failed the frozen 1e-3 gate.

Increasing interpolation order again would be unguided. Before another
candidate, separate two possible residual sources:

1. the event-segment body evolution may differ from the discrete per-step
   trajectory;
2. the body trajectory may be correct while interpolation of nonlinear distress
   inside the segments is too coarse.

## Frozen diagnostic algorithm

Reuse Candidate C/D unchanged:

- outer projection chunks `1,2,4,8,16,32,64,128`;
- `_projection_next_event_segment`;
- `_projection_advance`;
- the individual's own learned drift and restoration;
- exact gamma discounting;
- absorbing death.

Inside each event segment, do **not interpolate distress**.

For each discrete endpoint `step = 1..run`, evaluate the body by calling the
same event-aware continuous endpoint from the segment start, evaluate distress
at that exact discrete body, and accumulate that one endpoint with its exact
gamma weight.

This construction is called **event-exact** only in the laboratory diagnostic.
It is not added to `PROJECTION_ACCOUNTING`, not selectable by runtime, and not
a promotion candidate. It may spend the full 255 endpoint evaluations.

After a predicted death, the remaining endpoint rewards are the absorbing
`-d_max` value and remain explicitly billed so the diagnostic work count is
comparable to per-step truth.

## Frozen grid

Use the exact existing projection-consistency grid:

- fixtures:
  - sleep learned;
  - sleep unlearned;
  - projection-equivalent;
- genomes:
  - midpoint;
  - generation-zero seeds 6000..6004;
- 27 bodies;
- horizon 6;
- plans:
  - prefix;
  - prefix +1 wait;
  - prefix +3 waits.

Total: **486 cases**.

Truth remains the existing `(1,)*255` per-step projection.

## Recorded quantities

For event-exact versus per-step:

- maximum prefix-value error;
- maximum decision bias for +1/+3 wait comparisons;
- projection-equivalent invariant maximum gap;
- maximum direct final-body channel error;
- direct projection paid units min/mean/max.

For Candidate D versus event-exact:

- maximum prefix-value difference;
- maximum decision difference.

## Frozen interpretation

Numerical-trajectory tolerance: **1e-10**. This is descriptive, not a selection
gate.

- If event-exact vs per-step is <=1e-10 for decision bias, invariant and final
  body, while D remains materially different, classify the residual as
  `INTERPOLATION_SOURCE_CONFIRMED_ON_FROZEN_GRID`.
- If event-exact materially differs from per-step, classify as
  `SEGMENTED_BODY_EVOLUTION_CONTRIBUTES`.
- If both are material, report the mixed result without tuning.

No candidate is promoted by this diagnostic.

## Boundaries

This slice does not:

- modify P1.3 default `chunk_end`;
- change Candidate C or D;
- add a new runtime projection mode;
- change genome or ω;
- rerun the ω falsifier;
- open a World, life, development index, selection, validation or reserve.

Only after the residual source is identified should a new projection candidate
be prospectively frozen. Any candidate must independently pass the existing
`<=1e-3` bias gate before ω is rerun with it. Reference adoption remains an
ADR-0015 decision.
