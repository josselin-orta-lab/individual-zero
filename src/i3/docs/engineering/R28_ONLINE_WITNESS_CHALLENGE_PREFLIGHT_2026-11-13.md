# I3 R2.8 / #1339: nonce-bound online witness challenge, preflight

**Frozen 13 November 2026 BEFORE implementation.** R2.8 is engineering-only, no scientific World, life, source/index permission or engine activation. It builds on [R2.7 HTTPS signed latest witness results](R27_HTTPS_LATEST_WITNESS_RESULTS_2026-11-13.md). This is a **challenge-response protocol test**, not an independent M11 release, external deployment or actual monotonic custody.

## Question and falsifier

R2.7 authenticates a TLS endpoint and an Ed25519 signed publication receipt, but its simple `GET` has no client-generated cryptographic freshness challenge; a captured old response can be replayed unchanged. Can a client require an authenticated **response to this exact request's fresh nonce** under a **separately pinned online responder key**, while still requiring full issuer-signed checkpoint verification and R2.6 read-only local reconciliation?

**Required:** a new `PinnedHTTPSChallengedWitness.fetch_required_latest` that generates a fresh CSPRNG 128-bit nonce *per call*, sends it once via an exact versioned `POST /v1/i3/receipt/challenge`, verifies strict canonical wire/schema/size, pinned CA+hostname and Ed25519 **responder signature over domain-separated canonical fields including nonce and complete encoded signed receipt**. The publisher's pre-existing Ed25519 receipt signature must also match the separate approved `issuer` key, authority, source, and key ID. Both keys are operator inputs, never discovered from the reply. The wrapper returns **exact issuer receipt bytes**, suitable for the existing R2.6 `reconcile_required_witness` callback. No fallback to R2.7 GET, local publisher, unsigned response, HTTP, redirect or retry.

The response `schema=i3-online-challenge-witness-response/v1` is exactly `{schema, nonce, responder_key_id, signed_receipt_b64, signature_b64}`; the `signature_b64` authenticates bytes `b"I3-R28-ONLINE-WITNESS/v1\\0" + canonical({schema,nonce,responder_key_id,signed_receipt_b64})`. Request schema `i3-online-challenge-witness-request/v1`, exact `{schema, nonce}`. Exact 32-char lowercase nonce, 64-byte Ed25519 reply signature, canonical base64, unique keys, canonical UTF-8 JSON, 16,384-byte response cap. Use the existing strict R2.7 HTTPS endpoint validation, external CA, `CERT_REQUIRED`, hostname check and bounded socket timeout. No server production implementation or private key in runtime code.

## Frozen no-World adversarial matrix

| Case | Expected |
| --- | --- |
| Real TLS loopback with ephemeral CA, server signs fresh challenge with a *different* temporary key from issuer signer, valid latest receipt and R2.6 reconciliation | `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`, no World or write path |
| Reuse identical captured old response for a second fresh request | DENY even with valid TLS/issuer/responder signatures |
| Responder signs **wrong nonce**, forged responder key, wrong pinned responder ID or payload tamper | DENY |
| Issuer receipt content tampered while responder signs the tampered bytes | DENY due to independent issuer signature |
| Wrong CA / hostname, malformed URL, status/redirect, malformed Content-Length, cache/type/compression, closed connection | DENY / STOP, one request, no fallback |
| Valid TLS + newly signed responder challenge over a **stale but properly signed issuer receipt**, newer publisher/authority surviving | R2.6 DENY: request freshness does **not** ensure publisher recency |
| Both SQLite stores and the online test server's retained receipt coherently rolled back, online responder still signs **fresh nonce** | **ACCEPT negative** `FAIL_INDEPENDENT_M11` |
| Truly distinct administrative host, protected signer + monotonic service, mTLS writer admission and cross-host network / rollback experiments | **NOT_RUN / NOT_ATTESTED** |

**Stop/CI:** exact code SHA Python 3.11/3.12 full I3 software tests, engine/ownership/navigation pass, frozen matrix exercised, no ignored tests. Keep #1339/#1331 OPEN, I3 reference and I1 active; I3 remains `proposal/NOT_REGISTERED_NOT_EXECUTABLE`, P1.3 funded-v2 Stage 2.1 science `NOT_ISSUED/HOLD_NO_VERDICT`, all new scientific World/cohort/index permissions false. A valid challenge proves a response was signed *for the nonce*, NOT that the remote high-water is the newest or administered independently.
