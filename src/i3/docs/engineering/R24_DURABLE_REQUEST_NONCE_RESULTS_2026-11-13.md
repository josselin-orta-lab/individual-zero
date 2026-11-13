# I3 R2.4: durable server-side request nonce, exact-source software results

**Date:** 13 November 2026. **Engineering-only result:** \`R24_SERVER_REQUEST_NONCE_SOFTWARE_PASS\`. **Independent monotonic M11:** \`NOT_ATTESTED\`; full authority-store rollback **still succeeds** (\`FAIL_INDEPENDENT_M11\`). **Scientific Stage 2.1 verdict:** \`NOT_ISSUED\`.

## Source custody and verified execution

- Frozen pre-implementation falsifiers: [R24 durable request nonce preflight](R24_DURABLE_REQUEST_NONCE_PREFLIGHT_2026-11-13.md), committed **before** code at \`140c057993cc799c32950a90cf37fcd6d738bc05\`.
- [PR #1365](https://github.com/josselin-orta-lab/individual-zero/pull/1365): exact tested PR source head \`dc7c023f9c528c33799db97530c8a0d8ed84efa2\`, squash merged to \`main\` at \`a63f40db2f72409ceb808531cc017d98733a330f\`.
- [Actions #43414788550](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43414788550): **SUCCESS**, two exact-source software jobs:
  - Python 3.11, job \`131849844956\`: **1,320 / 1,320** tests, 162.557 s, navigation and immutable generation contract checks PASS.
  - Python 3.12, job \`131849845333\`: **1,320 / 1,320** tests, 198.955 s, immutable generation contract checks PASS. The separate navigation step is conditional to Python 3.11.
  - Ten new tests in \`test_engineering_remote_request_nonce.py\` PASS under each interpreter, including duplicates, bad signatures, concurrent senders, process-equivalent service restart, failed CAS, non-migration and negative full-database rollback. Historical 1,310 I3 tests continue to pass.
- This results document is a **post-merge interpretation**, not part of the exact CI-tested PR source. No scientific runner, World or old cohort was launched for the new server-nonce tests.

## Technical change and observable matrix

The loopback-only \`AuthorityStore\` in [engineering_remote_authority.py](../../lab/engineering_remote_authority.py) moves from **v2** to **v3**, refusing older DBs rather than silently migrating them. A new \`request_nonces(nonce, request_sha256)\` table records each successfully authenticated 32-character lowercase hexadecimal HTTP request nonce as part of the same SQLite transaction as its \`register\`, \`prepare\`, \`commit\` or \`verify\` operation. A failed command rolls back the nonce. Each committed nonce is unique **globally for the test authority**, not only within one life/operation. The already-authenticated client request/response HMAC, response nonce, CAS wire protocol and original I3 engine policy remain unchanged.

| Frozen falsifier / control | Observed software result | Interpretation |
| --- | --- | --- |
| Normal signed CAS and fresh-nonce \`verify\` | PASS, original tests remain green | Original loopback engineering protocol remains usable |
| Reuse of identical signed HTTP \`verify\` nonce | REJECTED with 409 | Successful requests cannot be repeated while the v3 store is retained |
| Replay after stopping/recreating loopback service over retained disk DB | REJECTED with 409 | Restart within same rollback domain retains nonce history; **not** separate-host custody |
| Reuse across different operation or engineering birth claim | REJECTED | Nonce uniqueness is per authority database |
| Invalid HMAC and failed CAS followed by a valid request with same nonce | Previous refusal, then valid request ACCEPTED | No false nonce consumption on unsuccessful transaction |
| Two concurrent, validly signed requests with identical nonce | Exactly one 200 and one 409 | SQLite serializes nonce acceptance; no duplicate successful receipt |
| \`verify\` audit-event count | No extra motor/CAS audit event | It **does** write one durable nonce row; this costs storage/IO and is no longer storage-read-only |
| Old v2 schema reopened as v3 | REJECTED | No silent migration of historical test authority stores |
| **Full old SQLite file restored**, including CAS head, transition audit and nonce history | Previously consumed nonce **ACCEPTED again** | **Expected negative**: this is \`FAIL_INDEPENDENT_M11\`, not a release PASS |
| Actual separately administered host, protected keys, independent backups/rollback, source/operator attestation and long-life throughput | **NOT_RUN / NOT_ATTESTED** | No real M11 release acceptance |

The negative rollback result is deliberately represented by a **passing regression test** that expects the wrong-world security property to remain *unmet*. This does not make the external trust objective PASS. Nonce rows and their hashes share the same alterable SQLite file; an administrator able to restore or rewrite the file can erase request memory and replay a previously signed request. Signature/HMAC strength is limited to the existing test-key trust assumption; the server still uses \`127.0.0.1\` and a CLI-supplied shared test secret.

## New operational cost and pending falsification

Every successful authenticated \`verify\` now writes a durable nonce row even though the CAS audit chain remains unchanged; the on-disk nonce set grows with **successful requests**, and v3 uses \`BEGIN IMMEDIATE\`. The exact test suite durations above measure the **whole software suite**, not the per-request service cost or a native cognition-energy tariff. No normalized throughput claim is made. A release benchmark must measure SQLite size/latency/lock contention, long-lived reconstruction and secure rotation/pruning/checkpoint policy without restoring replayability. Do not delete accepted nonce history merely for speed.

## Governance and next release boundary

**Unchanged after code merge:** \`reference_generation=I3\`, \`active_generation=I1\`, I3 \`engine.status=proposal\`, \`activation=NOT_REGISTERED_NOT_EXECUTABLE\`, \`entrypoints={}\`; P1.3 funded-v2 scientific reference, Stage 2.1 \`REPLAY_GATE_CAPACITY_SHOWN\` software status and scientific \`NOT_ISSUED\` / \`HOLD_NO_VERDICT\`. All new scientific World/index/cohort authorities remain false. Original E1/E3 negatives and prior cohort archives are untouched.

**Next gate (#1339 / #1331):** independently administered, protected monotonic storage and attested endpoint/credential lifecycle, including combined local/server backup-rollback, partitions, ambiguous native motor and cold recovery under actual distinct host privileges. Separately measure bounded-state cost before a dedicated engine release PR. Neither a v3 nonce journal nor this test-suite PASS permits i3 activation or scientific Stage 2 promotion.
