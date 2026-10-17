# I0 historical tests and workflows (2026-10-17)

Source: `main` at `704a20ee048d7dee5151ccfed439be37ba02e36b`.

This snapshot preserves **127** old workflows and **297** old test-directory files, including `tests/README.md`, at their exact original Git blob SHA. Files are moved without changing their bytes:
- `.github/workflows/X.yml` -> `archive/i0/workflows/X.yml`
- `tests/X` (except files named `test_i1_*.py`) -> `archive/i0/tests/X`

**Scope:** primarily I0 and historical common Lab/Stage1–12 tests. These tests are *not* an oracle for the natural I1 cognitive behavior. The historical YAML is inert under GitHub Actions because it is outside `.github/workflows`. It is available for research and recovery, not scheduled CI.

**Preserved current protections:** the active `.github/workflows/i1-current-ci.yml` and `tests/test_i1_*.py` remain. The I1 harness continues to instantiate its real current actor. `src/i0/`, `src/i1/`, `src/i1_overlays/`, `src/lab/` and the I1 generator are unchanged. The unchanged I1 workflow still refers to `test_stage6_planning.py` in the old location; a follow-up modification must replace that invocation with the archived path. Existing historical CI workflows that depend on archival evidence remain retrievable via the Git tree, but **must not** be reported as executing after this move.

**Important:** Some historical tests assume `Path(__file__).parents[1]` is the repository root. They cannot be run correctly merely from `archive/i0/tests/`. Restore the original paths in an isolated checkout to rerun historical results; do not change those tests to fit natural I1. The original test suite and existing historical workflows are preserved byte-for-byte so they can be restored without rebuilding assumptions.

## Reproduction

```bash
git checkout 704a20ee048d7dee5151ccfed439be37ba02e36b -- tests .github/workflows
python -m unittest discover -s tests -p 'test_*.py'
```

Perform this only in an isolated checkout or temporary worktree. This command **restores** the original test-tree/CI state for archive inspection; it is *not* the new I1 acceptance gate.

The archive does not establish I0 scientific acceptance, nor justify skipping functional regressions in the live code. All runtime mechanics and irreversible mortality contracts remain in source.
