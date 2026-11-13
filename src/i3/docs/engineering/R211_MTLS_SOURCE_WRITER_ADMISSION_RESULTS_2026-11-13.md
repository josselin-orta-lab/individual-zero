# I3 R2.11: source-pinned mutual-TLS writer admission, exact software result

**13 November 2026. Technical status:** `R211_LOOPBACK_MTLS_WRITER_SOURCE_SOFTWARE_PASS`. **Independent M11:** `NOT_ATTESTED` and the previously demonstrated `FAIL_INDEPENDENT_M11` remains release-blocking. **Scientific Stage 2.1:** `NOT_ISSUED / HOLD_NO_VERDICT`.

## Precommitted source and executed CI

- [R2.11 preflight](R211_MTLS_SOURCE_WRITER_ADMISSION_PREFLIGHT_2026-11-13.md), committed **before any implementation** as `b4abd0f329e81aa5d62ce34577e976262b612a6f` from main `cc3153fd6bc0b2711583b1d6c03c648a9270bba7`.
- [Code PR #1389](https://github.com/josselin-orta-lab/individual-zero/pull/1389), source-exact tested head **`2f4b3bf9ceeebb5ec9da85b4df4352d31920afb5`**, squash merged to main as **`807045f7a43f9cf63fa01c5f5a87c3296719a75c`**.
- [GitHub Actions #43497921685](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43497921685) **SUCCESS**, same exact PR head:
  - Python **3.11**, job `132135790253`: **1,410 / 1,410 I3 software tests PASS**, 188.660 s; all eight new actual TLS tests PASS, engine/generation ownership PASS; **540/540 entrypoint navigation checks PASS**, errors/warnings 0.
  - Python **3.12**, job `132135789813`: **1,410 / 1,410 I3 software tests PASS**, 156.101 s; all eight new TLS tests PASS, engine/generation ownership PASS. Navigation is conditional on Python 3.11.
  - Workflow's additional scientific/original-exposure jobs were **SKIPPED**. No new scientific World, cohort, source index, registered I3 life or engine activation.
- This results document is authored **after** the exact software merge. The doc commit itself was not included in that earlier source-specific suite; no unfounded extra CI claim.

## Observed no-World fault matrix

The original `serve_test_loopback` still defaults to HMAC-protected **plain HTTP bound only to `127.0.0.1` for tests**, not production. R2.11 adds a strictly opt-in test fixture requiring **all three** separately supplied settings: a server-side `ssl.SSLContext(PROTOCOL_TLS_SERVER)` with `CERT_REQUIRED` and explicit TLS minimum 1.2, an exact **DER client certificate SHA-256 pin**, and an exact operator-configured **source SHA-256 pin**. Missing/partial/malformed settings fail **before database creation**. The request is checked for its actual CA-verified TLS peer certificate before HMAC input, then for exact approved claim source after normal HMAC/canonical JSON validation and **before `AuthorityStore.apply`**. No new CAS schema, P1.3 action policy or off-host credential storage.

| Preannounced case | Actual outcome | Bounded observation |
| --- | --- | --- |
| Authorized writer/client/server with valid ephemeral CA and exact source; real HTTPS register → verify → prepare → commit → verify | **PASS** | Full synthetic no-World CAS path works; phase transitions acknowledged, no native motor executed |
| Same ephemeral CA but **different** writer leaf and same application HMAC key | **REJECT** | Exact client cert pin denies before SQLite history/nonce writes |
| No TLS client certificate | **REJECT** | Actual mutual-TLS handshake fails, no history or nonce |
| Client certificate issued by foreign CA | **REJECT** | Server's CA verification fails, no history or nonce |
| Writer trusts wrong server CA | **REJECT** | Client rejects handshake, no authority write |
| Correct writer cert/HMAC, foreign `claim.source_sha256` | **REJECT** | Server pins allowed source separately from the claim, no history/nonce |
| Disallowed writer attempts PREPARED after authorized genesis | **REJECT** | No pending CAS transition or nonce consumed by refused request |
| Partial/invalid/unverified server-side mTLS configuration | **REJECT before DB creation** | No implicit HTTP fallback for a partly configured strict mode |
| Historical plain `127.0.0.1` test-only CAS and all I3 software regressions | **PASS** | Original test interface retained, not an off-host deployment |
| Real independent B/C operators, source-release attestation, managed secrets/revocation, off-host WORM/monotone state, cross-host rollback/crash/partition | **NOT_RUN / NOT_ATTESTED** | Missing operational evidence; cannot promote to M11 |

## Interpretation, remaining negative and handoff

**Accept the software-only ingress capability.** R2.11 shows that an exact *test-configured* certificate writer principal and source SHA can be jointly required before test CAS mutation. It does **not** prove actual executable build provenance from an independently controlled authority, a per-life writer certificate assignment, off-host credential rotation/revocation, independent operators, protected monotonic high-water or deployed mTLS server. Everything in the test, including issuing CA/key, server and SQLite, still belongs to the **same CI worker and rollback domain**. A forged/build-substituted source can still be associated with a claimed SHA by a sufficiently privileged operator; a SHA pin is not a physical build witness.

Most importantly, the [R2.8 coherent rollback counterexample](R28_ONLINE_WITNESS_CHALLENGE_RESULTS_2026-11-13.md) is **still `FAIL_INDEPENDENT_M11`**. There is no actual separately protected high-water C. A freshly signed online reply attached to a restored publisher can continue to authenticate old state when all relevant storage domains are restored together.

The operational [off-host release gate](OFFHOST_M11_INDEPENDENCE_RELEASE_GATE_2026-11-13.md) must be completed under genuinely distinct identities and privileges; privileged rollback of service working state while protected high-water survives must **STOP before native motor**, and full Mind/World/RNG/body cold recovery must be separately evidenced. **Keep #1339 and parent #1331 OPEN**. Do not activate I3 or open new scientific Worlds on the basis of 1,410 green tests. `reference_generation=I3`, `active_generation=I1`; I3 `proposal/NOT_REGISTERED_NOT_EXECUTABLE`; P1.3 funded-v2 Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, all new scientific World/cohort/source/index permits false.
