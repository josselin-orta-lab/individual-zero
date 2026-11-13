# R2.4 / M11: durable authenticated request-nonce ledger, frozen engineering preflight

**Date:** 13 November 2026. **Issue:** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339). **Type:** test-only loopback CAS protocol hardening, not scientific evidence, a production M11 authority or an authorization to open Worlds.

## Existing baseline and precise hypothesis

The verified [response-custody result](R24_RESPONSE_CUSTODY_FAULT_RESULTS_2026-11-13.md), [PR #1363](https://github.com/josselin-orta-lab/individual-zero/pull/1363), proves the client authenticates remote replies against each freshly generated request nonce, but the test **server does not persist accepted request nonces**. A previously authenticated and captured HTTP request can be replayed to the server. Some duplicate transitions are rejected by CAS, but a `verify` remains successfully replayable and a full store rollback can reopen previously consumed commands.

**Narrow H0 falsifier:** for the same live authority DB, any previously successfully authenticated request nonce must be refused on a second use, even if the HTTP request is signed, sent after server restart, or targets a different operation/identity. Only an authorized **new** nonce may be accepted. Failed/invalid commands must not consume a nonce. Existing `register`, `prepare`, `commit`, `verify`, terminal and source binding must remain valid under fresh nonces.

## Frozen test matrix and implementation boundaries

| Case | Declared result | Criterion |
| --- | --- | --- |
| Fresh signed `register`, `verify`, `prepare`, `commit` | `PASS` | Original CAS state machine preserved |
| Same signed HTTP `verify` request/nonce replayed | `REJECT` | HTTP refusal, no signed successful custody response |
| Previously successful request/nonce replayed **after cold server restart** | `REJECT` | Duplicate refusal persists across process exit |
| Same nonce used for different claim or operation | `REJECT` | Global authority namespace, not per-life memory only |
| Bad signature or failed CAS followed by a valid request with the same nonce | `ACCEPT_VALID_ONLY` | Rejection does not poison a nonce; transaction atomic |
| Duplicate same-nonce concurrent callers | `ONE_ACCEPT` | SQLite one-writer uniqueness; no conflicting successful receipt |
| `verify` operation | `PASS_NO_AUDIT_APPEND` | Its nonce is durably journaled, but it does not append a motor/CAS transition audit |
| Complete restoration of authority DB **including nonce ledger** | `FAIL_INDEPENDENT_M11` | A consumed nonce can become usable again. This intentionally demonstrates the remaining common-domain vulnerability |
| Restart with legacy v2 store | `REJECT_NO_MIGRATION` | New v3 store never silently uses an older authority schema |
| All old scientific boundaries | `UNCHANGED` | No World, Mind, genome, policy, scientific cohort, registry or engine activation |

Implementation scope: `src/i3/lab/engineering_remote_authority.py` only for server changes. Advance the **engineering-only** local authority DB to `i3-remote-cas-authority-store/v3` with `request_nonces` in the same SQLite transaction as the accepted response/CAS. Every server dispatch passes a required 32-character lowercase hexadecimal `request_nonce` into `AuthorityStore.apply`. Client HTTP message format, HMAC, nonce generation and response format do not change. The transaction must atomically insert the nonce and apply the CAS or roll back both. Add dedicated no-World request-auth/replay tests and adjust low-level store tests to pass unique fixture nonces.

A successful `verify` now performs one durable nonce-table write but **does not append** a normal `register/prepare/commit` audit event; this is an intentional overhead/semantics change. Do not claim it is side-effect-free on storage. All nonces share the rollback domain of the authority SQLite and remain manipulable by privileged operators; the extra table is not an off-host monotonic trust anchor. The v3 code rejects v2 stores instead of silently migrating old experiments. Persisting every signed request also raises storage and throughput costs that require future measurement and operational policy, not a production-ready assertion.

## Stop / release rule

Execute exact-source Python 3.11 and Python 3.12 I3 software CI, with route/contract/navigation guards. Any acceptance of a duplicate nonce while the later DB persists, retry of an uncertain native motor, old v2 auto-migration, scientific test launch or engine registry promotion is a STOP. **Even green CI does not release M11**: external independently administered protected store, endpoint and signing identity, credential rotation, off-host rollback controls and long-life throughput remain `NOT_RUN / NOT_ATTESTED`.

**Science and governance:** P1.3 funded-v2 retained, Stage 2.1 `NOT_ISSUED` / `HOLD_NO_VERDICT`, `reference_generation=I3`, `active_generation=I1`, old evidence untouched, new scientific World/index permission unchanged and false.
