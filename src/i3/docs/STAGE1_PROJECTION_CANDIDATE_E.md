# Stage 1 projection Candidate E: canonical event + local quadratic-4

Issue #1111. Baseline:
`dc2438e907ba52aa163af81ddd6432e91c7b058d`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE ONLY.**

## Preconditions

Candidate E starts only after:

- #1117 authorized the end-to-end high-precision laboratory oracle for future
  candidates;
- #1118 showed that canonical event segmentation itself matches that oracle to
  numerical noise.

Therefore E changes only the density of distress evaluation inside already
validated event segments.

## Candidate mode

Opt-in projection accounting:

`event_local_quadratic4`.

The default remains `chunk_end`.

Candidate E uses the canonical numerical state semantics established by #1117
and #1118 inside the projection calculation:

- Decimal state, precision 100;
- `Decimal.from_float` for the existing represented body, drift,
  restoration and theta values;
- exact canonical event boundaries;
- unchanged outer geometric horizon `1,2,4,8,16,32,64,128`;
- unchanged vital, clamp and absorbing-death semantics.

This is an internal numerical representation only. It introduces no new body
or world law and no hidden information.

## Frozen local approximation

Inside each canonical event segment, split further into deterministic blocks of
at most **4 discrete steps**.

The block-start distress is already known from the previous paid endpoint. The
initial projection start is evaluated and paid once.

For each block:

### Length 1

Evaluate and pay the discrete endpoint. The block is exact.

### Length 2

Evaluate and pay:

- midpoint at t=1;
- endpoint at t=2.

Together with the inherited start, every discrete endpoint is directly
evaluated, so the block is exact.

### Length 3

Evaluate and pay:

- fixed midpoint at t=1.5;
- endpoint at t=3.

Fit the unique quadratic through start/mid/end and evaluate it at discrete
endpoints t=1,2,3.

### Length 4

Evaluate and pay:

- fixed midpoint at t=2;
- endpoint at t=4.

Fit the unique quadratic through start/mid/end and evaluate it at t=1,2,3,4.

The endpoint reward is reused as the start reward of the next block.

Thus no block reconstructs more than two unpaid discrete endpoints between
paid reward evaluations.

No adaptive error tolerance, extra node insertion, post-result subdivision,
or result-dependent block length is allowed.

## Accounting

Each distinct distress evaluation is billed as one simulated projection unit.

- initial start reward: 1 unit;
- one-step block: 1 new unit;
- block length 2, 3 or 4: 2 new units;
- no further reward evaluation is required after predicted death because
  maximal distress is absorbing.

Decimal arithmetic itself is not a new cognitive work category; I3 accounting
prices model-level projected reward evaluations, as in Candidate C/D.

## Frozen characterization

Use exactly the existing 486-case plan-comparison grid:

- 3 fixtures;
- midpoint + G0 seeds 6000..6004;
- 27 bodies;
- horizon 6;
- prefix / +1 wait / +3 waits.

Truth: the #1117 end-to-end high-precision oracle.

Also run direct candidate projections on all fixture/genome/body cases to
measure final-body error and paid candidate projection cost.

Record:

- max prefix-value error vs oracle;
- max decision bias vs oracle over +1/+3 waits;
- projection-equivalent invariant max gap;
- max direct final-body error vs oracle;
- direct candidate paid units min/mean/max;
- worst-case metadata.

## Frozen selection gate

Candidate E is promoted only as an **opt-in candidate** if all are true:

1. max decision bias vs #1117 oracle <= **1e-3**;
2. projection-equivalent invariant max gap <= **1e-3**;
3. max direct final-body error vs oracle <= **1e-10**;
4. maximum direct candidate projection cost is strictly less than **255**
   paid reward evaluations.

Pass verdict:

`CANDIDATE_E_PROMOTED_AS_OPT_IN`.

Fail verdict:

`NO_CANDIDATE_PROMOTED`.

If any criterion fails, E is rejected unchanged in this PR. The block size is
not tuned after exposure.

## After a pass

A pass does **not** adopt E into reference cognition.

The next slice must:

1. update/freeze Stage-1 forecast-ceiling accounting for E's dynamic paid
   projection cost;
2. rerun the already-frozen omega falsifier with E;
3. record that result without changing E.

Any reference adoption still requires a separately preregistered ADR-0015
architecture gate.

## Boundaries

This candidate does not:

- change the default `chunk_end`;
- alter genome or world/body laws;
- open World/life/selection/validation/reserve data;
- alter historical C/D results;
- rerun omega in this PR.
