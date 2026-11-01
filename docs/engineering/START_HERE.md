# Start here: current Individual Zero engineering

**Active: I1. Frozen: I0. Proposal only: I2.** This page routes technical work; it is not the scientific or runtime authority. The root [README](../../README.md) is the current public overview. The old `individual-zero` CLI is an I0 bootstrap example, **not** an active natural-I1 run.

1. Read the [agent navigation index](AGENT_NAVIGATION.md), [root instructions](../../AGENTS.md) and [generation registry](../../config/engine-registry.json).
2. For I1, read [generation-specific instructions](../../src/i1/AGENTS.md), [handbook](../../src/i1/docs/README.md), [current status](../../src/i1/docs/STATUS.md) and [evidence matrix](../../src/i1/docs/EVIDENCE_MATRIX.md).
3. For I2 synthetic research, read [I2 instructions](../../src/i2/AGENTS.md), [handbook](../../src/i2/docs/README.md) and [current status](../../src/i2/docs/STATUS.md). I2 is **not** registered or executable.
4. Review [strict autonomy](../decisions/ADR-0001-strict-generation-autonomy.md), [generation map](../architecture/ENGINE_GENERATIONS.md) and [promotion procedure](ENGINE_PROMOTION.md) only for generation-sensitive work.
5. For old I0 material, see [archive index](../../config/archives/i0-20261017.json); do not rewrite preserved bytes.

## Research-first intervention selection

If the task is not already narrowly specified, first run `python tools/research_coordinator.py status` and `python tools/research_coordinator.py recommend`. Its recommendations are provisional and do not authorize experiments, births or changes to scientific gates. See [global research coordination](RESEARCH_COORDINATOR.md).

For documentation/agent-navigation changes (including the separate architecture atlas), use the single path-scoped `agent-context-static.yml` check. It runs `check_repo_navigation.py`, `test_repo_navigation.py` and the focused agent/research tests, **not** a living engine. Source-integrity drift in a current status page is flagged for research reconciliation; frozen scientific sources must retain their exact Git blobs. See [research coordination](RESEARCH_COORDINATOR.md) and [source dossiers](RESEARCH_DOSSIERS.md).

When citing the same source in both curated research manifests, use `python tools/research_coordinator.py audit --structure-only` to detect **cross-manifest source-SHA disagreement** before proposing research work; a structural PASS with `SOURCE_REVIEW_REQUIRED` still demands manual source reconciliation. See the [1 November provenance record](../research/audits/RESEARCH_SOURCE_RECONCILIATION_2026-11-01.md).

## Lightweight first checks

```bash
python tools/check_repo_navigation.py --scope entrypoints
python scripts/check_engine_repository.py --json
python scripts/check_engine_contracts.py --json
python scripts/check_i1_handbook.py --json
```

These are structural checks, not scientific evidence. For changing I1 behavior, consult the exact commands in `src/i1/engine.json` and [I1 test plan](../../src/i1/docs/TEST_PLAN.md) before running smoke/full and relevant M11 parity suites. For I2 synthetic fixtures, see [I2 test plan](../../src/i2/docs/TEST_PLAN.md). Use the **exact commit SHA** when reporting CI. Do not run repeated heavy tests merely because documentation changed.

## Current CI routing (do not use the archived I0 policy)

The **actual workflow files** determine what runs. The older [I0 CI policy](../research/ci-execution-policy.md) describes historical behaviour only.

| Changed scope | Verification |
| --- | --- |
| I1 executable source, engine contracts, relevant scripts and structural tooling | [I1 CI](../../.github/workflows/i1-current-ci.yml), Python 3.11 and 3.12, potentially expensive |
| I1 Markdown, `AGENTS.md`, navigational guides and examples only | `python tools/check_repo_navigation.py --scope current` and targeted local unit tests; **do not start a full mortal cohort run** |
| I2 prototype source or generation-owned documentation | [I2 proposal-only CI](../../.github/workflows/i2-proposal-safety.yml), synthetic tests only; no birth or motor authorization |
| Explicit architecture/custody/promotion change | Required [engine structural guard](../../.github/workflows/engine-structural.yml) and generation-specific review, with full checks if executable invariants change |

The I1 workflow excludes generation-owned Markdown from its expensive automatic run; negatives in its ordered GitHub `paths` list must stay **after** positive patterns. The I1 workflow still activates for changes to `scripts/check_engine_repository.py` and its own YAML. Avoid gratuitous CI re-runs on adjacent documentation commits. A skipped check is never a PASS. Preserve the exact commit SHA and any manual approval gate.

For a dated account of the October 17 native-source migration, consult [the historical I1 migration ledger](I1_NATIVE_MIGRATION.md). Its old PR statuses and paths are snapshots, not current implementation authority.

## Boundaries

Each generation owns its own world, Lab, cognition, UC and persistence. I1's generated `i1lab` namespace is an existing I1-specific persistence contract, not a shared runtime. Never inject Oracle truth, force a choice, waive UC, resurrect, silently restore, or treat an I2 test opinion as motor authority. Software PASS, observed behavior, and scientific GO are different claims.
