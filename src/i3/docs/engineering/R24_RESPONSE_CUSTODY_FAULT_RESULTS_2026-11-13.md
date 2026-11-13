# I3 R2.4 signed-response custody and full-domain rollback falsification

**Date:** 13 November 2026. **Scope:** exact-source engineering-only software/negative-control result. **Technical status:** `R24_RESPONSE_CUSTODY_SOFTWARE_PASS`; **independently anchored M11:** `NOT_ATTESTED` / **negative full-domain rollback:** `FAIL_INDEPENDENT_M11`. Scientific Stage 2.1 remains `NOT_ISSUED`.

## Source, custody and execution

- Frozen before implementation: [R2.4 response and rollback preflight](R24_RESPONSE_CUSTODY_FAULT_PREFLIGHT_2026-11-13.md), first committed at `45147d22f36cf6637abd81b4d2648f2a81530b21`.
- [PR #1363](https://github.com/josselin-orta-lab/individual-zero/pull/1363), exact CI-tested **code head** `5cea3951831b82cc6926fc0b522dcdac81714ee8`, squash merged to **main** `2815e6d5909d9a9d23fa928061d4db1784c5e6fb`.
- Exact-source [Actions #43411537219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43411537219) **SUCCESS**:
  - Python 3.11 job `131838888859`: 1,310/1,310 I3 tests OK in 103.345 seconds, contract/navigation guards PASS.
  - Python 3.12 job `131838889232`: 1,310/1,310 I3 tests OK in 118.024 seconds, contract/navigation guards PASS.
  - New tests: five signed-response tests with **zero World**, one existing technical-World rollback test added, all PASS under both interpreters.
- No scientific launcher or birth was executed; no new cohorts, indices, genome, Life, Mind or BodyLaws policy changes. This **result document** is additive after the tested code commit and is not itself counted as tested code evidence.

## What the client now rejects

[RemoteEngineeringWitness](../../runtime/engineering_remote_witness.py) already verifies a request-nonce-bound HMAC, canonical response bytes, authority identity and basic state. It now **also** enforces a complete mutually exclusive state shape before returning an authenticated response:

| Network reply | Required invariant | Test outcome |
| --- | --- | --- |
| `COMMITTED` | Both `pending_sequence` and `pending_intent_sha256` are exactly `null` | PASS, malformed signed response denied |
| `PREPARED` | `terminal=OPEN`, pending sequence exactly `int` and equal to committed sequence + 1, pending digest 64 lowercase hex | PASS, malformed signed response denied |
| Any signed reply | Reused signed answer bound to old request nonce N1 must fail against N2 | PASS, prior HMAC rejected |
| Any signed reply | Wrong authority ID, invalid sequence type or terminal state | PASS, malformed signed response denied |

All test signatures use a fixed **test key**. This is protocol consistency and response replay resistance within the assumed key trust boundary, not evidence that the key, authority or client process has independent custody. The server's request-nonce persistence, cryptographic credential lifecycle, external endpoint attestation and host trust domain remain unsolved production questions.

## Key negative control: entire rollback domain can replay history

The new `test_complete_rollback_including_volatile_pin_is_not_independent_m11` in [the R2.4 fault tests](../../../../tests/i3/test_engineering_remote_committed_anchor.py) is intentionally an **acceptance of an attack**:

1. Start an I3 native *engineering-only* local synthetic World; complete sequence 1 with POST_PAID_LEARNING.
2. Save coherent backups of local birth SQLite, local journal SQLite, remote authority SQLite and the current **volatile Python pin**.
3. Complete native sequence 2, then stop the test authority.
4. Restore **all four** old state-bearing objects, including the pin, restart the service and cold-reconstruct from sequence 1.
5. **Observed:** the old state verifies, reconstructs, and accepts another technical sequence-2 motor. The receipt still declares `independent_m11_antirollback=False`.

This is a **FAIL for the independent M11 hypothesis**, although the regression *test* is PASS because it checks the known missing security guarantee. By contrast, the older positive control restores only the three SQLite stores while leaving a newer pin; that fails closed before another action. **A pin in the same rollback domain is no independent witness.**

## Remaining R2.4 release gates

1. A protected monotonic, independently administered/off-host authority or immutable external source, with attested endpoint, source, writer and signing keys that are **not** controlled by the rollback adversary.
2. Protected secret provisioning, rotation and revocation; no production use of CLI-supplied shared HMAC test secrets or `127.0.0.1` loopback implementation as an external server.
3. Exact cross-host crash, network partition, stale-writer, concurrent-writer, partial/complete authority rollback, backup/restore and external motor exactly-once matrix, including irrecoverable STOP.
4. Measured authority full-audit and long-life reconstruction cost, and justified bounded-state high-water checkpointing without losing source, terminal or anti-replay evidence.
5. Exact-source release acceptance of an actual independently anchored M11 implementation under #1339/#1331, then **separately** an active I3 engine release. No stage-science verdict is inferred.

**Governance after merge:** `reference_generation=I3`, `active_generation=I1`; I3 still `engine.status=proposal`, `entrypoints={}`, `NOT_REGISTERED_NOT_EXECUTABLE`. P1.3 funded-v2 retains Stage 2.1 `REPLAY_GATE_CAPACITY_SHOWN` as **software capacity**, scientific verdict `NOT_ISSUED`; `fresh_lived_worlds_allowed=false` and `next_scientific_cohort_authorized=false`. Closed E1/E3 and historical study originals remain unchanged. [ADR-0021](../../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) authorizes no new World.

**Follow-up:** [issue #1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339), parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331). They remain **OPEN** until the separate trust domain is actually demonstrated.
