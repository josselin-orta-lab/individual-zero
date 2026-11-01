# Research-specific software tests

These are **software contract tests**, not scientific evidence or authorization for a living cohort. The test implementations live with the test hierarchy, while their source analysis tools remain in `tools/` and `tools/research/`.

- `a1c/`: targeted A1-C mechanism isolation and statistical criterion contracts.
- `a2r/`: A2-R launch/one-shot custody guards and a narrowly scoped reward-birth contract.
- Other experiment-specific fixtures under `tools/research/tests/` are not yet moved because many workflows cite their exact paths and import context.

Run focused checks, from the repository root, only with the corresponding source dependencies installed:

```bash
PYTHONPATH=tools:tools/research python -m unittest discover -s tests/research/a1c -p 'test_*.py' -v
PYTHONPATH=tools:tools/research python -m unittest discover -s tests/research/a2r -p 'test_i1_a2r_launch_gate.py' -v
```

Do not run full living-engine cohorts for repository housekeeping. A2-R birth contract tests are opt-in for their dedicated lightweight CI and are not a scientific GO. For scientific verdicts, consult the original preregistration, pinned evidence, and `src/i1/docs/EVIDENCE_MATRIX.md`.
