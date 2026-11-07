# Candidate F omega falsifier: first rerun invalidated by proxy dispatch defect

**INVALID_MEASUREMENT. NOT EVIDENCE FOR OR AGAINST OMEGA CAPACITY.**

Protocol: [STAGE1_OMEGA_CANDIDATE_F_RERUN.md](../../STAGE1_OMEGA_CANDIDATE_F_RERUN.md).

Exact audited head: `8b6d82e42aad891d52968103dcac8c4844386560`.

CI run: `42401111208`.

## Frozen falsifier output

The unchanged 80-state, six-arm falsifier completed mechanically:

- all 80 states evaluated in every omega arm;
- no unfunded state;
- common forecast ceilings identical across omega state-by-state;
- every actual work vector remained within its ceiling;
- R2 monotone direction passed;
- R3 capacity failed;
- all six omega arms returned numerically identical behavioral summaries.

The raw formal verdict was:

`NO_CAPACITY_THROUGH_CANDIDATE_F`.

That verdict is **invalidated** by the post-hoc dispatch audit below and must not
be used as scientific evidence.

## Dispatch audit

One exact drink plan was evaluated with explicit observed effects:

- positive: `[0,0,+10,0,0]`;
- negative: `[0,0,-10,0,0]`.

Reference simulation preserves the observed-effect proxy:

| arm | value | first forecast |
| --- | ---: | --- |
| reference +10 water | -0.546148051392444 | +10 water, uncertainty 0 |
| reference -10 water | -1.1385339205756377 | -10 water, uncertainty 0 |

Reference value separation: **0.5923858691831937**.

Candidate F before repair collapses both branches:

| arm | value | first forecast |
| --- | ---: | --- |
| Candidate F +10 water | -0.5926656806694962 | none |
| Candidate F -10 water | -0.5926656806694962 | none |

Candidate-F value separation: **0.0**.

Classification:

`OBSERVED_EFFECT_VIEW_BYPASSED_BY_CANDIDATE_F_DISPATCH`.

## Mechanism

`paid_simulate_after_observed_effect` intentionally calls
`Mind.simulate.__func__(ObservedEffectView,...)` so the proxy's
`_read_plan_prediction` override remains visible.

The reference path reads that method directly.

Candidate F dispatch calls `self._simulate_candidate_f(...)`. Before repair,
`ObservedEffectView` did not define that helper, so `__getattr__` returned the
owner Mind's already-bound helper. Helper `self` therefore became the owner
Mind rather than the proxy, bypassing the exact observed effect before the
Candidate-F sparse projection began.

This explains the otherwise suspicious equality of all six omega arms.

## Decision

- invalidate the first Candidate-F omega rerun;
- do not claim `NO_CAPACITY_THROUGH_CANDIDATE_F`;
- preserve the run as defect evidence;
- repair only proxy-preserving Candidate-F helper dispatch in a separate PR;
- after that repair passes its integration suite, rerun the **same frozen**
  omega protocol without changing grid, omega arms, kernel, R2 or R3;
- no World/life exposure and no reference adoption.

The defect does not invalidate Candidate F's #1120 numerical gate or #1122
forecast-ceiling proof. It invalidates the use of Candidate F through the
observed-effect proxy required by this Stage-1 information kernel.
