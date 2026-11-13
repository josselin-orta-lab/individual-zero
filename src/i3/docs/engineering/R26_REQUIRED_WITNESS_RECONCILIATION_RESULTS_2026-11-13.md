# I3 R2.6: required signed-witness reconciliation, exact-source software results

**Date:** 13 November 2026. **Technical outcome:** `R26_REQUIRED_WITNESS_READ_ONLY_SOFTWARE_PASS`. **Actual independent M11:** `NOT_ATTESTED` with an explicit all-domain-rollback `FAIL_INDEPENDENT_M11`. **Science:** Stage 2.1 `NOT_ISSUED`, general `HOLD_NO_VERDICT`; 0 World, 0 new life, 0 new scientific source/index or cohort permission.

## Source lineage and executed CI

- [Precommitted R2.6 falsifier matrix](R26_REQUIRED_WITNESS_RECONCILIATION_PREFLIGHT_2026-11-13.md), first committed **before code** at `bd3f5c2cae23733a9975dc23aaa67b73b25dcfa9`, against the [R2.5 publisher baseline](R25_ATOMIC_RECEIPT_PUBLICATION_RESULTS_2026-11-13.md).
- [PR #1378](https://github.com/josselin-orta-lab/individual-zero/pull/1378), exact CI-tested head `9afbf1ea071b36391d8ca3fdb583e7087e3e2220`, squash merged in `main` as `63b2a267169a004d87e468edfab44059c30d2c31`.
- [GitHub Actions #43444367396](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43444367396) **SUCCESS** at that exact head: **1,368 / 1,368 I3 software tests PASS on Python 3.11** (job `131949836438`, 163.525-second test step) and **1,368 / 1,368 PASS on Python 3.12** (job `131949836772`, 178.912-second test step). Eleven new no-World reconciliation tests PASS under both, including the all-domain rollback control; engine/generation and navigation checks PASS.
- This report was written **after** the code SHA was tested and merged. Its Markdown is not falsely described as part of the exact-source executed code suite.

## Narrow mechanism and what it cannot mean

1. [Publisher v1 reader](../../lab/engineering_remote_checkpoint_publisher.py): `TestOnlyCheckpointPublisher.inspect_existing_latest` revalidates an **existing** local publisher SQLite through `mode=ro`, without running the writer constructor or supplying a signer/private key. Every receipt in its journal retains canonical Ed25519 signature, pinned authority/source/key and contiguous monotonic linkage checks. A missing/foreign journal fails closed, not auto-initialized.
2. [Authority read snapshot](../../lab/engineering_remote_checkpoint_probe.py): optional `expected_open_identity_sha256` requires a specific target claim to be `COMMITTED/OPEN`, no `pending_seq` or `pending_intent`, and `sequence < horizon` in the **same full-audit SQLite read transaction** that calculates the full checkpoint and verifies all configured source claims. Without the option, the original checkpoint capture contract is unchanged.
3. [Required witness inspector](../../lab/engineering_remote_recovery_reconciliation.py): `reconcile_required_witness` accepts a **required injected `fetch_required_latest` callable** that must return nonempty exact bytes of a canonical, valid pinned Ed25519 signed receipt. It then compares the **whole bytes** to the audited local publisher tip, and the signed checkpoint to the fully audited authority checkpoint with its exact open target identity. No automatic local fallback, publication, native motor, current World/Mind/RNG/body reconstruction, or source/engine authorization.
4. A match returns `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY` with explicit `motor_authority=false`, `scientific_world_authorized=false`, `independent_m11_attested=false`. **This is only a point-in-time diagnostic, not a cold-recovery license.** The two local databases cannot be read atomically as one distributed transaction; their privileged operator could swap one after the check. The callback does **not** itself prove that its contents came from an independent trust domain.

## Executed R2.6 adversarial matrix (both interpreters)

| Frozen fault | Observed software result | Scope/interpretation |
| --- | --- | --- |
| Stable OPEN synthetic engineering identity, signed latest equals full audited publisher/authority state | `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY` | Diagnostic match only; no motor authorization |
| Writer constructors forbidden by test injection; World construction forbidden | PASS | Inspection does not create a publisher, CAS writer or World |
| Required witness callback absent, returns empty/nonbytes, or raises simulated timeout | REJECT | Missing external high-water never silently falls back to local receipt |
| Wrong trusted public key, source, authority or issuer ID | REJECT | Explicit trust pins are required |
| Publisher receipt digest corrupted, or publisher database deleted | REJECT | No self-healing initialization of untrusted state |
| Authority SQLite rolled back, but newer publisher and witness retained | REJECT | Conditional rollback detection under surviving newer references |
| Publisher SQLite rolled back, but later witness retained | REJECT | Local signed receipt is insufficient if it lags the expected latest |
| Authority receives a later accepted `verify` not yet signed/published | REJECT | Local state ahead of witness is not silently resumed |
| Old signed witness tip replayed while publisher is newer | REJECT | No freshness inference from signature alone |
| Target identity unknown, pending `PREPARED`, terminal `CENSORED` | REJECT | An uncertain or terminal motor is not admitted as OPEN |
| Additional audited claim has a different source SHA | REJECT | Pinned source applies to **all** local claims, not source authenticity of the external binary |
| **Authority SQLite + publisher SQLite + callback-supplied witness all restored together** | **ACCEPT negative control** | `FAIL_INDEPENDENT_M11`, no independent protected high-water exists here |
| Real protected witness operator, distinct host/administrator, key custody, transport, restart/fault-matrix cross-host | **NOT_RUN / NOT_ATTESTED** | Still required before any M11 release claim |

## Result, recovery blockers and next gate

**ACCEPT only:** fail-closed read-only *software reconciliation* when a caller supplies a putatively external latest receipt. Do not interpret an accepted test callback as an off-host witness, a birth owner, a durable R2 runtime or an executable recovery result. In particular, the gate does not prove Mind/World/RNG/body-energy/vigilance parity, post-paid-learning receipts, crash-atomic two-phase motor recovery, hardware-backed key storage, source admission, protected external high-water or partition handling.

**STOP conditions retained:** witness unavailable or inconsistent, local publisher ahead/behind the witness, authority ahead/behind its signed checkpoint, PREPARED, terminal, foreign source, corrupt history and ambiguous motor. Even a consistent `OPEN` state only passes a read-only proof, not the full native R1/R2/R3/R4 activation gates.

**Next meaningful independent M11 deliverable:** operationally attest a separately administered signer + non-rewindable high-water, pin release source/writer/endpoint identities, protect and rotate credentials, and execute a genuinely cross-host privilege-separated rollback/crash/partition fault matrix. The current repository, CI mocks and GitHub test runner cannot substitute for those distinct principals. Never optimize full audit or prune nonce history based on this software PASS.

**Status confirmed:** keep [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) OPEN. `reference_generation=I3`, `active_generation=I1`, I3 `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE` with no entrypoints. P1.3 funded-v2 remains scientific reference and all new scientific World/cohort/index flags stay false.
