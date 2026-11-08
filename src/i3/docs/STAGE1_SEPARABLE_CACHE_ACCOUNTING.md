# Stage 1 exact cache: physical-accounting sensitivity on Candidate-G

Issue #1061. Baseline:
`ebc9d1894e67ac56f9e6a88f5e4bbbb26cc61cbc` (#1151).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ONLY.**

No World, no life, no study index, no runtime projection mode, no reference
adoption. P1.3 remains the reference.

## Why this slice exists

#1151 established a narrow fact: the 255-step per-step projection can be
factorized into exact channel-local traces and reused inside one decision batch
with numerical-noise error only.

It did **not** establish affordability because current I3 prices model-level
reward evaluations, not one channel-local distress sample.

Do not choose a convenient conversion after seeing Candidate-G behavior. This
slice brackets that unresolved compute price with two predeclared mappings while
holding cache-memory accounting fixed. The question is whether the conclusion
is robust to that ambiguity.

## Candidate representation held fixed

Use the exact #1151 decision-local cache only. A fresh cache is created for each
of the frozen 80 #1146 states and discarded after that complete kernel call.

There is no persistent cache, no cross-decision reuse and therefore no
learned-drift invalidation mechanism in this slice.

The stored trace is reduced to the minimum exact payload needed by #1151's
combination rule:

- 255 channel levels;
- 3 x 255 gamma-discounted distress-prefix values;
- one predicted death-step item;
- one final-distress-contribution item;
- an exact cache key.

No interpolation, quantization, nearby-level reuse or body grid is allowed.

## Fixed memory accounting

Existing I3 information kernels charge five memory items for a five-channel
body cell, and personal-history reads/writes are also paid as memory items.
Therefore this slice treats one retained/read scalar model value as one
`memory_item`.

A uniform conservative exact key size is frozen at **13 memory items** per
trace, large enough for the E/F/V key with restoration coupling.

Per new trace:

- stored payload: `4 * 255 + 2 + 13 = 1035 memory_items`;
- build writes are paid once when the trace is created.

Per projection use of one trace, hit or miss:

- exact key/read payload ceiling: **19 memory_items**
  (13 key items + death step + level + 3 prefixes + final contribution).

A projection uses five traces and pays **1 cycle** for cache orchestration.
Scalar arithmetic itself creates no new work category, consistent with the
existing projection-candidate accounting.

These are work charges, not a new persistent-memory gene or global RAM limit.
Decision-local capacity is bounded structurally by the complete matrix and
physically by the precomputed CognitiveBudget ceiling.

## Two frozen compute-price arms

A trace build always computes 255 channel endpoint/distress samples.

### A. `bundle5_lower`

Optimistic lower mapping only:

- every group of up to five channel samples is one existing
  `simulated_step`;
- one trace build therefore pays **51 simulated_steps**.

Rationale: one ordinary projected reward evaluation consumes all five channel
contributions. This is the most favorable whole-reward-equivalent bundling.
It is explicitly a **lower accounting bound**, not an adopted tariff.

### B. `scalar1_upper`

Conservative mapping:

- every channel endpoint/distress sample is one `simulated_step`;
- one trace build therefore pays **255 simulated_steps**.

This intentionally refuses any sub-reward discount.

Both arms pay the identical memory/cycle charges above. Cache hits pay no trace
build simulation or write cost, only the common read cost.

## Common forecast ceiling

The frozen Stage-1 kernel requires one complete common work ceiling before its
branch values are compared.

For each #1146 state, quote the cache with **zero assumed hits** across the
complete matrix. The quote therefore covers every possible trace build and
read before any candidate result is known.

Actual work may be lower through exact hits and must be reported separately.
Unused ceiling is never billed.

If the common ceiling cannot be funded from the state's real body, record
`UNFUNDED_COMMON_CEILING` and do not execute that arm/state.

No favorable cache hit may be used to make the preflight quote affordable.

## Frozen fixture

Reuse #1146 unchanged:

- 5 body channels;
- levels 20, 30, 40, 50;
- horizons 4, 6, 8, 12;
- 80 states total;
- same personal effect memory;
- same personally learned recurrence gaps 2, 6, 10;
- same explorer/ordinary continuation;
- same unsupported-effect prior and information reduction.

The only changed mechanism is the projection implementation/accounting arm.

The cache must still reproduce per-step projection values at <=1e-10 direct
error in focused software tests.

## Baselines frozen from #1149

On the same 80-state grid:

| arm | selected epistemic | mean simulated steps/state |
| --- | ---: | ---: |
| P1.3 reference | 1 | 53 |
| Candidate-F accurate projection | 24 | 470 |
| per-step truth | 32 | 1288 |

Cycles = 18 and memory items = 201 for those three #1149 arms.

Under current BodyLaws this corresponds to mean work bills:

| arm | energy | vigilance |
| --- | ---: | ---: |
| reference | 0.5062 | 1.006 |
| Candidate-F | 1.3402 | 1.840 |
| per-step | 2.9762 | 3.476 |

These are software work bills, not life outcomes.

## Report per accounting arm

- funded / unfunded states and their body/horizon metadata;
- selected epistemic, selected water-deficit, selected other-deficit, declined;
- max information value and best/worst trial advantage for completed states;
- mean/max actual CognitiveWork by field;
- mean/max common forecast ceiling by field;
- mean/max actual energy and vigilance bill;
- cache trace builds/hits and hit fraction;
- trace build samples, memory writes/reads and max live entries;
- any actual-work > common-ceiling violation (must be zero).

## Frozen interpretation

Define:

- `decision_relevance_retained`: selected epistemic >= **24**, the already
  observed Candidate-F accurate-projection count on this exact grid;
- `cheaper_than_candidate_f_mean_bill`: mean actual energy <= 1.3402 **and**
  mean actual vigilance <= 1.840.

Primary accounting classification:

1. If `scalar1_upper` funds all 80 states:
   `CACHE_ACCOUNTING_ROBUSTLY_FUNDED`.
2. Else if `bundle5_lower` fails to fund any of the 80 states:
   `CACHE_ACCOUNTING_UNFUNDED_EVEN_LOWER_BOUND`.
3. Otherwise:
   `CACHE_ACCOUNTING_SENSITIVE`.

This classification is about funding robustness only. Report relevance and
Candidate-F cost comparison separately.

A later runtime candidate is authorized by this slice only if the conservative
`scalar1_upper` arm simultaneously:

- funds all 80 states;
- retains >=24 selected epistemic states;
- has mean energy and vigilance bills both <= Candidate-F's frozen #1149 bill.

Otherwise do not pick the optimistic tariff after exposure.

If the result is accounting-sensitive, the next architecture step must either
derive a less ambiguous model-level work unit or compress the exact
representation enough that both bounds agree. If even the lower bound is
unfunded, close this stored-trace cache and treat compression as a new
architecture hypothesis.

## Boundaries

This slice does not:

- alter BodyLaws or CognitiveWork rates;
- add a new work category;
- modify P1.3 or Candidate-F;
- persist a cache across decisions;
- change Candidate-G recurrence or information semantics;
- open World/life/development/selection/validation/reserve conditions;
- authorize Stage 2.
