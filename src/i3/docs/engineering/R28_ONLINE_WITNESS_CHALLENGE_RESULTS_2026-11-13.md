# I3 R2.8: nonce-bound online signed witness, source-pinned software results

**Date:** 13 November 2026. **Technical outcome:** `R28_NONCE_CHALLENGE_WITNESS_SOFTWARE_PASS`. **Independent M11:** `NOT_ATTESTED`, with deliberately executed `FAIL_INDEPENDENT_M11` under a full coherent rollback of both local SQLite stores **and the loopback server's published receipt**, even though the live test responder signs a **new challenge**. **Science:** Stage 2.1 `NOT_ISSUED` / general `HOLD_NO_VERDICT`. No new World, living individual, source/index/cohort authorization or engine activation.

## Preannounced source and exact CI

- [R2.8 protocol and falsifier matrix](R28_ONLINE_WITNESS_CHALLENGE_PREFLIGHT_2026-11-13.md) was committed **before implementation and tests** as `52cac3418a2b9f16d59945e9193fd68620ae518e`.
- [PR #1382](https://github.com/josselin-orta-lab/individual-zero/pull/1382), exact CI-tested code head **`d985c9d59d0bae671ca79bb29d75e051fa246d99`**, squash merged to `main` as **`7e0d2a56948d6327f23c672a8a7ccc97c3f43ee3`**.
- [GitHub Actions #43455950980](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43455950980) **SUCCESS**, source-exact:
  - Python **3.11**, job `131990002074`: **1,391/1,391 I3 software tests PASS**, test step 185.214 s; ownership/engine contract and navigation PASS.
  - Python **3.12**, job `131990002453`: **1,391/1,391 I3 software tests PASS**, test step 210.695 s; ownership/engine contract and navigation PASS.
  - Exactly **13 new no-World R2.8 tests**, all PASS on both Python versions. The preceding 1,378 tests are retained and no scientific study entrypoint was executed.
- This document was authored **after** the tested code merge; do not retroactively claim its Markdown was part of the software CI head.

## Mechanism and explicit boundaries

The read-only laboratory client [`PinnedHTTPSChallengedWitness`](../../lab/engineering_remote_online_challenge_witness.py) provides the existing R2.6 callback `fetch_required_latest`. Its new wire contract is separate from the previous, unchanged R2.7 simple `GET`:

1. Client selects a fresh **128-bit cryptographic nonce** for every call and sends one canonical JSON `POST` to the exact CA-verified TLS origin and path `/v1/i3/receipt/challenge`. There are no redirects, retries, HTTP fallback, cached response or local substitution. The origin inherits R2.7 validation: explicit DNS hostname, port, trusted external CA, `CERT_REQUIRED`, hostname check, TLS >= 1.2 and bounded socket timeout.
2. The test responder returns a **separate Ed25519 signature** over domain-separated canonical bytes covering the response schema, **exact client nonce**, pinned online responder key ID and base64-encoded **complete issuer-signed receipt**. The client requires a distinct explicitly pinned **online responder public key** in addition to the existing checkpoint **issuer public key**. The response is canonical JSON with unique exact fields and one valid canonical Ed25519 base64 signature (64 decoded bytes); size <= 16,384 bytes. HTTP status must be 200, content type `application/json`, `Cache-Control: no-store`, no compressed/chunked body and exactly one canonical bounded Content-Length.
3. The embedded **original signed checkpoint receipt** is decoded with canonical base64 and verified separately against the operator-pinned issuer key, authority SHA, source SHA and issuer ID. No new birth claim, source index or checkpoint schema was added; the existing v1 publication receipt is unchanged.
4. The returned **exact issuer receipt bytes** can be passed to [R2.6 `reconcile_required_witness`](../../lab/engineering_remote_recovery_reconciliation.py), which still checks the local signed publisher tip, the fully audited authority v3 state, source consistency and a specific `COMMITTED/OPEN` target. A match returns **`READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`** with `motor_authority=false`, `scientific_world_authorized=false` and `independent_m11_attested=false`.

The two signer keys in tests are independently **generated within a single process/CI worker**. There is **no production challenge server, private key file, managed CA lifecycle, distinct operator, protected remote high-water, HSM/KMS, mTLS writer authorization or off-host M11 release**. Responding with a signature for the latest client nonce attests possession of the responder private key **at response time**, subject to ordinary cryptographic assumptions. It does **not** prove that the remotely stored latest receipt is fresh or monotonically preserved.

## Precommitted fault matrix, tested under both Python interpreters

| Case | Software observation | Bounded interpretation |
| --- | --- | --- |
| Real TLS handshake to ephemeral-CA loopback responder using a different Ed25519 key from the checkpoint issuer; three successive unique client nonces and R2.6 source/OPEN check | **PASS**, `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY` | TLS/signature/protocol implementation, no actual operator independence |
| Capture one authentic complete signed HTTPS response and replay it for a **new nonce** | **REJECT**, no retry | A previously captured static network response cannot answer a fresh challenge |
| Authentically signed response containing a **wrong nonce** | **REJECT** | Signed bytes must bind the exact ongoing request |
| Foreign online responder signing key, wrong pinned responder public key or wrong responder key ID | **REJECT** | Responder pin is separate from issuer key |
| Online responder legitimately signs a **tampered issuer receipt** | **REJECT** | Issuer Ed25519 signature independently required |
| Foreign TLS CA, certificate SAN/hostname mismatch, malformed endpoint or missing pins | **REJECT** | TLS and configuration fail closed |
| Redirect/503, abrupt HTTPS connection drop | **REJECT/STOP**, exactly one request | No redirect, retry or local fallback |
| Missing/malformed/duplicate/oversized/inconsistent HTTP length, cache policy, type or transfer encoding | **REJECT** | Strict bounded HTTP frame/content policy |
| Duplicate JSON fields, noncanonical JSON, invalid base64 or corrupt responder signature | **REJECT** | Exact canonical envelope and signature |
| Test-injected unusable random nonce source | **REJECT before network** | No silently weak challenge |
| **Server signs a genuine older issuer receipt with the NEW nonce** while local publisher/authority have advanced | Online signature verifies; R2.6 **REJECTS** | Challenge freshness alone does **not** imply receipt recency |
| **Authority SQLite + publisher SQLite + HTTPS responder's stored receipt all restored together**, online responder then signs a **fresh new nonce** | **ACCEPT negative control** | **`FAIL_INDEPENDENT_M11`** despite legitimate TLS, issuer signature, online signature and new nonce |
| Distinct operated host/admin, release source/build attestation, protected signing keys and monotonic state, cross-host rollback/crash/partition evidence, credential rotation/revocation | **NOT_RUN / NOT_ATTESTED** | No independent M11 release |

## Decision and next gate

**Accept only a software-level defense against replay of a *static captured HTTPS response*.** Even cryptographically sound challenge/response has no answer to a **live signer attached to a rolled-back publication store**. The decisive negative test is therefore not a success claim for M11. A locally consistent old state remains exploitable if the external endpoint and both local files share the same rollback adversary.

A future genuine M11 acceptance requires, in separate scoped operational evidence: an independently administered endpoint and key principal, a protected non-rewindable high-water/append authority, source/writer admission, credential rotation/revocation, cross-host power/network/partition/crash fault injection with independent receipts, and a disaster-recovery rule that cannot rewind the external authority. No audit pruning, faster CAS, automatic retry of an uncertain paid motor or engine activation is justified here.

**Status unchanged on merged `main`:** keep [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) **OPEN**. `reference_generation=I3`, `active_generation=I1`, I3 `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, `entrypoints={}`. Scientific reference P1.3 funded-v2 and Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, all new scientific World/cohort/index permission flags `false`.
