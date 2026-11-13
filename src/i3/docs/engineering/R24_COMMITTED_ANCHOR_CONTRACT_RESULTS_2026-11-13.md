# I3 R2.4: optional committed-anchor interface and three-store rollback fault verification

**Date:** 13 November 2026. **Scope:** engineering-only identity/motor custody, not a scientific result or I3 release. **Result:** `COMMITTED_ANCHOR_INTERFACE_SOFTWARE_PASS`, independently deployed M11 anti-rollback **NOT_RUN / NOT_ATTESTED**. I3 remains the selected development reference, I1 the active engine, P1.3 funded-v2 unchanged, and scientific Stage 2.1 `NOT_ISSUED`.

## Source and execution provenance

- [Frozen pre-implementation contract](R24_COMMITTED_ANCHOR_CONTRACT_PREFLIGHT_2026-11-13.md): branch `engineering/i3-r24-committed-anchor-contract-20261113` first preflight commit **`12aaaac215955241d5af87005cac484999173f4b`**, based on main `24dadc509e3a96339def0ddb5f68c257feeabf08`. Historical scientific E3/DEV originals were not reused.
- [PR #1360](https://github.com/josselin-orta-lab/individual-zero/pull/1360), exact CI-tested head **`4cd47bbb585ecbab2058cb3a90ce0f0e62c39c45`**, source change confined to [`engineering_remote_witness.py`](../../runtime/engineering_remote_witness.py), [five adversarial tests](../../../../tests/i3/test_engineering_remote_committed_anchor.py) and preflight. Squash merged to `main` at **`89a7ef8025e28bf585e6e03977b393284a256515`**.
- [GitHub Actions #43398453113](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43398453113), tested **the exact pre-merge PR source head**:
  - Python 3.11 software job `131795033150`: **1,297 / 1,297 tests OK**, 178.895 seconds, repository/navigation checks PASS.
  - Python 3.12 software job `131795033774`: **1,297 / 1,297 tests OK**, 142.430 seconds.
  - All **five new** `test_engineering_remote_committed_anchor.py` cases passed in each environment. No scientific generation job authorized or executed by this PR. The two-platform CI does not constitute deployment validation or independent review.

## What changed, exact contract

An optional `commit_anchor` interface can now be passed to `RemoteEngineeringWitness`; it must implement `assert_current(authenticated_committed_receipt)` and `publish(authenticated_committed_receipt)`. The default remains `None`, preserving existing engineering behavior and **not providing a safety guarantee**. The trusted host/operator must later supply a truly independent, durable service implementation and its authentication.

1. After authenticated `register`, the exact genesis is **published** to the caller-provided pin before success is reported.
2. A `verify` must agree with the exact native local ledger **and** the retained committed pin before a new native action. In pin mode, the `prepare` path independently repeats this authenticated check before contacting the authority for PREPARED, preventing a stale previous local view from substituting for remote attestation. This creates **an extra network request** per prepared step in opt-in mode; no physiological CPU-to-energy tariff calibration is claimed.
3. Only after a genuine locally settled `POST_PAID_LEARNING` step, authenticated remote `commit` and matching exact local head does the client publish the next committed pin.
4. Any exception from the pin propagates. If the remote commit has already occurred but pin publication fails, the original native session stops; it **must not assume the action was unexecuted or retry the motor**. An independent reconciliation could later be designed but is not implemented.
5. No Mind, World, BodyLaws, genotype, native Action Control, active registry or scientific source was changed. The native receipt still explicitly reports `independent_m11_antirollback=False`.

## Engineering fault matrix, all five newly executed tests PASS

| Fault / control | Observed software outcome | Interpretation |
| --- | --- | --- |
| Normal remote CAS, two authentic paid steps, cold reconstruct then continue | Steps 1/2 receipts and head match, further step permitted | Preserves native action autonomy and physical settlement in **test** World |
| **Both local stores AND remote authority DB** rolled back to a coherent earlier image, while **volatile test pin remains newer** | Reconstruction refuses before new `World.step` with `external committed high-water mismatch` | A **separately retained** high-water can distinguish a three-store rollback; the test pin is **not durable or independent M11** |
| Remote COMMITTED, then pin publication acknowledgement fails | Exactly one actual `World.step`, local receipt sealed, session blocked, cold reconstruction also denied until independent reconciliation | No speculative replay of uncertain motor |
| Pin unavailable before native motor | Permission denied, zero new native `World.step`, ledger sequence remains zero, old session cannot resume | Fail-closed on loss of required off-path evidence |
| Invalid pin interface and default without pin | Invalid contract rejected; unpinned client retains old engineering mode, no M11 release flag | The new hook does not silently promote all existing clients |

The test pin is an **in-memory Python object retained by the test process**, capable of remembering a greater `sequence/head` while SQLite snapshots are reverted. It has neither protected off-host persistence, an independent administrative principal, secret rotation, server-only signing key, nor proof that the remote host was beyond an adversary's rollback domain. Thus the test only shows **conditional software detectability**. If both test pin and authority are rolled back, this test offers no protection. No external remote rollback defense has been demonstrated on a deployed service.

## Release blockers and economical next dependency

- **R2.4 independent authority remains OPEN.** Provision a third protected, independently administered monotonic anchor (or equivalent protected audit storage), attest its endpoint and signing identity separately from local client secrets, then test cold restart and **simultaneous rollback of all unprotected stores**. Document cryptographic trust, permissions, rotation, failure/reconciliation procedure, external audit and throughput of the extra verified roundtrip.
- Measure the O(total events) authority audit cost and native state reconstruction under longer engineering workloads before production; never treat host CPU measurements as physiology joules without explicit tariff assumptions.
- The genuine independent M11 release/fault and disaster-recovery matrix is still NOT_RUN. Do not register I3 active, migrate I1 lives, or change Stage-2 science as a consequence of this software PASS.

**Stop rule:** no repeated artificial source permutations or new scientific birth for this runtime change. The next M11 PASS requires concrete off-host infrastructure and verified independent custody, not another same-machine test dressed as an independent reviewer.
