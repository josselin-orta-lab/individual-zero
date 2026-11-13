# R2.4 / #1339: detached Ed25519 checkpoint receipt + monotonic acceptance preflight

**Frozen date:** 13 November 2026. **Type:** engineering-only, test-signer software contract; **not** an external M11 attestation, source admission, protected key, deployment, motor authorization, scientific World or Stage-2 promotion. **Baseline:** R24_READONLY_CHECKPOINT_INSPECTION_RESULTS_2026-11-13.md and existing I3 checkpoint probe v1.

## Primary question and trust boundary

Can a caller require a strictly shaped, source- and authority-bound **asymmetrically signed** receipt for an existing fully audited v3 COMMITTED checkpoint, then refuse replays or forks relative to a **separately held later high-water**? A genuine Ed25519 signature proves control of the matching key at some point, **not independent custody, freshness, current server authority, physical life or anti-rollback by itself**. Caller must provide a separately trusted exact 32-byte public key, expected issuer key ID, source SHA-256 and authority. No key bootstrap from receipt metadata, no permissive fallback, and no secret in source, console or CI.

**Protocol:** `i3-remote-cas-signed-checkpoint-receipt/v1`. Envelope is exactly `{schema,payload,signature}`, Ed25519 signature covers canonical UTF-8 JSON of `{schema,payload}` with domain separation and strict fields. Payload is `{authority_id,source_sha256,key_id,publication_index,previous_receipt_sha256,checkpoint}`. Checkpoint is exactly the existing v1 fully audited public snapshot, including authority ID, audit ordinal/head, identities/history digest, accepted nonce digest/count, checksum. Signature `{algorithm,key_id,value}` is base64-encoded exact 64 bytes. Publication indices are positive ordinary integers; no bool coercions. The `previous_receipt_sha256` is SHA-256 of **canonical complete previous signed envelope**, so cross-key rotation needs independent custody policy and cannot silently rebind.

A receiver's acceptance needs (1) a valid pinned Ed25519 public key, pinned authority/source/key-ID, (2) an externally retained **latest signed receipt** / last accepted index, (3) next index exactly +1, previous full-receipt digest equal to retained latest, and (4) the new checkpoint forward-consistent: audit ordinal nondecreasing, accepted-nonce count nondecreasing, at least one strictly increasing, plus a changed checkpoint checksum. This is a narrow *step-by-step* monotonic software acceptance protocol, not a production history compactor, proof of causal lineage between arbitrary snapshots, nor a key-rotation implementation. For first receipt, index=1 and previous digest exactly 64 zeros, with explicit genesis admission.

**No network authority change:** this slice provides a **verifier** and an explicit *test-only* signer in tests, never a deployed signing endpoint or a private key in production code. The existing client shared-HMAC CAS protocol, SQLite writer, read-only capture, scientific repositories, World/Mind/BodyLaws, engine, registry and permissions remain unchanged. Add a test-only cryptography dependency (`cryptography>=42,<47`) through a scoped requirements file and exact-source I3 CI step; import failure must fail closed, never skip the security test.

## Frozen adversarial cases

| Case | Expected |
| --- | --- |
| Fresh v3 COMMITTED record signed by ephemeral test key | Verification PASS for exactly pinned public key, authority, source and issuer key ID |
| Same receipt with altered source/authority/checkpoint/sequence/signature | DENY with no fallback |
| Signer/key ID swapped or untrusted public key | DENY |
| Receipt after legitimate next accepted verify nonce | ACCEPT *only* with fresh index, previous full signed receipt digest and monotonic accepted-nonce count |
| Signed fork: same index, wrong previous digest, skipped index, equal checkpoint, ordinal/nonce regression | DENY even though Ed25519 signature verifies |
| Signed old receipt + older coherent DB and old public checkpoint, latest separately retained | DENY against surviving latest, including unchanged signature |
| Old DB + old signed receipt + **old external retained high-water** all rolled back | Intentionally ACCEPT negative control: `FAIL_INDEPENDENT_M11` |
| Malformed JSON / duplicate keys / non-canonical wire input / invalid base64 | DENY before receipt use |
| Missing crypto dependency or invalid public key length | DENY; no HMAC/unsigned fallback |
| Actual independently operated remote authority, protected keys/high-water, signed server publication, revocation, real cross-host restore | `NOT_RUN / NOT_ATTESTED` |

**Stop criteria:** exact-source Python 3.11 and 3.12 full I3 suite and navigation GREEN; no skipped crypto test, no E3/Stage-2 cohort, no source/index authorization. On failure, fix fixture or code and rerun from new SHA before merging. Explicitly retain negative same-domain rollback. No scientific conclusion: `NOT_ISSUED / HOLD_NO_VERDICT`, P1.3 funded-v2 remains; I3 architectural reference, I1 active.
