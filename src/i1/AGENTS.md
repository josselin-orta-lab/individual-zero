# I1 agent instructions: active generation

Scope: `src/i1/` and its generation-owned Lab, runtime and cognitive modules. Follow the [repository agent rules](../../AGENTS.md) and [strict autonomy ADR](../../docs/decisions/ADR-0001-strict-generation-autonomy.md).

## Read only what you need

1. [I1 handbook](docs/README.md) for the mechanism map and theory.
2. [Current I1 status](docs/STATUS.md) for limitations and open gates; `docs/STATUS_HISTORY.md` is **historical**.
3. [Cognitive flow](docs/COGNITIVE_FLOW.md), [Stage/owner map](docs/STAGES_AND_INTERFACES.md), and the specific mechanism guide for the impacted path.
4. [Evidence matrix](docs/EVIDENCE_MATRIX.md) for strictly separated implementation, software tests, observed behavior and science.

## Runtime boundaries

`engine.json` and current code own executable behavior. I1 owns `lab/`, `runtime/`, `modules/` and its born persistence. The temporary `i1lab` import namespace is part of **I1's own** authenticated birth contract, not permission to run I0 or revive old H1/H2 modes. Never replace a genuine life with a test script, inject hidden WorldBody truth, waive UC charges or rewind/restore a dead individual.

Use `docs/DEVELOPMENT_PLAYBOOK.md` for a causal investigation: physical body -> first-person capture -> value/goals -> candidates -> Competition/Action Control -> physical effect -> experienced consequences -> memory -> paid consolidation and M11. An experimental file's presence does not make it an active born mechanism.

## Verification

Read `engine.json.validation.suites` for exact test vectors. Targeted structural checks: `python scripts/check_engine_repository.py --json`, `python scripts/check_engine_contracts.py --json` and `python scripts/check_i1_handbook.py --json`. For runtime changes, execute relevant `tests/i1/`, smoke/full and M11/source parity checks as warranted, and verify the exact pushed SHA under Python 3.11/3.12. Separate software result from any prospective scientific study. Avoid repeated heavy CI for documentation-only checkpoints.
