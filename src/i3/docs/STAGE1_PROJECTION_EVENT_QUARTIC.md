# Stage 1 projection candidate D: fixed five-node event accounting

Issue #1061. Baseline:
`50c4679ed46560809631115852a3fe590a7428ed`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE ONLY.**

## Motivation

Candidate C established that event segmentation can compress the 255-step
per-step diagnostic to 11-33 paid projection evaluations, but its one-midpoint
quadratic interpolation retained 0.06015 maximum decision bias and failed the
1e-3 gate.

I3 genome distress powers are bounded to `p in [1,3]`. Candidate D therefore
tests one structurally motivated higher-order approximation while keeping C's
event segmentation unchanged.

## Frozen algorithm

Use the exact Candidate-C event boundaries.

For every event segment longer than one discrete step, sample personal distress
at fixed normalized positions:

```text
x = 0, 1/4, 1/2, 3/4, 1
```

The segment-start sample is inherited from the prior endpoint, so four new
distress evaluations are paid per segment.

Fit the unique degree <=4 interpolating polynomial through those five samples.
Evaluate that polynomial at each discrete step endpoint inside the segment and
sum it with the exact gamma discount weights.

One-step event segments remain exact endpoint accounting. Death remains
absorbing. Every distinct distress sample is billed as one simulated projection
unit.

No adaptive tolerance, no extra node insertion and no result-dependent
subdivision are allowed.

## Frozen characterization

Exactly the same executable projection grid as Candidate C and per-step truth:

- 3 fixtures;
- 6 genomes;
- 27 bodies;
- 486 cases per scheme;
- horizon 6;
- prefix / +1 wait / +3 waits.

## Gate

Candidate D becomes only an opt-in candidate if all are true:

1. max decision bias vs per-step <= 1e-3;
2. projection-equivalent invariant max gap <= 1e-3;
3. max direct projection cost <255 paid units.

Report max prefix error, wait gaps and min/mean/max paid units.

If any criterion fails: `NO_CANDIDATE_PROMOTED`. D is not tuned in this PR.

If D passes, the next slice must update Stage-1 forecast-ceiling quoting for
dynamic projection cost and rerun the already-frozen omega falsifier before any
reference-adoption proposal.

Default P1.3 remains `chunk_end`.
