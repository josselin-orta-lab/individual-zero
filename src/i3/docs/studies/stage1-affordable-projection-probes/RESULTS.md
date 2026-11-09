# Affordable consistent projection: two cheap ideas fail feasibility

**Declared exploratory probes, not a protocol.** No World, no life, no study
index, nothing adopted. Script:
[`stage1_affordable_projection_probes.py`](../../../archive/stage1/lab/stage1_affordable_projection_probes.py);
data: [probes.json](probes.json). Reference cognition unchanged.

## Why

#1149 showed that Candidate-G becomes decision-relevant only under an accurate
projection (24–32/80 epistemic trials versus 1/80), at ×8.9–24 paid simulation.
The open architectural question is an **affordable** consistent projection. Two
cheap ideas were measured against the per-step projection on the #1146
fixtures (10 bodies; decision-relevance limit used elsewhere: 1e-3).

## 1. Local sensitivity (one accurate projection + gradient, reused for all options)

| Option end state | Maximum error of the linear expansion |
| --- | --- |
| wait | 0.0034 |
| sleep | 0.0055 |
| eat (+12 food) | 0.30 |
| drink (+30 water) | **1.91** |

It fails, and fails worst where decisions matter. Consumption options move the
predicted death time, a strongly nonlinear effect that no local expansion
captures. Even small options exceed 1e-3.

## 2. Decision-time anchored grid (same chunk_end accounting, shared boundaries)

| Projection | Maximum decision bias over option pairs, vs per-step |
| --- | --- |
| reference (`chunk_end`, grid restarts after each plan) | 0.2164 |
| anchored grid (boundaries 1, 3, 7 … 255 from decision time) | 0.2153 |

It does not help. The bias is not mainly a misalignment of chunk boundaries
between options of different lengths. It is the coarse end-point accounting of
the large far chunks, which options with different bodies cross differently.

## What this establishes

Consistency needs per-step-equivalent accuracy along the whole projected
horizon, which is what makes Candidate F expensive. Cheap shortcuts that keep
coarse far-future accounting cannot reach 1e-3. Do not retry these two ideas.

## Next design (not implemented): separable cached projection

Two structural properties of P1.3 point to an affordable exact scheme:

- **Separable distress.** `D(h) = Σ_c w_c · d_c(h_c)`, so without death each
  channel's discounted future distress depends only on its own start level,
  its own learned drift, γ and its genes.
- **Slow variation.** Within a life, the drift (personally learned wait effect),
  θ, p, w and γ change slowly.

Candidate scheme (generic, first person, no behavioral content):

1. Per channel and per γ, tabulate exactly (per step) the discounted distress
   `S_c(level, τ)` up to a cut time `τ`, for levels 0–100 on a fixed grid.
   Keep the table as a paid, capacity-bounded memory.
2. Rebuild a channel's table only when its learned drift changes beyond what
   the table supports, paying the rebuild.
3. For an option's end body, read death time `τ = min over vital channels of
   level/(−drift)`. The value is the tabulated per-channel sums up to `τ`, plus
   `d_max` for every later step, with interpolation between grid levels.
4. Handle energy and vigilance restoration by sleep (piecewise linear until the
   threshold) as one extra breakpoint per channel.

Falsifier to freeze before any code:

- decision bias versus per-step ≤ 1e-3 on the #1146 grid, the #1101 grid and
  the plan set above;
- paid work per decision, table storage and rebuild cost reported against the
  reference, including a full rebuild after every drift change;
- `chunk_end` stays the default, and any adoption needs an ADR-0015 gate.

If storage plus rebuild cost exceeds the reference budget envelope in realistic
lives, the honest conclusion is that consistent foresight is unaffordable at
current physical prices. That itself would be a scientific result about I3's
stake, not something to hide with a cheaper but biased projection.
