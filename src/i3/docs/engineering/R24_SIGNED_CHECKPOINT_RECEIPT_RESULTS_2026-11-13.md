# I3 R2.4: pinned Ed25519 signed checkpoint receipt, software evidence

**Date:** 13 November 2026. **Outcome:** `R24_SIGNED_CHECKPOINT_RECEIPT_SOFTWARE_PASS`. **Actual independent M11:** `NOT_ATTESTED`, with explicit `FAIL_INDEPENDENT_M11` when all rollback domains are restored. **Stage 2.1 science:** `NOT_ISSUED`, general `HOLD_NO_VERDICT`. No new scientific World, cohort, birth, experimental source/index or activation.

## Source custody and exact test execution

- [Signed receipt preflight](R24_SIGNED_CHECKPOINT_RECEIPT_PREFLIGHT_2026-11-13.md) committed **before implementation** at `54aca12da40d26d5ab925ff3af2cb8a6b1993bd1`.
- [PR #1374](https://github.com/josselin-orta-lab/individual-zero/pull/1374), exact tested head **`a4f4eabbc6318a971d1757f63195780698b4ecb3`**, squash merged to `main` at **`8fe2c41810aaa707b6bbb1ac5bf678030cce1eba`**.
- Exact-source [Actions #43434015538](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43434015538) **SUCCESS**: Python 3.11 job `131914392510` **1,346/1,346 I3 tests PASS** (98.515 seconds test step), Python 3.12 job `131914392973` **1,346/1,346 PASS** (201.311 seconds test step). Cryptography dependency installation and engine/generation contracts PASS for both; navigation PASS under Python 3.11. **All ten new no-World receipt tests executed and passed on both.**
- Test-only dependency `cryptography>=42,<47` is declared at [tests/i3/requirements-attestation.txt](../../../../tests/i3/requirements-attestation.txt) and installed only by the I3 software workflow. **Not** a managed production key, deployed signer or frozen production release dependency lock. This interpretation was written *after* the tested code SHA and is not a new test of the report itself.

## Exact module scope

[engineering_remote_signed_checkpoint_receipt.py](../../lab/engineering_remote_signed_checkpoint_receipt.py) checks an **Ed25519 detached signature** over domain-separated canonical UTF-8 JSON, with no private key in runtime source. Each v1 envelope includes `authority_id`, `source_sha256`, approved `key_id`, positive `publication_index`, `previous_receipt_sha256` over **the entire prior signed receipt**, plus the full existing v1 public checkpoint. The verifier requires a 32-byte independently supplied public key and exact expected authority/source/issuer ID; rejects duplicate JSON keys, noncanonical bytes, invalid signature encoding, wrong type/algorithm and missing cryptographic library.

The **limited advance check** also requires:
1. Explicit index `1`, zero previous hash for first-time admission, or exactly prior index + 1 and prior entire signed-receipt digest if `retained_latest_raw` is supplied.
2. Audit ordinal and accepted nonce count nondecreasing, with at least one strictly increasing and a changed checkpoint checksum.
3. **Exact equality against the current SQLite v3 read-only audited state** before accepting that receipt.

This is a **software contract**, not a real trust root. The signer in unit tests is an ephemeral test key generated in the test process; the library does **not** produce receipts or deploy a signing endpoint. The `source_sha256` is an **issuer assertion under signature**, not independent proof of source authenticity and not, by itself, a verification that each entry in an authority's multi-life `claim_json` originated from that source. Current comparison requires a valid state and integrity digest, **not** a mathematical proof that all later history is a causal extension of the previous one.

## Adversarial result matrix

| Case | Observed under both interpreters | Valid interpretation |
| --- | --- | --- |
| Properly signed v3 checkpoint with explicitly pinned Ed25519 key, issuer, authority and source | PASS | Signer key possession checked; no off-host attestation |
| Signed new `verify` nonce state, exact index +1, prior full-receipt digest | PASS | Logical forward check when retained high-water survives |
| Wrong public key/key ID/source/authority or foreign signing key | REJECT | No automatic signer trust from supplied receipt |
| Payload/checkpoint/signature tampered, bool index, invalid base64/shape/duplicate/noncanonical JSON | REJECT | Strict parsing and signature checks |
| Signed fork, repeated index, skipped index, wrong predecessor or unchanged/regressed checkpoint | REJECT | Signature alone does not authorize a duplicate, jump or fork |
| Signed earlier checkpoint that no longer matches SQLite | REJECT | Still requires current, fully audited authority snapshot |
| Crypto verification module deliberately unavailable | REJECT | No unsigned or HMAC fallback |
| Old authority/old signed receipt restored, **later signed receipt retained outside rollback scope** | REJECT | Conditional detection by externally surviving reference |
| **Old authority and old signed receipt and old retained high-water restored together** | **ACCEPT negative** | **`FAIL_INDEPENDENT_M11`**: no protected monotonic counter actually exists here |
| Separate signer host, private-key HSM/KMS custody, independently immutable receipt publication, compromised key, source admission, rotation/revocation, full network crash/partition | **NOT_RUN / NOT_ATTESTED** | Cannot claim M11 release or physical truth |

## Residual trust and performance gates

- **No real independent trust domain:** the caller chooses the pinned public key and passes the prior receipt bytes. If those inputs are themselves under the rollback adversary's control, a correctly signed old history can be accepted again; all old local/remote rollback counterexamples stay valid.
- **Key-lifecycle and signed source:** no hosted signer, protected private key, certificate, externally attested source or writer admission exists. The v1 chain intentionally does not silently support key rotation: a future protocol must define witnessed rotation and revocation without treating new key IDs as automatic trust.
- **Publication atomicity:** the code doesn't atomically publish accepted high-water to a protected service, retry an ambiguous motor or authorize a new World. A crash after signature but before independently durable publication remains a release STOP.
- **Cost:** all original full-chain SQLite audit and accepted nonce checks remain. The module adds signature verification but no O(1) hot-path optimization; host CPU cost is not the individual's endogenous paid cognition budget.
- **Production evidence required:** separately administered signer/authority storage; pinned release source and operator inventory; protected monotonic high-water independent of i3; cross-host key/DB/full-rollback, stale writer, network partition, crash/ambiguous-motor test matrix; long-life throughput; source-specific owner authority for any scientific World.

**Governance unchanged:** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remain **OPEN**. `reference_generation=I3`, `active_generation=I1`, I3 `engine.status=proposal` and `activation=NOT_REGISTERED_NOT_EXECUTABLE` with no entrypoints. P1.3 funded-v2 remains the scientific reference and no new World/index/cohort permission is created.
