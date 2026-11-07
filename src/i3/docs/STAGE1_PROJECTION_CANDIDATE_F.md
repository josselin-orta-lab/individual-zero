# Stage 1 projection Candidate F: end-to-end canonical local quadratic-4

Issue #1111. Baseline:
`f566bf5e378fa28a59e05f0380d7c94981502200`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE LABORATORY INTEGRATION ONLY.**

## Motivation

Candidate E established that the sparse local quadratic-4 projector is directly
accurate and cheap, but fails when ordinary-float explicit plan simulation feeds
the canonical Decimal bootstrap.

Candidate F changes only that integration boundary.

## Frozen semantics

Candidate F keeps Candidate E unchanged:

- same canonical event boundaries;
- same local blocks of at most 4 steps;
- same start/mid/end quadratic reconstruction;
- same paid reward evaluations;
- same direct projection cost.

The explicit simulated plan phase now uses one canonical Decimal body state:

- `Decimal.from_float` for initial body and learned action means;
- precision 100;
- same movement grouping;
- same horizon counter semantics;
- same one simulated-step CognitiveWork charge per explicit simulated block;
- same learned mean/uncertainty readout;
- same clamp and vital death predicate;
- same reward timing and gamma arithmetic.

If the plan survives, that exact Decimal body is handed directly to the
unchanged Candidate-E sparse bootstrap. There is no state round-trip through
float between the plan and projection.

Body conversion to float occurs only at the existing I3
`feats/distress/value` readouts.

## Frozen characterization

Use the same 486-case plan grid and #1117 oracle.

Record:

- max prefix-value error vs oracle;
- max decision bias vs oracle;
- projection-equivalent invariant max gap;
- unchanged E direct final-body error;
- unchanged E direct paid projection units;
- worst-case metadata.

## Frozen gate

Candidate F passes the software laboratory gate iff:

1. max decision bias <= **1e-3**;
2. projection-equivalent invariant max gap <= **1e-3**;
3. direct final-body error <= **1e-10**;
4. direct projection max cost < **255**.

Pass verdict:

`CANDIDATE_F_PASSES_LAB_SOFTWARE_GATE`.

Fail verdict:

`NO_CANDIDATE_PROMOTED`.

A pass does not alter `Mind.simulate` or reference cognition. It authorizes a
later, separate opt-in integration slice only.

Omega remains unauthorized until that opt-in runtime-equivalent integration has
its own parity/cost checks.

No World, life, selection, validation or reserve data are opened.
