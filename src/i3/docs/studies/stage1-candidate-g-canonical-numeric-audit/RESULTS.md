# Candidate-G canonical numerical audit: historical water selections are a float artifact

Protocol:
[STAGE1_CANDIDATE_G_CANONICAL_NUMERIC_AUDIT.md](../../STAGE1_CANDIDATE_G_CANONICAL_NUMERIC_AUDIT.md),
declared before execution at `5863dacfdd21467777aeaf038ee8858842c7adb4`.

Baseline: `819182ee7a749c8667f114fcf14bf38439091708` (#1154).
Characterized source: `ce6c16bbae6bdf9d3f46cdb38bebbdcd0dc776ee`.
GitHub Actions run `42474206334`: Python 3.11 PASS, Python 3.12 PASS.

Software only: no World, no life, no runtime promotion.

## Frozen classification

`HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT`

The authorized high-precision end-to-end oracle and historical float per-step
both pay the same full 255-unit projection quote and the same total mean work:
18 cycles, 201 memory items and **1288 simulated steps/state**.

Their decisions differ anyway:

| Arm | Selected | Water-deficit | Other-deficit | Declined |
| --- | ---: | ---: | ---: | ---: |
| historical float per-step | 32 | **8** | 24 | 40 |
| canonical high-precision per-step | **24** | **0** | **24** | 40 |
| Candidate-F projection | **24** | **0** | **24** | 40 |

Candidate-F mean work is 18 cycles, 201 memory items and **470.05 simulated
steps/state** on the same frozen grid.

## Statewise result

The canonical high-precision selected set is **exactly identical** to the
Candidate-F selected set:

- overlap: 24/24;
- canonical-only states: 0;
- Candidate-F-only states: 0;
- water states in either set: 0.

The historical float arm has exactly eight additional states, and every one is
water-deficit:

- water 40, horizons 4/6/8/12;
- water 50, horizons 4/6/8/12.

Canonical high precision selects none of them.

No non-water selection changes between historical float and canonical high
precision.

## Numerical signature

Historical versus canonical high precision:

- maximum information-value difference:
  **1.2761166003905089e-06**, at water 50 / horizon 12;
- maximum trial-advantage difference:
  **0.0074818702381935775**, at water 20 / horizon 12.

The historical water-only information values exposed in #1149 were tiny
(~1e-9..1e-6), consistent with a boundary-sensitive numerical branch rather
than robust new information value.

This is coherent with the earlier independent death-boundary audit, which
showed repeated IEEE-754 accumulation can delay a vital-zero predicate by one
discrete step while canonical high-precision/event arithmetic reaches the
boundary at the earlier endpoint.

## Consequence for #1149

#1149's important result survives, but its interpretation is sharpened.

Still supported:

- P1.3 `chunk_end` suppresses canonical decision-relevant information;
- Candidate-F's consistent projection raises selected epistemic states from 1
  to **24** on the frozen Candidate-G recurrence grid;
- personal recurrence is not the principal bottleneck.

Retracted as a target:

- the historical float per-step count of **32**, including 8 water states,
  must not be treated as canonical truth;
- a new architecture must not be tuned to recover those eight states.

The expensive exact/cache/death-truncation work after #1149 remains useful as
a cost/representation characterization, but historical repeated-float parity is
not a promotion objective.

## Architectural implication

On the #1146 grid, Candidate-F's event-local projection reproduces the complete
**canonical selected-state set** at about 36.5% of the oracle's simulated work
(470.05 versus 1288).

The next Stage-1 question should therefore stop redesigning the projector and
return to the integrated candidate:

**Candidate-G personal recurrence + Candidate-F canonical projection, with no
genomic omega policy.**

That combination already exists as the #1149 software diagnostic arm. Before a
new World/life panel, freeze a bounded integration gate that separates:

1. projection cognition cost;
2. recurrence/information policy;
3. the genomic-omega policy that was present in the rejected Candidate-F live
   architecture.

Do not infer live viability from this software audit alone.
