# Start here: current Individual Zero engineering

**Active generation: I1. Preserved reference: I0.** Lab sources are now generation-owned: `src/i1/lab/` and `archive/i0/lab/`; there is no active shared `src/lab/`. The repository's older top-level README describes an early bootstrap and is not current operational authority for I1.

1. [Engine map](../architecture/ENGINE_GENERATIONS.md) explains boundaries, ownership and how future generations are promoted.
2. [Machine registry](../../config/engine-registry.json) declares locations and test entrypoints.
3. [Historical archive index](../../config/archives/i0-20261017.json) pins every archived file to its original Git blob.
4. [PR #246 test audit](../research/i1-pr246-current-test-audit-2026-10-17.fr.md) documents I1 SMOKE/FULL, residual scientific limits and I0 protections.
5. [Historical I0 README](../../archive/i0/README.md) documents restoration of old tests and GitHub workflows.

## Day-one commands

```bash
python -m pip install -e .
python scripts/check_engine_repository.py --json
python -m unittest discover -s tests -p test_engine_repository.py -v
python scripts/test_i1_ci.py --mode smoke --seed 246 --junit reports/i1-smoke.xml
python scripts/test_i1_ci.py --mode full --seed 246 --junit reports/i1-full.xml
```

The current I1 builder is `scripts/build_i1_fork.py`. Run it into a temporary directory, not `src`. The active GitHub workflow remains `.github/workflows/i1-current-ci.yml`. Old research and I0-specific scenarios belong outside the current I1 CI and remain independently retrievable.

**Hard boundary:** No I0 rewriting, rollback, postmortem activity, Oracle/Bench data in cognitive observation, disabling current-I1 modules or imposing obsolete H1/H2 expectations. A real failure must fail CI; an individual's plausible death under ignorance is not automatically a software failure.
