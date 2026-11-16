# Software tests: where each suite belongs

This active portal deliberately lives at `tests/TEST_LAYOUT.md`:
`tests/README.md` is reserved by the preserved I0 archive manifest.
Do not recreate that old source path; its original bytes remain under
`archive/i0/tests/README.md`.


**Software tests are not scientific evidence.** Check the exact generation, commit SHA and purpose before interpreting a PASS. Tests and old research fixtures have different owners, so not all historical tests live beneath this directory.

| Purpose | Location | How to select |
| --- | --- | --- |
| Living I1 engineering contracts and mechanisms | [`tests/i1/`](i1/README.md) | `python -m unittest discover -s tests/i1 -p 'test_*.py'` |
| I3 generation-owned engineering software | [`tests/i3/`](i3/) | Focused T1/T2 module, or exact-head 3.11/3.12 [I3 software CI](../.github/workflows/i3-proposal-checks.yml), no science cohort |
| **Archived I2** synthetic research fixtures (SHA-pinned) | [`tests/i2/`](i2/) | **Historical manual reproduction only** through [I2 workflow](../.github/workflows/i2-proposal-safety.yml); ordinary PRs run static deny-tree guard |
| Shared infrastructure and legacy root tests | `tests/test_*.py` | Run a focused pattern with `python -m unittest discover -s tests -p 'test_repo_navigation.py'` |
| Research analysis tooling tests | `tests/research/a1p/`, `tests/research/a1c/`, `tests/research/a2r/` | Inspect the matching scientific tooling and its named CI contract before running |
| Frozen I0 historical tests | [`archive/i0/tests/`](../archive/i0/tests/) | Isolated historical verification only; not a natural-I1 acceptance oracle |

All 16 original root-level I1 tests have been classified and relocated. The two retained technical contracts live in `tests/i1/`; the fourteen historical witnesses live in `tests/research/i1-historical/`. Old dated reports may still cite their original paths, which remain historical references and must not be silently rewritten.

**New tests:** put I1 tests in `tests/i1/`, I3 development tests in `tests/i3/`, and shared structural tests in `tests/` (or a dedicated infrastructure suite with explicit discovery). **I2 is frozen**: do not add new I2 tests as part of ordinary development; a new archival disposition is required before reopening its source/tests. Do not add another `tests/test_i1_*.py` or `tests/test_i2_*.py` at the root. The lightweight placement guard checks this rule without running an engine.

```bash
python tools/repository_layout.py inventory --kind tests --match memory --limit 20
python tools/repository_layout.py check
```

Historical I1 A2.35 tests are isolated in `tests/research/i1-historical/` and are not active I1 acceptance oracles. A1-P, A1-C and A2-R research-only tests are organized in [`tests/research/`](research/README.md); their original tool modules remain under `tools/`.

All former `tools/research/tests/`, `tools/a1c_tests/` and `tools/a2r_tests/` suites have been consolidated. Do not reintroduce tests into these tool directories.

Tests under `archive/i0/` and synthetic I2 test opinions must not obtain I1 motor, state recovery or scientific authority. For living I1 see [engine contract](../src/i1/engine.json) and [evidence matrix](../src/i1/docs/EVIDENCE_MATRIX.md); for the owner-selected I3 development reference see the [short I3 test guide](../src/i3/docs/TEST_PLAN.md). The [archived I2 original plan](../src/i2/docs/TEST_PLAN.md) remains historical only.
