# I3 R2.5: source-bound, serialized signed checkpoint publication, software results

**Date:** 13 November 2026. **Result:** `R25_LOCAL_PUBLICATION_CAS_SOFTWARE_PASS` on a test-only publisher. **Independent M11:** `NOT_ATTESTED`, with intentional `FAIL_INDEPENDENT_M11` on a full coherent rollback of both local SQLite files and caller-held high-water. **Scientific Stage 2.1:** `NOT_ISSUED / HOLD_NO_VERDICT`. Zero World, zero scientific life, no generation activation or prospective cohort permission.

## Preannounced source and exact CI

- Frozen test protocol **before implementation**: [R25 atomic publication preflight](R25_ATOMIC_RECEIPT_PUBLICATION_PREFLIGHT_2026-11-13.md), committed at `2380f48afb1963ff3430cb9ed617b46db6c56f15`. It explicitly requires the negative full-domain rollback control.
- [PR #1376](https://github.com/josselin-orta-lab/individual-zero/pull/1376), exact CI-tested head **`9cd9c9591b2d1cd197f2521595adc390cdfd08d9`**, squash-merged into `main` at **`dd400b88682492ed70ccc9bb17415fc249866885`**.
- [Actions #43442194291](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43442194291) **SUCCESS** on that exact head: Python **3.11 job `131942359964`: 1,357 / 1,357 I3 software tests PASS**, test step 136.398 s and navigation PASS; Python **3.12 job `131942360230`: 1,357 / 1,357 PASS**, test step 111.421 s. All **eleven** new publisher fault tests PASS on both interpreters, previous 1,346 regression tests and engine/generation ownership checks remain green. This report was added **after** the tested PR head, not retroactively executed with the source SHA.
- All tests are engineering-only. No scientific runner or new World/individual was launched. Test Ed25519 key is ephemeral in unit tests and does not attest a distinct operator or deployed cryptographic service.

## Technical change, precise trust scope

[engineering_remote_checkpoint_probe.py](../../lab/engineering_remote_checkpoint_probe.py) accepts an **optional** `expected_source_sha256` for exact checkpoint capture. Inside the **same full-audit SQLite read transaction**, every canonical `histories.claim_json` source SHA is compared with the expected issuer source. The pre-existing capture API without this option keeps its behavior. Matching these **locally asserted claim bytes** is not independent verification of a build, input source, world or scientific provenance.

[engineering_remote_checkpoint_publisher.py](../../lab/engineering_remote_checkpoint_publisher.py) introduces `TestOnlyCheckpointPublisher`, **a local reference prototype** with **a separate SQLite file** from the v3 CAS authority, a strict v1 metadata schema bound to authority, source, issuer ID and pinned Ed25519 public-key digest, and an externally supplied *test signer callback*. No private key is written to this repo or to the publication store.

- On `publish(expected_previous_receipt_sha256)`, a publisher `BEGIN IMMEDIATE` serializes writers. It validates the **complete existing signed publication chain**, index continuity, prior full signed-receipt hash, pinned issuer and monotonic audit/nonce counts; rejects an incorrect caller predecessor; captures the existing fully audited `COMMITTED`, source-consistent v3 checkpoint; signs a canonical, domain-separated Ed25519 receipt using the injected test signer; authenticates the returned signature against its pinned public key; verifies exact audited-state equality and monotonic progression; then **commits the signed receipt and its digest in one publisher SQLite transaction**.
- `latest()` uses a read-only publication connection and revalidates the entire chain, so after an ACK is lost a caller can inspect what was committed. This inspection **must not** automatically repeat an ambiguous paid motor.
- There is **no cross-DB atomic transaction** between CAS authority and publication store. A CAS writer can advance after the publisher's final equality check; consuming parties must not treat the result as a simultaneously locked cross-host state. There is no network transport, mTLS/CA attestation, protected signer hardware, operator inventory, credential revocation, rotation, full crash/partition replay gate or production release. The full-chain checks are not optimized away.

## Adversarial matrix (executed, both Python versions)

| Precommitted falsifier | Observed result | Scope |
| --- | --- | --- |
| Source-consistent COMMITTED genesis and subsequent new accepted `verify` | **PASS**, signed indices 1 and 2, correct previous full-receipt digest, exact nonce count, cold restart parity | Durable logical publication within same test trust domain |
| Two concurrent publishers using the same expected predecessor | Exactly one **ACCEPT**, one **REJECT** | One SQLite writer transaction serializes publication |
| Caller loses response after publication COMMIT, then creates publisher again | `latest()` returns the committed exact receipt; stale retry **REJECTS** | Observation only; no motor retry or distributed exactly-once guarantee |
| Signer raises or wrong test signing key provided | **REJECT** and no signed receipt row; later legitimate attempt **ACCEPT** | Atomic rollback of local publisher transaction |
| New publication with no changed authority state | **REJECT** | No duplicate checkpoint dressed as fresh high-water |
| CAS authority `PREPARED` or tampered audit/head | **REJECT** | Ambiguous/potentially corrupt motor state not signable |
| Additional registered identity with a foreign `source_sha256` | **REJECT** | Every stored claim source in the same audited read snapshot is checked |
| Publisher receipt/digest mutation, wrong metadata/public key/source, missing authority, or same CAS/publisher DB file | **REJECT** | Schema, trust pins and distinct-path checks fail closed |
| Authority SQLite alone restored to an earlier valid state while newer publisher state survives | **REJECT** on next publication | Conditional rollback protection when the publication store and expected head survive |
| **Authority SQLite and publisher SQLite and caller expectation restored together** | **ACCEPT** the earlier branch, deliberate test **PASS** | **`FAIL_INDEPENDENT_M11`**: no independent anti-rollback anchor demonstrated |
| Real separate host/admin, independently protected monotonic high-water, HSM/KMS signer, source/operator admission, network partitions and disaster recovery | **NOT_RUN / NOT_ATTESTED** | No M11 engineering release allowed |

## Decision and next test boundary

**ACCEPT as software engineering:** a source-checked local publisher transaction and a distinct local persistent publication log, with the planned negative controls. **Do not close** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) or parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331). A separate SQLite filename is **not** a separate administrative principal.

The next genuine M11 gate must declare and demonstrate an independently controlled issuer and immutable/high-water service, pinned build and operator identity, protected key lifecycle and disaster recovery, plus two-phase motor fault injection across genuinely distinct hosts. A source SHA in an attested message is not itself proof that the binary or physics was sourced externally. Publication after an irrevocable paid motor is a separate non-retry problem; STOP must remain available for an ambiguous response. Real host CPU/disk/transport and cognition energy/vigilance are different tariffs. Do not introduce journal pruning or a hot-path checkpoint shortcut before this evidence.

**Governance rechecked on `main`:** `reference_generation=I3`, `active_generation=I1`, I3 `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE` with empty entrypoints; P1.3 funded-v2 reference, Stage 2.1 technical replay-gate-only capacity but scientific `NOT_ISSUED`, general `HOLD_NO_VERDICT`. `fresh_lived_worlds_allowed=false`, `scientific_gate_authorized=false`, `next_scientific_cohort_authorized=false`. No original cohorts, authorizations or physiological policies changed.
