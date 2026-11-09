# Stage 2.1: prospective DEVELOPMENT 80/81 (first exposure, completed)

**Verdict:** `DEVELOPMENT_COMPLETE_ENGINEERING_CONTINUATION_PASS`.
**Scientific status: descriptive DEVELOPMENT only; no confirmatory Stage-2.1
gate or survival non-inferiority verdict.** This panel was opened once,
after the explicit owner lift of ADR-0017, without reopening any Stage-1
or supplied 68/69 world.

## Exact-source and original custody

| Property | Frozen / executed value |
| --- | --- |
| Owner decision | [STATUS](../../STATUS.md), PR #1221, commit `e53e35a3` |
| Prospective [opening record](OPENING.md) | Before exposure, no retrospective arm/seed choice |
| Frozen [plan](PLAN.json) | SHA-256 `a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92` |
| Source checked out | `5d362e226f8e87df226dae5b239e26cc99072a13` |
| Transport fingerprint | `dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1` |
| One-shot GitHub Actions | [run 42641395586](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42641395586), Python 3.11, PASS |
| Pre-exposure claim | `custody/i3-stage2-1-development-80-81-claimed`, commit `3de2194328cede760c48c575a892447cadeec1fb` |
| Source-locked evidence | [branch](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-stage2-1-development-80-81-first-exposure), commit `5a13efc53dafc10e9b9248479a4756eda6a55eeb` |
| Phase G / Phase R | 36/36 generated; 36/36 reduced; 0 failures across 10 structural invariants |
| Sealed originals manifest SHA-256 | `c6893bb1b2457890e3d66680f10bf0c14b451e62c2e5c381951f1119f286b76e` |
| Canonical full result SHA-256 | `a6652f4d8cd1f8ccb87d8bf902ecb2eabf68ec0a548b187db140ea61dfc9401b` |

All 36 original `life-000..035.json.gz` files, immutable
[`MANIFEST.json`](evidence/MANIFEST.json) and
[`MANIFEST.sha256`](evidence/MANIFEST.sha256), source-locked
[`SOURCE_LOCK.json`](evidence/SOURCE_LOCK.json), and full
[`SCIENTIFIC_RESULT.json`](evidence/SCIENTIFIC_RESULT.json)
are archived. Each original was SHA-256 verified by the execution
workflow. No additional lives were run, and no generation retry occurred.

## Observed descriptive outcomes

The frozen panel consists of three ecologies (`stable`, `depletion`,
`pulse`), two previously unexposed development indices (80/81),
two birth genomes (911/912) and three arms (FIXED, GATE,
ZERO-PERCEIVED-COST), horizon 400. There are twelve same-world/genome
blocks, not twelve independent selected populations.

| Outcome | FIXED (P1.3) | GATE | ZERO-PERCEIVED-COST |
| --- | ---: | ---: | ---: |
| Lives | 12 | 12 | 12 |
| Replays per sleep step (pooled) | 15.997053 | 6.380623 | 12.623037 |
| Paid energy cognition per lived step (pooled) | 0.555897 | 0.469401 | 0.468159 |
| Paid vigilance cognition per lived step (pooled) | 0.674306 | 0.599448 | 0.599146 |
| Mean lifespan (steps) | 291.583 | 262.167 | 253.750 |
| Censored at 400-step horizon | 4 | 3 | 2 |
| Lives ending in death | 8 | 9 | 10 |
| Fraction of lived steps inactive | 0.224921 | 0.214876 | 0.303448 |
| Lives acquiring a drink | 9 | 8 | 8 |

The GATE arm executes **60.11% fewer replays per sleep step** and pays
**15.56% less cognitive energy and 11.10% less cognitive vigilance per
lived step** than FIXED in the pooled observed lives. This is real
*descriptive* replay-cost reduction, not a formal efficiency/survival
gate result: policy arms follow different trajectories, and the paid
per-lived-step denominators differ when individuals die earlier.

**Adverse survival signal is preserved.** Matched lifespan differences
(GATE minus FIXED) are positive in 3 blocks, negative in 3 blocks and
zero in 6. Mean difference is **-29.4167 steps** (median 0). A
`stable-81-g911` block reaches the 400-step censoring horizon under
FIXED but ends at 100 under both GATE and ZERO-PERCEIVED-COST:
a 300-step adverse difference. Other blocks show gains as large as
136 steps. With only twelve development blocks, **survival non-inferiority
has not been demonstrated**. The result also does not prove the gate
is causally responsible for that adverse case.

GATE has 6.38 replays/sleep compared with ZERO-PERCEIVED-COST's
12.62, but paid cognition per lived step is nearly equal between
those two arms. Different lived trajectories preclude a causal
statement about graded cost-awareness from these descriptive aggregates.
In the last recorded GATE sleep-gate state, the marginal cost estimator
was negative in 3/9 lives with a recorded gate, zero in 2/9, and
positive in 4/9. That is a **final-state diagnostic**, not the frequency
across all sleep steps or a license to change the frozen equation.
The software R3 pass also remained formally non-discriminating.

## Prospectively determined control parameter

The protocol predeclared that GATE's observed mean replay count per sleep
step in this development pilot sets the future RANDOM-EQUAL-MEAN arm.
The exact pooled value is

[
ar k_{mathrm{GATE}}=rac{5532 	ext{replays}}{867 	ext{sleep steps}}
=6.380622837370242.
]

This number is now fixed for prospective control design; see
[RANDOM_EQUAL_MEAN_PARAMETER.md](RANDOM_EQUAL_MEAN_PARAMETER.md).
Its sampling distribution, life-seeded stream, bounds, work settlement,
population sampling, statistical margins and held-out validation
indices must be frozen **before** any further World is exposed.
Do not use any validation or reserve World to tune this parameter.

## Interpretation and next authorized work

Engineering continuation: **PASS**, original archive and no-retry
requirements met. Mechanistic capacity: the earlier one-shot software
`REPLAY_GATE_CAPACITY_SHOWN` still stands. Lived efficiency is
promising on pooled cognitive spending but not a positive survival
or mechanism-value verdict.

**80/81 is now permanently closed; do not rerun it.** The owner's
previous narrow opening permission has been fully consumed. No
selection, validation, reserve or additional development World is
authorized by this result. Next is software-only design and prospective
preregistration of the RANDOM-EQUAL-MEAN control and ADR-0015 selected
multi-population Stage-2.1 gate, including ≥8 independent populations
and frozen primary non-inferiority margins. The next gate requires a
separate explicit authorization and, if its transport source changes,
new exact-source engineering custody. Never rescue the frozen
replay-gate formula or reinterpret this DEVELOPMENT result as a gate.
