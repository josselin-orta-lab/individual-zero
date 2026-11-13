# I3 R2.6: required externally held high-water reconciliation, preflight

**Frozen 13 November 2026, before implementation.** A bounded **engineering-only, read-only** recovery-inspection probe on prior #1376 R2.5. **No** scientific World, living individual, native motor replay or actual M11 independent deployment. Reference is [R2.5 results](R25_ATOMIC_RECEIPT_PUBLICATION_RESULTS_2026-11-13.md) and issues [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339), [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

## Falsifiable question and boundary

The local publisher journal's `latest()` is self-consistent but **not** a separate authority. Under a newly required latest-receipt callback that is **assumed, not proven**, to be outside the local rollback domain, can the inspector reject older/foreign/incomplete states even if local SQLite history and its local signed journal are internally valid?

The proposed operation **must never authorize native action**, only return `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY` when a strict set of predicates holds: (1) a separately supplied callable returns exact bytes of a pinned signature-valid Ed25519 latest receipt; (2) the **existing** publisher SQLite, inspected with `mode=ro` and full signed chain audit, has *exactly those bytes* as its tip; (3) an **existing, fully audited** authority v3 checkpoint matches those signed bytes, with **all** locally attested birth sources pinned; and (4) the **target** first-person identity is in `COMMITTED / OPEN` with no pending motor, and its `sequence < horizon`. Inspect target inside the **same authority read transaction** as the audited checkpoint. No separate writer-capable constructor or signing key may be used for inspection.

A valid Ed25519 signature **does not** grant freshness without external high-water custody; the read callback can be forged or rolled back in the same trust domain. No global atomic snapshot across the publisher and authority DBs or host/network. A successful read inspection **is not** a cold recovery equivalence proof, birth, permission to continue, or permission to retry an ambiguous paid motor. The actual Mind, World, RNG, body E/V and native recovery integrity remain outside this probe.

## Planned minimal implementation

- Add `TestOnlyCheckpointPublisher.inspect_existing_latest(...)` for strict, read-only inspection of an existing publisher DB with explicit key/source/authority pins. Reuse its full-chain validator, but **never** invoke `__init__`, open a writer transaction or accept a signing callback; reject missing/foreign/replaced files.
- Extend `capture_exact_checkpoint(..., expected_open_identity_sha256=...)` optionally to require one existing target `COMMITTED, OPEN, no pending, sequence < horizon` from the **same audited read transaction**; unchanged default behavior for all prior callers.
- Add `i3.lab.engineering_remote_recovery_reconciliation.reconcile_required_witness(..., fetch_required_latest)`: the callback is **mandatory** and must return nonempty exact bytes; no exception, stale response, bad signature, wrong pin or absent witness may trigger fallback to local state. Check existing local publisher and v3 authority against witness bytes. The output is a diagnostic dict with explicit `motor_authority=False`.
- No network client or self-declared "independent" signer, no credential rotation, no deployed key, no engine registration or source/index permission.

## Precommitted adversarial fault matrix

| Test | Required outcome |
| --- | --- |
| Stable OPEN engineering life, independently supplied identical latest signed receipt | `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`, no mutation, no writer constructor |
| Witness missing / returns None, invalid type, raises timeout or connection error | **STOP / REJECT**, never fallback to local receipt |
| Witness signed receipt from other source/authority/key | **REJECT** |
| Publisher database absent, corrupted or replaced; future witness retained | **REJECT** without initializing a new publisher |
| Authority database behind retained witness | **REJECT** even if locally well formed |
| Authority ahead of latest signed receipt (e.g. extra accepted `verify`) | **REJECT**, no automatic reconciliation or motor replay |
| Publisher behind latest witness, even if old receipt valid and local SQLite matches old | **REJECT** |
| Pending `PREPARED`, terminal `DEAD` or `CENSORED`, wrong target identity | **REJECT** read-only |
| Claim source in an additional recorded identity differs from pinned source | **REJECT** |
| Concurrent authority update between snapshots | STOP on detected mismatch; cannot claim cross-DB atomicity |
| **Rollback both local DBs and witness callback to same old receipt** | **ACCEPT negative**, mandatory `FAIL_INDEPENDENT_M11` |
| Physical separate hosts, distinct admins, hardware key custody, nonrewindable external monotonic store, real crash/partition scenario | `NOT_RUN / NOT_ATTESTED` |

## Exact-source acceptance

Python 3.11 and 3.12 full I3 software CI, generation ownership/static navigation and all previous R2.4/R2.5 negatives must pass on the *same tested SHA*. Any failed injection/fixture must remain documented before repair. Distinguish **local software PASS** from **independently anchored M11 PASS**, retain #1339/#1331 OPEN. I3 remains reference-but-unregistered, I1 remains active; P1.3 funded-v2 and Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`; all new scientific World, cohort and source-index permissions stay false.
