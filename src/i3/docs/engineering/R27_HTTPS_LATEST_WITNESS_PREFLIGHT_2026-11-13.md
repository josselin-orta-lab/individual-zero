# I3 R2.7 / #1339: HTTPS-only signed latest-witness retrieval, preflight

**Frozen:** 13 November 2026 **before code and tests**. **Type:** engineering-only HTTPS client + loopback TLS fault experiment for the existing R2.6 read-only reconciliation. **No scientific World/life, no native motor, no credential/private signing key deployment, no claim of independent M11**. Source baseline: [R2.6 results](R26_REQUIRED_WITNESS_RECONCILIATION_RESULTS_2026-11-13.md), [R2.5 signed publisher](R25_ATOMIC_RECEIPT_PUBLICATION_RESULTS_2026-11-13.md), [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339).

## Question and trust model

Can the required R2.6 `fetch_required_latest` dependency be supplied by an **explicitly pinned read-only HTTPS** latest-receipt client that fails closed against transport errors, foreign TLS certificates, stale/forked/unsigned receipt bodies, status redirects, cache/body ambiguities and missing/oversized data, while doing **no automatic retry**?

The contract remains three separate checks:
1. The TLS channel authenticates a service **for its operator-pinned hostname and CA bundle**, not a physical/admin-independent authority.
2. Each exact reply authenticates its v1 **Ed25519 signed receipt** against an independently configured public key/authority/source/key ID. The signature **does not prove the receipt is latest**, even when the channel is valid.
3. R2.6 reconciles this reply against the local publisher tip and fully audited **COMMITTED/OPEN** authority. A result stays `READ_ONLY_MATCH_NO_MOTOR_AUTHORITY`, not a fresh signed challenge, proof of whole-system liveness, cold-recovery equivalence or motor replay permission. A server controlled by the rollback adversary can serve valid old signed bytes.

## Narrow implementation contract

- New isolated laboratory module `i3.lab.engineering_remote_https_latest_witness` with `PinnedHTTPSLatestWitness` (`fetch_required_latest()`). Configure one **exact HTTPS URL**, with explicit port and a fixed versioned read path `/v1/i3/receipt/latest`, no credentials, fragment/query, redirects, HTTP fallback or caller-supplied insecure TLS context.
- Require an **external regular non-symlink CA certificate bundle** and use Python standard-library `ssl.create_default_context(purpose=SERVER_AUTH, cafile=...)`, `CERT_REQUIRED`, `check_hostname=True`. Require bounded positive socket timeout (no claim of whole-request wall-clock deadline). No TLS client certificate or mTLS/managed secret is invented; operational writer/source admission remains NOT_ATTESTED.
- Only one `GET` per `fetch_required_latest()`. Use `http.client.HTTPSConnection`, not an auto-redirecting/caching HTTP client. Require 200, `application/octet-stream`, `Cache-Control: no-store`, identity/no content encoding, no transfer encoding, **explicit canonical Content-Length 1..8192** and exactly matching bounded bytes. No decompression, redirects, retry on network error, local fallback, or on-disk caching.
- Verify v1 canonical Ed25519 bytes with operator-supplied pinned issuer/public key/source/authority before returning the raw bytes to `reconcile_required_witness` (which independently checks again).
- No changes to I1 runtime, existing loopback CAS protocol, R2.5 signing/publisher, R2.6 reconciliation, World/Mind/BodyLaws, I3 engine, manifest, scientific originals, authorizations or registry.

## Frozen adversarial acceptance matrix

| Case | Required observation |
| --- | --- |
| Live TLS loopback with ephemeral test CA, hostname SAN and test-pinned signature; R2.6 local equality | PASS as **read-only diagnostic**, explicit motor=false and M11=false |
| Unknown CA, wrong hostname/SAN, invalid URL or missing CA file | REJECT; no insecure bypass |
| HTTP 302/4xx/5xx or absent/invalid/mismatched Content-Length | REJECT; **no redirect** and no retry |
| Absent/wrong Content-Type, cache policy, compressed/chunked or oversized bytes | REJECT; bounded body |
| TLS connection closes, network partition/timeouts or malformed response | REJECT/STOP; never fall back to local |
| Authenticated HTTPS serves old signature while publisher/authority advance | R2.6 **REJECT** on stale witness, despite valid cert/signature |
| Wrong Ed25519 public key/issuer/source/authority or altered signed payload | REJECT |
| Both local SQLite databases **and** the loopback service's latest signed reply are restored together | **ACCEPT negative** `FAIL_INDEPENDENT_M11`, even with valid TLS/Ed25519 |
| Actually distinct host/administrator, external monotonic storage, protected key, mTLS writer admission, revocation and cross-host rollback/partition | **NOT_RUN / NOT_ATTESTED** |

**Stop rules:** a failure in security/functional tests must be repaired at a new head and rerun. Require exact-head Python 3.11 + Python 3.12 full I3 software checks (test-only crypto is already installed) and static generation/navigation guards. No synthetic test fixture is called an independently deployed M11. Keep #1339 and #1331 OPEN; P1.3 funded-v2 Stage 2.1 science remains `NOT_ISSUED/HOLD_NO_VERDICT`, I3 reference-but-`NOT_REGISTERED_NOT_EXECUTABLE`, I1 active and all World/index/cohort permission flags false.
