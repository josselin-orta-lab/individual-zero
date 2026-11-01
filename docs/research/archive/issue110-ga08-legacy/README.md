# GA08 Issue 110: historical source snapshot

**Navigation-only inventory**, observed on main commit `c16a352d41ba5aba16fe451cd334ab400e81508a` (1 November 2026). This is not an independent provenance attestation, a complete execution environment, or a scientific verdict. Source bytes below remain unchanged; the blob hashes are those returned by GitHub for the current archived paths.

## Exact archived files (12)

| Historical relative path | Git blob SHA-1 |
| --- | --- |
| [`.github/workflows/stage12-ga08-physical-science.yml`](.github/workflows/stage12-ga08-physical-science.yml) | `bc5289eb96b96062aa5059983d337a31381e56dc` |
| [`.github/workflows/stage12-ga08-return-goal-science.yml`](.github/workflows/stage12-ga08-return-goal-science.yml) | `e43b1dc5a653fcc7e96c1026ba59c24f6135334f` |
| [`.github/workflows/stage12-ga08-spatial.yml`](.github/workflows/stage12-ga08-spatial.yml) | `e8e5a1036c7daf95de529ba989d4a85eb145744f` |
| [`scripts/run_stage12_issue110_ga08_return_goal_science.py`](scripts/run_stage12_issue110_ga08_return_goal_science.py) | `64feb26fa48478da49e8c8fe113287f8658ce65d` |
| [`scripts/run_stage12_issue110_ga08_spatial_science.py`](scripts/run_stage12_issue110_ga08_spatial_science.py) | `4280d691750f23a185f9ba9a2a01e506c257b604` |
| [`src/i0/modules/stage12_spatial_goal_evidence.py`](src/i0/modules/stage12_spatial_goal_evidence.py) | `37fe9c77810bd2a1d229c30c1673167b2344321d` |
| [`src/lab/stage12_spatial_provenance_audit.py`](src/lab/stage12_spatial_provenance_audit.py) | `fac173d53ad40c7c99c9a19961ddcc5e84ff3652` |
| [`tests/test_stage12_ga08_m11_recovery.py`](tests/test_stage12_ga08_m11_recovery.py) | `8614282c113c4052959150ac42a7bf538b9795e5` |
| [`tests/test_stage12_ga08_owner_runtime.py`](tests/test_stage12_ga08_owner_runtime.py) | `0ebc89663c82f0f015027a304ae2ff1f843b9d04` |
| [`tests/test_stage12_ga08_physical_fixture.py`](tests/test_stage12_ga08_physical_fixture.py) | `eef8df3994396807833140d09f921f6c0be8d671` |
| [`tests/test_stage12_ga08_rehashed_semantic_audit.py`](tests/test_stage12_ga08_rehashed_semantic_audit.py) | `533fd22c82978158f7fed37b78a19c650bde8dca` |
| [`tests/test_stage12_ga08_spatial_evidence.py`](tests/test_stage12_ga08_spatial_evidence.py) | `6d604d17b348aff8b7d4ea804afa425f796638ef` |

The `.github/workflows/` children are **inert** at this nested archive path, not registered GitHub Actions workflows. Their original references to root-level `scripts/`, `tests/`, `src/i0/`, and `src/lab/` describe a different source layout. The two scripts import `i0` and the former unscoped `lab`, so executing them from this folder or importing them into I1/I2 would not reproduce an authorized historical experiment.

## Provenance and replay limits

- Original experiment protocol, independent evidence, initial commit/ref, caller history, source dependency closure and retained GitHub artifacts must be checked separately before declaring any reproduction complete.
- [Frozen I0 custody](../../../../archive/i0/README.md) protects a separate recorded migration of 127 workflows and 297 tests. Its manifest **does not attest** these 12 GA08-specific archived paths.
- The inventory records file identity **at the cited main SHA only**. Compare a later checkout's `git hash-object` for each file against this table before reusing its contents.
- Do not rewrite historical files to fix missing imports; reconstruct an authentic original checkout in a disposable worktree after verifying the original source commit and evidence.
- No experiment was run for this index. Status: `SOURCE_REVIEW_REQUIRED`; scientific verdict: `NOT_EVALUATED`.

Return to the [research archive index](../README.md), [study routing](../../studies/README.md) or [original research documentation](../../README.md).
