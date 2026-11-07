# Stage 1 event-projection residual decomposition: results

**Verdict: `SEGMENTED_BODY_EVOLUTION_CONTRIBUTES`.**

Protocol: [STAGE1_PROJECTION_ERROR_DECOMPOSITION.md](../../STAGE1_PROJECTION_ERROR_DECOMPOSITION.md).

Software only. No World, life, study index, omega rerun or projection promotion.

Exact checked code head: `44d771632a2b201e8b0a528f9289cdf575ba9d6d`.
CI run: `42389577522`.

## Frozen 486-case result

| Metric | Event-exact vs per-step |
| --- | ---: |
| Max prefix-value error | 0.01813728111588997 |
| Max decision bias | **0.01813728111589108** |
| Projection-equivalent invariant gap | 0.018137281115890636 |
| Max final-body channel error | **0.40000000000019753** |
| Paid endpoint units min / mean / max | 255 / 255 / 255 |

Candidate D versus event-exact still differs:
- max prefix difference: 0.022639009319109782;
- max decision difference: **0.015592015231826295**.

Therefore interpolation remains a material source of Candidate-D error, but it
is **not the only source**. Even after removing interpolation completely, the
event-segment body trajectory does not reproduce the current repeated-unit
per-step implementation on the frozen grid.

## Worst case

The maximum final-body difference occurs in the sleep-learned midpoint fixture
from body `[80,10,80,80,80]`.

- event-exact final body: `[80,0,59.99999999999999,90,80]`
- per-step final body: `[80,0,59.599999999999795,90.20000000000014,80]`
- differing channel: 2 (water)
- max difference: 0.40000000000019753

The difference is exactly one fixture drift step on water/integrity:
water differs by 0.4 and integrity by 0.2 while food is zero in both outputs.

The maximum decision bias appears on the same low-food body family, in the
sleep-learned G0-6003 fixture for +3 waits:

- event-exact gap: 0.018137281115890636
- per-step gap: -4.440892098500626e-16
- absolute bias: 0.01813728111589108

This strongly localizes the remaining body-evolution discrepancy around the
discrete death boundary. It does not yet establish whether the reference
per-step recurrence or the closed-form event endpoint should define canonical
projection semantics.

## Decision

- Candidate C remains rejected.
- Candidate D remains rejected.
- Do **not** add more interpolation nodes yet.
- Do **not** rerun omega.
- Default remains `chunk_end`.
- Before Candidate E, audit the exact death-boundary arithmetic on the already
  exposed worst case and freeze which discrete semantics is canonical.

No scientific or architecture promotion follows.
