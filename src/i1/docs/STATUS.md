# I1: current engineering and scientific status

**Snapshot:** 31 October 2026, documentation orientation based on [the repository registry](../../../config/engine-registry.json) and [I1 contract](../engine.json). **Always verify the latest HEAD, open PRs and CI before acting.** This is not a scientific GO.

## Current position

- **I1 is the active, born-capable generation.** I0 is frozen. I2 is an independent **proposal only**, not registered or born.
- Source of truth for what runs: `src/i1/engine.json` and the executable `src/i1/` tree. I1 owns `lab/`, `runtime/`, `modules/`, its `i1lab` build namespace, identity and M11 persistence.
- Invariants: only lived first-person inputs, paid UC, real Competition/Action Control, irreversible death, authenticated M11 current-state recovery, no hidden oracle or inherited older-generation runtime.
- **Scientific gates:** general adaptive benefit at L3 is **NOT_ESTABLISHED**; the A1-C confirmatory result was a targeted **NO_GO**; A2-R remains **NOT_EXECUTED (0/96)**. Do not infer generalized autonomous learning from software tests or short lived traces.
- Open research questions and defects must be checked against [live GitHub issues](https://github.com/josselin-orta-lab/individual-zero/issues), not old issue/PR state copied into historical notes.

## Where to inspect next

| Need | Authority |
| --- | --- |
| Active mechanisms and flow | [I1 handbook](README.md), [architecture](ARCHITECTURE.md), [cognitive flow](COGNITIVE_FLOW.md), [Stage map](STAGES_AND_INTERFACES.md) |
| Implementation versus scientific proof | [Evidence matrix](EVIDENCE_MATRIX.md) and original dated research traces |
| Actual birth integration | [Capabilities](CAPABILITY_INTEGRATION.md), `engine.json`, executable code and exact-SHA tests |
| Engineering intervention | [Development playbook](DEVELOPMENT_PLAYBOOK.md), [test plan](TEST_PLAN.md), current CI |
| M11, cost, sleep publication | [M11](MORTALITY_AND_M11.md), [UC](UC_AND_SCHEDULING.md), [consolidation](CONSOLIDATION_AND_PUBLICATION.md) |
| Historical change log | [Preserved I1 status ledger](STATUS_HISTORY.md) |

**Provenance rule:** a historic success on commit X never establishes a pass on commit Y. The [original status ledger](STATUS_HISTORY.md) is retained intact for audit, but its 17–20 October snapshots, PR dependencies and active/open labels are **not** a present-day status service.
