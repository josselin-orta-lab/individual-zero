# Stage 1 engineering gate: Candidate-I probe-restore learning authority repair

**PROSPECTIVELY FROZEN SOFTWARE/ENGINEERING PROTOCOL. SYNTHETIC FIXTURES ONLY.
NO 62/63 REPLAY.**

## Trigger

The one-shot Candidate-I DEVELOPMENT 62/63 transport opened the frozen panel
once from execution SHA
`81f05a7fb79c9e1f264cab63a363dc181ff663b2`.

The full Python 3.11/3.12 software matrix passed before World exposure.
Eighteen lives completed. Execution then stopped while generating:

`depletion-62-g903:personal_shared_prior_candidate_i_v1`

with:

`RuntimeError: missing branch decision settlement start body`

at:

`runtime.life -> prepare_learning -> ReferenceBranchMemoryMind.prepare_learning`.

The originals and failure receipt are archived on:

`evidence/i3-stage1-candidate-i-62-63-81f05a7fb79c`

at evidence commit `1e975da3`.

62/63 are exposed and closed. This protocol must not reopen them or use their
partial trajectories as an acceptance set.

## Root engineering question

Candidate-I first-contact probing is detached. If Stage A is not usable, the
implementation restores pre-probe first-person state before returning
`PROBE_UNFUNDED` or running a real fallback decision.

Before the 62/63 stop, Candidate-I took its rollback snapshot **before**
neutralizing decision/learning authority. The snapshot therefore contained the
previous step's `last` action and other pending authority fields. Candidate-I
then cleared the branch settlement receipt. On an unfunded Stage-A path,
`_restore_probe_state()` could restore that old `last` without restoring a
matching settlement receipt.

The runtime correctly interpreted non-null `last` as permission to prepare
learning and the repaired branch-memory layer correctly failed closed because
the matching settlement receipt was absent.

The repair must separate:

1. reversible first-person/perception state needed to discard a detached probe;
2. decision/learning authority, which belongs only to the current real
   decision and may never be resurrected from a rollback snapshot.

## Frozen repair semantics

At the start of a Candidate-I first-contact decision, before taking any rollback
snapshot, clear all prior decision/learning authority:

- `last = None`;
- pending branch store = None;
- branch-decision settlement receipt = empty;
- pending opportunity presence = None;
- pending opportunity commit = None.

The rollback snapshot may retain only state that a detached probe is allowed to
mutate and later undo:

- map/history;
- token/external-token mapping;
- accumulators and intention;
- visible cells and internal position;
- temporary unknown/presence option maps;
- drift;
- main RNG and budget-order RNG;
- observer-only competition/first-forecast state.

The rollback snapshot must **not** own or restore:

- `last`;
- pending branch storage;
- branch-decision settlement body/work;
- pending opportunity presence;
- pending opportunity commit.

Restoring a detached probe therefore cannot revive learning authority from a
previous physical action.

## Frozen synthetic reproducer

No World or life is required.

Use a Candidate-I mind with a deliberately stale preexisting authority state:

- `last = ((80,80,40,80,80), ("attendre",), "attendre", None)`;
- a nonempty stale branch settlement receipt;
- nonempty synthetic pending branch/opportunity sentinels;
- ordinary perceptual state and deterministic RNG state.

Use body:

`(80.0, 80.0, 40.0, 80.0, 80.0)`

and a directly perceived unsupported water offer.

A test-only Stage-A stub must:

1. execute after the real Candidate-I base perception has happened;
2. mutate reversible probe state;
3. return an unfunded complete-matrix status with nested
   `NO_FUNDED_SCORE`.

The legacy ordering/snapshot behavior must be reproduced in a pure helper:
restoring the old snapshot revives the stale `last` after the settlement
receipt has been cleared, and the learning boundary rejects that mismatch.

The repaired production path must instead return `PROBE_UNFUNDED` with no
current learning authority.

These fixture values and the nested funding class are frozen after the first
implementation run.

## Rules

### U0 — custody

Before interpretation:

- Candidate-I runtime v2 remains PASS;
- branch-decision settlement B0-B9 remains PASS;
- the 62/63 durable failure receipt remains
  `ENGINEERING_FAILURE_NOT_A_DEATH`;
- exactly 18 completed lives are recorded before the stop;
- no J1-J7 verdict is inferred from 62/63;
- #1187 remains closed and unmerged.

### U1 — exact legacy authority resurrection reproduced

A pure software reproducer of the old ordering must show:

- stale `last` exists before the new decision;
- settlement authority is cleared;
- old rollback restores stale `last`;
- settlement remains absent;
- the learning boundary rejects the mismatched authority.

This is an engineering reproduction, not a replay of 62/63.

### U2 — rollback snapshot has no learning authority

The production Candidate-I rollback snapshot and restore operations must not
contain or write:

- `last`;
- pending branch storage;
- branch settlement body/work;
- pending opportunity presence/commit.

### U3 — authority is cleared before snapshot

At the instant the production rollback snapshot is taken, all five prior
authority fields named above must already be empty.

A stale prior action supplied by a test fixture may not appear in the snapshot.

### U4 — PROBE_UNFUNDED restores perception only

For both unfunded first-contact exits:

- recurrence-read failure;
- common-matrix funding failure;

the returned public route is `PROBE_UNFUNDED`, and after restoration:

- `last is None`;
- branch settlement is empty;
- pending branch/opportunity authorities are empty;
- reversible map/history/token/RNG state equals the pre-decision rollback
  baseline except for the physically paid cognition receipt itself;
- no learning call is authorized by the state.

### U5 — FALLBACK creates fresh authority after restore

On `P1.3_BASE_FINAL`:

- rollback happens before the real final decision;
- exactly one real final perception is retained;
- any resulting non-null `last` comes from that final decision only;
- its branch settlement receipt belongs to the same current decision;
- Stage-A + Stage-B work/body accounting remains exact;
- addend-free fallback semantics remain unchanged.

### U6 — RELEVANT creates fresh current-decision authority

On `INFORMATION_FINAL`:

- any non-null `last` and settlement receipt are produced by the current
  finalizer;
- no stale prior `last` survives;
- V2-R1/R2 relevance and Competition/ActionControl semantics are unchanged.

### U7 — post-contact Candidate-H parity

The existing Candidate-I early post-contact route remains exact Candidate-H
#1163 semantics. It must not be altered merely to fix first-contact rollback.

### U8 — no physics, cost or scientific-rule change

The repair may not change:

- BodyLaws;
- cognitive prices;
- omega/RMS prior;
- V2-R1/R2;
- fallback addend policy;
- post-contact relevance;
- J1-J7 definitions;
- branch settlement B0-B9 semantics.

### U9 — authority boundary

The repair gate is software-only:

- no World construction;
- no `runtime.life`;
- no P2 ecology generation;
- no 62/63 evidence branch as an acceptance fixture.

The archived 62/63 `failure.json`, `TRANSPORT.json` and source receipt are
custody evidence only and are not inputs to the repair test.

## Frozen verdict

If U0-U9 pass:

`CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS`

Otherwise:

`CANDIDATE_I_PROBE_AUTHORITY_REPAIR_DEFECT`

A PASS repairs an engineering rollback-authority defect only. It does not
retroactively complete 62/63, produce J1-J7, authorize a retry, or advance
Stage 2.

## Handoff after PASS

62/63 stay permanently closed.

Any later lived comparison must use new conditions, new prospectively frozen
allocation and the same already-frozen scientific questions unless a scientific
reason for changing them is prospectively documented before exposure.

P1.3 remains reference. I3 remains unregistered. Selection, validation,
reserve and Stage 2 remain blocked.
