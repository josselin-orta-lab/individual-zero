# I3: current research and engineering status

## R2.10 strict TLS configuration on remote CAS writer: software PASS, independent M11 NOT_ATTESTED (13 November 2026)

The [R2.10 preflight](engineering/R210_TLS_CAS_WRITER_CONTEXT_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R210_TLS_CAS_WRITER_CONTEXT_RESULTS_2026-11-13.md), code [PR #1386](https://github.com/josselin-orta-lab/individual-zero/pull/1386), tested head `384d3312fce31de4cdcaf7dccbe68df5dbd4ac5e`, merged `3c4c129b6ea268574930540ff9d06c95ddd30c2b`, reject injected CAS writer HTTPS `SSLContext` objects that disable certificate/hostname verification or lack an explicit minimum TLS 1.2. Test-loopback HTTP cannot masquerade as TLS. [Actions #43496420728](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43496420728) **SUCCESS: 1,402/1,402 I3 software tests PASS under Python 3.11 and 3.12**, including all 8 new strict-context tests; generation ownership PASS, navigation PASS under 3.11.

**Remaining release failure:** no independently administered witness/operator, writer mTLS, protected monotonic high-water or off-host rollback drill is attested. The existing complete local + signer rollback remains `FAIL_INDEPENDENT_M11`. The [off-host release contract](engineering/OFFHOST_M11_INDEPENDENCE_RELEASE_GATE_2026-11-13.md) requires distinct A/B/C authority domains and a real cross-host negative test before M11 GO; its publication is **not** a deployment. #1331/#1339 remain OPEN. I1 remains active, I3 reference-only/unregistered, P1.3 funded-v2 Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`; all new science World/cohort/index permissions stay false.

## R2.9 full native genesis-state guard before first motor: software PASS, independent M11 NOT_ATTESTED (13 November 2026)

The [precommitted R2.9 virgin-state falsifier](engineering/R29_NATIVE_GENESIS_INTEGRITY_PREFLIGHT_2026-11-13.md) and [exact-source result/matrix](engineering/R29_NATIVE_GENESIS_INTEGRITY_RESULTS_2026-11-13.md) from [PR #1384](https://github.com/josselin-orta-lab/individual-zero/pull/1384), exact tested head `51683beaf9b0becb0a8afbffe81411271fc74d41`, code merge `f59e896d9586809f557395bd4f9779424c066368`, fix the native engineering session's previous unsealed sequence-zero state gap. The constructor retains complete process-local World and Mind state fingerprints and the first step now denies a changed hidden World effect or unpaid Mind learned value **before** any ledger PREPARED or native motor. Virgin detached reconstruction is covered. [GitHub Actions #43488834234](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43488834234) **SUCCESS: 1,394/1,394 I3 tests PASS under Python 3.11 and Python 3.12**, including three new adversarial no-motor regressions; generation ownership and navigation checks PASS.

**Negative preserved:** an in-process fingerprint is not remotely protected state, independent operator authority, true durable recovery or source attestation. The R2.8 full-domain dual-local + signer rollback remains deliberately accepted (`FAIL_INDEPENDENT_M11`), so #1339/#1331 remain OPEN. I1 remains the active engine and I3 reference-only/unregistered, P1.3 funded-v2 Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`, and scientific World/cohort/source authorizations remain false.

## R2.8 nonce-bound online signed witness: replay defense software PASS, independent M11 NOT_ATTESTED (13 November 2026)

The [precommitted R2.8 challenge protocol](engineering/R28_ONLINE_WITNESS_CHALLENGE_PREFLIGHT_2026-11-13.md) and [source-pinned results](engineering/R28_ONLINE_WITNESS_CHALLENGE_RESULTS_2026-11-13.md) from [PR #1382](https://github.com/josselin-orta-lab/individual-zero/pull/1382), code merge `7e0d2a56948d6327f23c672a8a7ccc97c3f43ee3`, add a **read-only, one-POST HTTPS challenge** for a fresh 128-bit nonce. A **separately pinned online Ed25519 responder public key** authenticates the exact nonce and complete issuer-signed receipt, which is also verified with its **different pinned issuer key** and reconciled by R2.6 against fully audited local state. No redirect, retry, local fallback, client-side signing key or motor permission. [Actions #43455950980](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43455950980) **SUCCESS: 1,391/1,391 I3 software tests PASS on Python 3.11 and 1,391/1,391 on 3.12**, including all thirteen new genuine loopback TLS tests and existing owner/navigation checks.

**Negative preserved:** a still-live online signing key can sign a **valid old receipt for a newly generated nonce** after authority SQLite, publisher SQLite and the test responder's latest state are restored together. That old state is ACCEPTED: **`FAIL_INDEPENDENT_M11`**. The two signing keys and local TLS service live in the same test worker; this is not an independently administered, non-rewindable authority or full cold recovery of Mind/World/RNG/body. #1339/#1331 remain OPEN, I1 active, I3 unregistered, P1.3 funded-v2 and Stage 2.1 scientific `NOT_ISSUED/HOLD_NO_VERDICT`; all new World/cohort/index permissions false.

## R2.7 signed latest-witness retrieval: real loopback HTTPS software PASS, independent M11 NOT_ATTESTED (13 November 2026)

The [frozen R2.7 HTTPS preflight](engineering/R27_HTTPS_LATEST_WITNESS_PREFLIGHT_2026-11-13.md) and [exact-source result/fault matrix](engineering/R27_HTTPS_LATEST_WITNESS_RESULTS_2026-11-13.md) from [PR #1380](https://github.com/josselin-orta-lab/individual-zero/pull/1380), merged `34b406cd25eed6c7fe7d4464875a54fbf2ba745a`, add a bounded **read-only latest-signed-receipt HTTPS client**. An operator-supplied CA/hostname/port and Ed25519 public key/authority/source/issuer pins enforce TLS certificate and receipt validation. HTTP redirect, caching, compression, oversize, invalid status, mismatched body and errors STOP without retry. [Actions #43449122655](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43449122655) PASS **1,378/1,378 I3 software tests on Python 3.11 and 1,378/1,378 on Python 3.12**, including ten new tests with a real test-loopback TLS server and ephemeral certs.

**Release-negative remains:** restoring both local SQLite stores and the presumed latest signed reply served by that TLS test server **ACCEPTS old state**. TLS and an authentic Ed25519 signature verify identity/bytes, not independent monotonic custody or recency. The server, CA and signing keys in tests all share one CI worker, not a separately governed M11 system. No client mTLS, key rotation, protected host/admin/high-water, WAN/partition test, production throughput or motor recovery grant. `FAIL_INDEPENDENT_M11` remains, #1339/#1331 OPEN. I3 architectural reference/unregistered, I1 active, P1.3 funded-v2 and Stage 2.1 scientific `NOT_ISSUED/HOLD_NO_VERDICT`; no new World/cohort/index authorization.

## R2.6 required-witness reconciliation: fail-closed software PASS, independent M11 NOT_ATTESTED (13 November 2026)

The [frozen R2.6 preflight](engineering/R26_REQUIRED_WITNESS_RECONCILIATION_PREFLIGHT_2026-11-13.md) and [source-pinned result matrix](engineering/R26_REQUIRED_WITNESS_RECONCILIATION_RESULTS_2026-11-13.md) from [PR #1378](https://github.com/josselin-orta-lab/individual-zero/pull/1378), merge `63b2a267169a004d87e468edfab44059c30d2c31`, add an **inspection-only** `reconcile_required_witness`. A **required injected** signed latest-witness callback must produce the exact Ed25519 bytes found at the source/key/authority-pinned local journal tip and in the fully audited v3 checkpoint; the target identity must remain `COMMITTED/OPEN`, with no pending motor and sequence below horizon, checked inside the same authority read transaction. The publisher reader opens **existing** DB via `mode=ro` without signer or writer initializer. [CI #43444367396](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43444367396) PASS **1,368/1,368 I3 software tests on Python 3.11 and 1,368/1,368 on 3.12**, eleven new no-World fault checks.

A match is explicitly `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`, not a native Mind/World/RNG/body cold-recovery equivalence or an executable life admission. A missing witness **STOPs** without local fallback. **Restoring both local databases AND the test callback's old receipt together still ACCEPTS the old state**, the required `FAIL_INDEPENDENT_M11` counterexample. The callback is not an independently deployed operator; no protected keys, non-rewindable external storage, mTLS, cross-host fault evidence, O(1) optimization or motor replay permission. Keep #1339/#1331 OPEN, I3 proposal/unregistered and I1 active; P1.3 funded-v2 Stage 2.1 science remains `NOT_ISSUED / HOLD_NO_VERDICT`, all new World/cohort/index permissions false.

## R2.5 atomic signed receipt publication: local software PASS, independent M11 still NOT_ATTESTED (13 November 2026)

The [source-frozen R2.5 preflight](engineering/R25_ATOMIC_RECEIPT_PUBLICATION_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R25_ATOMIC_RECEIPT_PUBLICATION_RESULTS_2026-11-13.md), code [PR #1376](https://github.com/josselin-orta-lab/individual-zero/pull/1376), merge `dd400b88682492ed70ccc9bb17415fc249866885`, add a **test-only** Ed25519 signer callback and a distinct **local** SQLite publication journal. It serializes writes against one accepted signed-receipt predecessor, checks every locally audited claim's source SHA in the same read snapshot, rejects PREPARED states, supports cold `latest()` inspection after an ACK loss, and refuses concurrent forks. [Actions #43442194291](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43442194291) PASS **1,357/1,357 I3 tests on Python 3.11 and 1,357/1,357 on 3.12**, including eleven new no-World faults.

**Release-negative retained:** restoring both local SQLite databases and the client-held head together accepts the older branch. **`FAIL_INDEPENDENT_M11`**; physically/admin-separated signer, protected high-water, key lifecycle, network fault matrix and source attestation remain `NOT_RUN / NOT_ATTESTED`. Publication CAS is not cross-database atomic, cannot authorize a paid motor replay and offers no O(1) fast path. Keep #1339/#1331 OPEN, I3 proposal/unregistered, I1 active, P1.3 funded-v2 and Stage 2.1 scientific `NOT_ISSUED / HOLD_NO_VERDICT`; no new scientific World/cohort/source rights.

## R2.4 signed receipt verification: Ed25519 software PASS, independently hosted M11 still NOT_ATTESTED (13 November 2026)

The [frozen contract](engineering/R24_SIGNED_CHECKPOINT_RECEIPT_PREFLIGHT_2026-11-13.md) and [source-specific fault matrix](engineering/R24_SIGNED_CHECKPOINT_RECEIPT_RESULTS_2026-11-13.md) from [PR #1374](https://github.com/josselin-orta-lab/individual-zero/pull/1374), code main `8fe2c41810aaa707b6bbb1ac5bf678030cce1eba`, add a **verification-only** Ed25519 checkpoint receipt. It pins public key, issuer, authority and source assertion, requires canonical signed bytes, a +1 publication index and prior signed receipt hash, and matches the fully audited v3 SQLite snapshot. [Exact CI #43434015538](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43434015538) PASS **1,346/1,346 I3 software tests on each of Python 3.11 and 3.12**, including ten new no-World cryptographic fault tests and explicitly failing closed if cryptography support is missing.

**Remaining negative:** a signed old receipt **and old SQLite and old retained high-water** restored together are accepted (`FAIL_INDEPENDENT_M11`). The key used in CI was generated inside a unit test; signing, source custody, protected monotonic storage and independent host/admin/operator are **not deployed or attested**. The signed source field is an issuer assertion, not independently authenticated physical data. There is no checkpoint hot-path speedup, motor replay grant, independent M11 release or Stage-2 scientific advancement. #1339/#1331 remain OPEN; I1 active, I3 unregistered, P1.3 funded-v2, `NOT_ISSUED / HOLD_NO_VERDICT`, scientific World/cohort authorizations unchanged and false.

## R2.4 checkpoint inspection now SQL read-only, independent M11 still not attested (13 November 2026)

The [frozen contract and exact source results](engineering/R24_READONLY_CHECKPOINT_INSPECTION_RESULTS_2026-11-13.md) from [PR #1372](https://github.com/josselin-orta-lab/individual-zero/pull/1372), merged `0b1827a79be377e62e2206917ebebbf77de20099`, correct the prior checkpoint's hidden use of `AuthorityStore.__init__` (`BEGIN IMMEDIATE`, writer capacity). The diagnostic capture now requires **existing SQLite `mode=ro`**, `query_only=ON`, a single read transaction and the full v3 authority audit. [Actions #43431825263](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43431825263) PASS **1,336/1,336 I3 software tests on Python 3.11 and 1,336/1,336 on Python 3.12**. Four no-World tests confirm no writer initialization, SQL-write rejection, foreign/missing denial and coherent concurrency.

This is an **SQL read-only correction**, not a protected OS filesystem or independent authority. It does not accelerate CAS/audit, remove model-cognition costs, grant a scientific World, prove off-host custody or fix simultaneous rollback of SQLite and its public checkpoint. `FAIL_INDEPENDENT_M11` remains the release-blocking negative control; #1339/#1331 stay open, I1 active and I3 proposal/unregistered, P1.3 funded-v2 Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`.

## R2.4 exact-state checkpoint custody: limited software PASS, independent M11 still unproven (13 November 2026)

The [preannounced R2.4 checkpoint contract](engineering/R24_EXACT_STATE_CHECKPOINT_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R24_EXACT_STATE_CHECKPOINT_RESULTS_2026-11-13.md) from [PR #1370](https://github.com/josselin-orta-lab/individual-zero/pull/1370), merge `1edaee0cdb4e8cb98d88beb67a88e142d62304f9`, introduce an isolated **read-only exact-equality** probe for fully audited authority v3 states, including all accepted nonce contents. [Actions #43426105969](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43426105969) passed **1,332/1,332 I3 software tests each** on Python 3.11 and 3.12. The first run #43425671982 failed a nonce-fault-injection fixture; it was corrected with a required one-row mutation assertion and remains in the PR history.

**Security boundary:** a retained **newer** public checkpoint rejects an older intact SQLite authority; an old SQLite paired with its matching **old** checkpoint is still accepted. That is deliberate `FAIL_INDEPENDENT_M11`, **not** off-host anti-rollback attestation. The probe performs a full authority audit; no checkpoint fast path, production release, World, life, source/index permission or cognitive policy change. Next implementation requires a genuinely protected monotonic witness and custody independent of the rollback adversary. Keep #1339/#1331 OPEN. I3 remains unregistered (I1 active), P1.3 funded-v2 Stage 2.1 scientific `NOT_ISSUED/HOLD_NO_VERDICT`.

## R2.4 authority-v3 measured growth: software probe only, M11 still not attested (13 November 2026)

The [frozen-contract no-World cost report](engineering/R24_AUTHORITY_COST_PROBE_RESULTS_2026-11-13.md), code [PR #1367](https://github.com/josselin-orta-lab/individual-zero/pull/1367), main `5c92fb5b8ed29869e7f2f990f772d8ab45992415`, uses an isolated engineering-only SQLite CAS v3 authority at 8, 32 and 80 steps. [Actions #43418531046](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43418531046) PASS **1,323/1,323 I3 tests on Python 3.11** and **1,323/1,323 on 3.12**, with exactly 17/65/161 CAS audit events, 25/97/241 accepted nonces, and 48/108/232 KiB of measured local SQLite storage. Median host-only CAS step time was 5.38/7.58/11.61 ms (3.11) and 6.84/9.66/14.74 ms (3.12) on those CI runners. This is not a hardware-calibrated throughput limit or a cognition E/V cost. The repeated full-history verifier and unpruned nonce storage deserve a **separately frozen, source-bound checkpoint and independent high-water** design before long-lived production.

The probe creates **no World, Mind or scientific life**, leaves all v3 integrity checks and security counterexamples intact, and does not grant an independently anchored M11 or engine release. Coherent rollback of authority + nonce SQLite is still accepted (`FAIL_INDEPENDENT_M11`); actual off-host host, key, source and rollback attestation remains `NOT_RUN / NOT_ATTESTED` under #1339 and #1331. `reference_generation=I3`, `active_generation=I1`, engine proposal/unregistered, P1.3 funded-v2 scientific Stage 2.1 `NOT_ISSUED`, E1/E3 local negatives, and all World/cohort permissions stay unchanged.

## R2.4 persistent request-nonce protection, **not** independent M11 (13 November 2026)

The [source-frozen engineering results](engineering/R24_DURABLE_REQUEST_NONCE_RESULTS_2026-11-13.md) from [PR #1365](https://github.com/josselin-orta-lab/individual-zero/pull/1365), code merge `a63f40db2f72409ceb808531cc017d98733a330f`, add a required durable 32-hex request nonce to the loopback authority's **v3** SQLite transaction. The same signed HTTP request now fails closed after first success, including across service restart; rejected CAS or bad-HMAC requests cannot poison the nonce. Signed `verify` now writes one durable nonce row but never an additional motor/CAS audit transition. [Exact CI #43414788550](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43414788550) PASS **1,320/1,320 I3 software tests each** on Python 3.11 and 3.12, with ten new no-World tests and previous suite preserved.

**Critical remaining negative:** restoring the *entire* authority SQLite file restores the nonce ledger too, and an earlier accepted request can be replayed. The regression's deliberate acceptance proves `FAIL_INDEPENDENT_M11` on common-domain rollback. The loopback server, shared HMAC test key, operator rights, lack of independent protected anchor and unbounded nonce-storage overhead cannot support an off-host custody claim. Actual off-host anti-rollback, independent source/credential attestation, disaster recovery and long-life latency remain `NOT_RUN / NOT_ATTESTED`. [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remain OPEN. I3 `proposal` remains unregistered, I1 active, P1.3 funded-v2 Stage 2.1 scientific `NOT_ISSUED` and new scientific World/cohort authority remains false.

## R2.4 signed-response replay protection and full-domain rollback **negative** result (13 November 2026)

The [source-frozen protocol and exact CI results](engineering/R24_RESPONSE_CUSTODY_FAULT_RESULTS_2026-11-13.md) from [PR #1363](https://github.com/josselin-orta-lab/individual-zero/pull/1363), merged as `2815e6d5909d9a9d23fa928061d4db1784c5e6fb`, establish a narrower engineering-only safety improvement: the signed remote witness now rejects inconsistent COMMITTED/PREPARED state even with correct test HMAC and rejects a replayed response authenticated for a different request nonce. [Actions #43411537219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43411537219) PASS **1,310 tests each** on Python 3.11 and 3.12, including the positive control that a separately retained volatile pin detects rollback of both local stores plus the remote authority SQLite.

**Critically, the deliberate four-state rollback negative control is accepted:** restoring both local stores, the remote authority SQLite and the *volatile pin itself* to older coherent snapshots allows the prior technical motor to be repeated in the isolated test World. **This is `FAIL_INDEPENDENT_M11`**, not a security PASS and not a science result. Off-host independently protected monotonic custody, real host identity and operational disaster-recovery tests remain `NOT_RUN / NOT_ATTESTED` under #1339/#1331. I3 stays an unregistered architecture reference with I1 active, P1.3 funded-v2, Stage 2.1 scientific `NOT_ISSUED`, no new science World/index authorization and no historical cohort reopening.

## Stage 2 RP-A1/RP-A2 documentary HOLD without mandatory reviewer (13 November 2026)

[ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) records the owner's removal of a mandatory external relecteur for the **RP-A1/S2-C01 internal methods disposition**, followed by RP-A2's conservative `HOLD_NO_VERDICT` suspension. The [bounded evidence matrix](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) rejects both universal inference from E3's 0/2 artificial legal-motor differences and false scientific success from B1's +8/96 exploratory survival contrast. E1/E3 original negative screens remain unchanged. No independent scientific review is claimed; this is a documented internal decision, not scientific Stage-2 closure. The canonical scientific verdict remains `NOT_ISSUED` and Stage 2.1 software capacity remains `REPLAY_GATE_CAPACITY_SHOWN`.

I3's scientific reference is still **P1.3 funded-v2**; I3 remains an unregistered architectural reference while I1 remains active. All existing original and cohort allocations are closed; `fresh_lived_worlds_allowed=false`, `scientific_gate_authorized=false` and `next_scientific_cohort_authorized=false`. No new Worlds/lives/tests are caused by this documentary decision. Subsequent science needs a genuinely new preannounced source, full endogenous paid-body causal design, defensible independent sampling/power and **new specifically scoped owner source/index authorization**. Autonomous **engineering** proceeds on native I3 M11 identity/durability/rollback without making a scientific efficacy claim.

## R2.4 remote authority audit chain: partial-tamper detection, not independent M11 (12 November 2026)

The [authority-side audit contract](ENGINEERING_REMOTE_AUTHORITY_AUDIT_2026-11-12.md) adds a source-isolated test-only v2 SQLite CAS transition log, verified before each signed network answer and on service startup. It catches partial manipulation of the authority state or audit record without touching P1.3 native Mind/World, but the **complete rollback of the authority database and its audit records is demonstrably accepted**. Thus a real independently administered, monotonic off-host witness and key/source custody remain unproven under [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339). Nine new no-World audit tests plus ten existing network tests passed locally; **exact-source GitHub CI remains the acceptance gate**. I3 stays the architectural reference, I1 the active registered engine; Stage 2.1 remains scientifically `NOT_ISSUED` and no new scientific World is authorized.

## R2 network monotonic authority: isolated transport proof, not M11 (12 November 2026)

The [remote monotonic protocol](ENGINEERING_REMOTE_MONOTONIC_AUTHORITY.md) introduces an optional third *engineering* custody mode: a separately running network CAS service with source/identity-bound genesis and PREPARED acknowledgement **before** `World.step`, followed by a COMMITTED receipt after native paid learning. Both local reservation and journal may be rolled back to older matching copies and are rejected while the network authority retains the newer head. The service shipped in this repository is **127.0.0.1 test-only**; credentials are shared-HMAC test secrets, not independent protected signing keys, and its SQLite database can itself be rolled back. This demonstrates only feasibility of the protocol in an isolated process, **not off-host attestation, operational M11, real external motor exactly-once or I3 active status**. The exact-source Python 3.11/3.12 CI is the engineering acceptance gate. No new science cohorts are opened; I3 P1.3 funded-v2 scientific Stage 2.1 remains `NOT_ISSUED` and R2 [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains open.

## R2 two-phase local rollback witness (12 November 2026)

The [conditional local rollback-witness engineering contract](ENGINEERING_LOCAL_ROLLBACK_WITNESS.md) extends the I3 reference native step with a **separately stored PREPARED witness before the motor** and an immutable-within-the-local-writer committed-head sequence witness after the paid learning receipt. A witness-bound ledger cannot be reopened through the native reconstruction API without the same witness; a ledger-only rollback or crash across one of the phases fails closed. The ledger schema advances from `i3-engineering-step-ledger/v1` to `v2` **without migrating old files**. A shared rollback of *both* databases remains undetectable; the witness is a local engineering check, **not independently authenticated M11, off-host monotonicity, state persistence for an external World or operational activation**. R2 issue [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains open. P1.3 funded-v2 is unchanged, Stage 2.1 scientifically `NOT_ISSUED`, no new scientific World authorized.

## R2 deterministic engineering restart by sealed replay, not M11 (11 November 2026)

The [source-pinned deterministic reconstruction](ENGINEERING_DETERMINISTIC_RECONSTRUCTION.md) recreates the P1.3 reference Mind/World on a **detached simulated World**, re-executes each *previously sealed* native decision and paid learning phase and requires exact original action/work/body/state-hash equality before another engineering motor. It includes a second-Python-process continuation test and rejects PREPARED/crashed or terminal histories. It neither persists a full state codec nor anchors local SQLite against malicious rollback, and is **not yet independent M11 cold recovery or production execution authority**. No old cohorts or scientific Worlds are reopened. Stage 2.1 scientific `NOT_ISSUED`, P1.3 funded-v2, registered active I1 and I3 reference selection remain unchanged. Exact-source CI required before merge.

## R2/R3 native engineering session: real paid steps, no cold continuation (11 November 2026)

The [isolated native-reference step integration](ENGINEERING_NATIVE_STEP.md) now drives the existing P1.3 `Mind.decide -> World.step -> prepaid outcome learning` inside a **fresh engineering-only fixture**, seals its factual energy/vigilance, body, terminal and observer-state hashes into the two-phase R2 ledger, and refuses uncertain continuation. The original `life.py`, production engine contract, experimental control and original studies remain unchanged. This is **in-process motor/receipt custody only, not an independently authenticated M11 owner or same-individual cold restart**. The technical test matrix includes paired software parity with a fresh reference `run_life` fixture, injected post-PREPARED motor failure, source binding, in-memory tamper and irreversible death. Local syntax and interface smoke were checked; exact-source GitHub CI is required for software acceptance. No new scientific cohort is permitted.

## R2 engineering custody prototype: two-phase step ledger, not actual M11 (11 November 2026)

The [R2 two-phase engineering ledger](ENGINEERING_STEP_LEDGER.md) is a source-isolated, local SQLite PREPARED intent then POST_PAID_LEARNING sealed-receipt protocol tied to the existing I3 birth reservation. It rejects uncertain prepared steps on read, stale/duplicate writers, damaged hash links, invalid two-currency receipts and further steps after death or horizon censorship. **Current scope is proof of software custody only:** the step receipt is caller-asserted, no born World/Mind drives the ledger, no full mutable state/RNG, genuine cold restart, external anti-rollback or M11 identity is proven. Focused isolated 14-test Python-3 validation passed locally (including energy/vigilance debit and mortality-body reconciliation); exact-source repository CI is independently required before acceptance. R1/R2 [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains open. I3 is the owner-selected development reference, not active runtime; P1.3 funded-v2, Stage 2.1 `NOT_ISSUED`, closed E3 result and no new scientific Worlds remain unchanged.

## Owner-selected development reference, not yet an active registered runtime (11 November 2026)

**First R1 technical implementation complete, not a new life:** [PR #1332](https://github.com/josselin-orta-lab/individual-zero/pull/1332) added [engineering-only SQLite birth-slot reservation](ENGINEERING_BIRTH_RESERVATION.md) with atomic unique local claim, read-only reopen and invalid/foreign/tampered receipt rejection. GitHub I3 software CI passed on Python 3.11 and 3.12 at the PR head, without new scientific Worlds. Its receipt unambiguously states `RESERVED_NOT_BORN`, `durable_m11=false`, `scientific_world_authorized=false`. The slot database is **not externally authenticated** and can be rolled back outside the owner; no native I3 state persistence, cold recovery or runtime activation is implied. Continue [R1/R2 issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) with genuine Mind/World owner and terminal M11 proof.

**ADR-0020 owner decision:** I3 is the project's architectural and engineering **reference generation** for new autonomous development. The canonical registry declares `reference_generation=I3`, while `active_generation=I1` still identifies the running, persistence-equipped registered engine. I3's own contract remains an unregistered proposal with no active runtime/birth entrypoints. The next technical priority is native generation-owned birth identity, durable M11 ownership, terminal-state and cold-recovery safeguards, followed by exact-source integration tests before an explicit deployment release. This requires no repeated owner signoff for routine engineering; it does not authorize a new scientific World or alter past lives. Inside I3 the reference policy remains **P1.3 funded-v2**; Stage 2.1 software capacity is known, its scientific verdict remains `NOT_ISSUED`, and frozen E3 is a candidate-specific negative result. See [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md).

## Stage 2.1 post-E3 inference gate: false scientific closure excluded (11 November 2026)

The accepted [post-E3 scientific stop assessment](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md) now has a separate [exact reproducible methods decision envelope](studies/stage2-replay-gate-selected-design/POST_E3_INFERENCE_DECISION_ENVELOPE_RESULTS_2026-11-11.md) (prospective [preflight](studies/stage2-replay-gate-selected-design/POST_E3_INFERENCE_DECISION_ENVELOPE_PREFLIGHT_2026-11-11.md) committed `26497d9f081304d730c61a5925dc5fefa1319ffa` **before** code). Exact tested software source [PR #1325](https://github.com/josselin-orta-lab/individual-zero/pull/1325) HEAD `a80cc1a0ea46e53a9c42df1ea03d52a264f6dfc9`; [Actions #43094305191](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43094305191) SUCCESS **1,161/1,161 I3 tests** under Python 3.11 AND **1,161/1,161** under Python 3.12. Identical bounded aggregate SHA-256 `88c13e176d8fdd460427e5ce613b86f7a61f81d2b58d6caacd70e27afc9d9f72`. No original read/generation, new World or new life in this methods source exercise; previous provenance reports are reused as finite numerical inputs.

Four separate completed old DEVELOPMENT contrasts have finite paired survival risk differences **B1 GATE−FIXED +8/96**, **three-arm GATE−paid-RANDOM 0/64**, **CONTENT-48 TD priority−random memory identity −6/48**, **NEXT-DECISION-24 TD priority−random content −1/24**. They have distinct interventions and no externally established independent target ecology; **do not pool**. Existing exact paired statistical method reproduces B1 conditional one-sided 95% lower `−0.04325164695153383`. This *numerically* exceeds the **unapproved, hypothetical** −0.05 NI margin but cannot be a valid scientific NI GO: independent iid ecology, accepted biological margin and external methods review are missing, while no new causal information-to-native-action-to-body mechanism is identified. E3 frozen **0/2** native motor differences and E1 **0/12** distinct fixed synthetic contexts are legitimate **candidate-level negatives only**; E1's 24 depth comparisons are not 24 independent units. Hypothetical iid binomial upper sensitivities (E3 0.7764, E1 0.2209) are **not applicable confidence intervals** for these fixed artificial samples.

**Current research decision: E3 exact candidate CLOSED NEGATIVE, full Stage-2 generalized adaptive-reflection question NOT IDENTIFIED.** No proof that autonomous thinking is universally worthless or generally beneficial. Next step remains one **independent scoped methods/futility review** of what negative scientific publication is defensible, not replaying consumed source Worlds, inflating study independence, introducing a fixed action heuristic or tuning E3 artificial contexts. A truly different action-relevant source would require its own precommitted no-World native discrimination and cost mechanism before separate born-source permission. **Governance unchanged:** I3 unregistered, P1.3 funded-v2, Stage **2.1**, scientific `NOT_ISSUED`, `fresh_lived_worlds_allowed=false`, no Stage 2.2/2.3 GO or Stage 3 transition. No production `Mind`, `World`, genotype or BodyLaws changed.

## Stage 2 post-E3 scientific stop checkpoint: candidate negative, Stage 2 NOT closed (11 November 2026)

The [full C05 closure-readiness and stop assessment](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md) reconciles the canonical [scientific Stage-2 roadmap](STAGE2_COMPLETION_AUDIT_AND_ROADMAP_2026-11-11.md), E0/E1 originals and counterfactual negatives, E2 personally action-indexed **software** source capacity and the frozen E3 [exact paired native choice result](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md). The last original E3 code was exact-head tested in [Actions #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480), **1,148/1,148 I3 tests in each Python 3.11/3.12**. One of two informed artificial histories changed a native option score; **zero** changed the legal native action/param, with equal paid additional operators and a separate empty-support control. The preregistered **specific E3 source/transform candidate is CLOSED NEGATIVE**; no seed, body, effect or policy tuning permitted to reverse that finite result.

**Stage-2 scientific release is still NOT_ISSUED.** A no-motor-effect result from synthetic states does not scientifically invalidate all adaptive cognition; nor does moving an intermediate score demonstrate useful autonomous reflection. Existing living replay studies are DEVELOPMENT only, with mixed/null survival and no independently valid survival NI. Full technical/experimental/scientific/transition predicates in the new stop checkpoint remain unfulfilled. **Minimum current action** is this negative-evidence custody and a hold on further speculative compute controllers; resume only on a newly justified, truly paid, first-person, native-action-discriminating information mechanism, or on a separately defensible narrow negative scientific closeout. New cohort source, power, source-index authority and actual post-paid-learning body evidence are not available now.

No change to P1.3 funded-v2, Stage **2.1** status, `src/i3/ACTIVE_SURFACE.json`, engine registration, old closed cohorts, permissions or scientific World count (**0 new lives**). No Stage 2.2/2.3 GO, Stage 3 or evolution generalization claim.

## Stage 2 E3: personally indexed branch information reaches native score, not motor (11 November 2026)

The owner-delegated campaign froze [E3 native paid branch-delivery protocol](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_PREFLIGHT_2026-11-11.md) at `762f8493366b5aafa7525e34c948db32c05f70f6` **before executable code**. [PR #1321](https://github.com/josselin-orta-lab/individual-zero/pull/1321), exact source SHA `e9706b90d4d13ecb318fb21d72fa6c0fb964b6c7`, merged as main `75bd4cb25e73c7dd006d83a1e5783f2a8b150bde`; [Actions #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480) **SUCCESS**: **1,148/1,148 I3 tests under each Python 3.11 and 3.12**, same deterministic complete aggregate SHA-256 `f078899c348944b076bd0038987c434f411571cc0c44aeba5f32bc9f005b4b01`. [Full finite results and stop rationale](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md).

**New technical evidence:** an opt-in **lab-only** `ReferenceBranchMemoryMind` subclass actually runs the **native** `Mind.decide` over normal offered options and original Competition/Action Control, while computing an equal-frequency expected score of genuinely evaluated **stored action-keyed empirical outcome deltas** through the **existing** `Mind.simulate` and `_ObservedEffectView`. Both VISIBLE and PAID_DISCARD actually execute the same prepaid source scans, views, simulations and reductions at the **same native model energy/vigilance tariff**, with an unspent conservative affordability quote protecting a 2.0 motor-energy reserve. Original native uncertainty and curiosity/risk terms are unchanged; PAID_DISCARD returns the original option score. All original P1.3 behavior and registry remain untouched.

**Predeclared outcomes, no retuning:** two E2 artificial/unpaid same-mean past-outcome histories `spread` and `flat` plus one empty-history control, same frozen body/genome/seed, 3 matched native software decision comparisons. **SPREAD=SCORE_ONLY**, **FLAT=NO_DISTINCT_SCORE**, **NONE=NO_DISTINCT_SCORE**; **0/2** learned-history software cases changed the actual `Mind.decide` admitted action/parameter, **0/3** total, despite **1/2** source shapes changing an option score. The old detached alternate action is NOT being counted as a native motor. This is **not** an actual World motor execution, born original, physically settled organism bill, generalized survival sample or proof of net reflection value. **Scientific verdict: `NOT_ISSUED`.** Technical source-specific verdict: **`E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN`**.

**Decision and stop:** the exact E3 readout/fixture candidate is **CLOSED NEGATIVE** per its preregistered rule. Do not enlarge the synthetic grid, retune body/seed, replace unfavorable histories, force eating/drinking, invent a risk/curiosity bonus or add a new predictor to create an attractive motor divergence. Reuse E2's established action-bound memory source only if a *separately precommitted* mechanism addresses genuinely independent information and justified decision relevance. Before any prospective new cohort, the project still lacks a demonstrated native **action difference**, measured full computation tariff, independent/ecologically valid matched population/power and **new exact-source, owner-index-scoped World authority**. The next most economical research decision is a **Stage-2.1 stop/negative-closure assessment** against the scientific goals, not another post-hoc E3 attempt.

**Current authority:** P1.3 funded-v2 reference, Stage **2.1**, I3 unregistered, `fresh_lived_worlds_allowed=false`, `all_new_worlds_currently_authorized=false`, scientific `NOT_ISSUED`; no Stage 2.2/2.3 GO, no change to Stage 1 CLOSED_NEGATIVE under ADR-0018 or any historical exhausted source.

## Stage 2 E2: existing paid action-keyed empirical branches retain information absent from native means (11 November 2026)

The owner-delegated campaign found and reused the **already implemented** `ReferenceBranchMemory`/`PersonalOutcomes` action-indexed empirical outcome ring, with native `CognitiveBudget` charges for storage/reads. [Prospectively frozen E2 software design](studies/stage2-replay-gate-selected-design/PAID_PERSONAL_BRANCH_SOURCE_COMPLEMENT_PREFLIGHT_2026-11-11.md) at commit `1d0836405641ce37a9f6874b453e58551f0e84ce` preceded [PR #1318](https://github.com/josselin-orta-lab/individual-zero/pull/1318), exact source `275d08fe568eb9ad1ad7278df1da6cc764cd20e9`, merged as main `9b774a80f00b8ba2c584b3ef67c76e700f288870`. [Actions #43061617485](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43061617485) **SUCCESS**: **1,140/1,140 I3 tests** each Python 3.11/3.12, identical deterministic E2 digest `09e9321bbb847693ae7023091cb640c922ca4dee9e73680c55d2915fab809ef2`. [Complete interpretation](studies/stage2-replay-gate-selected-design/PAID_PERSONAL_BRANCH_SOURCE_COMPLEMENT_RESULTS_2026-11-11.md).

Two frozen **synthetic/unpaid** history shapes, same genome/seed/action/body, two action events each, have identical `EffectsModel.stats` and native `Mind._read_plan_prediction` but distinct personal outcome support (`food=-4,+4` versus `0,0`) under the EXISTING action-keyed branch memory. All store/read model work was prepaid and reconciled in both native energy/vigilance currencies; a two-record branch read bills `CognitiveWork(cycles=1,memory_items=16)`, **0.0232 energy and 0.05 vigilance in modeled tariff**. Absent other action support, unfunded reads/writes, dead-state access and source mutation fail closed. First candidate CI source had a **JSON tuple-key serialization error** (not scientific negative); it was corrected without changing frozen fixture values before the two-Python full PASS.

**Scientific boundary:** source-format information *capacity* is now shown for **old existing infrastructure**, **not** born-person evidence, real-world physical debit, native choice use, net personal fitness gain, Stage-1 reopening or Stage-2.2 GO. Unlike already-consumed TD replay, this separate ring does carry action keys and empirical outcome variability beyond native means; however it is **not currently used by the P1.3 reference controller**. Therefore **do not build a new memory store** for this E2 hypothesis. The remaining E3 gate is one separately frozen opt-in equal-compute and native-two-currency-priced VISIBLE/PAID_DISCARD delivery of an explicitly defined **body-consequence** readout into native `Mind.decide` and Action Control, with null/unfunded cases included and no chosen motor imposed. If it does not alter native admissible choice under its frozen software design, stop the E3 candidate rather than synthetic fixture/seed hunting. Independent new World/power/source permissions and true POST_PAID_LEARNING impacts remain separate prerequisites.

**Authority unchanged:** I3 is unregistered Stage 2.1, P1.3 funded-v2 reference, scientific `NOT_ISSUED`, all old original cohorts CLOSED_NO_RETRY, `fresh_lived_worlds_allowed=false`, no Stage 2.2/2.3 GO. No native motor/World/genome/body law/engine registry behavior changed. Existing [PR #1309](https://github.com/josselin-orta-lab/individual-zero/pull/1309) is still a draft design, not born-cohort authorization.

## Stage 2.1: 144 immutable old originals authenticated, insufficient for new information-to-action causal evidence (11 November 2026)

The owner-approved evidence-first campaign [source audit #1316](https://github.com/josselin-orta-lab/individual-zero/pull/1316) froze its [protocol](studies/stage2-replay-gate-selected-design/OLD_ORIGINALS_CAUSAL_READINESS_PREFLIGHT_2026-11-11.md) at commit b32fe63377912488dad63eaaefb94c10a989261b **before new audit code**. Exact source PR HEAD 2df66a35fb7da2357c88a09577e691d5ad4a187d passed [Actions #43049277536](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43049277536): **1,133/1,133** I3 software tests on Python 3.11, **1,133/1,133** on Python 3.12, and a third independently run **old-original-only** SHA validator. Two original evidence refs matched immutably pinned commits, 96/96 CONTENT-48 plus 48/48 NEXT-DECISION-24 full original gzip and uncompressed files passed their original independent auditors, with all 72 paired units and exact historical outcomes. Compact audit digest e2296b900543ccf913ae0f57c3467037c96eb94c0004cad93f26fbb5558db2c4. **No new World or life.** [Full source-bounded report](studies/stage2-replay-gate-selected-design/OLD_ORIGINALS_CAUSAL_READINESS_RESULTS_2026-11-11.md).

**Scientific boundary:** OLD replay-content interventions are random versus priority *memory choice*, not new additional information VISIBLE versus same-compute PAID-DISCARD. The old next-decision experiment recorded 20/24 different funded replay forks with subsequent perception, but the one different priority next motor was a **DETACHED alternate**, **never executed in World at that same source capture**. Historical source results remain valid, but they do **not** contain the actual paid additional readout → delivered native choice → observed t1 POST_PAID_LEARNING causal chain. **Verdict: OLD_ORIGINALS_INSUFFICIENT_FOR_PAID_INFORMATION_CAUSAL_TEST.** Stop trying to reconstruct this new treatment from exhausted old studies. This negative is a source/identifiability result, **not** a negative theorem about generalized cognition or all replay.

**Authority unchanged:** I3 unregistered, P1.3 funded-v2 reference, Stage 2.1 scientific verdict NOT_ISSUED, no Stage 2.2/2.3 GO, `fresh_lived_worlds_allowed=false`, and no renewed old cohorts. Future E2/E3 requires a genuinely additional costed first-person action-relevant computation that demonstrably reaches native action, full two-currency/sleep/foregone-learning price, new exact-source owner-index-scoped prospectively independent World/entropy allocation and proper power/estimand review. The separate [#1309 proposed design](https://github.com/josselin-orta-lab/individual-zero/pull/1309) remains **draft**, not scientific authorization.

## Stage 2 E1: native Mind choice unchanged under paid depth caps, software negative on frozen grid (11 November 2026)

Owner-approved minimum scientific-Stage-2 roadmap [#1310](https://github.com/josselin-orta-lab/individual-zero/pull/1310) and source-backed E0/E1 triage [#1311](https://github.com/josselin-orta-lab/individual-zero/pull/1311) led to a prospectively frozen [native-choice depth protocol](studies/stage2-replay-gate-selected-design/NATIVE_OPTION_SET_DEPTH_DECISION_PREFLIGHT_2026-11-11.md), committed **before runnable code** as 72b996bae2fcdf2e654e529d987a8b80e39fe057. The helper and tests merged in [PR #1314](https://github.com/josselin-orta-lab/individual-zero/pull/1314) as main **4f8f8fc854c833dfc5f33ca7e77f1baaccef6a29**. Exact tested source c9cecd77ef76f9bcb9c200e3df6fbf46e1bdca7c passed [GitHub Actions #43043257219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43043257219) with **1,126/1,126 I3 software tests per Python 3.11 and 3.12**; the same result SHA-256 **9a08f583a99a15fcf0cafc1146e3c83a83af1a8d1adbd225ab3045c1e9fdf179** appeared in both jobs. The [full interpretation](studies/stage2-replay-gate-selected-design/NATIVE_OPTION_SET_DEPTH_DECISION_RESULTS_2026-11-11.md) is preserved separately.

The fixed 3-body x 4-context, synthetic/unpaid-effect fixture ran **48 actual Mind.decide software calls**, including plain P1.3 full-cap parity; **24/24** short-versus-full comparisons had the same fully scored option order. Although 3/24 native score vectors changed, **0/24 native final options** and **0/24 admitted native actions/parameters** changed. No funding-dropout confound, no new World, no born source, no actual living physical debit. Verdict **NO_DECISION_DISCRIMINATION_ON_FROZEN_GRID** is a legitimate bounded software negative, **not** proof all deeper thought is useless. The preregistered **stop rule now applies to this horizon-cap candidate**: no state/seed/effect retuning or expansion into another synthetic-grid hunt just to manufacture a positive action.

**Current authority unchanged:** P1.3 funded-v2 reference; I3 unregistered, still **Stage 2.1**; canonical replay-gate software capacity PASS does not establish utility; **scientific verdict NOT_ISSUED**, no Stage 2.2/2.3 GO, `fresh_lived_worlds_allowed=false`, all old originals and one-shot cohorts permanently CLOSED_NO_RETRY. The next defensible task is methods/source review for a genuinely additional, action-relevant, first-person **paid information** channel and independently sourced visible-versus-paid-discard causal transport, not an automatic new World or extra decision rule. Draft [#1309](https://github.com/josselin-orta-lab/individual-zero/pull/1309) is not approved science. Independent source, complete model tariff, source-index-scoped authorization and preregistered causal/NI estimands remain unresolved.

## Stage 2.1: 48 OLD original lives byte-reverified; living next-action and detached alternative separated (11 November 2026)

Following the synthetic-only [#1305/#1306](https://github.com/josselin-orta-lab/individual-zero/pull/1305) submitted-claim chronology preflight, the [prospectively frozen **OLD** archive read-only bridge](studies/stage2-replay-gate-selected-design/ARCHIVED_NEXT_ACTION_ACTUAL_VS_SHADOW_BRIDGE_PROTOCOL_2026-11-11.md) was committed **before code** as `e8ab645c975f5ea6935bf91c0a633d434c9bf94e` on exact main `0c63972774bde1c9cf8369e02946e4f31e68884e`. [Merged PR #1307](https://github.com/josselin-orta-lab/individual-zero/pull/1307), tested source `d8afdc7e5058ad514a47cac13176196f824cae09`, squash `ff7ce3b320b740fc6b3c301d45cd23403f16a45a`; [Actions #43017416135](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43017416135) **PASS 1116/1116 full I3 tests each on Python 3.11 and 3.12**, 7/7 engine/generation guards both versions, and 533 navigation checks with 0 errors/0 warnings on Python 3.11. A new branch-scoped **READ-ONLY job inside the already registered I3 workflow** independently fetched the consumed [exact evidence branch commit](https://github.com/josselin-orta-lab/individual-zero/tree/20ca7efbf7797fa7b1f12983ce68906b754b312c/archive/i3/stage2-next-decision-development-2026-11-10) `20ca7efbf7797fa7b1f12983ce68906b754b312c`, verified its commit pin and the existing original auditor's **48/48 packed plus 48/48 unpacked original SHA-256**, every source/plan/claim/paid-cognition identity and 24 reduced pairs **before** interpreting next decisions. Both versions produced the same bounded aggregate digest `d04e9c226340e9b8a14a2df5242765b7f9b2239b4c0bb66ced4077e5145d9776`. [Full original-read-only result and negative CI custody](studies/stage2-replay-gate-selected-design/ARCHIVED_NEXT_ACTION_ACTUAL_VS_SHADOW_BRIDGE_RESULTS_2026-11-11.md).

**All 24 OLD assigned developmental pairs** retained: 20 different funded memory replay subsets followed by next actual first-person perception, 4 no-different-replay negatives, 0 lost next perception after different replay. For the 20 next captured choices, the archived source observer recorded its random-content detached replica as equal to the **living random-content Mind's actual next choice and cognitive work**; the priority replay choice was **only a detached hypothetical** evaluated at that perception. **19/20** alternative priority choices selected the same motor/parameter, **1/20** selected a different *counterfactual* motor; **zero priority alternative actions were executed in any second World**. Byte-verified original records do not produce an alternative factual outcome, a delivered-information intervention or independent source/capture hardware attestation. The previous `1/24` remains a hypothetical action contrast, **not** causal survival mediation.

The initial new-workflow attempt was correctly **blocked** by engine workflow ownership [#43016629444](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016629444); its standalone **read-only** archival check had passed [#43016629615](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016629615). The extra workflow was removed and the verification job embedded in the existing approved I3 CI. An intermediate code run [#43016903680](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016903680) found two bad **new tests** (missing mock fixture and non-falsifying mutation), fixed without changing any original study, source bytes or declared counts; the final exact-head all-PASS is recorded above.

**Scientific boundary:** these **48 historical lives already existed** and were only read, not rerun; `new_Worlds=0`, `new_born_originals=0`, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`. No optional readout was delivered to the living next-action process, no cost-matched delivered-vs-discarded treatment or calibrated CPU-to-body pricing exists, and `NextActionPairCustody` #1305 is **not** falsely filled with the old replay-content population. I3 remains **unregistered Stage 2.1**, no Stage 2.2 GO, no new owner-index-scoped World authority or modification of Mind/Competition/genome/native laws. Future genuinely action-mediated prospective readout utility still requires independent approved source, native paid delivery, true later motor choice and post-paid-learning first-person outcome under full no-exposure/death/censor controls (issues [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062), [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276), [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283)).


## Stage 2.1: next factual-action custody substrate, not yet action-mediated learning evidence (11 November 2026)

After the [256-cell cost-only negative identifiability result](studies/stage2-replay-gate-selected-design/COMPUTATION_VALUE_IDENTIFIABILITY_RESULTS_2026-11-11.md), the next question was narrowed to the missing **actually executed future action**, not more synthetic distress thresholds. The [precommitted next-action preoutcome-custody protocol](studies/stage2-replay-gate-selected-design/NEXT_ACTION_MEDIATION_CUSTODY_PREFLIGHT_2026-11-11.md) was frozen **before code** as SHA `d7823fee56fbffe8a6ff2e3b6cbb5fb3a9a2583f` on exact `main` `1026d01044c2d010238def7cb36a19773df0e8b7`. [Merged PR #1305](https://github.com/josselin-orta-lab/individual-zero/pull/1305), source SHA `efa7adb030b5bbbb32950aa77bba554985a49ca0`, squash `8dbdf9caee2c690040fe3e04319c0a6b98f29327`, [Actions #43014223188](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43014223188) **PASS 1110/1110 I3 full tests on Python 3.11 and 3.12**, plus both engine/generation guards; the Actions navigation step was **SKIPPED**, not independently passed. [Complete structural-only findings](studies/stage2-replay-gate-selected-design/NEXT_ACTION_MEDIATION_CUSTODY_PREFLIGHT_RESULTS_2026-11-11.md).

The separate, inert `lab/stage2_next_action_mediation_custody.py` validates a **source-claim** two-arm sequence: same pre-exposure Mind/genome/WorldSpec hashes; equal-model-paid first action/readout; original actual t0 decision, World and learning dual-currency receipt with `POST_PAID_LEARNING` phase; then **a second, separately preoutcome-frozen choice from the reported living `Mind.decide`** and its actual next World and learning receipts. It rejects `DETACHED_SHADOW`, unaffordable tickets, stolen motor reserve, duplicate/tampered seals, partial or forged energy/vigilance bill, terminal/no-learning contradictions and a next choice without an executed source-claimed consequence. The four deliberately synthetic pair cases distinguish **same** versus **different** next actual-action claims, versus **terminal before next** and **right-censored** (both `INCOMPLETE_OR_CENSORED`). Explicit `None` stays physical inactivity, distinct from chosen `attendre`. All tests ran **without World construction, run_life, Mind.decide, or Mind.learn**.

**Scientific boundary:** These are **constructed software receipts**, not newly observed actions. Input hashes and words like `LIVING_MIND_DECIDE` are not independent born-life archive authentication. Accordingly the reducer **always** returns `source_originals_independently_verified=false`, `controller_delivery_independently_verified=false`, `next_decision_independently_verified=false`, `causal_information_benefit=null` and `scientific_verdict=NOT_ISSUED`. The historical 24-unit study's **1/24 detached hypothetical action difference** has not been promoted to an executed motor difference. No readout is yet delivered to the living action chooser, no actual first-person causal mediation has been observed, no born individual or original generated, and **`worlds_opened=0`, `scientific_lives=0`**. I3 remains **unregistered Stage 2.1**, no Stage 2.2 GO, no new source index authorization, no activation or change to P1.3, laws, learned memory or innate disposition. Future source-bound experiment must separately establish a genuine living readout available for later unforced choice versus equally paid discard, complete personally experienced consequences and independent ecologies, as tracked by [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062), [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283).


## Stage 2.1: inherited computation cost is measurable; information benefit remains unidentifiable (11 November 2026)

Following the completed #1298/#1300 **pure native model cost** campaigns, a [precommitted single 256-cell factorial identifiability protocol](studies/stage2-replay-gate-selected-design/COMPUTATION_VALUE_IDENTIFIABILITY_SOFTWARE_2026-11-11.md) was frozen **before code** at SHA `927c8cd42e1e63b2a502ab28981511cf116db7f4` against exact `main` `f530800bccbe454c811ad05b551cf1bf180fc0dc`. [Merged PR #1302](https://github.com/josselin-orta-lab/individual-zero/pull/1302), exact PR source `1c4f80516d0af8cd1cafe38f2e0ae3027ab44e4a`, merge `2ba8b2325212c47db69098fe8bafe62484d6019f`. [GitHub Actions #43005324828](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43005324828) **PASS: 1102/1102 I3 software tests on each Python 3.11 and 3.12**, 7/7 engine/ownership checks, 533 Python 3.11 navigation checks without error. Both versions produced identical 256-cell deterministic JSON SHA-256 `bd0d77088ae9244945c88f27a7db6ab2e7f4ec8056d7d899e3fb764e8e50f95c`. [Complete result, fixed-grid provenance, examples and next scientific boundary](studies/stage2-replay-gate-selected-design/COMPUTATION_VALUE_IDENTIFIABILITY_RESULTS_2026-11-11.md).

Under unchanged native v2 pure physics, actual reference `Mind.prepare_learning` **software allocator** and innate `-Mind.distress(feats(body))`, 256 fixed synthetic states × three model-payment arms (reference, paid readout visible to laboratory, paid readout executed but discarded) yielded **168 admissible optional extra-work cells, 88 denied without charge**. In admitted cells, the cost-only `POST_PAID_LEARNING` intrinsic scalar change was **140 negative / 28 exactly zero / 0 positive**; **46** lost a previously model-affordable next learning allocation and **6** had a native synthetic terminal contrast absent from reference. The two paid forecast arms have **exactly equal cognitive model work, physical body, learning allocation, terminal and innate reward in all 256 cells**. Different legally inherited food weights change the scalar significance of the *same* modeled physical cost without adding a designer-written food veto, special motor priority or new innate rule. Critically the fixed action means **`expected_information_benefit=null`, `realized_future_action_effect=null`, `net_value_of_computation=null`**: useful predictive information is **NOT identified** by a cost-only fixed-action comparison. A null intrinsic change is not free computation; a small synthetic squared loss is not a causal decision benefit.

**DRIFT DETECTED:** repeated synthetic threshold demonstrations can no longer resolve the crucial information→later motor→actually lived bodily outcome link. This technical work consolidates cost accounting, **not** an adaptive metareasoning mechanism or scientific cohort. Its EffectsModel history is synthetic unpaid construction, model charges are uncalibrated CPU proxy, `worlds_opened=0`, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`. I3 remains **unregistered Stage 2.1**; no Stage 2.2 GO, new World, action policy change, validation, selection or reserve. The manifest currently forbids fresh born Worlds. Resume genuine prospective value-of-computation research only after independent ecological source/owner custody and true forecast/decision/paid outcome capability, following [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062), [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276), and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283); never force a survival action or re-label old outcomes.


## Stage 2.1: restorative sleep can hide an optional cognition cost in vital food (11 November 2026)

After [#1298/#1299](https://github.com/josselin-orta-lab/individual-zero/pull/1298) showed that optional reading can prevent the next native learning allocation despite preserving the motor command, a [six-cell prospectively frozen *pure native body-law* falsifier](studies/stage2-replay-gate-selected-design/SLEEP_COGNITION_METABOLIC_TRANSFER_SOFTWARE_2026-11-11.md), protocol SHA `19e5c6568f8d926926b5c9522ef2c3794ee65315` on original main `13a7e7ae417d78997ddbe416bde8782bba5b3bd8`, tested whether restorative sleep can **convert an otherwise masked two-currency cognitive debit into additional consumption of food**. [Merged PR #1300](https://github.com/josselin-orta-lab/individual-zero/pull/1300) source `0203258d99cf78b44d210bb131514fd6ff67c54c`, squash `75839d2e3f731b56acf29930b6f6d0e93ccb1d49`. [Actions #42999412092](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42999412092) **PASS: 1095/1095 full i3 tests each on Python 3.11 and 3.12**, with engine/generation and navigation checks. [Complete results and all negative controls](studies/stage2-replay-gate-selected-design/SLEEP_COGNITION_METABOLIC_TRANSFER_RESULTS_2026-11-11.md) are source-preserved.

The same already selected `dormir` or `attendre` action, pure original `CognitiveWork(cycles=3,memory_items=12)` and optional proposed readout `CognitiveWork(cycles=6,memory_items=48)` (extra modeled **0.1296 energy, 0.30 vigilance**) were admitted by the native budget and processed only by unchanged `transition`. In the fixed high-recovery `sleep_saturated` body, **both arms ended with energy=100 and vigilance=100**, yet the additional cognitive work raised food converted into recovered energy from **0.00562 to 0.01210**, leaving **0.00648 less food**. In the preregistered `sleep_food_critical` pure body cell, the reference retained food `0.00438` (nonterminal), while the extra-work branch spent its remaining food and entered native `zero_food` terminal despite the same final E/V. This terminal finding is **a deliberately constructed software threshold**, not a newborn individual's death. The fixed `sleep_food_control` nonterminal near miss, unsaturated sleep (direct E/V loss but equal food), waiting (no additional food), and denied ticket (no phantom physical charge) all passed. **6/6 declared cells**, no reselected source. Food-conversion and food-to-repair contributions are separately reconciled; all effects arise from existing World-independent native laws.

**Scientific boundary:** No `World`, `run_life`, `Mind.decide`, new agent or actual physiological debit in a born organism; `worlds_opened=0`, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`. This is an important model-level *indirect cost/currency-transfer* observation, not evidence that i3 anticipates it, chooses computation adaptively or survives better. The optional readout price remains an **uncalibrated model-category bill**, not CPU-joule conversion. Do not impose an innate food veto, script a sleep preference, revive closed cohorts or claim ecological survival. i3 remains **unregistered Stage 2.1**, no Stage 2.2. Continue [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062), [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) for endogenous value-of-computation with full lifetime currency/food/learning opportunity accounting under separate prospective scientific authorization.


## Stage 2.1: native-readout expense can prevent funding the next learning allocation (11 November 2026)

Following merged [#1296](https://github.com/josselin-orta-lab/individual-zero/pull/1296) and phase semantics, the [precommitted four-case software-only readout/next-learning falsifier](studies/stage2-replay-gate-selected-design/READOUT_LEARNING_AFFORDABILITY_SOFTWARE_2026-11-11.md) was frozen on main `a6abe6475d393a71b620efc8ece458ac4fac690c` before first code/test execution as `75a85b930d5b5295b53c0e5e7d8788d818554adf`. [Merged #1298](https://github.com/josselin-orta-lab/individual-zero/pull/1298) `3d39761222483e5852243ed3817a1728b7ffbef3`, exact source `6a4d54e547e8b61ffdb0721603e7d09e0b8caffc`, [Actions #42988497425](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42988497425): **1088/1088 full I3 tests PASS on both Python 3.11 and 3.12** and both 7/7 engine/generation checks. Earlier CI failed one new test mocking signature; the correction changed no source bodies, native code or hypothesis. [Fully annotated fixed results](studies/stage2-replay-gate-selected-design/READOUT_LEARNING_AFFORDABILITY_RESULTS_2026-11-11.md) preserve all four outcomes.

The unchanged native software body law, prior chosen `attendre` motor command, simulated original decision ticket `CognitiveWork(cycles=3,memory_items=12)` and proposed extra readout ticket `CognitiveWork(cycles=6,memory_items=48)` (extra modeled **0.1296 energy / 0.30 vigilance**) were used to compare pure after-action bodies with/without optional readout and **actual original `Mind.prepare_learning`** next-phase allocations. At frozen starting `E=0.56`, base learning can be paid after the motor without readout but cannot after the admitted extra readout (post-action E `0.1476` vs `0.0180`). At starting `V=0.55`, same first-person original motor remains possible, but the readout changes next learning from affordable to unaffordable (post-action V `0.4` vs `0.1`). A high-reserve case retains next learning on both arms; a low-energy case rejects the extra ticket **without any additional charge or lost motor**. **2/2 declared boundary divergences and 2/2 positive/negative admission controls PASS.** Original Mind state and RNG unchanged, no invented outcome, no forced survival behavior.

**Important limitation:** these are **synthetic pure native model transitions**, not real World instances, paid lived forecasts or statistical survival results. No native `World.step`, no `run_life`, no `Mind.learn` and no physically lived learning debit ran. The fact that an optional readout consumes native model reserves needed by subsequent learning does not prove i3 predicts this tradeoff or benefits from an imposed “preserve learning” priority. The underlying action-neutral phase-aware forecast and category tariff remain uncalibrated to real CPU/memory energy. **`worlds_opened=0`, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`**, i3 unregistered Stage 2.1, no Stage 2.2, no new birth/selection/validation/reserve. Issues #1276/#1283 remain open; future independent prospective work must evaluate tradeoffs from the individual's own cumulative predicted distress, including possible foregone learning, without scripted action rules.


## Stage 2.1: action-conditioned outcome timing fixed; passive readout only model-authorized (11 November 2026)

After the purely synthetic action-effect provenance [#1294](https://github.com/josselin-orta-lab/individual-zero/pull/1294)/#1295, a [precommitted protocol](studies/stage2-replay-gate-selected-design/ACTION_CONDITIONAL_PHASE_AND_READOUT_BUDGET_2026-11-11.md) at `15461ff84fb8b64619440019a9eaab4231bd898b` on exact baseline `97cb83b386ef73883f949d357fcbe514b4f40260` addressed the remaining *phase-of-target* ambiguity and *readout cost* admission. [PR #1296](https://github.com/josselin-orta-lab/individual-zero/pull/1296), source `ed67a0c76d91ba2d4d80150d796210cadbd92ebc`, squash `4ac74d0aee8e6c52b5cbe74ecc424b5b0b894ad2`, [Actions #42929649585](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42929649585) **PASS: 1081/1081 full i3 software tests on both Python 3.11 and Python 3.12**, 7/7 generation/engine controls, Python 3.11 navigation PASS (3.12 navigation skipped). [Complete source-locked software result](studies/stage2-replay-gate-selected-design/ACTION_CONDITIONAL_PHASE_AND_READOUT_BUDGET_RESULTS_2026-11-11.md).

**Frozen bodily target semantics:** The reference runtime first calls `World.step` to return the body *after decision cognition and motor* (`IMMEDIATE_POST_WORLD`); **then**, for a nonterminal affordable outcome, it physically debits `learning.work` and passes the resulting `POST_PAID_LEARNING` body to `Mind.learn_from_outcome` and the existing `EffectsModel.observe`. Thus **PRIMARY** future scalar intrinsic-distress target for a later *action-conditioned* forecast must be `POST_PAID_LEARNING`, which matches the body delta learned natively; `IMMEDIATE_POST_WORLD` is an explicitly tagged **SECONDARY** control. In a constructed software-only `attendre` fixture, a pure native learning debit changed the action-forecast squared error from `0` immediately after the motor to `0.00001571025823412813` after learning: these numbers result from a deliberately aligned fake effect and **are not out-of-sample accuracy**. No affordable learning or an actually terminal outcome yields equal phase targets; observed terminal uses full `-d_max`, and absent future observations remain `RIGHT_CENSORED_NOT_SCORED`, never zero-loss successes. Tampered preoutcome SHA, action/param, phases, contradictory terminal, or forged native dual-currency receipts are rejected. Previous #1286/#1288/#1292 observations were immediately post-World outcomes and have NOT been rescored or relabeled.

**Proposed readout category model only:** `CognitiveWork(cycles=6,memory_items=48+n)` for three passive action/global/persistence forecasts, where n is the number of native four-field replay memories (0..genetically bounded m_max <=512) and provenance hashes are external laboratory CPU. Under unchanged body laws, n=0 costs **0.1296 energy / 0.30 vigilance** as a hypothetical model bill. A previously chosen original `Mind.last` action/body/param and an already-funded original decision are required. Native `CognitiveBudget` authorizes this extra proposal *before any readout or memory scan*, preserving motor energy and both currencies; explicit low-energy/vigilance/motor-reserve and null-action refusals perform no optional computation. **This is not a completed World debit or CPU-to-energy calibration**. The synthetic receipts validate pure `debit_cognition` arithmetic only. No new World or born organism executed (`worlds_opened=0`, `scientific_lives=0`); the historical experiments and model remained unchanged.

**Scientific decision:** i3 still unregistered, **Stage 2.1**, `scientific_verdict=NOT_ISSUED`, no Stage 2.2, survival improvement, policy/innate change or independent ecological validity. Keep [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) open for proper prospective action-conditioned forecast/outcome evaluation and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) open for a fully calibrated two-currency endogenous CPU-readout cost. The active manifest still forbids fresh lived Worlds without separately frozen index-specific custody/authority. **Do not promote the constructed synthetic zero-loss example or retroactively reinterpret the earlier paid technical cohorts.**


## Stage 2.1: provenance of the existing action-conditioned effects forecast, software-only (11 November 2026)

After the negative, fully balanced native-price/host-inference campaign [#1292](https://github.com/josselin-orta-lab/individual-zero/pull/1292) and canonical #1293, action-agnostic scalar replay regression has **not demonstrated predictive benefit** over fully paid discard. A [new strictly pre-exposure protocol](studies/stage2-replay-gate-selected-design/ACTION_CONDITIONAL_EXISTING_EFFECTS_PROVENANCE_2026-11-11.md), initial commit `7e1ce3330eabd22f9e220960bf81a2a2c46b07c1` on exact main `f6021034507665f19c314c3ff76b6f7a614e30e7`, tests a different readout path: can the **existing already-owned, action-indexed native EffectsModel** support a passive, choice-conditioned next-distress estimate without adding rules or inventing action-labeled replay memories? Merged [PR #1294](https://github.com/josselin-orta-lab/individual-zero/pull/1294), exact source `1a54cc055f128e1d770a4145bd133bd683afd380`, squash `cae90ae1cd77cc2f7275574cf6f3ffebbc5adf39`, [Actions #42923207456](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42923207456) **PASS**: **1072/1072 full i3 tests each on Python 3.11 and 3.12**, all engine/generation checks and Python 3.11 navigation PASS (3.12 navigation skipped in its workflow matrix).

**Provenance distinction:** native `Mind.buffer` entries contain only **(absolute TD error, before-body, after-body, dead)** and **do not retain the corresponding action**. Any mechanism pretending to derive past chosen action labels from this buffer would be a fabricated observation. The actual living `Mind.effects.stats` already records action-keyed personally learned mean bodily changes, normally updated by the **prepaid** reference learning path. The new *lab-only passive readout* reads only this existing model, the already-chosen actual action label checked against `Mind.last`, and original inherited `Mind.feats/distress`. It compares three same-body scalar next-distress estimates: `action` via action-generalized effects, `global` via the existing `('*',)` mean, and `persistence` with no assumed body delta. Unknown action history or actual inactivity uses an explicitly marked **global fallback**; no resource token, hidden World or prior action preference enters the readout. The preoutcome scalar forecasts and chosen action/param are SHA-frozen; the synthetic-only scorer rejects forged/tampered action or future-body/terminal results and uses existing terminal `-d_max`.

**Software outcome only:** One **constructed synthetic** contrasting-effects fixture produced a different action forecast for `attendre` vs `dormir` at an **identical before-body**, while its global and persistence forecasts were invariant. Missing action-specific effects returned exactly the existing global estimate; identical action-effect statistics produced an exact null; token renaming did not change the action-generalized readout. A deliberately constructed wait-step target exactly matched the synthetic learned wait effect, so squared error was `action=0`, `global=0.021287620563271718`, `persistence=0.012920111111111193`. **This engineered-zero score is a deterministic implementation check, NOT prospective predictive utility, independent sampling, or learned survival evidence.** Source Mind/learned statistics/RNG remain unchanged; no new policy/motor power is granted.

**Hard limitations:** `worlds_opened=0`, `scientific_lives=0`; **no authentic first-person future outcome was scored** in this software-only PR, and all fake prior EffectsModel observations were **unpaid synthetic construction**. The new readout, token-filter and proof hashes are **external laboratory CPU, NOT funded by the living body**. In native life, `Mind.effects` may learn a change between a before-body and a *post-outcome-learning debit* body, whereas the immediate `World.step` outcome is the body **before** that later learning fee: the future-scoring target must explicitly align time boundaries before testing predictive utility. `ACTIVE_SURFACE.json` currently states `fresh_lived_worlds_allowed=false`; no scientific or engineering World was opened. Continue [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) for action-conditioned first-person target semantics and forecast discrimination, and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) for a prospective full two-currency readout tariff and strict independent new-source custody. **I3 remains unregistered, Stage 2.1, `scientific_verdict=NOT_ISSUED`, no Stage 2.2 GO, no adaptive policy, no survival claim**. Do not calibrate or select from the exposed 990041–990043 results.


## Stage 2.1: equal counted inference and real native body payment, predictive advantage still absent (10 November 2026)

The previous source-locked [host-operation parity negative audit](studies/stage2-replay-gate-selected-design/COMPACT_FORECAST_HOST_OPERATOR_COVERAGE_FALSIFIER_2026-11-10.md) (#1290/#1291) established that paid-discard previously executed **one fewer actual inference** (4 vs 5) while receiving an equal body-model bill. The new [prospectively frozen equal-count/native-paid protocol](studies/stage2-replay-gate-selected-design/BALANCED_PAID_COMPACT_FIRST_PERSON_ENGINEERING_2026-11-10.md) was committed **first**, `d37e411d7829cb0dd138bf7ed6ab8fb080387a6d`, on exact baseline main `d29f326cb1b64aecaa72c29afa8f05d0aa8597d4`, before the new engineering Worlds. Source `86f677e178b74f4ed0e4618687b28b06cb35fe4d` was merged in [PR #1292](https://github.com/josselin-orta-lab/individual-zero/pull/1292) as `f90c1edf65b58d1ebe88ec49d787efeca9beaf7a`. [Actions #42913123113](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42913123113) **PASS**: **1064/1064 i3 software tests on each of Python 3.11 and 3.12**, 7/7 engine/owner-generation checks, navigation PASS on Python 3.11 (the Python 3.12 navigation step is explicitly skipped).

**New source-locked ENGINEERING only:** exactly three *new* fixed `midpoint()` seeds `990041/990042/990043` in one known `dev_open_field()` ecology, horizon 80, three actually paid modes (historical TD-priority, authentic life/step-seeded HMAC-random memory, and learned-then-discarded forecast) plus one non-cost-matched first-motor reference: **12 technical lives, 0 scientific births**. The first 12 chronological memory-eligible decisions (steps 7–18) per paid arm yielded **108/108 prospectively SHA-frozen forecasts scored exclusively on the next ACTUAL World bodily outcome**; **0 denied**, **0 missing/horizon-censored** in these fixed cases. All **108 funded slots** execute **exactly 5 counted `CompactPersonalDistressHead.predict` calls** (including a post-training prediction computed but intentionally ignored in discard), **3 genuinely executed direct-outcome replay updates**, **n key-priority memory visits** and **n HMAC identity computations** for n=6..17. **3/3** fixed-seed three-arm full `trace_head`/`evidence_head`/action/terminal/final-body/**dual-currency cognition** evidence parity, **3/3** initial precharge motor actions equal to the non-cost-matched reference. The native original `CognitiveBudget` funded and `World.step` actually debited `CognitiveWork(cycles=7,memory_items=4*n+6,replays=3)` at each actual step: **0.161..0.1698 energy** and **0.38 vigilance** per forecast; all actual World receipts show no unpaid work. No predictor changed the individual's choices, original Mind or innate laws.

**Unfavorable proper-loss finding despite balanced inference counts:** twelve-factual-outcome cumulative squared loss per fixed technical seed (TD-priority / HMAC-random / fully executed then discarded):
- `990041`: `0.0031127664924237397 / 0.0028305401131257677 / 0.0027148316301828243`
- `990042`: `0.003170283921054651 / 0.002843320092954864 / 0.0027591686243621013`
- `990043`: `0.003170283921054651 / 0.002886883934747786 / 0.0027591686243621013`.

Across the **36 paired chronological factual windows**, aggregate TD loss `0.009453334334533041`, random `0.008560744140828417`, discard `0.008233168878907026`; **paid-discard lowest-error in all 3 seeds**. Across windows TD was better than random **15/36** and random better **21/36**, zero ties. Only **20 distinct bodily target values** occurred across the 36 windows, so these are correlated, partly repeated exposures, emphatically NOT 36 independent outcomes or three independent ecological source populations. The negative learning result is preserved without post-hoc adjustment or source reselection. **Equal counted host inference operations is not the same as equal actual elapsed CPU work**, nor is the category tariff a measured CPU/bytes/HMAC-to-energy calibration; the extra custody SHA/hashing remains external laboratory instrumentation and is not endogenous cognition.

**Scientific boundary:** engineering feasibility and native model-payment check PASS; **sustained predictive utility, action-value improvement, ecological generalization and survival benefit NOT SHOWN**. The head is an externally monitored **fresh per-slot refit**, not a persistent adaptive policy. No new scientific birth/selection/validation/reserve, no independently held-out world family, no owner lift for a new scientific transport, no Stage 2.2 GO or I3 engine activation. **I3 unregistered**, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`. Keep [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) OPEN for full reproducible CPU/bytes-to-declared-work coverage accounting and an independently prospectively locked ecology before any new scientific intervention. Do **not** tune replay modes from the exposed 990041..990043 outcomes.


## Stage 2.1: equal native cognition bill does NOT imply equal host computation (10 November 2026)

Following the already closed [12-window actually paid first-person campaign](studies/stage2-replay-gate-selected-design/REPEATED_PAID_DISTRESS_PREQUENTIAL_ENGINEERING_2026-11-10.md), the [pre-exposure host-operator coverage falsifier](studies/stage2-replay-gate-selected-design/COMPACT_FORECAST_HOST_OPERATOR_COVERAGE_FALSIFIER_2026-11-10.md), protocol commit `d9b6e8e8f3ac4056f91b6abbd6d0547befd334e3` on main `ca2f474a8751bec20ce6e5491f95b2f7ab309d95`, completed in merged [PR #1290](https://github.com/josselin-orta-lab/individual-zero/pull/1290) (`410f93920cb16976752b466ec48fda2994fca6a5`). Exact source `213189590025f3a39fcaf4294d67b35007e1dadb`, [Actions #42908866216](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42908866216): **1058/1058 I3 tests PASSED under both Python 3.11 and Python 3.12**, plus all 7 generation/engine tests and 533 structural navigation checks (zero errors/warnings on Python 3.11).

**Confirmed negative software finding:** In the unchanged original compact paid engineering observer, the historical TD-priority and HMAC-random modes each execute **5** `CompactPersonalDistressHead.predict` calls, whereas its equally model-paid trained-then-discarded control executes only **4**: all three perform 3 genuine direct-outcome training updates, but paid-discard skips the additional posttraining inference. This was independently observed using a scoped read-only real-method spy in **10 synthetic source cells** (memory n=6,12,32,128,512 × 0/256 irrelevant spatial/effects entries), without any World. The v2 model's **declared `CognitiveWork` ticket was still identical** across arms. Therefore prior #1286/#1288 were **equal physically billed under the declared World model**, *not* equal in executed host inference operations; never describe the old cumulative losses as exactly CPU-matched or revise their frozen individual outcomes.

The new **laboratory-only balanced forecast helper** computes both pretraining and posttraining readouts in all three arms (5/5/5 inference calls) while returning the same old forecast, learned weights and three update counts; it was checked across the 10 fixed audit cells and the 48 existing synthetic personal Mind fixtures, with source/RNG preservation. It was **not used to rerun prior Worlds, promoted into Mind/World or installed in an action policy**. No born organism has yet paid this proposed computationally balanced path.

**Cost coverage finding:** Priority selection performs n key visits; the genuine life/ordinal-separated HMAC selector performs **n cryptographic identity messages** for n eligible memories, confirmed on all five fixed sizes. At n=512 there are 512 HMAC digest operations (2,450 message payload bytes plus 16,384 digest-output bytes). The provisional native `CognitiveWork(cycles=7,memory_items=4*n+6,replays=3)` is well-defined and physically charged *when run in a World*, but its operator categories do **not establish measured CPU, memory-copy, hash or sort energy conversion**. Separately, first-person `_source_seal` and SHA receipts are external laboratory provenance, not endogenous cognition; the observer's host allocations were recorded only as diagnostics and intentionally not treated as the individual's physical bill. No measured deficit in joules can be inferred from the operation counts.

**Scientific gate unchanged:** no new World/biological cohort executed (`worlds_opened=0`, `scientific_lives=0`), no independent ecological transfer, no confirmed predictive usefulness or causal survival benefit, no selection/validation/reserve, no Stage 2.2 or motor authority. I3 remains **unregistered**, `scientific_verdict=NOT_ISSUED`. Keep [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) **OPEN** for complete endogenous CPU/memory/selector tariff calibration, a future prospectively balanced equal-compute paid engineering intervention, and a separately authorized independent ecology design. **Do not tune from the already exposed #1288 first 18 steps or reinterpret past losses.**


## Stage 2.1: first twelve prequentially paid compact predictions, adverse learning control (10 November 2026)

Following the [completed three compact-body-paid single-window engineering sources](studies/stage2-replay-gate-selected-design/PAID_COMPACT_FIRST_PERSON_ENGINEERING_2026-11-10.md) and issue [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283), a new [pre-exposure frozen repeated-first-person protocol](studies/stage2-replay-gate-selected-design/REPEATED_PAID_DISTRESS_PREQUENTIAL_ENGINEERING_2026-11-10.md) was committed on `69a681f9ec975b27c8dc830eb05c88d06fcd6c1d` prior to any new engineering World. The original source was main `26f7278f237c8ed555312f8a5fa3085e2e08ac99`, new engineering source head `27425727105afb98fc7b5d3093c83ca06b75959b`, merged [PR #1288](https://github.com/josselin-orta-lab/individual-zero/pull/1288) as `3ccd8839535bdcafbc050753f3d664791359f8f2`; [Actions #42903949539](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42903949539) **PASS**, **1054/1054** complete I3 software tests on Python **3.11 and 3.12**, source/generation guards and 533 navigation checks without errors/warnings. No old scientific original or earlier engineering source was rerun.

Exactly **three new fixed non-scientific seeds** `950041/950042/950043`, `midpoint()`, `dev_open_field()`, horizon 80, with three equally paid external compact-head modes (TD-priority, genuine HMAC-random memory content, computed/paid-then-discarded learning) plus one zero-extra-cost reference each: **12 temporary technical lives**, no independent iid ecology. At each chronological eligible first-person step **7–18**, each paid mode reserved its *native* `CognitiveBudget` and `World.step` **actually debited** the same increasing compact work envelope `CognitiveWork(cycles=7,memory_items=4*n+6,replays=3)`, n=6..17, energy **0.161..0.1698** and vigilance **0.38** per opportunity. **108/108** forecasts were SHA-frozen before a real future World outcome, scored on that factual next first-person Body with original innate observed target; **0 funding refusals**, **0 terminal/horizon missing slots**, **36 distinct observed targets** across the 36 matched steps. Both selectors and all three actual regression updates ran equally in every paid mode, with discarded training retained only as an equal-cost negative control. **3/3** paid triplets had exact full physical/action/evidence/dual-currency cost parity, and first precharge actions matched the unpaid reference **3/3**. No head prediction ever altered motor choice or the individual's own persistent Mind. These are repeated *fresh per-slot refits*, **not** a persistent online model.

**Adverse technical predictive-loss observation**, retained across every assigned matched factual step: priority-vs-random squared error **priority lower 15/36**, **random lower 21/36**, zero ties. Twelve-step squared error SUMS per engineering seed (TD priority / random / equal-cost learned-then-discarded):
- `950041`: `0.0023952279707412974 / 0.00284495708482505 / 0.0032371732216515898`
- `950042`: `0.0031127664924237397 / 0.002866751609660639 / 0.0027148316301828243`
- `950043`: `0.003572892657596498 / 0.0034378628108769488 / 0.003084701639529786`.

Over the 36 matched factual windows, cumulative loss is TD **0.009080887120761535**, random **0.009149571505362638**, paid-discard **0.0090367064913642**. Training helps on seed 950041 and is **worse than paid-discard on 950042 and 950043**, a genuine mixed/negative result, not a stable demonstrated gain. No post-hoc adaptation to these already exposed outcomes is permitted.

This engineering-only work remains **one deterministic ecology**, 36 correlated chronological outcomes, not independent biological populations, randomized trial or out-of-sample generalization. The native bodily category tariff was genuinely charged, but host CPU/allocations and external integrity hashing remain **uncalibrated** in body currencies. The direct target is action-agnostic, no counterfactual value of choosing actions and no survival effect was assessed. **No new scientific lives or ecological independence, no causal predictive benefit, no confirmatory survival non-inferiority, no Stage 2.2/engine activation**. I3 remains **unregistered**, `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`. Keep [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) OPEN; next candidate scientific gate needs properly designed independent ecosystem sampling, prospective held-out outcomes and calibrated full cognition tariffs, not parameter selection on these same early-life engineering observations.


## Stage 2.1: compact distress predictor actually debited in 12 new engineering lives (10 November 2026)

After [full-Mind-copy cost defect and compact equivalence PR #1284](https://github.com/josselin-orta-lab/individual-zero/pull/1284), the separately [preregistered compact true-payment protocol](studies/stage2-replay-gate-selected-design/PAID_COMPACT_FIRST_PERSON_ENGINEERING_2026-11-10.md) has executed and [PR #1286](https://github.com/josselin-orta-lab/individual-zero/pull/1286) is merged as `c2ed0cacf850c3382150579343c109ae1066f40e`. Exact engineering source `7bdb510919dda8ff413d0728898741ee0c3d90ac`, baseline `d35fc3b43b46852394a66c92ff0754b3f9b6d939`, [Actions #42897182997](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42897182997): **1048/1048 complete I3 software tests PASS on Python 3.11 and Python 3.12**, plus engine contract checks.

**All 12 new technical lives** were completed on three fixed new `midpoint()` engineering life seeds `940041/940042/940043`, `dev_open_field()`, horizon 80: each reference plus priority/random/trained-then-discarded equal-price compact observer. **9/9 genuinely first-person predictions** froze before actual World step 7 and scored only that actual next bodily outcome. **3/3 equal-cost paid triplets** had identical full physical `trace_head`, `evidence_head`, decision actions, terminal, body and full energy/vigilance cognitive accounting. In **3/3** the motor choice made before the extra cognition agreed with the uncharged reference at the same first paid step. The unchanged native `CognitiveBudget` preauthorized and the native `World.step` **actually charged 0.161 energy and 0.38 vigilance** per predictor opportunity, including three executed personal-memory updates, with complete paid accounting/zero unpaid work. Unfundable, action-reserve and vigilance shortages, absent histories, tampered sealing, changed motor commands and an observed synthetic terminal penalty were separately software-tested; no optional head readout changed the living policy.

The *individual* squared-loss rows (priority / HMAC random / fully trained then discarded) are:
- `940041`: `8.586149938624242e-06 / 8.60897380678787e-06 / 1.4822500000000048e-05`;
- `940042`: `8.586149938624242e-06 / 8.384058242441209e-06 / 1.4822500000000048e-05`;
- `940043`: `8.47124855238917e-06 / 8.125251275432777e-06 / 1.4982920604938332e-05`.

Random-content lower loss **2/3**, priority **1/3**, both actual-trained controls lower than paid-discard **3/3**. Fixed technical lives in one ecology, **not three independent biological source populations**, and the predictive output never controlled action. The work envelope `cycles=7,memory_items=4*n+2*k,replays=k` is a *genuinely applied native physical model tariff* for this prototype, **not fully calibrated host CPU/actual bytes/observer work to organism energy/vigilance**. Hence no confirmatory causal predictive usefulness, action-value counterfactual, survival noninferiority, independent ecological transfer, or Stage 2.2 GO. **I3 remains unregistered; `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`.** Keep [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) OPEN for complete deployed computation-accounting calibration and new independently prospective future ecology design. All consumed source cohorts and their evidence remain closed.


## Stage 2.1: compact personal distress shadow resolves unpriced full-Mind copy (10 November 2026)

Following the exact [six genuinely billed engineering reference lives in PR #1281](https://github.com/josselin-orta-lab/individual-zero/pull/1281), the [preregistered full-copy cost falsifier](studies/stage2-replay-gate-selected-design/COMPACT_SHADOW_FULL_COPY_COST_FALSIFIER_2026-11-10.md), [merged PR #1284](https://github.com/josselin-orta-lab/individual-zero/pull/1284) at exact merged SHA `3fed22224e45696267cc601aa206a11efe56279b`, passed [Actions #42885829549](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42885829549) with **1042/1042 i3 tests on Python 3.11 and Python 3.12** and **533 structural navigation checks (0 errors, 0 warnings)**. It identified a real engineering tariff-coverage defect: the legacy detached predictor deeply copied all learned `Mind` states, including irrelevant maps, history, effects and RNG, while its #1281 model bill depended mainly on transition-buffer length. At constant 12 past memories, Python 3.12 median peak traced allocations grew from 38,928 bytes with no unrelated states to **221,288 bytes** with 256 unrelated map/effect states despite the unchanged prior bill. The source-locked synthetic, **no-World** audit repeated this five-size 0/256-state check for n=6,12,32,128,512; full-copy growth was present in 5/5.

A separate compact head now preserves solely original innate distress `theta,p,w,alpha,d_max` and an immutable copy of *personally recorded before/after/terminal body transitions*. Across the **48 existing software-only Mind fixtures** with TD-priority, authentic HMAC random-content and zero-replay controls, exactly equal predictive weights, point forecasts and terminal intrinsic penalties were checked; source Mind/history/RNG remained unchanged. At n=12 plus 256 irrelevant states, Python 3.12 peak traced memory for the compact proposal was **1,669 bytes** versus 221,288 legacy; at n=512 plus 256 irrelevant states **64,621 bytes** versus 272,775. These are platform-dependent host allocation diagnostics, **not organism energy**, and profiles may differ across Python versions.

A separately bounded proposed `CognitiveWork` operator-category envelope for **compact-only** learning is `cycles=7,memory_items=4*n+2*k,replays=k` for 6<=n<=512, 0<=k<=min(n,16). Under unchanged native v2 BodyLaws this models **0.1658 energy / 0.38 vigilance** at n=12,k=3 and **0.5658 energy / 0.38 vigilance** at n=512,k=3. Native `CognitiveBudget` motor reserve and insufficient-energy/vigilance failures have software tests, but **no subsequent living individual has yet paid this NEW envelope**; don't reuse #1281's real billing as evidence for it. The first CI attempt found an invalid less-than-six eligible memory guard and was corrected prospectively; no scientific source was reopened. This is a structural cost-model correction, **not a calibrated CPU-to-body tariff**, adaptive cognitive benefit, general survival improvement or Stage 2.2 GO. I3 remains unregistered; `scientific_verdict=NOT_ISSUED`. Next: a new prospective engineering-only, actually physically billed compact predictor with action-neutral cost-matched no-learning/random/priority and complete first-person outcome custody; only later independent ecological design with a separately justified tariff calibration.


## Stage 2.1: genuine first-person replay-sensitive shadow prediction, now physically billed in engineering (10 November 2026)

The independent next-outcome research question is tracked in [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276). The [original 48-case synthetic predictor](studies/stage2-replay-gate-selected-design/PERSONAL_DISTRESS_SHADOW_PREQUENTIAL_2026-11-10.md) in merged #1279 trained an action-agnostic direct-distress head from the individual's own remembered body transitions, with no World, policy change or physical payment. The follow-up [external engineering first-person result](studies/stage2-replay-gate-selected-design/LIVED_DISTRESS_FIRST_PERSON_ENGINEERING_2026-11-10.md), [PR #1280](https://github.com/josselin-orta-lab/individual-zero/pull/1280), [Actions #42873592692](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42873592692), completed **two unpaid observer ON/OFF matched 80-step real engineering lives**, 2/2 original future first-person predictions scored without changing any living action/body/funding trace. The synthetic work was not an organism bill.

The subsequent [fixed prospective three-arm paid engineering protocol](studies/stage2-replay-gate-selected-design/PAID_DISTRESS_SHADOW_ENGINEERING_2026-11-10.md), [merged PR #1281](https://github.com/josselin-orta-lab/individual-zero/pull/1281), exact merged SHA `af83780b115ee96bab6fa46187dcc94579894b37`, [Actions #42879979988](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42879979988), completed **6/6 genuine 80-step temporary engineering reference lives**, two predeclared life seeds × three branches. Their first eligible next-body forecasts were SHA-frozen before actual step 7, personally observed and scored. Native `CognitiveBudget` preauthorized and `World.step` *actually debited*, in all six branches, an identical declared `CognitiveWork(cycles=5,memory_items=9,replays=3)` amounting to **0.1168 energy and 0.28 vigilance** per observed opportunity. Three variants: historical TD-priority, life-seeded HMAC random memory identities, and a **fully computed and paid but discarded** learning control. Both 2/2 matched paid triplets have exact action/physical/evidence/paid accounting parity; unfundable/motor-depleting extra work is rejected before any shadow training. Full **1036/1036 I3 tests each on Python 3.11 and 3.12 PASS**, plus engine contracts/navigation. Initial PR run had a deliberately tested *unfundable boundary* incorrectly set to a still-fundable 2.12 energy, which was corrected to 2.10 and rerun; it is an engineering-test correction, not a scientific rebirth.

On the **same fixed engineering target** in each life, squared errors (priority / random / trained-then-discarded) were:
- seed `930041`: `8.586149938624242e-06 / 8.4583874635318e-06 / 1.4822500000000048e-05`;
- seed `930042`: `8.586149938624242e-06 / 8.252500482910544e-06 / 1.4822500000000048e-05`.

Thus random-content was lower-error in **2/2** engineering cases, while both trained arms scored below discarded in **2/2**. This is not evidence of stochastic iid generalization, causal survival improvement, action-value counterfactuals, population-level superiority or the cognitive efficiency of real CPU work. Both fixed cases share one deterministic engineering ecology and target, not two independent ecological tests. Crucially, the additional v2 physical body bill is **real for this provisional category work declaration**, but the category tariff is **not calibrated to all actual CPU/memory/copied-data overhead**; a complete production cost model is unestablished. Predictor output never controlled an action. **No scientific lives, independent iid ecological frame, selection/validation/reserve, activation, confirmatory survival or Stage 2.2 GO.** I3 remains unregistered. **Next:** bound and calibrate full cognition tariffs; independently design future-source proper predictive-utility plus cost and no-learning/random-content controlled generalization, before attempting any changed decision policy. Do not tune on the two exposed technical outcomes.


## Stage 2.1: next first-person decision from equal-count realstate replay forks (10 November 2026)

[24 new source-claimed matched G0/World/life pairs, 48/48 originals](studies/stage2-replay-gate-selected-design/NEXT_DECISION_24_RESULTS_2026-11-10.md): exact main source `d86474d4eea47e8066169988c152f24c40f8efb6`, [Actions #42837992463](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42837992463), prebirth claim `40dc37a565c7529793cbff24758b49b2371a2886`, [original gzip evidence](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-next-decision-24-development-20261110-originals/archive/i3/stage2-next-decision-development-2026-11-10), commit `20ca7efbf7797fa7b1f12983ce68906b754b312c`, original manifest SHA `53fdea10f56994a9171d274ecc6388a3301128503b98c1572052ee4b780196b5`. Primary finite assigned-unit result: **20/24** first genuinely prepaid different replay memory subset, **20/24** had next real first-person perception, **1/24** resulting different hypothetical next physical action (19/24 same), **4/24** no first fork. The random detached branch matched the real living action/option/work on every observed event; no alternative World was run. 19 same-action observed next-step bootstrapped TD residuals are **not** calibrated predictive loss. Secondary finite horizon-400 survivors TD priority **12/24**, random-content **13/24**, discordance 2 priority-only/3 random-only, with higher random per-assigned-life energy/vigilance expenditure. The second delayed main-push Actions #42838124872 failed *prebirth* after source was already claimed: zero additional Worlds. Scientific source 560000–560023, original executor and main launch are permanently **CLOSED_NO_RETRY**. The **independent read-only 48/48 packed and 48/48 unpacked original SHA audit PASS** on [Actions #42839406230](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42839406230), [merged PR #1275](https://github.com/josselin-orta-lab/individual-zero/pull/1275), independently reproduced the exact **20 fork/1 changed action/4 null** primary, all 24 pairs, physical costs, and secondary 12-vs-13 survival, without any new World. Both complete Python I3 suites passed. No iid ecology witness, predictive accuracy, biological causal survival mediation, confirmatory NI or Stage 2.2 GO; i3 remains unregistered.


## Stage 2.1: first real-state same-count replay-content learning fork completed (10 November 2026)

**48/48 actual funded original lives** on **24 new matched F0 G0/World/life units 540000..540023** were generated and reduced in the unique source-claimed [Actions #42819947791](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42819947791), source `24531b8a5033a2be1b738dd30734fac2f50a3a8b`. Source claim commit `92cd0964c49a99b1d00c97a77f5af72cf0b0aada` predates birth. [All original gzip lives, manifest and results](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-realstate-fork-24-development-20261110-originals/archive/i3/stage2-realstate-fork-development-2026-11-10) were preserved at evidence commit `e28211865fd1d1e17173a115e81772702fb8cef1`, original MANIFEST SHA `dddf6d3de5f2caadbdd684941bc8155a1333f428a032ce34b8dc65b7109aa753`. [Prospectively frozen results](studies/stage2-replay-gate-selected-design/REALSTATE_FORK_24_RESULTS_2026-11-10.md): **17/24 assigned pairs** had a first genuinely prepaid different-content replay at which two detached, equal-count TD updates of the *same actually learned pre-replay Mind* produced different learned-value vectors. **Seven absent forks stay null, no exclusions.** Secondary finite survival: priority **8/24**, random content **10/24** (8 both, zero priority-only, two random-only, 14 neither), actual physical cost reported by policy. The observer's work is external laboratory CPU and was never billed to the organism. The consumed 24-pair runner and trusted main-push job are now **hard-closed NO_RETRY**. The **independent read-only 48/48 packed and 48/48 unpacked original SHA audit PASS** on [Actions #42820936462](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42820936462), [merged PR #1271](https://github.com/josselin-orta-lab/individual-zero/pull/1271), reproduced the complete finite primary 17/24 plus seven nulls and secondary paired survival. Zero new Worlds were opened. No ecological iid attestation, causal biological survival mediation or Stage-2.2 scientific GO; I3 remains unregistered.


## Stage 2.1: first personally learned water/replay divergence in 24 new DEVELOPMENT pairs (10 November 2026)

[Prospectively registered new-source 24-pair observation](studies/stage2-replay-gate-selected-design/WATER_DIVERGENCE_24_RESULTS_2026-11-10.md), exact trusted merged source `2117ad76e5274d8d67b78a20200843af846febe4`, Actions [#42808996045](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42808996045): **48/48 original full lives executed, gzip sealed, G/R reduced and archived**, pre-birth source claim `3fafe7e8ea2b26f52eb016ef68557b4e69513e89`, original [evidence ref](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-water-divergence-24-20261110-originals/archive/i3/stage2-water-divergence-2026-11-10) commit `181940e18d8aaea84dfded2927dab302b2f7185b`, original manifest SHA-256 `27535f80e704d01c66a7b8d4a76b09ca78dd7ca1c086f6f0ff2f4ace96bee514`. **Primary:** 18/24 assigned matched pairs have the *first actual replay-memory selection difference* at exactly identical comprehensive pre-replay learned state and positive physically funded replay count; **16/24** later show differences in personally learned water beliefs and decisions. The remaining six no-first-difference pairs stay included; event order is **not causal mediation**. Secondary horizon-400 survival original GATE TD priority **8/24**, GATE genuinely random replay content **10/24** (7 both, 1 priority-only, 3 random-only, 13 neither), with higher total paid energy/vigilance under random. The consumed indices `510000..510023`, executor and CI trigger are **CLOSED_NO_RETRY**. Independent read-only post-archive [48-original packed/unpacked SHA, complete chronology and all paired F0 outcomes audit PASS](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42810066826), PR #1266, with no further World execution. All Python 3.11/3.12 regression suites passed. Source remained CLOSED_NO_RETRY. No iid ecology, controlled fixed replay count, scientific registration or Stage 2.2 GO.


## Stage 2.1: 48 new matched replay-content DEVELOPMENT pairs completed and original source CLOSED (10 November 2026)

**96/96 actual full funded developmental lives generated, sealed, reduced and archived once** in [Actions #42794047107](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42794047107), source `d7ea5a3be79fc7eb380aa6ce751df42474ab5ed3`; immutable-by-process [pre-birth claim](https://github.com/josselin-orta-lab/individual-zero/tree/custody/i3-content-48-development-20261110-claimed), exact original [evidence ref](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-content-48-development-20261110-originals/archive/i3/stage2-content-development-2026-11-10) commit `459d0d9f90ea8edae95881d4e3110b91a24f85f5`, original manifest SHA-256 `75d0b29136d6c872fcf379ae76498d02b7c77989c3f3e337dca42098e5d98a36`. [Full exploratory results](studies/stage2-replay-gate-selected-design/CONTENT_48_EXPLORATORY_RESULTS_2026-11-10.md): TD-prioritized GATE 17/48 horizon survivors, **random-content GATE 23/48**, paired discordance **1 priority-only, 7 random-only**, observed priority−random **−12.50 percentage points**. The negative priority sign is concentrated in depletion/pulse, while stable is neutral. Random-content costs more paid energy/vigilance per assigned life. Both use the identical GATE count **rule**, not identical endogenously realized replay numbers. The consumed 480000..480047 source/executor and main-push trigger are **hard-disabled NO_RETRY**. The separate **independent read-only** original audit [PR #1262 / Actions #42794879073](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42794879073) has since verified **96/96 packed and 96/96 unpacked original SHA-256s**, original-to-reduced costs and all adverse paired/F0 outcomes without a new World. Post-hoc review finds all seven priority deaths in random-content-only survivor pairs were `zero_water`, but selection on survival and lack of full step traces prevent causal attribution. Next: prospectively observe water-relevant memory/belief/decision divergence in entirely new Worlds without prescribing actions; see [issue #1258](https://github.com/josselin-orta-lab/individual-zero/issues/1258). No iid ecology, causal fixed-count, selected evolution, NI, reserve or scientific GO follows. I3 remains unregistered and Stage 2.2 blocked.


## Stage 2.1: replay memory-content local mechanism falsifier (10 November 2026)

The fully independent 192/192 historical three-arm gzip original audit is source-verified in [PR #1255](https://github.com/josselin-orta-lab/individual-zero/pull/1255). RANDOM-EQUAL-MEAN randomized replay **count**, not which memory was replayed: both original GATE/RANDOM used TD-priority. To isolate *memory content*, a separate [predeclared synthetic 48-Mind local test](studies/stage2-replay-gate-selected-design/CONTENT_SELECTION_LOCAL_FALSIFIER.md) executed 3 identical P1.3 TD memory updates on two detached copies at identical prepaid model counts. [Observed local results](studies/stage2-replay-gate-selected-design/CONTENT_SELECTION_LOCAL_RESULTS_2026-11-10.md): random-content and priority selected different memory subsets in **48/48** synthetic snapshots; learned values differed in **47/48**; modeled physical debit per arm **0.131 energy and 0.176 vigilance** in each case. It never instantiated a World or applied the debit physically. This demonstrates a local learned-state difference, **NOT** improved survival, selection fitness, ecological transfer or a scientific GO. [Future independent mechanism design issue #1258](https://github.com/josselin-orta-lab/individual-zero/issues/1258) is the next governance and experimentation dependency. I3 is unregistered at Stage 2.1; no closed cohort is reopened.


## Three-arm original audit and actual RANDOM-count semantics (10 November 2026)

The completed 64-triplet panel remains **CLOSED_NO_RETRY** with GATE versus RANDOM 27/64 versus 27/64 survivors (4 versus 4 exclusive). New [read-only original SHA audit and random-control methodological note](studies/stage2-replay-gate-selected-design/RANDOM_CONTROL_SEMANTICS_AND_NEXT_FALSIFIER_2026-11-10.md): RANDOM-EQUAL-MEAN changes the **nominal replay count (6 or 7)**, not the **TD-prioritized selection of which memories are replayed**. The existing `Mind.learn_from_outcome` still selects the highest-magnitude TD errors for GATE and RANDOM. This full-life comparison therefore **cannot** falsify whether TD-prioritized memory *content* selection is superior to randomized content selection. It also does not guarantee realized paid replay equality. A separate pure [post-archive 192-original auditor](../lab/stage2_three_arm_original_audit.py) and PR-only CI are the next custody check; no World, life or source authority is reopened. Next falsifier is a local same-state, same-count, physically paid prioritized-vs-random-*content* update probe, followed by a separately designed prospective full-life study only if justified. Stage 2.1 remains unregistered, exploratory, without NI/causal GO.


## Stage 2.1 three-arm 64-unit exploratory DEVELOPMENT complete, original source exhausted (10 November 2026)

**192/192 real FIXED/GATE/paid-RANDOM lives generated, original SHA-verified and reduced. PRIMARY GATE−RANDOM horizon survival difference = 0/64, not superiority or equivalence.** The [prospectively frozen, source-bound results](studies/stage2-replay-gate-selected-design/THREE_ARM_EXPLORATORY_RESULTS_2026-11-10.md) show FIXED 26/64, GATE 27/64, RANDOM 27/64 horizon survivors; GATE-only versus RANDOM-only **4 versus 4**, with longer average GATE life (+11.53125 steps) but higher mean energy and vigilance actually paid per assigned life than RANDOM. Depletion shows an adverse GATE−RANDOM survival sign (−2/16) that must not be excluded.

The original single-exposure main source `11879c46a78697aa1d3f664f1a17f489a948667d` ran in [Actions #42781264127](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42781264127) after permanent [pre-birth claim](https://github.com/josselin-orta-lab/individual-zero/tree/custody/i3-three-arm-development-64-20261110-claimed), exact claim commit `9090db869d8501a0030b49c700d9d1c7357d44e4`. All 192 unmodified original gzip lives, SHA manifest, reduced rows and full report are preserved on independent [evidence branch](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-three-arm-development-64-20261110-originals/archive/i3/stage2-three-arm-development-2026-11-10), commit `aaff20234b8a4f9d11595d6eb852371d0ce00f97`. Manifest SHA-256 `f493a30598c3dd82f56ab84653537286487bea61414cfc2226785209c724a50f`.

**CLOSED_NO_RETRY**: the scientific DEVELOPMENT 360000–360063 executor and its once-only workflow are hard-disabled after this exposure; old B1/80/81 remain closed. This is exploratory, not an iid source attestation, a causal replay-selection effect, non-inferiority, selected evolution, new reserve permission, Stage 2.2 or active I3 engine. Next intervention: full post-archive read-only 192-original verification and independent review of actual replay/cost matching versus nominal schedules before considering any new cohort.


## Stage 2.1 three-arm funded engineering completed (10 November 2026)

**144 real technical lives, 72 per Python version, 24 unused PUBLIC-synthetic F0 matched world/genome/life units, FIXED/GATE/paid-RANDOM.** [Exact source-bound G/R witness](studies/stage2-replay-gate-selected-design/THREE_ARM_ENGINEERING_WITNESS_2026-11-10.md): Actions #42779253162, PR #1251 merged as `6000ff97a974ba9fa18c062c56b1b0f18f50f2f6`, G/R **72/72 + 72/72 PASS**, zero failures across 22 structural invariant categories. Physical RANDOM nominal/eligible/paid replay counts were verified for funding, not assumed equal to GATE. Original technical lives were temporary and never disclosed for survival inference. This is **engineering only**, not scientific GO. Next: prospective exact-source three-policy matched DEVELOPMENT on new units, with preserved full original evidence, standalone no-retry claim and source authorization; iid, non-inferiority and I3 promotion remain blocked.


## B1 original evidence permanently archived and independently recounted (10 November 2026)

The already executed **192/192 B1 DEVELOPMENT original lives** are now preserved on independent GitHub evidence ref `evidence/i3-b1-96pair-development-20261110-originals`, exact commit `50380d16b0b6e7ac1e91702060be83784ba85cc7`, with unchanged ZIP SHA-256 `2aff70fff077be04042379355cda8c798ed9ec81745413563bc88e4320615361`, source/plan/manifest pins and original verification receipt (Actions run [#42775154043](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42775154043), archival job PASS). See [archival plan](studies/stage2-replay-gate-selected-design/B1_ORIGINAL_ARCHIVE_CUSTODY.md) and [finite post-hoc survival-cost decomposition](studies/stage2-replay-gate-selected-design/B1_POSTHOC_SURVIVAL_COST_DECOMPOSITION_2026-11-10.md). The GitHub Actions 90-day artifact is no longer the only copy; the evidence branch must remain protected from deletion. All B1 scientific source permissions remain **spent, NO_RETRY**.

Post-hoc original-only analysis shows that total GATE physical vigilance paid per life *increased* despite fewer executed replays and modestly lower energy per life. One GATE death occurred at step 400, not a horizon survivor. This is **not** a causal replay selection finding, an iid sampling attestation, or a biological NI GO. Next Stage-2.1 choice: prospectively freeze a 3-arm FIXED/GATE/paid-RANDOM mechanism-first matched design with independent study review and new unspent indices before any new World. I3 remains an unregistered proposal; Stage-2.2, selection/validation/reserve remain blocked.


## B1 new-world 96-pair exploratory DEVELOPMENT completed and closed (10 November 2026)

**192/192 real developmental lives generated, sealed, reduced on GitHub Actions #42735037051; the spent B1 runner is now closed NO_RETRY.** The [source-bound results](studies/stage2-replay-gate-selected-design/B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md) show 38/96 horizon survivors under GATE versus 30/96 FIXED, 13 GATE-only versus five FIXED-only, observed +8.3333 percentage-point paired survival difference and +27.2396 mean lived steps. Paid energy per assigned life was 133.1013 GATE versus 137.4370 FIXED; paid vigilance was **higher** with GATE (171.6070 versus 167.5939). Adverse family-specific and historical 80/81 results remain visible.

This is **development-only exploratory evidence**: no independent external iid source witness, no approved survival-loss margin, no confirmatory inference, no held-out selection/validation or reserve, and no I3 activation. Original sealed histories are currently in [Actions artifact #13725454291](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42735037051/artifacts/13725454291), which expires **8 February 2027**: permanent original custody is the next urgent research task. The exact execution head was `713d4621d28ed668bf5f5a37f2d105a38d19fb57`; the closed runner must never regenerate these 96 pairs. This result does not change the historical `REPLAY_GATE_CAPACITY_SHOWN` stage status or authorize Stage 2.2.


**PROPOSAL. UNREGISTERED. NO ACTIVE ENGINE ENTRYPOINT. NO GENERAL SCIENTIFIC GO.**
I1 remains the active engine. Authority: [engine contract](../engine.json),
[registry](../../../config/engine-registry.json),
[ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md).

Historical 6 November 2026 scenario-integration baseline:
[#1059](https://github.com/josselin-orta-lab/individual-zero/issues/1059).
Current governance and Stage-2.1 status are recorded below (9 November 2026).
Evidence baseline: `e4eb3e80c9dc48e131e05383d952909bd86213b7` (PR #1058).
That integration changed documentation and priorities only. The subsequent
Stage-0 slices add laboratory metadata/arithmetic and read-only funding/revision
receipts, not cognition or physics; no validation/reserve world or scientific-study life.


## Stage 2.1 B1 new-world paired G/R witness integrated (10 November 2026)

**192/192 ENGINEERING ORIGINALS SEALED AND REDUCED IN PYTHON 3.11 AND 3.12;
NO BIOLOGICAL SURVIVAL VERDICT.** The
[B1 96-pair result witness](studies/stage2-replay-gate-selected-design/B1_NEW_WORLD_GR_WITNESS_2026-11-10.md)
records exact-head Actions `42718347325`, final tested source
`7a4dc7e56aa64582edc72f58f895dc36a00017e0`,
source-content fingerprint
`6eb22c4d088084ca8751ba95b992c7b229da018523dc520b277d7a75e379bf9c`,
7 applicable CI successes, and zero failures across 14 structural
invariant categories. It also records the rejected local-ticket
minting attempt and correction by the sole central source guard.
This cohort used the fixed first 96 PUBLIC synthetic new-F0
units and must NEVER become scientific inference evidence.

## Stage 2.1 B1 new-world full-policy engineering G/R campaign (10 November 2026)

**96 PUBLIC-SYNTHETIC PAIRS / 192 REAL TECHNICAL LIVES / NO SCIENTIFIC
SURVIVAL CLAIM.** The [prospective-type WorldSpec paired G/R protocol](studies/stage2-replay-gate-selected-design/B1_NEW_WORLDS_PAIRED_GR.md)
uses the first 96 frozen PUBLIC synthetic B1 allocation rows on the
new high-range stable/depletion/pulse WorldSpec builder, same world,
genome and life seed per FIXED/GATE pair. It executes actual funded
policies in temporary G/R originals and verifies paid cognition,
admission bound to exact physical World, source fingerprint,
horizon, identity and no-shortfall, exposing only structural CI
receipt/digests. The historical Stage-2.1 science executor
still rejects all scientific calls. Even a complete PASS is
**engineering-only**, not a valid survival inferential sample;
independent review, scientific source witness, margin/estimand,
fixed n, full-scale rehearsal and new owner lift still block B1
science.

## Stage 2.1 B1 synthetic WorldSpec parity and collision audit (9 November 2026)

**NON-EVIDENTIARY SPEC-GENERATION CHECK / NO SCIENTIFIC LIFE.**
The [F0 WorldSpec preflight](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_WORLDSPEC_PREFLIGHT.md)
builds and structurally validates the 1,500 proposed **synthetic**
WorldSpecs via explicit non-development generator calls, preserving
P2 stable/depletion/pulse mechanics and comparing canonical fingerprints
to historical non-reserve P2 generation. It checks unique **full and
name-independent** initial ecology SHA-256s, not unique names alone.
Structural validation briefly constructs a World validator, but
no individual, step, motor choice or survival result is produced.
No source authority, iid ecology proof, new cohort or GO follows.
The historical P2 API, reserved seeds and old 80/81 archive remain
unchanged.

## Stage 2.1 B1 prospective sample-frame preflight (9 November 2026)

**SOURCE-LOCK CANDIDATE METADATA / NO SCIENTIFIC WORLD.**
The [B1 independent-pair preflight](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_SAMPLING_PREFLIGHT.md)
proposes a deterministic, domain-separated and collision-checked
**1,500-pair (3,000 potential lives)** metadata schedule covering
three known F0 ecologies with equal *sampling probability*, not
post-hoc forced equal counts. A public **synthetic preview** key
reproduces the schedule; no WorldSpec, genotype object or life
is constructed. New world/genome/life namespaces are disjoint from
P2/historical/engineering/reserve. **Unique PRF seeds DO NOT
prove iid ecological independence**, and the P2 generator's default
development-mode guard rejects future seeds above one million.
A separately reviewed prospective World adapter and independently
witnessed source/entropy, acceptable NI margin, sample size, full-scale
G/R and owner-scoped permission remain prerequisites.
No scientific admission, survivor, superiority or Stage-2.2 promotion.

## Stage 2.1 B1 engineering execution witness (9 November 2026)

**24/24 structural PASS on Python 3.11 and 3.12; NO SCIENTIFIC WORLD OPENED.**
The [read-only engineering witness](studies/stage2-replay-gate-selected-design/B1_ENGINEERING_WITNESS_2026-11-09.md)
records the first 21/24 fail-closed attempt, the prospective optional
post-decision audit motor-reserve correction, and the second 24/24 sealed
G/R PASS using unchanged engineering seeds. Source-content fingerprint
`5528827040a39135a5e3f788eac139b06e2dbc28a2444dd5a50a47500a1a367f`,
Actions `42710443746`. Ten engineering invariants have zero failures
in both Python jobs. Only allowlisted structural receipts and pure synthetic
power scenarios were published. This is NOT the full-scale rehearsal,
independent scientific review, new owner-scoped lift or proof of
survival non-inferiority.

## Stage 2.1 B1 engineering motor-audit funding correction (9 November 2026)

**SOURCE REVISION IN REVIEW; NOT A RETROACTIVE EQUIVALENCE CLAIM.**
The first B1 engineering-only smoke FAIL-closed at 21/24 generated
lives with `unfunded or unknown motor command` in a GATE case.
The optional residual-audit cycle could consume the energy already
reserved by P1.3 Action Control for the chosen motor action.
The prospective source now skips only that **optional** audit if
its exact cumulative debit would invalidate the previously admitted
motor command. GATE formula, chosen action, P1.3 competition,
cognitive tariffs and body physics remain unchanged, but the number
of future paid audits can change, requiring a **new** exact-source
rehearsal and research review. No world from the earlier frozen
DEVELOPMENT 80/81 pilot was reopened or reinterpreted.
[Failure and correction](studies/stage2-replay-gate-selected-design/SURVIVAL_B1_LAUNCH.md).

## Stage 2.1 autonomous survival campaign B1 (9 November 2026)

**COMPUTATIONAL SURVIVAL STUDY + LIVE ENGINEERING SMOKE LAUNCHED;
SCIENTIFIC WORLD AUTHORIZATION BLOCKED.** The
[autonomous B1 launch contract](studies/stage2-replay-gate-selected-design/SURVIVAL_B1_LAUNCH.md)
selects a known-F0-only matched newborn G0/world survival target
and implements a conditional exact Clopper-Pearson/Bonferroni
**one-sided finite-sample lower risk-difference bound** for iid paired
units, along with fixed-seed conditional power simulations. A dedicated
GitHub Actions workflow runs the actual existing G/R transport with
**24 temporary, non-evidentiary engineering lives** only, on Python
3.11 and 3.12; the plan has **no scientific indices** and the old
runner continues to reject every science cohort. The engineering
structural report publishes no mortality, behavior or cognitive
outcomes. Passing a smoke test cannot replace the future full-scale
exact-transport rehearsal, sampling review or owner/source authorization.
No new scientific lives or Stage-2.2 GO are claimed. I3 remains unregistered.

## Stage 2.1 confirmatory survival power study initiated (9 November 2026)

**STUDY DESIGN/POWER ANALYSIS ACTIVE; SCIENTIFIC WORLD EXECUTION BLOCKED.**
The [confirmatory survival power campaign](studies/stage2-replay-gate-selected-design/CONFIRMATORY_SURVIVAL_POWER_STUDY.md)
compares a rigorously bounded independent-paired-unit survival
non-inferiority approach with transparent hypothesis-dependent
normal-approximation sensitivity. Under illustrative one-sided
alpha=0.05, target power=0.80, margin=5 percentage points,
true mean difference zero, the conservative Hoeffding bound requires
**7,198 genuinely independent matched units** (14,396 two-arm lives);
the much smaller paired-model scenarios are **not** approved
sample sizes. The F0 8 population labels / 240 paired G0 blocks
are not demonstrably independent ecological draws and cannot
be inflated by recounting shared Worlds or genomes. An independent
reviewer must settle target sampling, meaningful margin, coverage,
ecological heterogeneity, resources and a new pre-exposure source
and owner authorization. Historical 80/81 is closed.
**No scientific lives opened, no inference GO or new adoption.**

## Stage 2.1 archived evidence analysis campaign launched (9 November 2026)

**READ-ONLY HISTORICAL ANALYSIS / NO NEW SCIENTIFIC WORLD.**
The [first analysis campaign report](studies/stage2-replay-gate-selected-design/ANALYSIS_CAMPAIGN_2026-11-09.md)
rechecks 36 archived DEVELOPMENT 80/81 original gzip lives and their
frozen full-reduction records using published SHA pins, then reports
survival, physical paid cognition **per assigned life**, paired deaths,
F0 family differences and leave-one-block/family sensitivity.
The observed GATE-minus-FIXED mean lived-time difference is -29.4167
steps, despite lower cognitive spending. Adverse effects differ by
F0 family; no causal mechanism, non-inferiority or ecological transfer
is established. A reproducible read-only reanalyst and synthetic
tamper/missingness regressions are provided.
**Internal recommendation: REVISE/NO SCIENTIFIC GO.** Next is a genuinely
independent prospective review of mechanism-first v3 versus a powered
survival study. No new cohorts or old index reuse are authorized.

## Stage 2.1 complete three-policy accounting (9 November 2026)

**SOFTWARE ONLY / NO NEW WORLD.** The existing v3 paired reader now
reports [RANDOM versus FIXED](studies/stage2-replay-gate-selected-design/PAIRED_SURVIVAL_PROFILE.md)
across the same 240 newborn-G0/world blocks, alongside GATE-FIXED and
GATE-RANDOM. The software exposes full-policy horizon discordance,
lived-time and paid cognition by population and ecological family,
and checks the arithmetic identity GATE-FIXED = GATE-RANDOM +
RANDOM-FIXED (with floating-point residuals recorded). This **cannot**
establish causal mediation, equal paid replay quantities, mean-survival
non-inferiority, owner authority, World access or engine promotion.
No new test acceptance thresholds are introduced.

## Stage 2.1 paired-survival harm profile (9 November 2026)

**SOFTWARE ONLY; NO NEW EXPOSURE.** The current v3
[matched interpretation contract](studies/stage2-replay-gate-selected-design/PAIRED_SURVIVAL_PROFILE.md)
adds exact 240-block GATE-versus-FIXED and GATE-versus-RANDOM horizon
survival discordances, lived-step direction and worst adverse delta,
death on step 400, plus lower paid cognition coexisting with shorter
life. The same counts remain visible per F0 family and population.
This prevents a zero mean contrast from hiding opposite deaths in
different ecologies. The existing sealed-reader gains these finite
descriptions without any World or Mind change. No statistical inference,
non-inferiority verdict, source permission or engine promotion follows.

## Stage 2.1 paid replay exposure audit (9 November 2026)

**SOFTWARE ONLY; NO NEW WORLD.** The [v3 original readout](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_SEALED_READOUT.md)
also reports funded decision-audit counts, reached and funded sleep,
physically paid replay counts, and RANDOM nominal/eligible/paid gaps by
arm, population and family. The frozen RANDOM nominal 5532/867 mean
does **not** establish equal actual replay work in v3; even perfect
physical parity is not proof of a causal replay-choice advantage.
This is descriptive, not a gate, source authorization, non-inferiority
test or reason to select or rerun lives.

## Stage 2.1 mechanism-first v3 sealed original reader (9 November 2026)

**SOFTWARE-ONLY; NO SCIENTIFIC WORLD.** The separate
[v3 sealed-readout contract](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_SEALED_READOUT.md)
matches exactly 720 original FIXED/GATE/RANDOM lives to the 240 paired
newborn-G0 blocks and F0 validation metadata, with an independently named
v3 lock schema. It reuses the corrected original run_life checks,
source/plan/manifest pins, funded cognition, and RANDOM physical replay
receipts. The original 5,040-life selected-pipeline reader and
historical 80/81 closure remain unchanged. A caller-supplied SHA is
NOT independent provenance or owner authority. The result is descriptive
only, with no survival non-inferiority verdict or World opening.

## Stage 2.1 exact original-life runtime contract repaired (9 November 2026)

**SOFTWARE-ONLY; NO SCIENTIFIC WORLD.** A follow-up to the sealed
selection bridge corrects its mismatch to actual `run_life`:
P1.3 `reference` has no replay admission, whereas GATE/RANDOM/
ZERO use the top-level `admission` receipt, with matching manifest
metadata and World-bound identity. Additional fail-closed checks now
compare original manifest, source, world and newborn G0 digests,
declared physically paid cognition and replay mode. See
[the corrected bridge contract](studies/stage2-replay-gate-selected-design/SEALED_SELECTION_BRIDGE.md).
External signed/pre-exposure source provenance remains unauthenticated,
and Stage 2.1's statistical NO_GO remains in effect.

## Stage 2.1 mechanism-first alternative proposed (9 November 2026)

**SOFTWARE ONLY / NO SCIENTIFIC EXPOSURE.** A separate
[fixed-newborn-G0 paired candidate v3](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_CANDIDATE_V3.md)
offers a smaller question: fixed birth genomes under the same worlds and
life seeds with FIXED/GATE/RANDOM, no genetic selection. Its pure
`lab/stage2_mechanism_first_design.py` layout specifies 720 proposed lives
(288,000 maximum steps) versus 5,040 in the earlier selected-pipeline
design. It does not test evolutionary selection or justify a mean survival
non-inferiority claim; scientific power, population independence and
margin remain unresolved. No F0 World index is approved or opened and
no old lift is reused. External methodological review and explicit owner
decision must precede any new scientific protocol.

## Stage 2.1 original-custody bridge proposal (9 November 2026)

**SOFTWARE-ONLY / NO NEW SCIENTIFIC OPENING.**
The [sealed selection-to-validation bridge](studies/stage2-replay-gate-selected-design/SEALED_SELECTION_BRIDGE.md)
checks complete original selection archives (3,840 expected lives), rebuilds
the five selected founders per architecture and population using the existing
persistence-only rank rule, then validates the exact 1,200-cell original
validation panel before descriptive reduction. It requires caller-supplied
source/plan/transport/manifest SHA pins, compares original World/genome
digests and funded cognitive settlement, and fails closed on mismatches.
It does NOT attest the provenance or pre-exposure authority of those pins,
grant permission, establish independent population sampling or change the
eight-population mean non-inferiority NO_GO. It never executes Worlds.

## Stage 2.1 finite-panel readout candidate (9 November 2026)

**SOFTWARE-ONLY, NO NEW SCIENTIFIC EXPOSURE.** The
[finite-panel receipt contract](studies/stage2-replay-gate-selected-design/FINITE_PANEL_RECEIPTS.md)
and `lab/stage2_finite_panel.py` now describe the complete candidate
1,200-cell validation panel by selected-founder ID, paired F0 world,
condition, death/censoring, actually paid energy/vigilance and replay
opportunity. Missing, duplicate or foreign reduced receipts fail
closed; the readout remains descriptive and cannot attest original
G/R custody, correctly selected founder ranking, ecological
independence or a scientific non-inferiority verdict.
The previous eight-population mean non-inferiority NO_GO and
unregistered I3 status are unchanged. No World opening or stage
promotion is authorized.

## Stage 2.1 selected-gate inferential revision proposed (9 November 2026)

**SOFTWARE-ONLY / NO_GO FOR CURRENT EIGHT-POPULATION MEAN NON-INFERIORITY.**
After the [inferential defect audit](studies/stage2-replay-gate-selected-design/INFERENCE_POWER_AUDIT.md),
the separate [v2 revision candidate](studies/stage2-replay-gate-selected-design/PROTOCOL_REVISION_V2.md)
specifies the target as equal-weight mean fixed-horizon survival contrast of
independently selected GATE and FIXED populations. Its deterministic
[bounded mean-survival sensitivity](../lab/stage2_mean_survival_sensitivity.py)
uses a conditional Hoeffding bound, not a scientific verdict: for eight
independent [-1,+1] population contrasts the alpha=0.05 radius is ~0.8654.
Consequently the original seven-of-eight sign rule cannot establish mean
survival non-inferiority, and the conservative alternative is too imprecise
for the proposed 5-point margin at realistic effects. Margin, independence,
sampling distribution, method and power require independent review and owner
arbitration; do not automatically create larger cohorts. This does not close
Stage 2.1 scientifically, alter its replay gate, or authorize any World.
The old 80/81 one-shot permission stays exhausted, P1.3 reference and I3
unregistered.

## Stage 2.1 continuation: opt-in funded RANDOM control (software only)

**9 November 2026, prospective engineering branch, no new scientific World.**
The development-only frozen mean 5532/867 now supplies an independently
seeded RANDOM-EQUAL-MEAN replay-count control (6 with 179/289 or 7 with
110/289 probability). The opt-in `p13_replay_gate_random_equal_mean_v1`
Mind is prepaid for its real decision audit, gate forecasts and replays;
it does not borrow hidden World knowledge or change P1.3 motor authority.
A separately counted executed-sleep ordinal prevents unfunded sleeps from
silently shifting later random draws. Software tests and engineering-only
rehearsals, not fresh selection/validation lives, cover this intervention.

**Operational hard stop:** the historical DEVELOPMENT 80/81 authorization is
consumed, and the retained `stage2_panel.execute()` / scientific admission
routes now **raise before constructing any scientific World**, irrespective
of the old ADR-0017 lift line. The historic source-locked evidence and owner
decision remain unchanged. The current source fingerprint differs from the
historical `dcada9e2…f1`; no new owner lift or scientific cohort is implied.

The [selected-gate design candidate](studies/stage2-replay-gate-selected-design/PROTOCOL.md)
is explicitly **not yet preregistered or owner-approved**: proposed margins,
power, uncertainty, full paid control/selection and a new irreversible,
index-scoped transport claim still require independent review and a new
prospective permission. P1.3 funded-v2 remains the reference, I3 unregistered,
and Stage 2.1 has no survival non-inferiority verdict.


## Stage 2.1 DEVELOPMENT 80/81: FIRST PROSPECTIVE EXPOSURE COMPLETE

**9 November 2026. DEVELOPMENT_COMPLETE_ENGINEERING_CONTINUATION_PASS.**
The owner-lifted, formerly unopened Stage-2.1 DEVELOPMENT indices
**80/81 were each used exactly once** in run
[42641395586](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42641395586).
The irreversible [claim branch](https://github.com/josselin-orta-lab/individual-zero/tree/custody/i3-stage2-1-development-80-81-claimed)
was created before any World. Executed source SHA
`5d362e226f8e87df226dae5b239e26cc99072a13`, fingerprint
`dcada9e2…f1`. **Phase G 36/36, phase R 36/36, zero failures on
ten structural invariants.** All 36 original gzip life records and complete
manifest are preserved on immutable [evidence commit
`5a13efc5`](https://github.com/josselin-orta-lab/individual-zero/commit/5a13efc53dafc10e9b9248479a4756eda6a55eeb).
Manifest SHA-256 `c6893bb1b2457890e3d66680f10bf0c14b451e62c2e5c381951f1119f286b76e`;
full result SHA-256 `a6652f4d8cd1f8ccb87d8bf902ecb2eabf68ec0a548b187db140ea61dfc9401b`.

**Descriptive DEVELOPMENT results, not a gate verdict:** GATE replayed
6.380623 memories/sleep versus FIXED 15.997053 and ZERO-PERCEIVED-COST
12.623037. Pooled paid cognitive energy/lived step was 0.469401 for GATE
versus 0.555897 for FIXED; vigilance 0.599448 versus 0.674306. Mean life
length was **262.17 steps for GATE, 291.58 for FIXED**, with 3/12 versus
4/12 censored at the 400-step horizon. GATE was longer than FIXED in
3/12 matched blocks, shorter in 3/12, equal in 6/12. A `stable-81-g911`
block was 300 steps shorter under GATE. **Survival non-inferiority has NOT
been demonstrated; no architecture is adopted from this pilot.**

The predeclared RANDOM-EQUAL-MEAN parameter is now **frozen** from
DEVELOPMENT only: **5,532 GATE replays / 867 sleep steps =
6.380622837370242**. See
[prospective results](studies/stage2-replay-gate-development-80-81/RESULTS.md)
and [control-parameter custody](studies/stage2-replay-gate-development-80-81/RANDOM_EQUAL_MEAN_PARAMETER.md).

**Development indices 80/81 are permanently closed and shall not be
rerun.** ADR-0017's owner lift remains historically valid, but its
**single authorized scientific exposure has been consumed**.
No additional development, selection, validation or reserve World is
currently authorized. Next is software-only preregistration of the
RANDOM-EQUAL-MEAN distribution and ≥8-population ADR-0015 Stage-2.1 gate,
including frozen margins, uncertainty, seeds and held-out allocation,
followed by separate approval and exact-transport custody as required.
I3 remains unregistered and P1.3 is the reference.

## Owner decision: ADR-0017 LIFTED for the exact Stage-2.1 transport (9 November 2026)

**Explicit owner validation received after the technical audit.** The owner
accepted both documented governance equivalences: declaring the disjoint,
permanently non-evidentiary `engineering` cohort beside the immutable
`P2.COHORTS`, and using the verified byte-for-byte identity of all 42
transport/plan files across the rehearsals and squash-merged `main`
as exact-transport continuity despite distinct Git commit SHAs.

ADR-0017 OWNER LIFT: Stage-2.1 transport dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1

**Four conditions satisfied:**

1. Same source-locked two-phase G/R generation and reduction, tested.
2. Disjoint `engineering` cohort, with the explicit owner-approved placement
   exception above; engineering originals never become scientific evidence.
3. Full-size sealed transport rehearsal PASS on Python 3.11 (run
   `42628475893`) and Python 3.12 (run `42629796562`): 36/36 generated
   and reduced on each, zero failures across ten structural invariants,
   exact fingerprint `dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1`. All 42 tracked transport/plan
   Git blobs were identical at merged commit `6d072c1c`.
4. Explicit owner approval and this canonical STATUS ledger entry.

**Narrow next authorization:** exactly one *prospective* DEVELOPMENT 80/81
pilot under the already frozen
[Stage-2.1 protocol](studies/stage2-replay-gate-development-80-81/PROTOCOL.md):
3 families × 2 indices × 2 genomes × FIXED/GATE/ZERO-PERCEIVED-COST,
36 planned lives, horizon 400, original archival G followed by R.
The pilot continues for engineering feasibility only and measures the
replay rate needed for the prospectively specified RANDOM-EQUAL-MEAN control.
It is **not** a confirmatory Stage-2.1 gate, not permission to inspect reserve,
not a general scientific GO, and does not register I3 as the active engine.
Validation, selection, reserve, other World indices and Stage 2.2 require
separate prospective authorization. Panels 58/59 through 68/69 remain closed.

At this owner-lift decision, no new scientific World has yet been opened.
Any transport-code or frozen-plan edit invalidates the rehearsed fingerprint
and requires renewed custody and owner authorization. Generation failure
prohibits retry. Reduction defects follow ADR-0017's blind repair rules on
immutable original bytes, with no partial-result reading.

Older sections below stating that ADR-0017 was still active are **historical
pre-lift custody**. This new explicit owner decision supersedes them for
current operations; their evidence remains unchanged.

## Stage 2.1 hardened exact transport: technical rehearsal PASS, owner lift pending

9 November 2026: PR #1220 imported the prospective 80/81 transport bundle
with its original three-commit history. Admission review revealed two
engineering-custody weaknesses (caller-selected owner STATUS, tickets bound
only to a World name). Both were repaired **before a new sealed rehearsal**.

The hardened full-scale engineering rehearsal on source
`75a4f325eb5c73c3c14d9f0dcdf313f651061fc0`, fingerprint
`dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1`,
**PASSED**: 36/36 lives generated, 36/36 reduced, 0 failures across 10
structural invariants and 0.816 ms per step. The same full-size sealed
engineering matrix **also PASSED on Python 3.12** (Actions `42629796562`):
36/36 G, 36/36 R, 0 invariant failures, same fingerprint, 1.244 ms per step. Source: [hardened rehearsal](studies/stage2-replay-gate-development-80-81/HARDENED_REHEARSAL.md).

The previous fingerprint `15136d13…d967f9` is superseded, **not** eligible
for a future lift. Confirm that merged source bytes retain the hardened
fingerprint before using the rehearsal as exact-transport custody.

ADR-0017 conditions: two-phase G/R met; disjoint non-evidentiary engineering
cohort met (declared alongside, not inside the pinned `P2.COHORTS`);
full-scale sealed rehearsal met on the stated source; **owner's explicit lift
entry NOT RECORDED**.

**ADR-0017 REMAINS ACTIVE. No scientific World, including DEVELOPMENT 80/81,
may open.** The engineering result is not a survival, learning, replay or
validation verdict.

## Stage 2.1 exact transport: sealed engineering rehearsal PASS (awaiting owner decision)

The exact Stage-2.1 transport required by ADR-0019 is implemented and rehearsed:

- **Runtime dispatch.** `p13_replay_gate_v1` and its zero-perceived-cost control
  run only with a guard-minted admission ticket bound to the exact World,
  verified before the World is built.
- **Fail-closed admission.** The guard admits only the engineering cohort.
  Development, selection, validation and reserve raise before any World exists.
- **One runner.** A single parameterized panel runner serves both the rehearsal
  and the later pilot.
- **Fresh plan.** Development pilot 80/81 was frozen first, after a collision
  search: [plan](studies/stage2-replay-gate-development-80-81/PROTOCOL.md).

Full-scale sealed rehearsal on transport commit `e23a28e`, fingerprint
`15136d132b5244bf511a576b44619a5f44ef945d6472324bc1102ce449d967f9`:
**PASS**. G 36/36, R 36/36, 0 failures on 10 structural invariants, 0.86 ms per
step ([rehearsal](studies/stage2-replay-gate-development-80-81/REHEARSAL.md)).

This is engineering custody only: not evidence and not a lift. **ADR-0017
remains active.** Development 80/81 stays closed until the owner records the
lift for this exact fingerprint in this file. The rehearsal record gives the
required line format. Any change to the transport requires a new rehearsal.

## Stage 2.1 transport governance: ADR-0019 owner-accepted

**Owner accepted [ADR-0019](../../../docs/decisions/ADR-0019-i3-exact-transport-rehearsal-before-lift.md) on 9 November 2026.**

The exact Stage-2.1 transport, including runtime dispatch, may now be built and
rehearsed before the ADR-0017 lift **only in the permanently non-evidentiary
engineering cohort**. Development, selection, validation and reserve remain
fail-closed. Source-identical G/R execution and an exact-SHA sealed rehearsal
are required. An engineering PASS is not a scientific verdict or an owner lift.
**ADR-0017 REMAINS ACTIVE. NO NEW SCIENTIFIC WORLD OR LIFE IS AUTHORIZED.**

## Stage 2.1 canonical software verdict: capacity shown

Canonical status code: **`REPLAY_GATE_CAPACITY_SHOWN`**.

9 November 2026: the corrected frozen-protocol R0-R4 falsifier was executed
exactly once from source
`e5d10aefea16cf4a5445b40848c2fff48b903e97`, Python 3.11, Actions run
`42599443436`. No World or life was opened.

All frozen rules PASS:

- R0: 0 decision, work, renaming or import-boundary failures;
- R1: forced-open identity with FIXED, 0 mismatches;
- R2: S0 replays 0/16, while every required high-E/V S1 state replays 16;
- R3: 84/84 ordered pairs pass the frozen monotonic rule;
- R4: 0 audit or gate overhead violations.

Machine result SHA-256:
`96e4ab5215e1f1eed4c5ef6d43b1d9e716c4629c4ef1dfcaecafd7642097ca61`.
See [canonical result](studies/stage2-replay-gate-software/RESULTS.md).

**Boundary:** R3 is formally green but non-discriminating: S1 replays the full
16-memory batch at every tested body. This is recorded, not repaired post hoc.
Software capacity therefore does not demonstrate lived replay reduction,
active cost-awareness or survival non-inferiority.

Stage 2.1 remains current. Its frozen protocol now proceeds to the lived path
**only after ADR-0017 is validly lifted**. Supplied 68/69 remains descriptive
and cannot be retroactively promoted or reused. The next work is to prepare a
fresh source-locked Stage-2.1 transport and pass the required exact-SHA sealed
engineering rehearsal. ADR-0017 remains active; no new **scientific** World is
authorized. Under accepted ADR-0019, pre-lift engineering-only rehearsal is
permitted behind a fail-closed scientific cohort admission guard.

## Stage 2 launched: decide how much to think (#1062)

9 November 2026: [launch document](STAGE2_LAUNCH.md). Reference: P1.3. No World,
no life, no runtime change. The owner-approved first slice,
[2.1 replay gate](STAGE2_REPLAY_GATE.md), remains frozen. Its corrected
software falsifier now returns **`REPLAY_GATE_CAPACITY_SHOWN`**; lived evidence
still waits for the ADR-0017 lift.

Pre-design measurements, disclosed but not scientific results:

- P1.3 spends about 30% of its paid energy and 27% of its vigilance on sleep
  replay, whose persistent effect showed no measured benefit in P5a;
- decision cycles take about one third of its vigilance, and simulation about
  30% of its energy;
- P1.3's cheap projection selected the same top option as the per-step Decimal
  oracle in 126/126 probed states, so precision-on-demand is deferred.

Stage 2 proceeds in this order:

1. **2.1 replay gate**: software capacity shown; next complete ADR-0017 engineering/lift custody, then a fresh prospective lived path;
2. **2.2 deliberation ceiling**;
3. **2.3 simulation depth**;
4. precision-on-demand remains deferred on the current P1.3 evidence.

No lived Stage-2 arm may run while ADR-0017 is active. The parallel engineering
track remains mandatory: two-phase G/R, disjoint non-evidentiary engineering
cohort, parameterized runner, exact-SHA sealed rehearsal, then explicit owner
lift in this status ledger.

## Stage 1 closed negative: Candidate-J software falsifier DEFECT (ADR-0018)

9 November 2026: the single execution of the frozen
[Candidate-J software falsifier](studies/stage1-candidate-j-software-falsifier/RESULTS.md)
returns **`CANDIDATE_J_DEFECT`**.

J0 fails for both declared projectors against the #1155 per-step Decimal oracle
(12,960 option scores, 2,088 decisive states):

- `event_quadratic`: max value error 0.0555 and 48 top mismatches;
- `event_local_quadratic4`: decision-equivalent on the decisive states, but
  max value error 0.0178, above the frozen 0.01 tolerance.

J1-J4 were not evaluated. First-contact capacity remains unobserved.

Under ADR-0018 decisions 4 and 5, **Stage 1 is closed negative**:

- **P1.3 remains the reference.** Its curiosity is recognized as an innate
  disposition with designer form and heritable weight `beta_u` (option B).
- **No Stage-1 candidate follows.**
- **Stage 2 is unblocked on P1.3.**

Changing the J0 tolerance or projector after this verdict would be a post-hoc
rescue and is excluded. ADR-0017 still governs every lived panel. Any lower
dated Stage-1 section that says Stage 2 is blocked is a historical ledger entry
and is superseded by this closure.

## World-opening moratorium: ADR-0017

9 November 2026: the owner accepted
[ADR-0017](../../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md)
after five consecutive DEVELOPMENT pilots, 58/59 through 66/67, opened and
closed on engineering defects without an H1-H6 or J1-J7 verdict. Three stops
occurred during reduction after a complete original had already been archived.
This is recorded as **DRIFT DETECTED** in the execution method, not as a
scientific result about Candidate-H or Candidate-I.

**Effective at ADR-0017 merge: no new I3 World index may open in development,
selection, validation or reserve.** Software-only work, read-only analysis of
already-archived originals under existing boundaries, and sealed engineering
rehearsals remain allowed. The already-frozen lifecycle-custody stress v3 W0-W9
is therefore still admissible because it opens no World.

The moratorium can be lifted only after all four conditions hold:

1. living-panel execution is split into generation (G) and reduction (R);
2. a disjoint, permanently non-evidentiary `engineering` cohort exists;
3. the exact SHA of the next intended transport passes a full-scale sealed
   rehearsal through the same G/R pipeline;
4. the owner records the lift in this file.

Reduction defects after a complete sealed generation no longer authorize new
lives. They enter `REDUCTION_DEFECT_PENDING_REPAIR`, allow at most two blind
reducer-repair cycles against immutable originals, and never permit changes to
scientific rules, thresholds, arms, seeds or original bytes.

58/59, 60/61, 62/63, 64/65 and 66/67 remain permanently closed and are not
retroactively completed.


## Historical Stage-1 closure arbitration: ADR-0018 and Candidate-J

**Historical pre-execution record. Superseded by the final closure above.**

9 November 2026: the owner accepted
[ADR-0018](../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md).
[Candidate-J](STAGE1_CANDIDATE_J.md) is now the **last allowed Stage-1
candidate** and its protocol is prospectively frozen before implementation.

Candidate-J is intentionally different from Candidate-I:

- no designer curiosity/relevance/prudence addend on any route;
- one decision phase, with no detached probe, rollback or second finalizer;
- one accurate projector for every option, with a predeclared projector
  fallback if J0 fails;
- one shared first-contact prior `(omega +/- 1) * s`, with
  `s = kappa * body_capacity`;
- existing omega is unchanged; kappa is a new generic persistence-selected gene;
- after personal contact, personal effects replace the inherited prior.

The first and only currently authorized Candidate-J exposure is its **software
falsifier**. It opens no World and therefore remains compatible with ADR-0017.
Its J0/J1 defect stops, J3 capacity criterion and J4 2.5x cost wall are frozen.
Any verdict other than `CANDIDATE_J_CAPACITY_SHOWN` closes Stage 1 negatively
with P1.3 retained.

If software capacity is shown, lived 68/69 remains blocked until ADR-0017 is
explicitly lifted. After a valid lift, the declared path is one three-arm
DEVELOPMENT pilot (P1.3 / J-native / same-genome J omega=0), then the Stage-1
ADR-0015 gate on R-depletion-v1. The current detached Stage-0 design reserves
validation indices 120-167 and records known historical allocation only through
119; this ADR does not open them.

Stage 1 closes at the first of: the Stage-1 gate verdict, a non-capacity
Candidate-J software verdict, two sealed-rehearsal-validated 68/69 executions
that fail to complete, or **15 December 2026**. No Candidate-K or other new
Stage-1 architecture may follow.

Stage 2 remains blocked **until that closure event occurs**. Under ADR-0018 it
is then unblocked on whichever reference the closure selects: J after positive
closure, otherwise P1.3.

The already-frozen lifecycle-custody stress v3 W0-W9 remains admissible as
software engineering work under ADR-0017; it does not open a World or replace
Candidate-J's scientific software falsifier.

## Latest software result: shared first-contact prior shows generic capacity

8 November 2026: the prospectively frozen
[shared first-contact prior gate](studies/stage1-shared-first-contact-prior/RESULTS.md)
passes D0-D7 and returns:

`SHARED_FIRST_CONTACT_PRIOR_CAPACITY_SHOWN`.

At omega=0 the imagined K80 path remains exactly Candidate-H:
**24 RELEVANT / 56 FALLBACK**, 40 declines, mean probe work 470.05 simulated
steps/state. P80, the directly perceived first-drink path, rises from
**48/80 RELEVANT at omega=0** to **56/80 at omega=0.25/0.5** and **72/80 at
omega=1**. All Stage-A states and fallbacks are funded; renaming and shared-prior
identity controls pass.

The positive result needs a strong boundary. The newly relevant P80 states are
**not water-deficit states**. At omega=0.25/0.5 they are energy=50 and
vigilance=50; at omega=1 they are energy=20/30/40/50 and vigilance=40/50.
The generic RMS prior is therefore demonstrating an inherited
action-opportunity expectation dominated by its energy/vigilance scale, not a
water-specific instinct.

F108 carried-food relevance also rises and saturates at 108/108 by omega=0.5,
while K80 imagined relevance is non-monotone (24 at omega=0, then 12/14/12 for
positive omega 0.25/0.5/1). D7 confirms that this divergence occurs **after**
the exact shared RMS prior; the imagined and perceived decision structures
respond differently to the same inherited expectation.

This is capacity evidence only. It does not authorize runtime adoption or a
new live panel.

Both prospectively frozen software prerequisites now PASS:

- [Candidate-I shared-prior integration](studies/stage1-candidate-i-shared-prior-integration/RESULTS.md):
  `CANDIDATE_I_SHARED_PRIOR_INTEGRATION_PASS`, I0-I9 all PASS, every
  first-contact fallback funded and exactly addend-free;
- [composite-funding reducer repair](studies/stage1-composite-funding-reducer-repair/RESULTS.md):
  `COMPOSITE_FUNDING_REDUCER_REPAIR_PASS`, R0-R6 all PASS.

The first prospectively frozen runnable multi-option protocol has now failed
its mandatory S1 identity rule:
[CANDIDATE_I_RUNTIME_INTEGRATION_DEFECT](studies/stage1-candidate-i-runtime-integration/RESULTS.md).

Its proposed "with-information top set differs from without-information top
set" rule disagrees with frozen #1170 on **700/1,128** one-trial P80/F108
states: 696 false negatives and 4 false positives. Both Python 3.11 and 3.12
reproduce the same fracture. The implementation was not merged and 60/61
remain unopened.

The failure clarifies that two semantics had been conflated. #1170 direct
first contact asks whether the unknown **trial itself is strictly worth taking**
versus its own no-trial comparator and every other offered option. #1163
post-contact asks whether extra information changes the decision top. Those
questions remain distinct.

The prospectively frozen successor
[Candidate-I runnable multi-option integration v2](STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION_V2.md)
now passes S0-S11:
[CANDIDATE_I_RUNTIME_INTEGRATION_V2_PASS](studies/stage1-candidate-i-runtime-integration-v2/RESULTS.md).

Final tested source `9c5ef3e2657c1d2be1e0e8f0b592b6a957dcff6b`,
Actions `42500166929`, Python 3.11/3.12, 918 tests. The exhaustive one-trial
reduction is **0/1,128 mismatches**. Multi-trial permutation/renaming,
addend-free fallback custody, omega ablation, composite funding, post-contact
parity and already-exposed runtime smoke all pass.

Two review defects were corrected before the final verdict: the fallback
Stage-A receipt omitted already-paid base/recurrence work, and forced-failure
restoration omitted transient `_unknown`/`_presence` caches. Neither repair
changed scores, relevance, actions, omega, fixtures or V2-R1/R2.

The fresh
[Candidate-I 60/61 DEVELOPMENT protocol](studies/stage1-candidate-i-development-60-61/PROTOCOL.md)
is now prospectively frozen. It allocates 12 matched blocks / 48 lives across
stable, depletion and pulse, with four arms: P1.3, Candidate-H, Candidate-I
native omega and same-genome Candidate-I omega=0. Canonical plan digest:
`a8e8dc955a3324e3f78986b4e4de8d8894f8196e1ba7321b89f295016dc1c876`.

The frozen 60/61 panel was subsequently opened exactly once by #1182 after
the omega=0 arm and source-locked runner had merged. The software matrix passed,
then the panel stopped after **5 completed lives** while generating
`stable-60-g902:personal_relevance_candidate_h_v1` with
`CognitiveFundingError: cognitive work exceeds available energy/vigilance`
inside `learn_from_outcome -> branch_memory.observe`.

This is
[ENGINEERING_FAILURE_NOT_A_DEATH](studies/stage1-candidate-i-development-60-61/RESULTS.md),
not a J1-J7 result. Originals are archived on
`evidence/i3-stage1-candidate-i-60-61-46c52b2a5a81`, evidence commit
`ebb8d1f9`. **60/61 are exposed and permanently closed. Do not rerun.**

The prospectively frozen
[branch-decision settlement repair](studies/stage1-branch-decision-settlement-repair/RESULTS.md)
now returns **`BRANCH_DECISION_SETTLEMENT_REPAIR_PASS`**. B0-B9 all pass on
Actions `42505811626`, Python 3.11/3.12. The synthetic legacy mismatch is
reproduced, full Stage-A + Stage-B cognition remains charged, Candidate-H/I now
bind total decision work to the matching pre-Stage-A body, ordinary learning
semantics remain unchanged, and stale/missing settlement receipts fail closed.
Merged repair authority: `5ee25b3b0f39050321b0b5c6147bdae0e3e68ec5`.

60/61 remain exposed and permanently closed with no J1-J7 verdict. The next
fresh lived question is now prospectively frozen on
[Candidate-I 62/63](studies/stage1-candidate-i-development-62-63/PROTOCOL.md).
It uses new DEVELOPMENT indices 62/63, world seeds 2062/2063, G0 903/904 and
new life seeds, while preserving the four arms and J1-J7 exactly. Machine plan
digest:
`ba8e934c33fd060318721883e4f6e92034dd68ed743cf044ac97f9f4dc3a21e7`.

The source-locked 62/63 runner subsequently merged in #1186. The separate
one-shot transport #1187 passed the full Python 3.11/3.12 software matrix and
then opened 62/63 exactly once from execution source
`81f05a7fb79c9e1f264cab63a363dc181ff663b2`, Actions `42507594360`.
**18 lives completed** before
`depletion-62-g903:personal_shared_prior_candidate_i_v1` stopped with
`RuntimeError: missing branch decision settlement start body`.

The originals and failure receipt are archived on
`evidence/i3-stage1-candidate-i-62-63-81f05a7fb79c`, evidence commit
`1e975da3`. This is
[ENGINEERING_FAILURE_NOT_A_DEATH](studies/stage1-candidate-i-development-62-63/RESULTS.md),
not J1-J7 evidence. **62/63 are exposed and permanently closed. Do not retry.**
PR #1187 is closed and unmerged.

Source inspection identifies a narrower rollback-authority defect: Candidate-I
captured its probe snapshot before clearing the previous decision's `last`.
An unfunded Stage-A restore could revive that stale `last` after the matching
settlement receipt had been cleared. The branch-memory fail-closed guard then
correctly rejected learning.

The prospectively frozen software-only
[Candidate-I probe-restore authority repair](studies/stage1-candidate-i-probe-authority-repair/RESULTS.md)
now returns **`CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS`** on repair-code
authority `5ca8f2dcb7f87c18880ea3c45b773eec0daab2d4`, Actions
`42517714784`, Python 3.11/3.12. U0-U9 all pass. Rollback snapshots no
longer own `last`, branch settlement or pending learning authority; unfunded
exits restore only reversible first-person state, while FALLBACK/RELEVANT create
fresh current-decision authority. The funded FALLBACK also recaptures the
current opportunity-presence receipt from its one real final perception, so
recurrence storage no longer loses that lived observation after rollback.

60/61 and 62/63 remain permanently exposed and closed with no J1-J7 verdict.

The prospectively frozen
[Candidate-I lifecycle-custody stress](studies/stage1-candidate-i-lifecycle-custody-stress/RESULTS.md)
now returns **`CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS`**. Tested source
`1bdca27ae95509e9b54817bd25b2c0a21872c069`, Actions
`42518978398`, merged authority
`5e85106157afa6c600dd1983efde94fb80032977`. Python 3.11/3.12 pass the
975-test suite; navigation passes on 3.11. All L0-L11 are green and all nine
already-exposed DEVELOPMENT-0 smokes reduce with `smoke_failures=[]`.

This is engineering readiness only. It does not evaluate survival, uptake,
route frequency, omega direction or J1-J7.

The frozen
[Candidate-I 64/65](studies/stage1-candidate-i-development-64-65/RESULTS.md)
panel was subsequently opened exactly once from execution source
`427eedd374575e84d725ef3a6e287a69f1991518`, Actions
`42522541342`. The Python 3.11/3.12 software matrix passed before exposure.

The runner admitted **35 complete reductions**. The 36th original,
`pulse-64-g905:personal_shared_prior_candidate_i_omega0_ablation_v1`,
also completed as a 141-step natural `zero_food` death, but reduction stopped
afterward in `stage0_revision._resource_events` with
`ValueError: processing status contradicts paid base block`.

The original and all prior evidence are archived on
`evidence/i3-stage1-candidate-i-64-65-427eedd37457`, evidence commit
`f09806130d0ea0d9d9a66a12d6baa3afe5b66d15`.
This is **ENGINEERING_FAILURE_NOT_A_DEATH**, not J1-J7 evidence.
**64/65 are exposed and permanently closed. Do not retry.** #1195 is closed
and unmerged.

Read-only inspection of the archived 36th original localizes the reducer defect
at decision 134: Candidate-H Stage A was fully paid
(4 cycles / 18 simulated steps / 248 memory items), Stage B was exactly zero,
and the final public status was `NO_PROCESSING_BUDGET`. The Stage-0 reducer
incorrectly applied that Stage-B status to total Stage-A+Stage-B work.

The prospectively frozen software-only
[multi-phase processing reducer repair](studies/stage1-multiphase-processing-reducer-repair/RESULTS.md)
now returns **`MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS`** on tested source
`252419ff099fbb95990fb7a19426864c0a5a8346`, Actions
`42523805013`. Python 3.11/3.12 pass **999 tests**; M0-M9 are all green.

The reducer now authenticates total work separately from route-specific
processing ownership: Candidate-H finals, Candidate-I P1.3 fallback and
post-contact use Stage B; Candidate-I `INFORMATION_FINAL` uses its retained
Stage A. All cognition remains physically charged.

After this independent PASS, a read-only check of the archived 36th 64/65
original found zero processing/work contradictions across all 141 trace rows;
the former t=134 failure reduces as Stage-B `processing_paid=false`. This does
not admit the life to J1-J7.

The prospectively frozen
[Candidate-I lifecycle-custody stress v2](studies/stage1-candidate-i-lifecycle-custody-stress-v2/RESULTS.md)
now returns **`CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS`** on tested
source `f9544cf2e22f69a953fdd4141adc6991547c7e16`, Actions
`42524858889`, merged authority
`fbaecde68d6fbcb5a9ec8c6d5908b4b1880137bd`. Python 3.11/3.12 pass;
the 3.11 suite runs **1008 tests**. Historical L0-L11 remain unchanged and
V0-V8 all pass on the generic paid-Stage-A / zero-Stage-B
`NO_PROCESSING_BUDGET` boundary using actual H/I production decisions.

This is engineering readiness only. 60/61, 62/63 and 64/65 remain permanently
exposed/closed with no J1-J7 verdict.

The fresh
[Candidate-I 66/67](studies/stage1-candidate-i-development-66-67/RESULTS.md)
panel was subsequently opened once by one-shot transport #1205 after the exact
Python 3.11/3.12 software matrix passed. Execution source:
`9db49f8c3b522e73fd42ab5ca63fcc5d74662b99`; Actions
`42532125173`.

**Ten lives were admitted.** The eleventh original,
`stable-67-g907:personal_shared_prior_candidate_i_v1`, completed runtime and
was archived, then Stage-0 revision reduction stopped with
`ValueError: invalid Candidate-I post-contact processing receipt`.

Evidence is preserved on
`evidence/i3-stage1-candidate-i-66-67-9db49f8c3b52` at
`18a7e27bd79de81280e171fdf682f8a5f4195830`. #1205 is closed/unmerged.

**66/67 are permanently exposed and closed. There is no J1-J7 verdict.**
Do not rerun, resume, complete remaining cases, retroactively admit the
eleventh life after repair, or use partial lived metrics to tune Candidate-I.

Read-only localization shows a reducer-ownership gap: Candidate-I post-contact
correctly delegates to Candidate-H #1163, but the reducer accepts only nested
complete Candidate-H finals. A legitimate nested Candidate-H
`PROBE_UNFUNDED` therefore fails before Candidate-H's already-valid processing
semantics are applied.

The prospectively frozen
[post-contact probe reducer repair](studies/stage1-post-contact-probe-reducer-repair/RESULTS.md)
now returns **`POST_CONTACT_PROBE_REDUCER_REPAIR_PASS`** on tested source
`78d09c98127fb55aebb5eca729fa4ce4795d007a`, Actions
`42533323063`, merged authority
`4bcb2f28488f289625558960cd93c7c65c69b107`. Python 3.11/3.12 pass;
the 3.11 suite runs **1031 tests**. Q0-Q9 all pass.

Direct Candidate-H and Candidate-I post-contact now share one authenticated
processing-owner definition: complete H finals use Stage B; H
`PROBE_UNFUNDED` accepts only the two incomplete nested funding classes,
requires zero Stage B and uses authenticated Stage A. Total physical work is
unchanged.

66/67 remain permanently exposed/closed with no J1-J7 verdict.

The next intervention is now prospectively frozen in
[STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V3.md](STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V3.md).
It uses actual production H/I classes on a fixed ten-value energy ladder and
must naturally expose both post-contact nested-H `NO_PROCESSING_BUDGET` and
`NO_FUNDED_SCORE` routes, then pass those production receipts through the
repaired reducer. It opens no World and may not retune the ladder after its
first software exposure.

## Current handoff: 58/59 exposed, no Candidate-H continuation verdict

8 November 2026: the frozen Candidate-H DEVELOPMENT 58/59 transport opened
the panel once under execution source
`c2f63445ce8a3033ce8a2adfb9a0b1417b21c021`, Actions
`42484179997`. Software checks were green before exposure.

The execution archived originals on
`evidence/i3-stage1-candidate-h-58-59-c2f63445ce8a`, but stopped while
reducing the third arm with
`ValueError: resource processing status disagreement`. The failure receipt is
`ENGINEERING_FAILURE_NOT_A_DEATH`: two cases were reduced before the stop
(reference 400-step censored; Candidate-G 98-step zero-water death), while the
Candidate-H original was archived but not admitted to the aggregate.

Because worlds opened, the frozen `STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT`
rule applies. **58/59 are exposed and closed.** Do not rerun, replace seeds or
infer H1-H6 from the partial panel. There is no Candidate-H engineering
continuation PASS/FAIL from 58/59.

## Read-only 56/57 audit: first contact is represented asymmetrically

The preserved
[first-contact audit](studies/stage1-candidate-g-development-56-57/POSTHOC_FIRST_CONTACT_AUDIT.md)
reduces the immutable 56/57 originals without replay or counterfactual scoring.

Its main new observation is structural: in all **28/28** Candidate-G
pre-contact on-water decisions, unsupported `boire` is forecast as the generic
average step (water -0.4, uncertainty 1, information value 0). The same unknown
first drink receives a paid unsupported-effect prior when it is *imagined* at
an unseen frontier. P1.3 can cross the flat first-contact decision through its
designer curiosity addend; Candidate-G usually cannot.

The audit also separates two descriptive failure modes: an unsupported mode
with little exploration/first-contact value, and a supported mode where
Candidate-F-like cognition cost and sleep/inactivity return. It does not alter
the 56/57 frozen verdict or authorize tuning on exposed evidence.

## Next Stage-1 software slice: shared first-contact prior

The owner-approved
[shared first-contact prior protocol](STAGE1_SHARED_FIRST_CONTACT_PRIOR.md)
is the next bounded Stage-1 intervention. It asks whether the same inherited
RMS/omega expectation can govern an unsupported action whether the trial is
imagined or the resource is already perceived.

This slice is **software laboratory only**. It must pass frozen defect stops
D0-D7 before interpreting capacity. The primary R1 question is whether some
declared `omega > 0` makes at least one perceived-water first drink relevant
where `omega = 0` does not. `NO_CAPACITY` is a valid result and must not be
rescued by widening omega, rescaling the prior or changing fixtures.

Do not modify Candidate-H runtime, do not consume 58/59 as a tuning set, and do
not open another World/life panel from this protocol. P1.3 remains reference;
Stage 2 remains blocked.

## Latest software integration: unified Candidate-H passes

8 November 2026: the prospectively frozen
[unified Candidate-H integration](studies/stage1-candidate-h-unified-integration/RESULTS.md)
passes U0-U9 on final tested source
`bf527c92dd445b4f4ffcab4c8a24cbe8ed0c959f`, Actions
`42482799511`, Python 3.11/3.12.

The integrated software preserves the two previously frozen relevance semantics
exactly: first contact remains 24 RELEVANT / 56 FALLBACK with zero mismatches;
post contact remains 68 / 12 with zero mismatches.

On the fixed 60-decision routing panel, Candidate-H produces 37 complete P1.3
final routes and 23 Candidate-F final routes. All five required route classes
are observed, all 37 P1.3 fallbacks match their independent same-body P1.3
controls, phase accounting passes, omega -1/+1 changes nothing, and projector
state always returns to `reference/chunk_end`.

Verdict:
**`CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS`**.

Three engineering verifier defects were corrected before the final verdict:
an over-strict import assertion, exact floating settlement equality despite the
prospectively frozen 1e-12 tolerance, and an extra bit-exact body condition
incorrectly folded into U3. None changed the candidate, relevance predicates,
60-decision panel or U0-U9 rules.

This PASS authorizes only a **separately frozen fresh DEVELOPMENT protocol**.
Candidate-H is still absent from `runtime/life.py`; no fresh World/life,
selection, validation, reserve, adoption or Stage 2 is authorized yet.

## Latest software gate: Candidate-H post-contact relevance fallback passes

8 November 2026: the frozen
[post-contact Candidate-H gate](studies/stage1-candidate-h-post-contact-relevance/RESULTS.md)
passes P0-P6:
`CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS`.

All 80 personally learned-water states fund the actionable-belief plus
commensurate Candidate-F Stage A. **68** states are genuinely decision-relevant;
**12** have positive information but do not change the top decision and
therefore fall back. All 12/12 fallback states fund a complete P1.3 decision,
match same-body P1.3 exactly (max score error 0), and preserve their pre-probe
P1.3 top set.

This confirms that positive information value alone is still too broad:
relevance must be defined by an actual decision-top effect under one score
geometry.

Together with the first-contact H0-H5 PASS, both relevance semantics now have
bounded software evidence. The next admissible slice is a **unified Candidate-H
runtime software-integration gate** only. It must combine the two already-frozen
rules without changing them, pay every probe/fallback, preserve P1.3 on
fallback, and reconcile runtime forecast ceilings. No fresh World/life panel is
authorized by this PASS.

## Latest software gate: Candidate-H first-contact relevance fallback passes

8 November 2026: the frozen
[Candidate-H first-contact gate](studies/stage1-candidate-h-relevance-fallback/RESULTS.md)
passes all H0-H5 rules:
`CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS`.

Candidate-H pays the canonical Candidate-F relevance probe first. In the 24
strictly relevant states it executes no fallback. In all **56/56** non-relevant
states it can still fund a complete P1.3 four-plan fallback from the body after
the paid probe, with exact same-body P1.3 score identity (max error 0).

Crucially, all **20/20** support-only projector-drift states identified by #1161
return to their pre-probe P1.3 top set. Across all 56 fallback states there are
**0** top-set changes versus pre-probe P1.3. The fallback adds paid work rather
than hiding it: mean combined simulated work is 503.36 steps in fallback states
versus canonical probe mean 470.05.

The first implementation run reported H4 FAIL because the H4 verifier
reconstructed fixture bodies with a captured outer-loop level=50. That
bookkeeping defect was corrected to use each row's immutable level; candidate
computation and H0-H5 were unchanged. Final run `42478647427` passes on
Python 3.11/3.12.

This PASS is **first-contact software evidence only**. No runtime Candidate-H or
fresh live panel is authorized. Next freeze a separate software falsifier for
**post-contact relevance gating** under personally learned actionable belief.
P1.3 remains reference; 56/57 remain exposed and closed.

## Latest software diagnostic: support is not decision relevance

8 November 2026: the declared
[support-vs-relevance diagnostic](studies/stage1-candidate-g-support-vs-relevance/RESULTS.md)
classifies **`SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT`**.

On the frozen #1146 grid, personal recurrence support exists in all 80 states,
but only 24 states strictly select the epistemic trial. Among the remaining 56
support-only states, switching the whole decision to the canonical Candidate-F
projector changes the ordinary top option set in **20/56**, including **4 unique
winner changes**. Across all states the top set changes in 44/80.

The effect is not a small accounting detail: the four fixed ordinary plans cost
37 simulated steps under P1.3 versus 368.79 on average under Candidate-F in the
support-only states, with maximum pairwise ordinary score-gap shift 0.02643.

This identifies a structural defect in Candidate-G's activation rule:
**personal support is treated as if it already implied current decision
relevance**. The accurate projector can therefore alter ordinary policy even
when the information trial is not strictly advantageous.

Candidate-G live remains closed and 56/57 remain exposed. The next admissible
work is a prospectively frozen **software-only relevance-gated fallback**
falsifier: pay to establish relevance, use P1.3 for the final ordinary decision
when the epistemic trial is not strictly advantageous, and use one commensurate
Candidate-F decision only when it is. Any fallback must pay both computations;
no reimbursement, omega, action-specific rescue or fresh World/life panel.

## Current engineering handoff: Candidate-G 56/57 continuation FAIL

8 November 2026: the prospectively frozen no-omega Candidate-G DEVELOPMENT
pilot is complete
([result](studies/stage1-candidate-g-development-56-57/RESULTS.md)).

Execution source `6ce6fbc2025f9f6e6b34b779142f90c10c28a1e0`, Actions
`42477021573`, 36/36 original lives preserved on
`evidence/i3-stage1-candidate-g-56-57-6ce6fbc2025f`.

The frozen continuation rule is **FAIL**. Candidate-G genuinely alternates
between the canonical accurate projector and P1.3 reference (368
information-active decisions, 1213 reference-only), and cuts lived projection
cost sharply versus rejected Candidate-F: 0.9161 vs 2.1983 energy/step and
1.2723 vs 3.1118 vigilance/step. But R5 fails unchanged:
`NO_PROCESSING_BUDGET` is **2.8463% Candidate-G versus 2.0436% Candidate-F**.

Survival was not a criterion, but is an adverse descriptive result:
Candidate-G reaches the 400-step censoring horizon in **0/12** lives, P1.3 in
**3/12**. Water uptake is 16 Candidate-G versus 196 reference.

A posthoc funding-composition read shows Candidate-G nevertheless has fewer
total unfunded decisions (9.1082%) than Candidate-F (21.4578%), because
Candidate-F more often fails earlier at `NO_FUNDED_SCORE`. This does **not**
replace R5 or rescue the candidate.

**56/57 are exposed and closed. Do not retune on them.** Stop the Candidate-G
live path. The next admissible work is read-only analysis of preserved evidence
or a new software-only architecture falsifier on established fixtures. No fresh
live panel, selection, validation, reserve, reference adoption or Stage 2 is
authorized.

## Latest scientific gate: genomic omega Candidate-F rejected

7 November 2026: the full frozen
[Stage-1 omega ADR-0015 gate](studies/stage1-omega-adr0015/RESULTS.md)
completed under execution source
`ca506554e67eddde08e71ba6872df3b50f3ea4be`, Actions run
`42416437088`, with durable prerelease
`i3-stage1-omega-adr0015-ca506554e67e`.

All technical custody completed: 16/16 selection shards, 24/24 validation
shards, both aggregates, 47 workflow jobs with zero failures, and 85 durable
release assets. G6 custody passes. The scientific verdict is
**`FAIL_FROZEN_STAGE1_OMEGA_GATE`**.

Validation survival over 240 main lives per arm is stark:

- P1.3 reference: **82/240** survivors;
- selected Candidate-F with inherited omega: **0/240**;
- the same selected candidate genomes with omega forced to zero: **0/240**.

Candidate survival is zero in every F0 family and every population. Reference
survival is stable 25, depletion 41, pulse 16.

Revision also collapses: candidate complete-rank mean is 401.0 with zero
reacquisitions, versus reference 282.5875 with 35 reacquisitions. Candidate is
worse in all 8 populations.

Selection shifts omega upward in only 6/8 populations, below the frozen 7/8
G3 rule. Pooled omega does shift from 0.076728 in the candidate pools to
0.154818 among selected genomes, but this does not rescue G3.

Actual omega versus same-genome omega=0 has zero survival difference in all
8 populations and all three F0 families because both candidate arms die
universally. Therefore G4/G5 fail as well.

Frozen rule verdicts: **G1 FAIL, G2 FAIL, G3 FAIL, G4 FAIL, G5 FAIL, G6 PASS**.

Candidate cognition on realized validation trajectories costs about
2.23494 energy / 3.13911 vigilance per lived step, versus 0.58475 / 0.71725
for P1.3. Omega-zero has nearly the same cost as the candidate. This is
descriptive, not proof that cost alone causes the collapse.

**DRIFT DETECTED:** Candidate-F/omega is rejected on F0. Do not tune omega,
change G1-G6, select the six favorable populations, or add a Stage-2 compute
rule to rescue exposed validation 120..167.

The next bounded Stage-1 question is causal and narrower: preserve P1.3
decisions while physically paying an equivalent Candidate-F information
computation burden. That **cost-only reference-choice control** can distinguish
cost collapse from policy-choice collapse. It must be software-falsified first
and use fresh development conditions only if later executed.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked and
the P4 reserve remains sealed.

## Latest correction: canonical Candidate-G set is 24, not historical 32

8 November 2026: the frozen canonical numerical audit
([result](studies/stage1-candidate-g-canonical-numeric-audit/RESULTS.md))
completed at source `ce6c16bbae6bdf9d3f46cdb38bebbdcd0dc776ee`,
Actions `42474206334`, Python 3.11/3.12 PASS.

Historical float per-step and canonical high precision both pay exactly
18 cycles, 201 memory items and 1288 simulated steps/state. Yet canonical high
precision selects **24 states / 0 water**, while historical float selects
32 / 8 water. The only eight changed state identities are water 40 and 50 at
horizons 4/6/8/12.

Crucially, canonical high precision's selected set is **identical 24/24** to
Candidate-F's event-local projection set, with no extras or misses. Candidate-F
uses mean 470.05 simulated steps/state.

Classification:
**`HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT`**.

This resolves the residual noted after #1149. Do not spend further Stage-1 work
trying to recover the historical eight water states. The projection question is
now sufficiently answered for this grid: Candidate-F is cheap and
decision-equivalent to the canonical oracle.

Next bounded question: separate Candidate-F's projection from the rejected
genomic-omega live architecture. Freeze a Candidate-G integration gate that
uses personal recurrence plus Candidate-F projection **without omega**, and
measures whether projection cognition itself is fundable before any new life
panel.

## Latest negative diagnostic: exact distress reuse remains too expensive

8 November 2026: the declared exact distress-reuse diagnostic
([result](studies/stage1-distress-reuse-diagnostic/RESULTS.md)) completed at
source `96455f010a8ad150536db1bded0f01843b761860`, Actions
`42473511648`, Python 3.11/3.12 PASS.

The frozen classification is **`FEATURE_REUSE_INSUFFICIENT`**. Starting from
#1153's 853.3 simulated steps/state, consecutive identical feature reuse gives
an optimistic 778.5. An ideal decision-local exact feature memo, with **no
memory/read/write charge at all**, still gives 657.9. Candidate-F's prospective
threshold was 470.

Therefore further exact memo/cache work cannot plausibly close this gap under
the exposed fixture. The 32/8/24/40 decision surface remains unchanged.

**DRIFT DETECTED:** close this engineering route. The next bounded Stage-1
question is architectural: audit why Candidate-F's cheap event-local projection
misses the 8 water-deficit decisions that exact per-step recovers. Test whether
the residual is localized around generic predicted-death, distress-threshold,
restoration or option-shifted event times. No water/action-specific patch is
authorized.

## Latest exact-cost reduction: predicted-death truncation passes

8 November 2026: the death-truncated per-step falsifier, frozen at
`5fe2edb52f73e133178fbd77c579b2f9b6149c04`, completed at source
`0c3dc70d1de64a3c62c5e60e7ac6e1392b0fd549`, Actions
`42472935275`, Python 3.11/3.12 PASS. See the
[durable result](studies/stage1-death-truncated-per-step/RESULTS.md).

The structural verdict is **`DEATH_TRUNCATED_PER_STEP_EXACT_PASS`**.
Projection/value/body errors are at numerical-noise scale. The frozen #1146
Candidate-G counts exactly match per-step truth: 32 selected, including 8
water-deficit states, and 40 declines.

All 400 projection calls reach predicted death before step 255. Paying only
endpoints actually reached reduces mean work from 1288 to **853.3 simulated
steps/state** and mean bill from 2.9762/3.476 to **2.1068 energy / 2.6066
vigilance**, with the common forecast still fixed at 1288.

Candidate-F cost parity is not reached, so **no runtime candidate is
authorized**. The remaining compute gap is now about 383 simulated steps/state.
Before another cache, measure exact common prefixes among the five projection
calls within each frozen Candidate-G state. Only a demonstrated reuse opportunity
may justify a new decision-local representation.

## Latest accounting result: exact cache funds 80/80 but memory dominates

8 November 2026: the frozen exact-cache accounting sensitivity
([result](studies/stage1-separable-cache-accounting/RESULTS.md)) completed under
source `fddf08637651f7e1b5f0cf5577e3415ca4edf2e5`, Actions
`42472340815`, Python 3.11/3.12 PASS.

Both predeclared accounting bounds fund all 80 #1146 states, so the primary
classification is **`CACHE_ACCOUNTING_ROBUSTLY_FUNDED`**. The exact cache also
retains decision relevance: 32 selected epistemic states under the optimistic
bound and 39 under the conservative bound.

The separately frozen runtime-advance rule nevertheless **fails**. Mean actual
bill is 7.7591 energy / 3.5322 vigilance for the lower bound and 17.1839 /
12.9570 for the upper bound, versus Candidate-F's frozen #1149 bill of 1.3402 /
1.840. No runtime candidate is authorized.

The bottleneck is no longer projection accuracy or yes/no funding ambiguity.
It is the stored representation: 1,848 fresh traces write 1,912,680 memory items
while only 152 later accesses hit a trace (7.6%). Paying four 255-element exact
arrays per trace is a bad exchange for that reuse rate.

Next Stage-1 architecture falsifier: **exact death-truncated per-step
projection**. Stop computation at the first predicted vital zero and sum the
absorbing maximal-distress tail analytically. The current per-step diagnostic
prepays all 255 unit chunks even though no new bodily distress is evaluated
after death. This candidate changes work only, never projected value. Open
sparse exact checkpoints only if this simpler optimization remains too costly.

## Latest structural result: exact separable projection cache passes

8 November 2026: the exact decision-local separable-cache falsifier, frozen at
`2887239575771c9ec3afe17d898a8d38135f68b6`, completed at source
`74725372f82ad490467f20cf0a69e815650bae7b`, Actions run
`42471715382` (Python 3.11/3.12 PASS). See the
[durable result](studies/stage1-separable-projection-cache/RESULTS.md).

The candidate reproduces the 255-step per-step truth at numerical-noise scale:
max pairwise decision bias **2.22e-15**, projection-equivalent invariant
**1.33e-15**, max final-body channel error **0**. All frozen structural rules
pass. Exact reuse is observed in both fixture families: 972 trace hits on the
486-case grid and 50 on the nonlinear #1150 option set.

This establishes **representational feasibility only**. The current I3
accounting prices full model-level simulated steps, not an isolated
channel-distress sample. The descriptive channel-sample lower bound is therefore
not a CognitiveWork bill and cannot support an energy/vigilance claim.

Next bounded question: freeze a physical accounting/capacity contract for cache
construction, reads, storage and rebuilds, then run the frozen #1146 Candidate-G
80-state kernel under real CognitiveBudget. If a defensible paid construction
is not fundable, report consistent foresight as unaffordable at current physical
prices. P1.3 remains reference; no World/life or runtime adoption is authorized.

## Latest exploration: cheap consistent-projection shortcuts fail

Two declared exploratory probes on the #1146 fixtures, measured against the
per-step projection ([results](studies/stage1-affordable-projection-probes/RESULTS.md)):

- **Local sensitivity.** Linear expansion errors: wait 0.0034, sleep 0.0055,
  eat 0.30, drink 1.91.
- **Decision-time anchored grid.** Decision bias 0.2153, against 0.2164 for the
  reference.

Neither approaches 1e-3. The next design, not implemented, is a separable
cached projection: exact per-channel discounted tables held as paid,
capacity-bounded memory, rebuilt on drift change, with death coupled through
the minimum time-to-death. The honest alternative outcome is a scientific
result: consistent foresight unaffordable at current physical prices.

## Latest diagnostic: Candidate-G depends on projection consistency, not recurrence

#1146 passed Candidate-G's software gate with 1/80 strictly advantageous
epistemic trials under the P1.3 `chunk_end` projection. A declared, descriptive
rerun of the same grid ([results](studies/stage1-candidate-g-projection-dependence/RESULTS.md))
changed only the projection:

| Arm | Epistemic trials | Paid simulated steps per state |
| --- | --- | --- |
| reference | 1 | ×1 |
| Candidate-F projection | 24 | ×8.9 |
| per-step | 32 | ×24.3 |

The accurate projections make information decision-relevant. Their cost is
the architectural obstacle, consistent with the processing-budget failures of
the funded Candidate-F gate. Candidate-F's projection selects 0 water-deficit
states where per-step selects 8, which is worth an audit.

Next proposal, frozen before any code: an affordable consistent projection,
namely one accurate projection plus paid local sensitivity per decision, reused
across options. No world or panel is authorized.

## Latest complete causal diagnostic: 54/55 cost-versus-policy remains unresolved

8 November 2026: the fresh 54/55 panel completed all 36 preregistered lives once
under execution source `a27e4c3ccebfcfec610b79f02f00fd2440d1b7dc`, Actions run
`42426687157`. All originals are preserved in evidence commit
`18bfda8bc680afc9df01d1d2ebb308b79efcbc70`.

See the
[complete result](studies/stage1-candidate-f-cost-vs-policy-development-54-55/RESULTS.md)
and
[read-only causal audit](studies/stage1-candidate-f-cost-vs-policy-development-54-55/POSTHOC_CAUSAL_AUDIT.md).

The frozen primary rule required at least one matched block where Candidate-F
dies while the deliberately **overcharged** P1.3-choice control survives.
Observed: **0/12**. Candidate-F and upper-cost both die in all 12 blocks;
ordinary P1.3 survives 4/12. Therefore the preregistered strict
cost-sufficiency counterexample is **not observed**.

This null does not prove cost sufficiency because the control pays Candidate-F
shadow cognition plus an additional P1.3 decision. It is intentionally not
cost matched.

The secondary paired behavior nevertheless implicates policy. Upper-cost lives
longer than Candidate-F in 7/12 blocks, shorter in 1 and ties in 4. In every
one of the four blocks where P1.3 survives, Candidate-F obtains zero water while
the upper-cost P1.3-choice arm obtains water and lives longer than Candidate-F,
although it still dies before horizon.

Aggregate positive water uptake is reference 232, Candidate-F 4, upper-cost 25.
Movement is 831 / 79 / 216 respectively. Across upper-cost lives the shadow
action differs from the actual P1.3 action on 510/2395 decisions.

Cost also remains severe. Upper-cost accumulates 868 P1.3
`NO_PROCESSING_BUDGET` steps and 36.24% physical inactivity. Realized paid
energy/vigilance per lived step is 0.60876/0.75158 reference,
2.06095/2.90923 Candidate-F and 1.66955/2.11048 upper-cost. Trajectories differ,
so these rates are descriptive, not mediation.

**Current interpretation: cost and policy are both implicated; exact mediation
remains unresolved.**

**DRIFT DETECTED:** Candidate-F/omega is already rejected by the frozen gate.
Do not tune it, rerun 54/55, or build another increasingly artificial causal
control merely to obtain a clean percentage. A tighter control is admissible
only if it can match physical cost without granting unpaid P1.3 cognition,
reimbursing the body, forcing actions or otherwise violating I3 contracts. If
no such paid construction is available, stop causal decomposition here and
return Stage 1 to architecture design.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked and
the reserve remains sealed.

## Latest causal diagnostic attempt: 52/53 closed on observer engineering failure

7 November 2026: the prospectively frozen 52/53 Candidate-F cost-vs-policy
diagnostic opened once under execution source
`e10365f605c6e919af1651a5c20f335ae6fd5f40`, Actions run
`42422888044`.

Py3.11/3.12 software preconditions passed. Twelve complete original lives were
archived before the runner stopped while reducing the twelfth life. Durable
evidence commit: `60c5ae22c0b381865ec81678015c41efc1b9d975`.
Artifact: `13593974371`.

The failure is **ENGINEERING_FAILURE_NOT_A_DEATH**. The physical upper-cost
life `stable-53-g902` completed 286 steps and died from zero water. At step
177 the Candidate-F shadow paid 3 cycles + 347 memory items, then P1.3 had
insufficient remaining budget for its own processing block and correctly
reported `NO_PROCESSING_BUDGET` with zero P1.3 work. The historical Stage-0
revision join incorrectly required total decision work to be zero whenever that
P1.3 status was present.

The upper-cost receipt itself is consistent: total work equals shadow +
reference work on all 286 decisions, P1.3 remains sole motor authority, and the
maximum sequential-vs-cumulative settlement gap is only
1.4210854715202004e-14.

Therefore 52/53 are **closed with no rerun** under their frozen stop-and-archive
rule. Only three complete matched stable blocks were reduced before failure;
depletion/pulse were never generated. No cost-vs-policy causal verdict is
evaluated from this incomplete prefix.

See
[52/53 result](studies/stage1-candidate-f-cost-vs-policy-development-52-53/RESULTS.md)
and
[observer failure audit](studies/stage1-candidate-f-cost-vs-policy-development-52-53/POSTHOC_OBSERVER_FAILURE_AUDIT.md).

Next intervention: correct Stage-0 revision's processing-work check **only for
the explicit upper-cost policy** so P1.3 funding status is checked against
`reference_choice_work`, while total physical decision work remains
independently authenticated. Ordinary policy semantics must remain unchanged.
Any renewed diagnostic requires a fresh prospective allocation.

**DRIFT DETECTED:** do not rerun 52/53, reinterpret the partial stable prefix as
a causal result, or weaken the physical-work receipts globally.

## Latest diagnostic: cost paralysis receded, local policy still fails

7 November 2026, [cost-reduced development result](studies/stage1-cost-reduced-development/RESULTS.md)
and [read-only zero-information audit](studies/stage1-cost-reduced-development/POSTHOC_INFORMATION_ZERO_AUDIT.md),
PR #1075. The prospectively frozen 46/47 panel completed once: 24 lives, no
retry or engineering crash, originals archived before reduction.

The candidate meets its **engineering-only** continuation rule: aggregate
physical inactivity is 403/1792 = 22.49% and there are 12 positive water
uptakes. Only 3/12 candidate lives enter terminal NO_PROCESSING lock, versus
the first diagnostic's pervasive early funding collapse. This does **not**
constitute a Stage-1 gate result.

The candidate nevertheless remains 0/12 alive at horizon, with 10 dehydration
and 2 starvation deaths. Reference is 4/12 alive. Candidate cognition costs
2.059937 energy and 3.166388 vigilance per lived step versus 0.476000 and
0.584084 for reference; trajectories differ, so this is descriptive rather
than cost-matched mediation.

The newly visible bottleneck is behavioral rather than merely computational:
candidate sleep occupies 1241/1792 steps (69.25%). None of 8666 paid option
scores has positive information value above 1e-12, despite 8224 (94.90%) having
complete empirical support. In stable/pulse, all eight candidate lives remain
fully funded until death, obtain zero water, and never score a local `boire`
option. Across 400 funded decisions with sensed water <=20 in those families,
drink is available 0 times while sleep is chosen 381 times.

The read-only audit does not reconstruct unarchived branch values. It therefore
does not claim whether zero information is dominated by signal aliasing or an
unchanged best continuation. It does show that 4255 fully supported zero-value
scores introduce at least two distinct new payoff-cell keys, so total payoff
collapse is not a sufficient explanation. Synthetic kernel tests separately
prove that the implementation can produce positive information value.

**DRIFT DETECTED:** stop optimizing duplicate work and do not add a Stage-2
budget heuristic to rescue this local prototype. Its deliberate local repertoire
cannot value discovery of unseen cells: hypothetical movement reveals no new
map cell, while repertoire/memory/prior also differ from P1.3. The next Stage-1
candidate should preserve P1.3's existing first-person spatial repertoire and
learned state, changing the information-value mechanism as narrowly as possible.
Do not rerun exposed 44-47, tune the stationary prior, force resources, or
rewrite Competition. P1.3 remains reference.

Stage 0, #1026, #1054 and the scientific Stage-1 survival/revision gate remain
open. No selection/validation/reserve exposure, activation or scientific GO.

## Current Stage-1 engineering handoff: reference-preserving path

The adverse local prototype has been replaced by a staged P1.3-preserving path:

- #1076: fixed paid 18-record empirical branch memory, empty at birth.
- #1077: `reference_branch_memory_v1`, storage-only P1.3 cost control with
  unchanged decisions and replay allocation before extra storage.
- #1078: paid exhaustive conditional replanning over existing P1.3 plans.
- #1080: conservative frontier belief using P1.3's existing Laplace resource
  rate; unsupported/newborn resource mass remains non-actionable.
- #1081: observable branch-specific continuation plans with a fail-closed
  anti-oracle rule.

The first live integration is now the opt-in
`reference_frontier_information_v1` **engineering probe**. It preserves
P1.3 perception, map/history, effects, TD values, option repertoire, concrete
first motor commands, Competition and Action Control, and inherits #1077's
branch-memory storage/replay rule. Its experimental score removes additive
curiosity/relevance/prudence.

Its information scope is deliberately narrow: each existing `explorer:*`
option is treated as one generic newly revealed-cell probe. If #1080 supplies
personally supported actionable-water belief, the informed forecast may reveal
the existing travel prefix plus one generic move and `boire`. Food probability
and all unsupported mass are non-actionable in this partial mechanism.
Multi-cell independence is not assumed and old `_unknown` counts do not
multiply the probability.

All scored options share one conservative decision-work forecast ceiling.
Actual work alone is physically billed. The default P1.3 reference is unchanged.

This is **not** the complete Stage-1 candidate: unknown-food integrity-effect
distributions, multi-cell joint outcomes, frozen-projection ablation,
zero-perceived-cost diagnostic and scientific source/genotype/case/margin/
multiplicity/stopping locks remain open. No new 48/49 development, selection,
validation or reserve world is authorized by this implementation.

Stage 2 stays blocked. Stage 0, #1026 and #1054 remain open.

## Latest fresh diagnostic: 48/49 stopped by observer engineering failure

The prospectively frozen [48/49 protocol](studies/stage1-frontier-water-development/PROTOCOL.md)
was opened once in run `42364436764`. It stopped in the first three-arm block
after two completed lives. See the immutable
[engineering-failure result](studies/stage1-frontier-water-development/RESULTS.md).

Completed `stable-48-g901` lives:

- P1.3 reference: 128 steps, dehydration death, no water uptake;
- storage-only control: 128 steps, dehydration death, no water uptake, first
  NO_PROCESSING at step 34 followed by 95 inactive steps.

The candidate case did **not** produce a complete life. The external P5e
Competition observer rejected the new frontier witness because its historical
score identity did not include the explicit `information_value` term.
Runner status is `ENGINEERING_FAILURE_NOT_A_DEATH`.

The artifact and six original files are archived under execution source
`a1e53daee016e801289a85c9cd7855798b048051` and evidence commit
`89a36a9186bb9ff89769598baba021f7c79af62a`.

**No scientific or candidate mechanistic verdict is available.** The
preregistered 48/49 panel is closed under its no-retry/no-replacement rule.
Do not resume its remaining cases.

Next: a narrow software-only Competition-observer compatibility fix. It must
preserve the anti-forgery checks and historical witness behavior. Only after
that fix may a new, separately allocated development panel be prospectively
defined. Stage 2 remains blocked.

## Latest complete diagnostic: 50/51 frontier-water mechanism is real but bootstraps too late

The separately preregistered [50/51 result](studies/stage1-frontier-water-development-50-51/RESULTS.md)
completed all 36 lives once in run `42365345012`, with all originals archived
before reduction. The [read-only bootstrap audit](studies/stage1-frontier-water-development-50-51/POSTHOC_BOOTSTRAP_AUDIT.md)
adds no new life.

The candidate's engineering continuation rule is **met**: 7/12 candidate lives
contain positive frontier information and 121 frontier options have positive
information value. This is the first live I3 evidence that the reference-
preserving value-of-information path becomes numerically positive in ordinary
paid lives.

The mechanism activates immediately after relevant personal experience. In all
seven positive-information lives, the first positive information score occurs
exactly one step after the first positive water uptake. Five other candidate
lives never experience water, never obtain positive information and all die.

Survival remains adverse and is not a Stage-1 gate result: reference survives
3/12, storage-only 6/12 and candidate 2/12. Candidate gains no survival block
relative to either control, loses one block relative to reference and four
relative to storage-only. These 12 matched blocks are not independent
populations and no significance claim is made.

The candidate is **not computationally paralyzed**: physical inactivity is only
1.11% and there are 30 NO_PROCESSING_BUDGET steps. Instead it executes 1021
waits and only 410 moves, versus 465 waits and 826 moves in storage-only.
Candidate cognitive cost is also higher on realized trajectories: 0.7612 energy
and 1.0457 vigilance per lived step versus 0.5851 / 0.7274 for storage-only.

The mechanistic interpretation is now sharper: the conservative #1080 belief
refuses to invent a bodily consequence for an unseen resource. That keeps the
model first-person and non-oracular, but creates a circular bootstrap. Before
the individual has personally learned that water can help its body, discovering
water has no actionable frontier-information value. Once the first useful water
experience occurs, the mechanism comes online on the very next step.

Candidate deaths are 7 dehydration and 3 starvation. Food information remains
explicitly unimplemented, so the three starvation deaths show a known scope
limit but do not explain the water-bootstrap failure.

**DRIFT DETECTED:** do not respond by restoring curiosity as a hidden bonus,
tuning 50/51, inventing favorable water behind a frontier, or jumping to Stage
2. The next Stage-1 work must address unknown-outcome bootstrap generically and
prospectively. Any new prior must be action/token/world-renaming invariant and
must not be selected from exposed 44-51 development results.

P1.3 remains reference; I3 remains unregistered. No selection, validation,
reserve exposure or scientific Stage-1 GO.

## Stage-1 bootstrap substrate after 50/51

The adverse 50/51 result is preserved and closed. No later slice reruns those
worlds. The current software-only bootstrap chain is:

- **#1088:** `paid_zero_mean_stake_prior`. Two opposite unsupported effect
  hypotheses along the current distress gradient, p=.5/.5, exact zero expected
  external bodily delta, no action/token/map/World input. Exact CI: 457 I3
  tests.
- **#1089:** exact observed-effect view for future reuse of one action inside
  one subjective branch. No mutation of real EffectsModel/TD/map/RNG and no
  cross-action propagation. Exact CI: 466 I3 tests.
- **#1090:** nested unsupported-action trial value. It separately reports
  no-trial value, frozen post-trial value, informed post-trial value,
  `information_value` and `trial_advantage`. A synthetic test demonstrates
  positive information value from the strictly zero-mean prior. Exact CI: 476
  I3 tests.
- **#1091:** first-person frontier modality prior. P1.3's existing Laplace
  resource-presence formula is retained; conditional water/token modality uses
  symmetric Laplace smoothing over personal incidences. Zero-incidence
  distribution is .5 no resource / .25 water / .25 token. No body utility or
  effect enters the prior. Exact CI: 486 I3 tests.

These pieces answer different uncertainties and must not be collapsed:

1. what modality an unseen frontier may reveal;
2. what an unsupported newly available action might do;
3. how behavior should change after that effect becomes observable.

The source scenario states **2-3 simulated branches** for Stage 1. A direct
3-way modality x 2-way effect product would exceed that declared envelope.

**DRIFT DETECTED:** do not build a generic recursive belief tree, add Stage-2
compute selection, or reopen development 44-51. The next bounded Stage-1 design
must express the existing water-frontier engineering question with at most
three outcome leaves, while keeping resource observation distinct from action
effect. Any such composition remains software/development-only until
prospectively frozen on a fresh allocation.

P1.3 remains reference. I3 remains unregistered. Stage 0, #1026 and #1054
remain open; no scientific Stage-1 GO.

## Latest Stage-1 decision-boundary result: information is real, winner unchanged

The 7 November software sequence now resolves the immediate local ambiguity.

- #1099: without a future matching action opportunity, information was zero in
  160/160 tested multi-deficit states.
- #1101: exact P1.3 water explorer-prefix semantics retained positive
  information but selected an epistemic trial in 0/80 states.
- #1102/#1104: carried unknown food gives genuine information from personal
  safe/toxic experience; in the rich competing-needs fixture it improved meal
  rank in 9/27 states.
- #1105: under **one shared complete cognition-depleted forecast body**, all
  27/27 rich states were fundable; information was positive in 9/27 and raised
  the meal score in 14/27, but the raw winner changed in **0/27**.

This removes the main cost-comparability ambiguity. The Stage-1 computation is
not numerically dead and its real v2 burden does not erase the signal. The
current bottleneck is that P1.3 contains too little representation of reusable
future opportunities for learning an effect to become decision-dominant.

**DRIFT DETECTED:** stop adding local water/food score patches, synthetic
competitor variants or Stage-2 budget rules. The next bounded intervention is a
single generic first-person future-opportunity representation used only to
unblock Stage 1. It is an operational prerequisite, not permission to launch
full Stage 3. It must not encode hidden stock, source persistence, schedules,
world-family identity or a favorable effect prior.

P1.3 remains the reference. I3 remains unregistered. No new scientific life,
selection, validation or reserve exposure follows from these software results.
Stage 2 remains blocked; Stage 0, #1026 and historical #1054 remain open.

## Stage-1 ω (owner decision A): capacity shown, projection bias found

The owner chose option A (7 November 2026): a heritable generic expectation
toward the unknown, ω ∈ [−1, 1], drawn symmetrically and set only by lineage
persistence. Recorded before code in
[STAGE1_OMEGA_SOFTWARE_FALSIFIER.md](STAGE1_OMEGA_SOFTWARE_FALSIFIER.md):

- **Uniform, need-agnostic shift.** The personal RMS prior becomes (ω ± 1)·s,
  so its mean is ω·s and its spread unchanged.
- **Not yet in the genome.** ω is an explicit kernel parameter for now; the
  genome change is deferred so archived v3 digests stay valid.
- **Reference semantics.** The #1101 exact-explorer source change is reused for
  reference-preserving semantics; #1101's rejection stands.

Falsifier 1, executed once on the #1101 grid, no world or life:
`CAPACITY_SHOWN`.

- **R0–R2 pass.** ω = 0 reproduces #1101 exactly, paid work is identical
  across ω, and the direction is monotone.
- **R3 passes.** ω = 0.5 and ω = 1 add 4 positive water-revelation states
  (52 → 56); ω = −1 removes 4.
  ([results](studies/stage1-omega-software-falsifier/RESULTS.md))

**Post-hoc finding, the next blocker.** The P1.3 simulator values longer plans
higher even when the extra steps are waits: food-stressed −1.4263, +1 wait
−1.4151, +3 waits −1.3938. The likely cause is end-of-chunk distress accounting
in the self-projection, an inconsistent bootstrap.

- **Unaffected:** ω's effect, because every arm compares the same plans.
- **Uninterpretable:** absolute signs of Stage-1 trial and revelation
  advantages, including #1101's.

Proposed next slice: a bootstrap-consistency invariant and a projection fix,
gated as a reference change. ω's genome slice and live integration wait for it.

## P1.3 projection consistency: confirmed defect, no cheap fix yet, D1 reframes Stage 1

The plan-length bias is confirmed as a bootstrap inconsistency of the P1.3
projection's end-of-chunk accounting. Per-step projection satisfies the
invariant to 8.9e-16. Measured on a frozen grid
([results](studies/projection-consistency/RESULTS.md)):

- **Opt-in `trapezoid` accounting** (same 8 paid units, exact when distress is
  linear) reduces the worst decision bias only from 0.169 to 0.133.
  Verdict `NO_CANDIDATE_PROMOTED`. The default stays `chunk_end`, bit-identical
  on 60 compared values.
- **Declared diagnostic D1.** The ω falsifier rerun with unbiased per-step
  projection gives:
    - ω's effect strong and monotone: 16 → 52 trial states;
    - at ω = 0, 32 of 40 selected trials epistemic, versus 0/80 under the
      biased projection.

  #1101's sub-decisive-information verdict was largely an artifact.
  Per-step costs 255 units instead of 8 and is not a live option.

Next: candidate C, event-aware accounting (split chunks at closed-form
threshold-crossing and death steps, pay any extra evaluation), under a new
frozen protocol, then the ω falsifier again. Reference adoption needs an
ADR-0015 gate.

## Current reference and observed limits

| Area | Implemented / observed status |
| --- | --- |
| Core | P1.3 adopted on the funded v2 substrate under ADR-0015; first-person cognition is actually paid. P1.2's original rejection remains unchanged. |
| P2 | Equal initial opportunities support lineage comparisons; 0/7729 exact static probe work-vector matches. Probes are descriptive, not cost-matched ceilings. |
| P3 / P4a | Original lineage and held-out pilots completed. P4a selected 47/144 versus random 42/144; population differences -2,+9,-1,-1. General lineage advantage not demonstrated. |
| P4b | Retained learning 84/288 survivors versus 0/288 paid-discard; 144/144 same-genome history pairs have distinct learned-model hashes. This does not demonstrate stable acquired behavioral individuality. |
| P5a / P5b | Learned effects and action-specific readout show strong bounded survival dependence. Removing TD values or replay did not show the same collapse. Actual work and activity differ. |
| P5c | Normal 110/288, curiosity discarded 4/288, risk discarded 105/288, both 7/288. Four genetic populations; no conventional confirmatory inference or information-only cost-equivalence claim. |
| P5d | Original development evidence includes 125 paid carried-food opportunities without a meal selected in the masked-curiosity arm. Full competing scores were not recorded; cause remains open. |
| P5e | Full paid Competition observer and 24 original development lives archived. Normal 7/12 censored, masked 6/12. Masked arm: no collections and no carried-food exposure, so its meal competition is NOT_OBSERVED. |

P5e had 342 normal-arm carried-food opportunities: 333 had another candidate
with a strictly higher raw score. Threshold effects included three raw-top meal
losses and three lower-score meal wins. **This does not establish a generally
broken Competition or resolve the P5d masked-arm case.** The supplied report's
additional hunger/competing-needs interpretation is post-hoc and attributed to
its author, not independently re-executed by this integration.

## Accepted direction; implementation slices and limits below

[ADR-0016](../../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md)
and the single [development plan](DEVELOPMENT_PLAN.md) integrate the
[unaltered supplied scenario](GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md).

Next: **Stage 0** independent-population design, energetic mediation and
first-person diagnostic exposure ([#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060)).
Keep individuality under [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026)
and P5d resource uncertainty under [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054).
Then **Stage 1** information value in predicted bodily distress
([#1061](https://github.com/josselin-orta-lab/individual-zero/issues/1061)), followed
by **Stage 2** paid value of computation
([#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062)).

Change detection/latent causes/factorization, successor features, topological
maps and multi-family lineages remain deferred Stages 3-6. No such mechanism
is implemented or adopted by this update. Competition is a low-priority audit,
not the next survival-policy rewrite. No scripted drinking/eating or hidden
reward bonus may replace a failed experiment.

New validation requires separate preregistration, genuinely independent
populations and previously unopened allocations >=120. The original P4 reserve
1200000..1200199 remains sealed. Eight populations improve exact-test resolution
but do not guarantee power; the proposed 7/8 later lineage direction is not
itself a significance result. See the plan's explicit operational clarifications.

## Evidence and historical custody

Full pre-integration [status ledger](STATUS_BEFORE_GENERALIZATION_2026-11-06.md),
[plan ledger](DEVELOPMENT_PLAN_BEFORE_GENERALIZATION_2026-11-06.md) and
[documentation ledger](README_BEFORE_GENERALIZATION_2026-11-06.md) are retained
byte-for-byte at the same directory depth. Their old next-task instructions
are historical, not the current priority queue. Original artifacts are unchanged.

Direct current references: [P3](studies/p3-mutation-pilot/RESULTS.md),
[P4a](studies/p4a-g2-heldout/RESULTS.md),
[P4b](studies/p4b-paid-outcome-learning/RESULTS.md),
[P5a](studies/p5a-paid-component-screen/RESULTS.md),
[P5b](studies/p5b-paid-readout-heldout/RESULTS.md),
[P5c](studies/p5c-paid-score-addends/RESULTS.md),
[P5d analysis](P5D_POSTHOC_COLLECTION_CONSUMPTION.md),
[P5e protocol](P5E_DEVELOPMENT_PROTOCOL.md) and
[P5e results](P5E_DEVELOPMENT_RESULTS.md).

[TEST_PLAN.md](TEST_PLAN.md) describes software checks; historical test counts
and CI links certify their own SHAs only. Exact current checks belong to the
integration PR. A documentation merge does not create a new scientific result.

## Stage 0: first non-executing design slice

[Design contract](STAGE0_DESIGN.md), issue #1060: eight new G0 candidate pools
(K=40, m=5 per architecture/population), separate F0 selection/validation blocks,
strict complete-outcome ranking and exact sign-test arithmetic with explicit
ties/effective n. New validation identifiers are 120-167; the reserve stays
sealed. Identifiers are not generated genomes, selected winners or observed
lives. This is not a preregistration or a completed Stage 0.

Standalone scalar/metadata tests and full-repository integration checks are
separate; exact CI results belong to the implementation PR. Final family-R
protocol/source locks, practical margins, multiplicity, lineage controls and
#1026/#1054 remain open. No survival, individuality or generalization result is added.

## Stage 0: actual funded-life receipt connection

`lab/stage0_energy.py` verifies full runtime evidence chains and original
phase work/body debits, then summarizes complete declared reference/candidate
pairs in eight population blocks. Actual decision/learning energy and vigilance,
replay work, early deaths and total lived time remain explicit. Chosen waiting
is not physical inactivity. Zero-lived-step rates are undefined, not zero.
Pair opportunities must match; actual spending need not. Output is descriptive,
not causal energetic mediation, authenticated custody, or a scientific verdict.

Development-only integration tests check observer on/off equality of actual
receipts, body, actions, learned state and per-decision RNG. Exact results belong
to the implementation PR, not this status text. No Mind/runtime/physics/genome
change, default observer, new study life or validation/reserve exposure.
Study-specific case/genotype/intervention binding and prospective registration
remain required; the fixed design is not automatically executable.

## Stage 0: personally available revision endpoint

[Concrete R-depletion-v1 contract](STAGE0_REVISION.md) explicitly chooses the
existing depletion ecology as a first F0 revision stratum, not a new family.
`lab/stage0_revision.py` joins existing resource sidecars to paid life receipts:
positive uptake at a personally used source, first local absence, separately
paid processing, then positive uptake elsewhere. The clock never starts from
hidden stock. No exposure/failure/death and unknown latencies remain explicit;
reacquisition is neither survival nor proof of internal belief revision.

No new generator, observer hook, allocation or scientific cohort. Sidecar joins
are consistency checks, not original-chain authentication. Next: bind the
bounded Stage-1 candidate and these definitions to a prospective gate rather
than expand the observer framework. Stage 0 and #1026/#1054 remain open.

## Stage 1: paid information-value kernel, not a deployed cognitive candidate

[Kernel contract](STAGE1_INFORMATION_VALUE.md): a new computational primitive
compares one common continuation against observation-conditional re-planning
across two/three subjective forecasts in the existing distress-return units.
All branch scoring/projection and reduction work is funded before execution;
the total computation cost enters the predicted body. Indistinguishable
signals and body states cannot confer perfect hidden-outcome information.

No automatic prior, World input, action command, learned-state mutation or new
genome. The default reference does not call it; its curiosity/prudence remain
unchanged. The personal builder and opt-in local online prototype below are
implemented, not promoted. Budget consumption is not a physical settlement receipt;
the ordinary runtime must debit it. Zero perceived cost still requires payment.

Software tests include actual Mind projection/World debit and unchanged
reference-life behavior on a development fixture. Exact results belong to the
implementation PR. No new scientific study, held-out exposure, activation or
survival/generalization finding. #1060, #1061, #1026 and #1054 remain open.

## Stage 1: paid personal empirical hypotheses

`modules/personal_outcomes.py` records a bounded private history from applied
pre-decision/post-physics bodily outcomes, correcting only known own decision
cognition. Recording and constructing hypotheses consume real allowance; the
ordinary world owner must settle it. Exact-key recent experience precedes
same-action transfer to a new token. Unknown actions remain NO_PERSONAL_SUPPORT.
Two/three empirical hypotheses and their same-key persistence assumption feed
the unchanged kernel; body-only signals never expose sample identities.

These are fallible recent empirical hypotheses, not calibrated uncertainty,
true hidden effects or a new innate favorable prior. The default reference has
no extra store; the opt-in prototype below shares its episodic budget. The
original constructor software integration uses
fixed development fixtures with actual Mind decisions, World steps, new paid
recording and physical settlement. It is not a reference-cost-parity or survival
study. That constructor slice left existing executable source unchanged. The
subsequent local integration below changes runtime dispatch only by explicit
opt-in; genome, physics and historical evidence remain unchanged.

## Stage 1: local online information choice, not reference promotion

[Integrated local prototype](STAGE1_INFORMATION_VALUE.md): explicit run_life policy
`local_information_v1` connects personal outcome recording, fully funded
conditional forecasts and actually executed motor commands. Old additive
curiosity/relevance/prudence do not enter this score; original Competition and
motor control are reused. Default P1.3 behavior remains the reference.

An explicit stationary zero-delta ignorance prior replaces missing support
only in this prototype. It creates no positive resource gain but can be
optimistic about unknown decay. Episodic m_max is split between TD/replay and
personal effects, not enlarged. The complete batch has a common cost forecast;
unused Competition-cycle ceilings are predicted, never billed. Actual recording
is included once in the ordinary learning-phase debit. Policy identity enters
the manifest before birth; unsupported historical ablations fail before birth.

This changes the local planning repertoire and memory partition as well as
scoring. It is not the full spatial mechanism or a one-mechanism scientific gate.
Software checks include actual acquired-history use, a synthetic history-to-motor
contrast, observer/RNG parity, exact receipts and pinned previous-runner default
parity. Exact PASS/FAIL/NOT_RUN belongs to the implementation PR.

The first prospective development diagnostic remains adverse and immutable.
PR #1072 added phase receipts; #1073 removed per-key rescans; #1074 adds a
decision-local, owner/version-bound support index so later option constructions
pay explicit lookups without retraversing the same history. Forecast-only
compatibility work preserves the old common predicted body. The minimal
populated synthetic decision is now 1.3104 energy / 1.76 vigilance, with unique
rollouts the largest measured phase. **Stop exact-cost optimization here:** the
next informative step is a new source-locked development diagnostic, not another
observer or hidden budget heuristic. Full live ablations and the scientific
survival/revision gate remain open; Stage 0, #1026 and #1054 are not resolved.
No selection/validation/reserve exposure, activation or scientific GO.
