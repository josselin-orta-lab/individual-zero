# Stage 1 omega ADR-0015: execution registration

Issue #1061.

**PROSPECTIVE EXECUTION REGISTRATION.**

This file is committed before the first construction of P2 selection world 72.

## Frozen implementation base

Merged source baseline before the execution-only PR:

`034349844ced2f3d6ba00efe7a0fdc42e74fbbaa`.

The execution PR may change only:

1. `tests/i3/test_stage1_omega_adr0015_execution_registration.py`;
2. this protocol document;
3. `.github/workflows/i3-stage1-omega-adr0015-execute.yml`.

No `src/i3/**/*.py` change is permitted.

The workflow records its exact pull-request head SHA as the execution source and
passes that SHA to every shard launch guard.

## Frozen digests

Stage-1 omega gate design SHA-256:

`e4934b4994bc97043deee9b9760df9fe31481aeb8ed4d0a75715eebc5f5e5d48`.

Runner protocol SHA-256:

`125d708706bce266abb41446ef577dbe0096ba96d0e7be60169165e327d11944`.

The execution-registration unit test independently requires both exact values
before any workflow shard is allowed to run.

## Scientific allocation

No allocation is changed from #1130/#1131.

### Selection

- populations: 8;
- candidate genomes/population: 40;
- selected/architecture/population: 5;
- arms: P1.3 reference and `genomic_omega_frontier_information_v1`;
- P2 cohort: `selection`;
- indices 72..119;
- world seeds 10072..10119;
- stable/depletion/pulse, two worlds each per population;
- horizon 400.

There are 16 selection shards, each exactly 240 I3 lives.

All 16 must complete before any ranking.

### Validation

- P2 cohort: `validation`;
- indices 120..167;
- world seeds 30120..30167;
- same F0 family/repeat structure;
- arms: selected reference, selected candidate, same candidate genomes with
  omega forced to zero;
- 24 validation shards;
- each shard: 30 main lives plus six exact rank-0 replays.

Validation cannot begin before the complete immutable selection aggregate is
created from all 16 selection shards.

All 24 validation shards must complete before G1-G6 arithmetic.

P4 reserve `1200000..1200199` remains sealed.

## Gate

The scientific gate is exactly #1130 with pre-exposure A1:

- G1 family survival non-inferiority, deficit <=2/80 per family;
- G2 complete R-depletion-v1 revision-rank superiority;
- G3 persistence selection shifts omega upward;
- G4 actual omega beats equal-common-gene omega-zero ablation;
- G5 omega benefit appears in at least two F0 families;
- G6 all custody floors.

All six must pass.

A zero-lived-step physical death is retained as a real selection outcome.
Crashes/missing receipts are engineering failures.

No gate threshold may be changed after exposure.

## One-shot launch

The workflow is allowed to run scientific shards only when all of these are
true:

- event is the initial pull-request `opened` event;
- workflow run attempt is 1;
- head repository is this repository;
- head branch is
  `i3/stage1-omega-adr0015-execute-20261107`;
- base SHA is exactly
  `034349844ced2f3d6ba00efe7a0fdc42e74fbbaa`;
- the execution PR changed exactly the three registered paths above;
- Python 3.11 and 3.12 full I3 software suites pass on the exact head;
- the registration test confirms both frozen digests;
- the runner launch guard confirms exact HEAD, clean I3 source/tests and pinned
  P2 source blobs.

A synchronize event or workflow rerun cannot launch scientific shards.

A software/preflight failure before the selection matrix opens no study world.

## Durable prerelease custody

After software/preflight succeeds but before selection world 72 is created, the
workflow creates one GitHub **prerelease** targeted at the exact execution SHA.

Tag:

`i3-stage1-omega-adr0015-<first-12-hex-of-execution-sha>`.

The prerelease receives:

- protocol manifest;
- all completed deterministic selection shard ZIPs;
- selection aggregate JSON, if selection completes;
- all completed deterministic validation shard ZIPs, if validation starts;
- final validation aggregate JSON, if complete;
- final campaign-status/asset index.

Every shard bundle is also retained as an Actions artifact.

The release is never deleted because a later shard fails. An incomplete
campaign is labelled engineering failure and preserves all completed assets.

## Failure semantics

No retry, seed replacement, candidate replacement, reranking of successful
subsets, validation on incomplete selection, early stopping or horizon extension
is permitted.

A failed selection shard prevents selection aggregation and all validation.

A failed validation shard prevents final G1-G6 arithmetic.

Already completed mortal lives remain historical evidence. They are not rerun.

## Compute envelope

I3:

- 3,840 selection lives;
- 720 validation main lives;
- 144 exact validation replays;
- total 4,704 I3 executions;
- max 1,881,600 physical life steps.

Descriptive systematic-search probes:

- 48 selection;
- 48 validation;
- 96 total;
- explicitly non-I3 and not cost matched.

## Interpretation ceiling

Even a frozen-gate PASS would support only the F0 Stage-1 omega claim defined by
#1130.

It would not by itself authorize:

- general I3 GO;
- registration/activation;
- Stage 2;
- F1-F5 generalization;
- food-information completeness;
- evolved-lineage claims;
- stable acquired individuality.

The current reference remains P1.3 until a separate owner promotion decision.
