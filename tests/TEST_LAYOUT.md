# Software tests: where each suite belongs

This active portal deliberately lives at `tests/TEST_LAYOUT.md`:
`tests/README.md` is reserved by the preserved I0 archive manifest.
Do not recreate that old source path; its original bytes remain under
`archive/i0/tests/README.md`.


**Software tests are not scientific evidence.** Check the exact generation, commit SHA and purpose before interpreting a PASS. Tests and old research fixtures have different owners, so not all historical tests live beneath this directory.

| Purpose | Location | How to select |
| --- | --- | --- |
| Living I1 engineering contracts and mechanisms | [`tests/i1/`](i1/README.md) | `python -m unittest discover -s tests/i1 -p 'test_*.py'` |
| I2 proposal-only synthetic fixtures | [`tests/i2/`](i2/) | `python -m unittest discover -s tests/i2 -p 'test_*.py'` |
| Shared infrastructure and legacy root tests | `tests/test_*.py` | Run a focused pattern with `python -m unittest discover -s tests -p 'test_repo_navigation.py'` |
| Research analysis tooling tests | `tests/research/a1p/`, `tests/research/a1c/`, `tests/research/a2r/` | Inspect the matching scientific tooling and its named CI contract before running |
| Frozen I0 historical tests | [`archive/i0/tests/`](../archive/i0/tests/) | Isolated historical verification only; not a natural-I1 acceptance oracle |

Sixteen older I1 tests still live at the test root. They are **legacy placements**, not examples to follow. Do not rename or relocate them until their imports, direct invocations, workflow globs and published references have been independently checked.

**New tests:** put I1 tests in `tests/i1/`, I2 synthetic tests in `tests/i2/`, and shared structural tests in `tests/` (or a dedicated infrastructure suite with explicit discovery). Do not add another `tests/test_i1_*.py` or `tests/test_i2_*.py` at the root. The lightweight placement guard checks this rule without running an engine.

```bash
python tools/repository_layout.py inventory --kind tests --match memory --limit 20
python tools/repository_layout.py check
```

A1-P, A1-C and A2-R research-only tests are organized in [`tests/research/`](research/README.md); their original tool modules remain under `tools/`.

All former `tools/research/tests/`, `tools/a1c_tests/` and `tools/a2r_tests/` suites have been consolidated. Do not reintroduce tests into these tool directories.

Tests under `archive/i0/` and synthetic I2 test opinions must not obtain I1 motor, state recovery or scientific authority. For the active generation's official suites and scientific limits, see [I1 engine contract](../src/i1/engine.json), [I1 evidence matrix](../src/i1/docs/EVIDENCE_MATRIX.md), and [I2 test plan](../src/i2/docs/TEST_PLAN.md).
