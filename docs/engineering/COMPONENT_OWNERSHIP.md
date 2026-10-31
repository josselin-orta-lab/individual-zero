# Component ownership and boundaries: first navigation map

This is an **index of places to inspect**, not a claim that every present module is wired into a born individual. Actual ownership and activation are verified through generation contracts, constructors, call sites, publication custody and current source. The canonical I1 detail remains in [`STAGES_AND_INTERFACES.md`](../../src/i1/docs/STAGES_AND_INTERFACES.md), [`COGNITIVE_FLOW.md`](../../src/i1/docs/COGNITIVE_FLOW.md) and [`CAPABILITY_INTEGRATION.md`](../../src/i1/docs/CAPABILITY_INTEGRATION.md).

| Concern | Primary source to inspect | Boundary / evidence |
| --- | --- | --- |
| Generation selection | `config/engine-registry.json`, `src/iN/engine.json` | Registry status vs actual executable entrypoints |
| I1 living body / WorldBody | `src/i1/lab/`, `src/i1/runtime/` | Physical effects and first-person sensory feedback are separate from observer diagnostics |
| I1 perception / needs | `src/i1/modules/perception.py`, `value_needs.py` | First-person data and bodily reserves; never hidden-world oracle values |
| I1 memory / consolidation | `src/i1/modules/memory.py`, `consolidation_*` | Provenance, UC costs, publication and M11 custody |
| I1 action / arbitration | `src/i1/modules/competition.py`, `action_control.py` | Opinions/candidates vs admitted real action |
| I1 mortality / M11 | `src/i1/runtime/m11_transactional_mortal.py`, `sqlite_runtime_custody.py` | Exact generation identity, authenticated persistence, irreversible death |
| I2 research fixtures | `src/i2/modules/`, `tests/i2/` | G2 synthetic software only, no registered runtime or birth |
| I2 synthetic witness | `src/i2/modules/lifecycle_external_witness.py`, `uncertain_witness_inspection.py` | Injected witnesses cannot grant independent M11, retry or motor rights |
| Research observations | `src/i1/docs/EVIDENCE_MATRIX.md`, `src/i2/docs/STATUS.md`, `docs/research/` | Actual preregistered observations distinct from code tests |
| Tools / workflows | `config/tool-inventory.json`, `.github/workflows/` | Tool classification is not an authorization to execute |

For an intervention: identify the *producer*, *consumer*, *state owner*, *permission to act*, *persistence owner* and *targeted test*. If any of these is unknown, record `UNVERIFIED` and inspect the real call graph instead of guessing. A module may be active, dormant, synthetic or experimental even when it lives under a seemingly active directory.

The machine-readable [agent context map](../../config/agent-context-map.json) selects an initial subset of these owners. It intentionally does not encode a complete call graph or replicate normative cognitive specifications.
