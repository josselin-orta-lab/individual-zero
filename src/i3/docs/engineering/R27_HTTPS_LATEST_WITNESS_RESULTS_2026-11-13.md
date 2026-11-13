# I3 R2.7: pinned HTTPS signed-witness retrieval, exact-source evidence and limits

**Date:** 13 November 2026. **Technical result:** `R27_HTTPS_SIGNED_WITNESS_FETCH_SOFTWARE_PASS`. **Independent M11:** `NOT_ATTESTED` with deliberate `FAIL_INDEPENDENT_M11` on a full coherent rollback of the loopback server reply and both SQLite stores. **Science:** Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`. No scientific World, life, new index/source or study permission.

## Source provenance

- [Frozen protocol, before code](R27_HTTPS_LATEST_WITNESS_PREFLIGHT_2026-11-13.md), first committed at `bca738598cfe341fd06d5040970b41e780311eed`.
- [PR #1380](https://github.com/josselin-orta-lab/individual-zero/pull/1380), exact tested head **`1ecc27f7df99001ece9d5acbd6862e6c6f76d364`**, squash merged to `main` as **`34b406cd25eed6c7fe7d4464875a54fbf2ba745a`**.
- [GitHub Actions #43449122655](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43449122655) **SUCCESS** at this exact code head:
  - Python 3.11 job `131966328185`: **1,378/1,378 I3 software tests PASS**, test step 167.277 seconds; engine/ownership and navigation PASS.
  - Python 3.12 job `131966327747`: **1,378/1,378 I3 software tests PASS**, test step 202.854 seconds; engine/ownership and navigation PASS.
  - **All ten new R2.7 no-World TLS tests executed and passed on both versions.** Existing tests including R2.6 full-domain negative unchanged. This document is *post-test*, and its own Markdown SHA is not being counted as part of the code test run.

## Software scope of the transport

[engineering_remote_https_latest_witness.py](../../lab/engineering_remote_https_latest_witness.py) implements `PinnedHTTPSLatestWitness.fetch_required_latest`, a **read-only client**, not a server:

1. Require exact canonical `https://DNS:port/v1/i3/receipt/latest` with explicitly configured port, external non-symlink CA bundle, actual `ssl.create_default_context(SERVER_AUTH, cafile=...)`, `CERT_REQUIRED`, `check_hostname=True` and TLS >= 1.2. No insecure TLS option, HTTP fallback, credentials in URL or redirection.
2. Make **one** `GET`, with bounded **socket timeout** (not a hard total request-duration cap). Require HTTP 200, `application/octet-stream`, `Cache-Control: no-store`, no compressed/chunked body, exactly one canonical `Content-Length` from 1 to 8192 and an exactly matching bounded body. A transport/server error means STOP, **never a second attempt**, a cached response or local fallback.
3. Verify v1 canonical domain-separated Ed25519 receipt against **separately supplied** authority ID, source SHA-256, issuer key ID and 32-byte public key, then provide raw signed bytes. The [R2.6 reconciliation](../../lab/engineering_remote_recovery_reconciliation.py) validates the signature again and requires exact byte equality against the signed publisher tip and full-audit current authority with the designated `COMMITTED/OPEN` identity. A read-only match returns `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`, with `motor_authority=false`, `scientific_world_authorized=false`, `independent_m11_attested=false`.

The CA bundle and trusted public key are **inputs**, not issued or independently validated by the repository. TLS authenticates the service for a pinned hostname against the configured CA trust; Ed25519 authenticates receipt bytes against a pinned public key. **Neither proves that the service's signed high-water is presently the latest or safe from being rolled back.** No client-certificate mTLS or operator/source-release attestation is added.

## Adversarial matrix: real loopback TLS, all checks ran in software CI

| Frozen case | Exact-source test outcome | Scope |
| --- | --- | --- |
| Real HTTPS handshake to loopback server with ephemeral test CA and DNS SAN `localhost`, fresh Ed25519 receipt and exact R2.6 reconciler | PASS diagnostic | Actual TLS certificate verification under CI; no independent server administration |
| Foreign/untrusted CA and SAN/hostname mismatch | REJECT | TLS certificate trust and host pin enforced |
| HTTP URL, userinfo, fragment/query, wrong path, implicit port, invalid CA path or invalid timeout/key input | REJECT | No permissive origin or trust downgrade |
| 302 redirect, 404, 503 | REJECT with exactly one request | No automatic follow/retry |
| Missing, malformed, duplicated, oversized or inconsistent `Content-Length` | REJECT | Strict bounded wire format |
| Wrong media type, cacheable/missing cache policy, gzip or transfer encoding | REJECT | No ambiguous body decoding or caching |
| Abrupt TLS connection closure | REJECT/STOP with exactly one request | Fail closed on synthetic transport interruption |
| HTTPS returns a **valid older signed receipt** while local signed publisher/authority advanced | R2.6 REJECT | Signature and TLS alone do not prove freshness |
| Altered signed payload or wrong pinned Ed25519 public key over valid TLS | REJECT | Cryptographic pin separate from TLS trust |
| **Authority SQLite, publisher SQLite and test server's reply all restored to older coherent state** | **ACCEPT negative** | `FAIL_INDEPENDENT_M11` even with verified TLS and genuinely valid old signature |
| Distinct machines, separately administered CA/secret/monotonic high-water, mTLS writer admission, real cross-host partition/rollback, key rotation/revocation | **NOT_RUN / NOT_ATTESTED** | No release claim |

Unit-test-only TLS key material is created in an isolated temporary directory and destroyed by the test cleanup; no new secret/certificate/URL is committed to the repository. The test server is bound to loopback **127.0.0.1**, runs within the same CI worker and therefore **cannot establish an independent M11 principal**.

## Decision, release gates and cost caveats

**ACCEPT:** narrow no-World HTTPS/Ed25519 transport-validation behavior, input pins and negative fault controls. **Do not accept:** independently protected monotonic witness, deployed signer, privileged recovery, physical life/exact motor, off-host source build authentication, long-life latency/throughput or Stage-2 scientific inference.

- No data or engine activation changed. The client is not connected to an actual remotely managed issuer; no private Ed25519 signing key, CA management, mTLS writer role, revocation, network operator inventory or independent admin/storage identity is supplied.
- HTTP no-store is a **cache policy**, not cryptographic freshness. The current signed receipt v1 is **not nonce-challenge-bound**, so a compromised or rolled-back endpoint can serve a previously legitimate receipt. R2.6 only rejects an old receipt when a newer publisher/authority tip **survives**.
- The nominal socket timeout limits a stalled read, not necessarily total end-to-end time under adversarial slow streaming. Do not infer production availability or exact transport budget from this small loopback test.
- The entire SQLite publisher journal and full v3 authority audit remain O(history) per inspection. There is no hot-path optimization, signing service or distributed snapshot.
- Next genuine release gate: independent host/administrative principal with protected key and monotonic high-water, exact release-source and client/writer identity custody, mTLS or equivalent writer authorization, remote attested rollback detection, cross-host crash/partition tests, key rotation and disaster recovery. These require operational facilities not simulated by a single GitHub Actions worker.

**Preserve status:** keep [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) **OPEN**. `reference_generation=I3`, `active_generation=I1`, I3 `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, no entrypoints. P1.3 funded-v2 remains the scientific reference; all new World/cohort/index flags false; Stage 2.1 scientific `NOT_ISSUED`.
