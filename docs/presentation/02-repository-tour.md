# Repository tour

Individual Zero separates active research engines, historical references, scientific evidence, and research tooling. **I1 is the active generation; I0 is frozen; I2 is a proposal only** (31 October 2026).

## Start with the engine registry

[config/engine-registry.json](../../config/engine-registry.json) identifies the active generation and archived reference. A folder under `src/` does **not** imply an engine is registered or authorized to instantiate a living individual.

## Directory map

```text
individual-zero/
├── config/engine-registry.json
├── src/
│   ├── i0/                 # historical reference
│   ├── i1/                 # active engine, generation-owned Lab/runtime/docs
│   ├── i2/                 # inactive research proposal/fixtures
│   └── adapters/           # external integration adapters
├── archive/i0/             # immutable historical material
├── docs/
│   ├── presentation/       # first-visit guides
│   ├── architecture/       # generation map, references and proposals
│   ├── decisions/          # architecture decision records
│   ├── engineering/        # current engineering entrypoints
│   └── research/           # scientific methodology and evidence
├── experiments/            # experimental questions and records
├── benchmarks/             # reusable comparison scenarios
├── tests/                  # code invariants, not scientific proof
└── tools/                  # inspection and operator utilities
```

## Where to look

- [Development agent instructions](../../AGENTS.md) and [short navigation map](../engineering/AGENT_NAVIGATION.md): establish generation ownership before inspecting implementation details.
- [I1 handbook](../../src/i1/docs/README.md): actual active mechanisms, causal boundaries, scientific obligations.
- [I1 evidence matrix](../../src/i1/docs/EVIDENCE_MATRIX.md): implemented, software-tested, observed, and **not established** are separate categories.
- [Engine generation map](../architecture/ENGINE_GENERATIONS.md): code and Lab ownership, archive policies, and promotion procedure.
- [I2 research gates](../architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md): proposal status, remaining safety and science prerequisites.
- [ADR-0001](../decisions/ADR-0001-strict-generation-autonomy.md): successors own their runtime and living state; no obsolete-engine fallback.
- [Research workflow](03-research-workflow.md): scientific protocol and decision logic.
- [Engineering start guide](../engineering/START_HERE.md): current I1 technical commands and verification.

The `individual-zero` console command and [bootstrap guide](06-running-the-bootstrap.md) illustrate **historical I0** tooling; they are not a natural-I1 run or an I2 activation.

## Choosing the right location

Place behavior-changing active I1 code in its generation-owned source directory; place experimental questions, protocols, and evidence in their research records; place software correctness checks in tests. Reusable benchmarks define comparison conditions, not conclusions.

New-generation work must remain isolated until independently reviewed and authorized. Archived experiments remain useful for research and reproducibility but cannot supply an artificial individual's birth memory or serve as unearned evidence for a successor.

See [CONTRIBUTING.md](../../CONTRIBUTING.md) before proposing changes.
