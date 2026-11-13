# R2.4 / #1339: exact-state checkpoint custody probe, frozen before implementation

**Date:** 13 November 2026. **Type:** engineering-only read-only checkpoint verifier for authority v3; no motor, World, Mind, new life, scientific cohort or independent M11 attestation. Source baseline: [R2.4 cost report](R24_AUTHORITY_COST_PROBE_RESULTS_2026-11-13.md) and [full rollback counterexample](R24_DURABLE_REQUEST_NONCE_RESULTS_2026-11-13.md).

## Hypothesis and security boundary

The v3 test authority's full audit scan can verify local transitions, but its own rollbackable SQLite does **not** provide an independent checkpoint. This slice asks the narrow falsifiable question: *when a checkpoint record remains outside a mutated/replaced authority SQLite, can a fully audited v3 state be compared to it without accidentally accepting a stale, substituted or incomplete committed state?*

The proposed `i3-remote-cas-checkpoint-probe/v1` record binds: exact authority ID and v3 schema, audited last ordinal/hash (including empty genesis), all current history identities and states, and the full existing set of accepted request nonces with request hashes. Use canonical JSON/SHA-256 and explicit strict types. This is a public **integrity checksum**, not a signature, custody token, proof of timestamp or source of authority. A record in the same rollback domain can be forged or restored along with the DB.

**Scope restriction:** the validator accepts only an **exact, stable, COMMITTED v3 state**. A pending PREPARED phase is a fail-closed refusal. Any subsequently accepted CAS or verify (nonce write) makes the prior checkpoint stale; callers must stop and use a separately, legitimately published new snapshot. This deliberately supplies **no fast path**, no checkpoint-aware production CAS, no nonce pruning and no automatic retry. Always run the current full `AuthorityStore._check_audit` before trusting any state. The term *checkpoint* here is a research equality proof, **not** a deployable storage release.

## Frozen fault matrix

| Case | Expected | Interpretation |
| --- | --- | --- |
| Original valid single-claim COMMITTED state | CAPTURE + EXACT_MATCH | Source/history/nonce bytes bound as read-only snapshot |
| Audit transition tamper or forged local final head | REJECT | Full authority audit still mandatory |
| Delete/replace an accepted nonce row at unchanged cardinality | REJECT | Must bind **content**, not count alone |
| Old authority SQLite restored while a newer checkpoint is retained | REJECT | Conditional rollback detection **only when the new record survives** |
| New accepted `verify` nonce or new `commit` after capture | REJECT_STALE | Exact match cannot silently treat a stale pin as high-water |
| PREPARED unresolved pending action | REJECT | Never checkpoint ambiguous motor |
| Checkpoint type/shape/hash/source/authority altered | REJECT | No permissive fallback |
| All of DB **and** checkpoint restored to a prior matching pair | ACCEPT_NEGATIVE | **FAIL_INDEPENDENT_M11**, required counterexample |
| Actual independently administered off-host key/storage/host, high-water publication/recovery | NOT_RUN | No independent attestation or production release |

## Smallest implementation and acceptance

Implement isolated helper in `src/i3/lab/engineering_remote_checkpoint_probe.py` and **no-World** unit tests under `tests/i3/`. It may import the existing v3 `AuthorityStore` and canonical JSON helpers, but must not modify the server, engine registry, permit new Worlds, or shortcut the full audit/nonce checks. The SQLite read is transactionally consistent. Do not use a mutable file-backed checkpoint as an authority. An exact-state match is *diagnostic*; a transition to independent M11 needs a separate protected principal and a monotonic out-of-band receipt.

CI: source-exact Python 3.11/3.12 I3 software suite and static navigation. **PASS** means the test fixture discriminates these conditions, including deliberate all-domain rollback failure, **not** that checkpoint performance or rollback resistance is solved. No extrapolation to cognitive energy/vigilance or Stage-2 scientific success. `reference_generation=I3`, `active_generation=I1`, P1.3 funded-v2 and Stage 2.1 `NOT_ISSUED`, all scientific World/cohort gates remain unchanged.
