# Stage 1 projection: high-precision state oracle

Issue #1111. Baseline:
`eb044035e9e026913164f90bc5dea5b43ee043cc`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE DIAGNOSTIC ONLY.**

## Motivation

#1114 showed that removing interpolation does not make Candidate-C/D event
segmentation identical to the historical repeated-unit per-step diagnostic.

#1115 localized the largest discrepancy: repeated IEEE-754 addition leaves food
at approximately `2.05e-15` instead of exact zero at step 50, delaying death
to step 51. The resulting extra step accounts exactly for the observed
water/integrity state difference.

Historical Candidate C and D remain frozen against their original per-step
truth. They are not rescored.

Before any Candidate E, future projection work needs a numerical oracle whose
boundary semantics do not depend on accumulated state-rounding path.

## Frozen oracle

The oracle retains the **same represented I3 model**.

For body, theta, learned drift and learned restoration:

1. convert each existing Python float using `Decimal.from_float`;
2. use decimal context precision **100 digits**;
3. execute exactly 255 one-step projection transitions;
4. apply the same order:
   - passive F/W/I drift;
   - learned sleep restoration when needed;
   - clamp each body channel to [0,100];
   - death when F/W/I <= 0;
5. once dead, body state is frozen and maximal distress is absorbing.

There is no epsilon around zero and no replacement of learned coefficients by
human-friendly decimal constants. For example, the binary float represented by
`-0.2` is preserved exactly by `Decimal.from_float(-0.2)`.

At each resulting discrete endpoint, convert the body back to ordinary float
and evaluate the **existing** I3 `feats` and `distress` functions. Gamma
discount accumulation remains the existing float calculation. The diagnostic
therefore changes state arithmetic only.

A direct oracle projection is billed as exactly 255 simulated projection units,
matching the historical per-step diagnostic.

The oracle is laboratory-only. It is not added to
`PROJECTION_ACCOUNTING` and cannot be selected by runtime cognition.

## Frozen characterization

Use the existing 486-case projection grid:

- 3 fixtures;
- midpoint + G0 seeds 6000..6004;
- 27 bodies;
- horizon 6;
- prefix / +1 wait / +3 waits.

Compare:

1. event-exact (#1114) versus high-precision oracle;
2. historical repeated-float per-step versus high-precision oracle.

Record for both comparisons:

- max prefix-value error;
- max +1/+3 decision bias;
- projection-equivalent invariant gap;
- max final projected-body channel error.

Also retain worst-case metadata.

## Prospective interpretation

Numerical-equivalence tolerance: **1e-10** for decision bias, invariant gap and
final body.

If event-exact is within tolerance on all three quantities while historical
per-step differs materially, classify:

`EVENT_EXACT_MATCHES_HIGH_PRECISION_ORACLE`.

That classification authorizes the high-precision state oracle as the
comparison truth for **future projection candidates frozen after this result**.
It does not promote event-exact to live cognition and does not modify historical
C/D gates.

If event-exact exceeds tolerance, classify:

`EVENT_SEGMENTATION_DIFFERS_FROM_HIGH_PRECISION_ORACLE`.

Then no new projection candidate should be frozen until the remaining
state-transition discrepancy is understood.

If both comparisons are numerically identical, classify
`NO_NUMERICAL_SEMANTICS_DIFFERENCE_ON_FROZEN_GRID`.

## Boundaries

This diagnostic does not:

- change `chunk_end`;
- alter body/world laws;
- add a tolerance-to-zero death rule;
- modify Candidate C/D;
- add Candidate E;
- change omega or genome;
- rerun omega;
- open World, life, selection, validation or reserve data.

Only a later projection candidate that independently passes the existing
prospective bias gate (<=1e-3) against the newly frozen oracle may proceed to a
newly authorized omega falsifier rerun.
