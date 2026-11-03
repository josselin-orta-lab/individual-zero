# Native I2: experience-grounded, persistent resource associations

**Design and research correction, 3 November 2026.** Scientific ruling:
[ADR-0010](../../docs/decisions/ADR-0010-stable-world-evidence-based-association.md).
Source-locked earlier negative evidence remains in
[NATIVE_RECURRENT_NEED_RESULTS_906.md](NATIVE_RECURRENT_NEED_RESULTS_906.md):
both arms in #912 drank degraded water ineffectively 42 times, and neither
returned to critical thirst in 96 paid physical ticks.

## Problem: wrong target and instantaneous belief reversal

The generic G2 chosen-result heuristic uses rounded GLOBAL physiological
relief +5; drinking can produce no water gain yet obtain a positive learned
evaluation. The previous draft of #914 proposed a special one-point
penalty for each *consecutive* failure, but reset the entire penalty after
a **single** later successful drink. That would make an otherwise stable
environment artificially volatile and violate the intended low-abstraction
memory. The initial #914 CI also exposed two *test contract errors*:
a new test prescribed `boire` at water=50 even though Competition chose
`NO_ACTION`; another broke a critical provenance suffix by adding a
marker after it. The failures were real and are retained in Actions
run [41633243029](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41633243029).

## Corrected, falsifiable native research rule

For `boire`, `boire_decouverte` and `manger`, use only physically
committed BEFORE/AFTER states and the actual targeted reserve, **provided
the corresponding need was measurably unmet before the chosen action**.
Each restoration counts +1, each nonrestoration -1 in this simple
exploratory unit-score association. Recompute the accumulated
`successes - failures` from the **same immutable born SQLite owner**
at every paid decision, adding it to the born prior and current innate
need pressure. The journal is constrained by `MAX_BORN_STEPS=128` and
cold replayed; the separate generic G2 chosen-outcome working window
remains at 64. No second persistent H2 owner or speculative memory is
created. Non-resource choices continue the previous generic G2 scoring
path, with its known limitations.

A single success after 42 failures changes -42 evidence to -41, **not
zero**. A single failure after 10 successes changes +10 to +9, not an
instant permanent rejection. Neither passage of time nor a hidden world
reversal changes the association in the absence of personal evidence.
This is **not calibrated natural learning**: the symmetric one-unit
weight is a declared engineering hypothesis with failure/noise and
action-selection falsifiers, and linear counts within the technical
born horizon have known saturation/scale limitations.

The separate critical survival reflex and its evidence sufficiency
remain unchanged. The resource remains available if physically offered,
even when its subjective score is negative; there is no forced motor
action, artificial re-exposure, free UC, hidden phase lookup or fixed
staleness bonus. A personally lived success changes the evidence score
but never certifies that all future source outcomes are safe.
The evidence suffix for the original critical last-resort contract is
retained, with new target-outcome provenance placed BEFORE `:native-body`.
The independently replayed scores and provenance must match the paid
event journal. The native genesis is versioned **v9** to avoid
reinterpreting earlier research births.

## Result boundary and next experiment

Tests now cover first autonomous noncritical drinking in a matched
learning ON/OFF birth, source-specific successes and failures, long
history without time-based forgetting, one surprising success, no
wrong-need credit, no-learning controls and cold replay. Neither the
tests nor the source-locked 96-cycle #912 histories establish a superior
survival result. Next, in a prospectively frozen **stable environment**
with an actual alternative affordance, contrast *chosen actions* and
paid physiological consequences after repeated stable failures against
a no-learning comparator. Only afterward study gradual change with
real cues; sudden uncued flips remain stress tests, not assumed
knowledge. G3/H2, independent M11 and naturally learned competence
remain **NOT_ESTABLISHED**.
