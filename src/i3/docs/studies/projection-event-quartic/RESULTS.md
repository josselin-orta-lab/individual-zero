# Stage 1 projection candidate D: results

**Frozen verdict: `NO_CANDIDATE_PROMOTED`.**

Protocol: [STAGE1_PROJECTION_EVENT_QUARTIC.md](../../STAGE1_PROJECTION_EVENT_QUARTIC.md).
Software only. No World, life or study index.

Exact checked head: `d1b149fee25216a0bea303ff12c33a02fbf1a27a`.
CI run: `42388102157`.

## Frozen 486-case result

| Metric | Candidate D | Candidate C |
| --- | ---: | ---: |
| Max decision bias vs per-step | **0.0337292963** | 0.0601516822 |
| Projection-equivalent invariant max gap | **0.0337292963** | 0.0601516822 |
| Max prefix error vs per-step | 0.0226390093 | 0.0561701313 |
| Max absolute +1 wait gap | 0.0603828537 | 0.0603784877 |
| Max absolute +3 wait gap | 0.1405649000 | 0.1405561745 |
| Paid units min | 19 | 11 |
| Paid units mean | 39.5926 | 22.5844 |
| Paid units max | 55 | 33 |
| Per-step truth | 255 | 255 |

Prospective accuracy limit: 1e-3.

Candidate D passes the cost criterion and improves prefix/decision error
substantially relative to C, but fails both accuracy gates.

## Interpretation

Adding fixed quarter points is useful but insufficient. The remaining error is
too large to justify simply increasing interpolation order again without
decomposing its source.

In particular, D's raw +1/+3 wait gaps are almost unchanged from C while its
error versus per-step shrinks. The next useful question is whether the residual
comes from:

1. approximation of distress inside otherwise correct event segments; or
2. a difference between event-segment body evolution and the discrete per-step
   body trajectory, especially around restoration/clamping.

That decomposition can be answered without a new candidate by evaluating every
discrete endpoint inside the same event segmentation.

## Decision

- Candidate D rejected unchanged.
- Default remains `chunk_end`.
- Do not use D in Stage-1 kernels.
- Do not add more interpolation nodes before the error-source decomposition.
- Retain D's 19-55-unit cost and improved bias as evidence that event-aware
  compression remains promising.

No scientific or architecture promotion follows.
