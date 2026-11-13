# I3 R2.4 read-only checkpoint inspection: exact-source software result

**Date:** 13 November 2026. **Result:** `R24_CHECKPOINT_SQL_READONLY_SOFTWARE_PASS`. **Independent M11:** `NOT_ATTESTED`, same-domain rollback counterexample still `FAIL_INDEPENDENT_M11`. **Scientific Stage 2.1:** `NOT_ISSUED / HOLD_NO_VERDICT`. No new scientific World, birth, index, source authority, model policy or engine release.

## Source provenance and unchanged evidence

- **Preflight frozen before code:** [R24 read-only inspection preflight](R24_READONLY_CHECKPOINT_INSPECTION_PREFLIGHT_2026-11-13.md), first commit `95c272470df585fb04f4f6306fa364abb36711e1`.
- [PR #1372](https://github.com/josselin-orta-lab/individual-zero/pull/1372), exact CI-tested head **`679958677f0d433064f436b4f5bfd705debcf857`**, squash merged to `main` as **`0b1827a79be377e62e2206917ebebbf77de20099`**.
- [Actions #43431825263](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43431825263) **SUCCESS** on that exact head: **1,336/1,336 I3 software tests** on Python 3.11 (job `131906948132`, 130.167 s) and **1,336/1,336** on Python 3.12 (job `131906947756`, 121.026 s), including four new no-World tests, previous checkpoint fault matrix, engine/ownership contract checks and navigation.
- This results document is written **after** the tested code merge, so its own Markdown bytes are not claimed to have been part of that CI head. No scientific launcher, source index or cohort was executed.

## Discrepancy that prompted the change

The prior [R2.4 checkpoint probe result](R24_EXACT_STATE_CHECKPOINT_RESULTS_2026-11-13.md) described its snapshot capture as read-only. Its implementation had called `AuthorityStore(...)` during inspection. That constructor enables WAL and takes a **`BEGIN IMMEDIATE` writer transaction** for v3 initialization/audit. The old snapshot routine didn't itself update CAS rows, but acquiring writer capacity was inconsistent with the strict observation-only intention and could unnecessarily block a live writer.

The new [AuthorityStore.open_existing_verified_readonly](../../lab/engineering_remote_authority.py) checks path and authority, opens the **existing** SQLite v3 store via URI `mode=ro`, sets `PRAGMA query_only=ON`, starts a deferred read transaction, runs the **same full `_check_audit`** and yields a transactionally coherent view of the audited head, all histories and accepted nonce contents. [capture_exact_checkpoint](../../lab/engineering_remote_checkpoint_probe.py) now consumes that verified view and never invokes `AuthorityStore.__init__`.

**Claim boundary:** the connection cannot issue SQL data writes or acquire the former writer transaction on this code path; SQLite in WAL mode can still require kernel reads/shared-memory files and filesystem access. This does **not** assert zero OS I/O, immutable backups, permission separation or protection against a privileged replacement of the database pathname between path validation and open. Future deployment must harden file descriptor/canonical path custody or avoid local authority access entirely.

## Fault matrix verified under Python 3.11 and 3.12

| Frozen case | Software observation | Scope |
| --- | --- | --- |
| Normal v3 COMMITTED checkpoint capture | PASS, exact prior payload and full audit | No schema/receipt change |
| Force `AuthorityStore.__init__` to raise | Capture and equality verification still PASS | Writer-capable initializer is **not called** |
| Attempt SQL UPDATE of authority and INSERT of request nonce inside verified context | Rejected by SQLite, `PRAGMA query_only=1` | No writable SQL connection supplied |
| Missing database or wrong authority | REJECT; no silently initialized replacement | Fail closed |
| `verify` accepted via independent writer during an open verified read | Previous snapshot stays coherent; new read sees exactly one extra nonce | Snapshot isolation under SQLite WAL |
| Existing corrupt audit, PREPARED state, stale pin/nonce tamper | REJECT, old no-World tests remain PASS | Full chain, terminal and nonce checks unchanged |
| Roll back authority v3 under a newer retained public checkpoint | REJECT | Only conditionally secure if that record survives |
| Roll back authority and matching public checkpoint together | ACCEPT negative control, **`FAIL_INDEPENDENT_M11`** | No independent monotonic evidence or protected signer |

This change does **not** improve observed 8/32/80-step CAS throughput or switch the writer to O(1). All authority writer behavior and v3 nonce persistence continue as before. The new read path does not provide a trust anchor for activation or a secure off-host signing protocol.

## Next meaningful gate

1. Source-lock an **independent** authority host/operator/storage threat model, supported by verifiable administrative and key-custody evidence, not just a remote URL or mutable hash pin.
2. Provide a server-owned or externally attested **signature** over each source-bound receipt and an independently preserved **monotonic high-water**. Authentication alone cannot prevent replay of an earlier valid signed receipt.
3. Run failure experiments with distinct privileges, controlled rollback of every local store and the authority (separately and jointly), partition, crash, stale writer, ambiguous paid motor and terminal life. Require STOP on unresolvable crashes, never silent motor replay.
4. Only then freeze and test checkpoint publication/compaction, bounded audit and nonce lifecycle with measured cost. Do not bypass full audit, prune accepted nonces or claim a performance gain from this read-only correction.

**Governance:** keep [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) OPEN. `reference_generation=I3`, `active_generation=I1`; `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE` and no entrypoints. P1.3 funded-v2 remains reference, Stage 2.1 software capacity does not imply science, canonical `NOT_ISSUED`, all new scientific World/cohort flags false.
