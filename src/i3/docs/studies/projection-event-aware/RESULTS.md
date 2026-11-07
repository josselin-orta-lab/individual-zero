# Stage 1 projection candidate C: results

**Frozen verdict: `NO_CANDIDATE_PROMOTED`.**

Protocol: [STAGE1_PROJECTION_EVENT_AWARE.md](../../STAGE1_PROJECTION_EVENT_AWARE.md).
Software only: no World, life or study index.

Exact checked head: `b544fc92c4bdd1ec9dfac329d96897711a9d0591`.
CI run: `42387763077`.

## Frozen-grid result

The executable grid contains 486 cases per scheme:
3 fixtures x 6 genomes x 27 bodies. Amendment A1 corrected the inherited
prose count before Candidate-C metrics were read.

| Metric | Candidate C |
| --- | ---: |
| Max decision bias vs per-step | **0.0601516822** |
| Projection-equivalent invariant max gap | **0.0601516822** |
| Max prefix error vs per-step | 0.0561701313 |
| Max absolute +1 wait gap | 0.0603784877 |
| Max absolute +3 wait gap | 0.1405561745 |
| Paid projection units, min | 11 |
| Paid projection units, mean | 22.5844 |
| Paid projection units, max | 33 |
| Per-step truth units | 255 |

Prospective limits were 1e-3 for decision bias and invariant, with every case
strictly cheaper than per-step.

Candidate C passes only the cost criterion.

## Interpretation

Event segmentation is useful: it compresses the 255-step diagnostic projection
to at most 33 paid distress evaluations on this grid.

But one midpoint plus a quadratic segment approximation is not accurate enough
for the nonlinear distress curves. The remaining error is large enough to
preserve the same order of bootstrap inconsistency that Stage 1 is trying to
remove.

This is not evidence against the projection-bias diagnosis. Per-step D1 still
removes the inconsistency and makes Stage-1 information decisive. It is evidence
that **quadratic event-aware interpolation is too coarse**.

## Decision

- Keep reference `chunk_end` unchanged.
- Do not use Candidate C in Stage-1 kernels.
- Do not tune Candidate C after this result.
- Retain the event boundaries and measured 11–33-unit cost as useful evidence
  for a separately frozen higher-order candidate.
- Any next candidate must be declared prospectively and must still satisfy the
  same <=1e-3 accuracy criteria while remaining strictly below 255 units in
  every frozen-grid case.

No scientific or architecture promotion follows.
