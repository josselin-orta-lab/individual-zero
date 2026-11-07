# P1.3 projection bootstrap consistency: results

**Frozen selection verdict: `NO_CANDIDATE_PROMOTED`.** The discounted trapezoid
keeps the cost (8 paid units) but cuts the worst decision bias only from 0.169
to 0.133, far above the 1e-3 limit. The reference default stays `chunk_end`.

**Declared diagnostic D1** (unbiased per-step projection): the plan-length bias
was hiding both ω's effect and the decisiveness of Stage-1 information value.

Protocol: [STAGE1_PROJECTION_CONSISTENCY.md](../../STAGE1_PROJECTION_CONSISTENCY.md)
(frozen `6183162`, D1 declared `107b5c6`, before execution). Implementation:
`11228c6`. Software only: **no World, no life, no study index**. Data:
[characterization.json](characterization.json), [d1_omega_per_step.json](d1_omega_per_step.json).

## Selection characterization

The grid had 270 cases per scheme: 3 fixtures × 6 genomes × 27 bodies, horizon 6.

| Scheme | Paid units | Max decision bias vs per-step | Max prefix error vs per-step | Projection-equivalent invariant gap |
| --- | --- | --- | --- | --- |
| `chunk_end` (reference) | 8 | 0.169 | 0.802 | 0.168 |
| `trapezoid` (candidate) | 8 | 0.133 | 0.286 | 0.132 |
| per-step (truth) | 255 | 0 | 0 | **8.9e-16** |

Per-step projection satisfies the bootstrap-consistency invariant exactly,
which confirms the diagnosis. The trapezoid is exact only where distress is
linear (tested). Its residual error comes from events inside large chunks
(64 and 128 steps): threshold crossings, deaths and sleep restoration, which a
single linear segment cannot represent.

On the reference fixtures even the per-step gap for one extra wait reaches
0.060. That gap is real, not bias: an explicit wait costs energy, while the
projection assumes energy is held and restored by sleep.

## D1 — ω falsifier rerun with per-step projection (descriptive)

| ω | Trial among best | Epistemic trials | Positive water revelation | Max revelation advantage | Unfunded |
| --- | --- | --- | --- | --- | --- |
| −1 | 16 | 16 | 16 | 0.0003 | 0 |
| −0.5 | 36 | 36 | 36 | 0.0016 | 0 |
| 0 | 40 | **32** | 40 | 0.0058 | 0 |
| 0.25 | 44 | 12 | 44 | 0.0063 | 0 |
| 0.5 | 44 | 12 | 44 | 0.0076 | 0 |
| 1 | 52 | 12 | 52 | 0.0118 | 0 |

Compared with the biased run (52 positive revelations at every ω from −0.5 to
0.25, epistemic trials 0 at ω = 0):

- **ω's effect is strong and monotone** once the bias is removed: 16 → 52 trial
  states across the range, and a 45-fold range in maximum revelation advantage.
- **Stage-1 information becomes decisive.** At ω = 0, 32 of 40 selected trials
  carry positive information value. #1101's "information sub-decisive"
  (0/80) was largely produced by the plan-length bias.
- **Hope can crowd out learning motives.** Above ω = 0, more trials are taken
  but fewer are epistemic (12): with strong hope, trying pays for itself before
  information is needed.

## What this establishes and what it does not

Established in software: the P1.3 projection's end-of-chunk accounting biases
every comparison between plans of different lengths. Removing it makes both
information value and ω's expectation shift act as designed.

Not established: any survival effect. Per-step projection costs 255 paid units
instead of 8 and is not a usable live cognition under v2.

## Next intervention (not implemented)

**Candidate C: event-aware projection accounting**, under a new frozen protocol:

- Split each chunk at the analytically computed threshold-crossing and death
  steps (linear drift makes them closed-form), and apply the trapezoid on each
  segment.
- Add a midpoint evaluation on long segments if needed. Each extra distress
  evaluation is paid.
- Selection: decision bias ≤ 1e-3 against per-step, with paid units reported.
  Kernels that forecast `len(proj_chunks)` units must then read one projection
  cost function instead.
- Then rerun the frozen ω falsifier with C, prospectively. Adoption into the
  reference still requires an ADR-0015 gate, consigned before any exposure.
