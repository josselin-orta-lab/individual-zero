# I3 R2.4 exact-state checkpoint probe: source-locked results and negative trust boundary

**Date:** 13 November 2026. **Technical outcome:** `R24_EXACT_STATE_CHECKPOINT_PROBE_SOFTWARE_PASS` (read-only, local equality checks under a separately *retained* public record). **Independent M11:** `NOT_ATTESTED`, deliberate **`FAIL_INDEPENDENT_M11`** for a coordinated authority/checkpoint rollback. **Science:** Stage 2.1 `NOT_ISSUED`, general `HOLD_NO_VERDICT`. No new World, scientific life, source/indices, P1.3 change or engine activation.

## Source and executed controls

- Frozen **before any code**: [exact-state checkpoint preflight](R24_EXACT_STATE_CHECKPOINT_PREFLIGHT_2026-11-13.md) committed at `6564c2bacd631c38a97601dc14c9b8ae28ed60f5`, after the earlier [R2.4 CAS cost profile](R24_AUTHORITY_COST_PROBE_RESULTS_2026-11-13.md).
- [PR #1370](https://github.com/josselin-orta-lab/individual-zero/pull/1370), exact **CI-tested code head** `dd6071e74d16428a0955b56f9c24019154aa0257`, merged to `main` as `1edaee0cdb4e8cb98d88beb67a88e142d62304f9`.
- [Actions #43426105969](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43426105969) **SUCCESS**, source-exact:
  - Python 3.11, job `131887907087`: **1,332/1,332** I3 software tests PASS in 178.177 s.
  - Python 3.12, job `131887906577`: **1,332/1,332** I3 software tests PASS in 199.441 s.
  - Nine new no-World checkpoint fault tests PASS in both jobs. Immutable generation and navigation checks PASS.
- A first CI [#43425671982](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43425671982) **FAILED 1/1,332** in Python 3.11 because the test fixture attempted to modify the **wrong nonce** (`"1"*32` instead of the actually stored `f"{1:032x}"`). This silently changed zero SQLite rows, so the test correctly failed. [Correction commit](https://github.com/josselin-orta-lab/individual-zero/commit/dd6071e74d16428a0955b56f9c24019154aa0257) fixes the nonce and asserts `mutated.rowcount == 1`. Both exact-source reruns then passed. The failed first CI is kept as evidence of the fixture correction, **not** a scientific adverse outcome.

## Minimal result matrix

| Frozen adversarial case | Exact-source software observation | Narrow interpretation |
| --- | --- | --- |
| V3 COMMITTED state, full audit and accepted-nonce rows | CAPTURE / EXACT_MATCH | Public checkpoint matches this one stable local snapshot |
| Cold restart with unchanged v3 SQLite and externally retained same record | EXACT_MATCH | Restart continuity **conditional on the record remaining unchanged** |
| PREPARED or unresolved pending motor | REJECTED | No ambiguous action may be checkpointed |
| Additional accepted `verify` nonce or later `commit` after capture | REJECTED as stale | This is an **exact-equality** check, not a monotonic forward-certification API |
| Accepted-nonce **substitution with equal row count** | REJECTED after verified one-row fault injection | Snapshot binds nonce content/hash, not merely cardinality |
| Audit-chain tamper | REJECTED | Existing full authority audit remains mandatory |
| Wrong authority, malformed or recomputed untrusted checkpoint fields | REJECTED for mismatch/shape | Public checksum cannot authorize a different principal |
| Older coherent v3 SQLite restored; **newer checkpoint kept aside** | REJECTED | Detects this rollback **only because** a newer record survived elsewhere |
| Older coherent SQLite **and matching old checkpoint** both restored | **ACCEPTED negative control** | **`FAIL_INDEPENDENT_M11`**. Same-domain integrity is not independent monotonic custody |

The module [engineering_remote_checkpoint_probe.py](../../lab/engineering_remote_checkpoint_probe.py) uses the original v3 `AuthorityStore` full audit, a SQLite read transaction, canonical digests of all history rows and all accepted nonce identities/request hashes. [No-World tests](../../../../tests/i3/test_engineering_remote_checkpoint_probe.py) inject faults and test the exact-match behavior. The checkpoint's SHA-256 is an **unkeyed public checksum**; it supplies no trusted time, independent operator identity, external signature, backup policy or source of truth. It can be recomputed by an adversary who controls the pin. The helper has **no server wire change, no checkpoint-aware CAS fast path, no replay recovery, no journal pruning, and no reduction of the O(n) complete validation cost**.

## Resulting engineering decision

1. **Retain v3 full audit/nonce checks**: no O(1)-per-step CAS or partial-history bypass is justified merely because this test passes.
2. **Require an independently protected monotonic source and credential custody** before accepting any checkpoint as an off-host release trust boundary. The distinct host/administrative principal, protected storage, non-rewindable high-water, credential rotation/revocation, source/writer admission and independent disaster-recovery attestation remain `NOT_RUN/NOT_ATTESTED`.
3. Before optimizing, freeze a separate versioned model of (a) what an authenticated checkpoint signs/publishes, (b) how it binds birth/source/terminal/pending state and prior accepted nonces, (c) how crash and incomplete checkpoint publication force STOP, (d) how full chain and random tamper verification continue off the hot path, and (e) how an entire host/storage rollback is rejected.
4. [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remain **OPEN**. No engineering release R5 and no scientific promotion.

**Governance unchanged on merged `main`:** I3 remains the *reference generation* while I1 is active; `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, `entrypoints={}`; P1.3 funded-v2, Stage 2.1 technical `REPLAY_GATE_CAPACITY_SHOWN`, scientific `NOT_ISSUED` and general `HOLD_NO_VERDICT`. `fresh_lived_worlds_allowed=false`, `scientific_gate_authorized=false`, `next_scientific_cohort_authorized=false`. No original studies or prospective authorizations were changed.
