# Exact separable projection cache: structural gate PASS

Protocol: [STAGE1_SEPARABLE_PROJECTION_CACHE.md](../../STAGE1_SEPARABLE_PROJECTION_CACHE.md),
frozen at `2887239575771c9ec3afe17d898a8d38135f68b6` before implementation.

Final characterized source: `74725372f82ad490467f20cf0a69e815650bae7b`.
GitHub Actions run `42471715382`: Python 3.11 PASS, Python 3.12 PASS.
Software only: **no World, no life, no study index, no runtime projection mode,
no reference adoption**. P1.3 `chunk_end` remains the reference.

Data: [characterization.json](characterization.json).

## Verdict

`SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_PASS`

The 255-step per-step projection can be factorized into exact channel-local
traces and reused inside one option batch without interpolation, rounding or a
body grid. The result is an exact-reuse result, **not yet an affordability
result**.

| Frozen rule | Result |
| --- | --- |
| pairwise decision bias <= 1e-3 | PASS; max **2.22e-15** |
| projection-equivalent gap <= 1e-3 | PASS; **1.33e-15** |
| final-body channel error <= 1e-10 | PASS; **0** |
| cache hit in 486-case projection grid | PASS; **972** hits |
| cache hit in nonlinear option set | PASS; **50** hits |
| actual raw trace reuse in both families | PASS |

## Accuracy

### Existing 486-case projection grid

- max option-value error: **2.220446049250313e-15**;
- max pairwise decision bias: **1.3322676295501878e-15**;
- projection-equivalent invariant max gap: **1.3322676295501878e-15**;
- max final-body channel error: **0.0**.

Worst option-value case: sleep-learned fixture, G0-6000,
body `[80, 80, 10, 80, 80]`, prefix. Candidate
`-2.7032413540432465` versus per-step `-2.7032413540432487`.

Worst pairwise case: sleep-learned fixture, G0-6004,
body `[80, 10, 80, 80, 80]`, prefix versus +3 waits,
absolute bias `1.3322676295501878e-15`.

### Nonlinear #1150 option set

- max option-value error: **1.7763568394002505e-15**;
- max pairwise decision bias: **2.220446049250313e-15**;
- max final-body channel error: **0.0**.

Worst option-value case: body `[80, 80, 10, 80, 80]`, +3 waits.
Candidate `-2.3944903089687717` versus per-step
`-2.39449030896877`.

Worst pairwise case on the same body: +3 waits versus drink,
absolute bias `2.220446049250313e-15`.

These errors are at floating-point rounding scale and are more than eleven
orders of magnitude below the frozen 1e-3 decision threshold.

## Raw reuse

The structural probe deliberately does not invent a new physical price for a
single channel-distress sample.

| Fixture family | project calls | trace builds | trace hits | channel samples | uncached full endpoints |
| --- | ---: | ---: | ---: | ---: | ---: |
| 486-case grid | 1458 | 6318 | **972** | 1,611,090 | 371,790 |
| nonlinear set | 60 | 250 | **50** | 63,750 | 15,300 |

Maximum live cache entries are 15 and 25 respectively.

For descriptive orientation only, dividing channel samples by five and rounding
up gives 322,218 and 12,750 full-endpoint equivalents. Those numbers are
**not a CognitiveWork bill** and must not be converted into energy or vigilance
claims.

The important observation is narrower: exact trace reuse exists. The candidate
does not merely re-express five fresh channel traces for every projection.

## Interpretation

The obstacle identified by #1149 can be split into two independent questions:

1. **Can consistent foresight be represented without approximation error?**
   This slice answers **yes** for a decision-local separable representation.
2. **Can that representation be paid by an individual under I3's physical
   cognition economy?** This remains unanswered.

This distinction matters. Candidate F showed that a correct projection can
destroy the individual when cognition is expensive. Calling the present cache
"affordable" before defining and paying its build/read/write work would repeat
the same methodological error in a quieter form.

## Next authorized slice

Freeze, before implementation, a physical accounting and capacity contract for
the cache. It must:

- price trace construction and cache storage/read work without retroactively
  choosing a convenient divisor;
- keep every charge inside existing energy/vigilance settlement;
- expose storage capacity and rebuild/invalidation cost;
- preserve exact per-step decisions;
- run the frozen #1146 Candidate-G 80-state kernel under real
  `CognitiveBudget`;
- compare the resulting physical work with reference, Candidate-F projection
  and per-step baselines.

If no defensible accounting makes the exact representation fundable, the
scientific result is that consistent foresight is unaffordable at current I3
physical prices. No approximation is authorized as a rescue.

No World or life panel is authorized by this result. Stage 2 remains blocked.
