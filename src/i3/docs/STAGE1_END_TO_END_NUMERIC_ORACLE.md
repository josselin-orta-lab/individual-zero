# Stage 1 projection: end-to-end high-precision numerical oracle

Issue #1111. Baseline:
`0a3ffe082395a2128e731e83f19a2e3af667c8f6`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE DIAGNOSTIC ONLY.**

## Motivation

#1115 showed that the historical repeated-float per-step diagnostic can delay an
exact vital-zero boundary by one discrete step through accumulated IEEE-754
rounding.

#1116 then showed that changing state arithmetic inside `project()` alone is
not coherent: explicit simulated plan transitions remain ordinary float while
the bootstrap becomes high precision, breaking the projection-equivalent
invariant.

Before Candidate E, any prospective numerical truth must therefore use one
continuous state arithmetic across the full simulated chain.

## Frozen end-to-end semantics

Use Decimal state arithmetic at context precision **100 digits**.

All existing model values are preserved exactly as represented by Python float
using `Decimal.from_float`:

- initial body;
- learned action-effect means;
- passive drift;
- learned restoration;
- theta thresholds.

Do not replace represented floats by ideal human decimal constants.

The body remains Decimal continuously from the first explicit plan transition
through the 255-step bootstrap projection. It is never converted to float and
back between those phases.

The explicit plan phase preserves the current `Mind.simulate` algorithm:

- same plan iteration;
- same grouping of consecutive movement keys;
- same horizon counter semantics;
- same one `CognitiveWork(simulated_steps=1)` charge per simulated plan
  transition block;
- same learned mean and uncertainty readout;
- same clipping and `F/W/I <= 0` death rule;
- same reward timing;
- same gamma discount arithmetic.

At each existing feature/reward readout only, the Decimal body is converted to
float and the unchanged I3 `feats`, `distress`, and value-feature functions
are used.

If the explicit plan survives, the same Decimal body is passed directly into a
255-step Decimal bootstrap:

- same passive drift/restoration order;
- same clamp and death rule;
- same absorbing death reward;
- same float distress and gamma arithmetic;
- exactly 255 simulated projection units prepaid.

The diagnostic does not alter ordinary cognitive-cost rates. It changes only
laboratory state arithmetic.

## Frozen grid

Use exactly the existing projection-consistency grid:

- 3 fixtures:
  - sleep learned;
  - sleep unlearned;
  - projection-equivalent;
- midpoint + G0 seeds 6000..6004;
- 27 bodies;
- horizon 6;
- plans:
  - prefix;
  - prefix +1 wait;
  - prefix +3 waits.

Total: **486 cases**.

## Frozen gate

Numerical tolerance: **1e-10**.

Authorize this laboratory oracle for future newly frozen projection candidates
only if all are true:

1. its projection-equivalent invariant max gap <= 1e-10;
2. the exposed #1115 direct midpoint/sleep-learned body
   `[80,10,80,80,80]` reaches the high-precision vital boundary at food zero
   with terminal water/integrity `60/90` within 1e-10;
3. every direct bootstrap costs exactly 255 simulated projection units;
4. neither `end_to_end_high_precision` nor any equivalent name is added to
   runtime `PROJECTION_ACCOUNTING`.

If all pass, classification:

`END_TO_END_HIGH_PRECISION_ORACLE_AUTHORIZED_FOR_FUTURE_CANDIDATES`.

Otherwise:

`END_TO_END_HIGH_PRECISION_ORACLE_REJECTED`.

Authorization means comparison truth only for candidates whose protocols are
frozen **after** this result. It does not alter P1.3, Candidate C/D, historical
results, world/body physics, or scientific selection.

## Descriptive comparisons

On the same grid report:

- historical repeated-float per-step decision bias versus the end-to-end oracle;
- existing event-exact decision bias versus the end-to-end oracle;
- max prefix-value differences;
- final direct-bootstrap body differences.

These descriptive comparisons do not form the authorization gate and do not
rescore historical Candidate C/D.

## Boundaries

This slice does not:

- change `Mind.simulate` or `Mind.project`;
- add a runtime projection accounting mode;
- change genome or omega;
- run Candidate E;
- rerun the omega falsifier;
- access World, life, selection, validation or reserve data.

Only after this oracle passes may a new Candidate E be prospectively frozen.
Candidate E must still independently pass the existing <=1e-3 bias gate before
any omega rerun can be authorized.
