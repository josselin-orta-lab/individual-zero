# Stage 1 projection: canonical event-segmentation diagnostic

Issue #1111. Baseline:
`10cbc0e014afd68fc5d0661ea1c27a3a10677862`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE DIAGNOSTIC ONLY.**

## Purpose

#1117 authorized one end-to-end high-precision laboratory oracle for future
projection candidates. Before freezing Candidate E, separate the remaining
event-aware problem into:

1. event-boundary/state evolution;
2. sparse distress evaluation inside otherwise correct segments.

This diagnostic tests item 1 only.

## Frozen numerical semantics

Reuse #1117's canonical represented-float semantics:

- `Decimal.from_float` for body, learned drift, learned restoration and theta;
- Decimal context precision 100;
- no epsilon death rule;
- exact `F/W/I <= 0` death predicate;
- unchanged float I3 `feats`, `distress` and gamma arithmetic at reward
  readouts.

The body remains Decimal for the entire direct bootstrap.

## Frozen event definitions

Preserve the existing event-aware structural definitions, but evaluate them in
the canonical Decimal state:

- completion of learned E/V restoration;
- crossing of 0, theta or 100 for each body channel under the active linear
  segment rates;
- bounds imposed by the existing outer geometric chunks
  `1,2,4,8,16,32,64,128`.

A segment must end before a non-integer event it would cross. If an event lies
exactly on an integer endpoint, that endpoint is evaluated in a unit segment so
the regime/death boundary is explicit.

No adaptive tolerance or result-dependent segmentation is allowed.

## No interpolation

Within every resulting event segment, evaluate **every discrete endpoint**.

For endpoint `step=1..run`:

- compute the Decimal body algebraically from the segment-start state;
- apply the same restoration amount active in that segment;
- clamp;
- apply the exact vital death predicate;
- convert the resulting body to float only for the unchanged distress readout;
- apply the exact existing gamma discount weight for that discrete endpoint.

After death, maximal distress is absorbing.

Every discrete endpoint is billed, including absorbing endpoints. Therefore a
direct diagnostic projection must cost exactly 255 simulated units.

## Frozen grid

Use the same already-exposed direct grid:

- 3 fixtures;
- midpoint + G0 seeds 6000..6004;
- 27 bodies.

Total: **486 direct projection cases**.

For every case compare the canonical event-exact projection against #1117's
direct end-to-end high-precision oracle.

Record:

- maximum absolute projected-value error over all three gamma horizons;
- maximum final-body channel error;
- min/mean/max event segment count;
- min/mean/max paid endpoint evaluations;
- worst-case metadata.

## Gate

Numerical tolerance: **1e-10**.

If:

- max projected-value error <=1e-10;
- max final-body error <=1e-10;
- every projection costs exactly 255 endpoints;

classify:

`CANONICAL_EVENT_SEGMENTATION_MATCHES_ORACLE`.

Otherwise classify:

`CANONICAL_EVENT_SEGMENTATION_DIFFERS_FROM_ORACLE`.

Passing this gate clears event boundaries/state evolution for a later
prospectively frozen Candidate E. It does not authorize any sparse evaluation
scheme by itself.

## Boundaries

This slice does not:

- add a runtime projection mode;
- change `Mind`, body or world laws;
- alter #1117's oracle;
- add Candidate E;
- rerun omega;
- access World, life, selection, validation or reserve data.
