# Start here: current Individual Zero engineering

**Active: I1. Frozen: I0. Proposal only: I2.** This page routes technical work; it is not the scientific or runtime authority. The root [README](../../README.md) is the current public overview. The old `individual-zero` CLI is an I0 bootstrap example, **not** an active natural-I1 run.

1. Read the [agent navigation index](AGENT_NAVIGATION.md), [root instructions](../../AGENTS.md) and [generation registry](../../config/engine-registry.json).
2. For I1, read [generation-specific instructions](../../src/i1/AGENTS.md), [handbook](../../src/i1/docs/README.md), [current status](../../src/i1/docs/STATUS.md) and [evidence matrix](../../src/i1/docs/EVIDENCE_MATRIX.md).
3. For I2 synthetic research, read [I2 instructions](../../src/i2/AGENTS.md), [handbook](../../src/i2/docs/README.md) and [current status](../../src/i2/docs/STATUS.md). I2 is **not** registered or executable.
4. Review [strict autonomy](../decisions/ADR-0001-strict-generation-autonomy.md), [generation map](../architecture/ENGINE_GENERATIONS.md) and [promotion procedure](ENGINE_PROMOTION.md) only for generation-sensitive work.
5. For old I0 material, see [archive index](../../config/archives/i0-20261017.json); do not rewrite preserved bytes.

## Lightweight first checks

```bash
python tools/check_repo_navigation.py --scope entrypoints
python scripts/check_engine_repository.py --json
python scripts/check_engine_contracts.py --json
python scripts/check_i1_handbook.py --json
```

These are structural checks, not scientific evidence. For changing I1 behavior, consult the exact commands in `src/i1/engine.json` and [I1 test plan](../../src/i1/docs/TEST_PLAN.md) before running smoke/full and relevant M11 parity suites. For I2 synthetic fixtures, see [I2 test plan](../../src/i2/docs/TEST_PLAN.md). Use the **exact commit SHA** when reporting CI. Do not run repeated heavy tests merely because documentation changed.

## Boundaries

Each generation owns its own world, Lab, cognition, UC and persistence. I1's generated `i1lab` namespace is an existing I1-specific persistence contract, not a shared runtime. Never inject Oracle truth, force a choice, waive UC, resurrect, silently restore, or treat an I2 test opinion as motor authority. Software PASS, observed behavior, and scientific GO are different claims.
