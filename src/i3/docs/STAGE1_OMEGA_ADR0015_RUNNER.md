# Stage 1 omega: source-locked sharded ADR-0015 runner

Issue #1061. Runner baseline:
`3d9a0701d338af3a40f5bec77097acc4c8dc6f36` (#1130).

**RUNNER SOFTWARE ONLY. NO WORKFLOW OR EXECUTION AUTHORIZATION.**

This file implements the already-frozen G1-G6 design without changing its
allocation, ranking, margins or endpoints.

## Why sharding exists

The frozen gate requires 4,704 I3 executions. A single CI job is therefore a
poor custody unit.

Sharding is permitted only as an engineering partition. It may not change the
scientific population or allow successful jobs to become the analyzed sample.

Two hard barriers are implemented.

### Selection barrier

There are exactly:

`8 populations * 2 architecture arms = 16 selection shards`.

One shard contains:

`40 founders * 6 declared selection worlds = 240 complete lives`.

No architecture/population ranking exists until **all 16 COMPLETE shards** are
present with one execution source and one runtime source digest.

A missing/crashed shard blocks selection. No successful-subset reranking,
replacement founder, replacement seed or retry is permitted.

### Validation barrier

After the immutable selection aggregate exists, there are exactly:

`8 populations * 3 validation arms = 24 validation shards`.

Each shard contains:

- 5 selected genomes * 6 worlds = 30 main lives;
- one exact replay of the rank-0 selected genome on all six worlds.

No G1-G6 gate result exists until **all 24 COMPLETE shards** use the exact same
selection aggregate and source.

## Original custody

Every I3 life is run with:

- full trace;
- full Competition observer;
- Mind digest custody;
- depletion resource sidecar on validation depletion cases.

The canonical life JSON is gzip-compressed and written **before any reduction**.
The archive records both compressed and canonical JSON SHA-256 values.

A failure after some completed lives writes an
`ENGINEERING_FAILURE_NOT_A_DEATH` receipt and raises. Already archived
originals remain evidence of an incomplete engineering run but cannot enter
selection or validation.

## Paid-v2 verification

Every main life is verified through
`stage0_energy.energy_receipt` against the study protocol and exact runtime
source digest.

Validation depletion lives additionally pass through
`stage0_revision.revision_receipt`.

A main receipt records:

- terminal and lived steps;
- source/world/trace/evidence digests;
- full cognitive accounting;
- final body and action counts;
- paid energy/vigilance;
- inactivity;
- full Competition witness length;
- frontier counters where present.

The runner never converts a crashed or malformed receipt into a physical death.

## Exact replay

For every validation population/world/arm, the rank-0 selected genome is
executed a second time with the exact same genome, world and life seed.

Replay identity includes:

- trace head;
- evidence head;
- terminal state;
- lived steps;
- world digest;
- final body;
- action counts;
- the complete cognitive-accounting object.

Any mismatch is an engineering failure inside the shard. The final gate also
carries a replay custody floor.

## Source and allocation lock

Before importing runtime or constructing a world, the execution function
requires:

- exact expected Git HEAD;
- exact protocol-manifest digest;
- clean `src/i3` and `tests/i3`;
- P2 ecology Git blob
  `f7e277da48309aef698b327f328e1f786e313ae2`;
- P2 world-generator Git blob
  `7d6548662664afbab28627ea432977a9d658af79`.

Selection and validation metadata come only from the frozen Stage-0 design.

The reserve path is not available through this runner and P2 itself refuses to
open its reserve cohort.

## Genome binding

Selection reference and candidate arms use the same declared founder seeds and
current genome-v4 digest.

Validation genomes must belong to the immutable selected set.

The omega-zero arm uses only
`stage1_omega_adr0015_design.omega_zero_genome`: the exact candidate-selected
founder with all 30 common genes unchanged and omega set to zero before birth.

No omega-zero population is ranked.

## Descriptive systematic-search probe

ADR-0015 requires the systematic-search reference to remain visible.

The runner executes it exactly once per declared world, in the reference shard
only:

- 48 selection-world probe trajectories;
- 48 validation-world probe trajectories.

These **96 probe trajectories are not I3 lives and are not cost matched**.
Their output is labelled
`DESCRIPTIVE_SYSTEMATIC_SEARCH_NOT_COST_MATCHED` and never enters selection or
G1-G6.

Selection aggregation also reports every founder's persistence tuple and how
many G0 founders beat/tie/trail the systematic probe. This is descriptive
evolvability, not a gate.

## Published genome custody

The complete selection aggregate publishes, per population:

- all 40 founder seeds;
- genome digest;
- inherited omega;
- the five reference-selected genomes;
- the five candidate-selected genomes.

Thus the later G3 omega-selection calculation is auditable from immutable
selection evidence rather than reconstructed from validation outcomes.

## Aggregate commands

The runner exposes explicit commands for:

- one selection shard;
- selection aggregation;
- one validation shard;
- validation aggregation.

Aggregation commands do not execute a life. They require all expected shard
keys and reject duplicate, foreign or mixed-source shards.

The final validation aggregator calls the already-frozen #1130
`analyze_gate` unchanged and publishes:

- G1-G6 arithmetic;
- actual validation energy/vigilance and inactivity descriptively;
- systematic probe descriptors;
- PASS/FAIL of the **frozen F0 Stage-1 omega gate** only.

A PASS is not a general I3 GO.

## Execution envelope

Scientific I3 executions remain exactly the frozen #1130 envelope:

- 3,840 selection lives;
- 720 validation main lives;
- 144 exact validation replays;
- total **4,704 I3 executions**;
- maximum **1,881,600 physical life steps**.

Additionally, 96 non-I3 systematic-search probe trajectories are executed
descriptively on the same declared worlds.

No early stopping is permitted even if a gate appears mathematically won or
lost.

## What this PR does not do

This runner is not connected to a workflow.

It does not:

- open selection index 72;
- create any P2 world at import;
- execute a life in tests;
- authorize GitHub Actions;
- change G1-G6;
- change the genome;
- modify the candidate or reference;
- register I3;
- open validation or reserve worlds.

A separate execution PR must freeze the **merged runner source SHA** and the
protocol-manifest digest before the first selection-world construction.
