# Research-specific software tests

These are **software contract tests**, not scientific evidence or authorization for a living cohort. The test implementations live with the test hierarchy, while their source analysis tools remain in `tools/` and `tools/research/`.

- `a1p/`: offline A1-P historical replay gate (pure software, no original downloads).
- `a1c/`: targeted A1-C mechanism isolation, reward shadow, TD replay, wait gate and statistical criterion contracts (six tests).
- [`a2r/`](a2r/README.md): A2-R launch/one-shot custody guards, pure archive/pair-witness contracts and a narrowly scoped reward-birth contract.
- All previously embedded research test files now live under `tests/research/`; source analyzers remain under `tools/research/`. The static repository-layout check rejects regressions into the deprecated tool test folders.

Run focused checks, from the repository root, only with the corresponding source dependencies installed:

```bash
PYTHONPATH=tools:tools/research python -m unittest discover -s tests/research/a1c -p 'test_*.py' -v
PYTHONPATH=tools:tools/research python -m unittest discover -s tests/research/a2r -p 'test_i1_a2r_launch_gate.py' -v
```

Do not run full living-engine cohorts for repository housekeeping. A2-R birth contract tests are opt-in for their dedicated lightweight CI and are not a scientific GO. For scientific verdicts, consult the original preregistration, pinned evidence, and `src/i1/docs/EVIDENCE_MATRIX.md`.
