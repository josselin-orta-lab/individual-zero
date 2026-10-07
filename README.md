# Individual Zero

**Individual Zero** is an open research project exploring a modular, reproducible architecture for an artificial individual capable of learning, adapting, and mobilizing knowledge in novel situations.

The project does not assume that human-inspired cognitive mechanisms are the answer. They are hypotheses to test. The goal is to build an architecture whose important mechanisms can be understood, observed, measured, challenged, and replaced.

## What is I0?

**I0** is the first integrated reference architecture of Individual Zero. It is not a promise of AGI and it is not meant to be final. It is the smallest integrated baseline from which research questions can be tested reproducibly.

Future names such as I1 or I2 refer to architectural generations, not ordinary software releases.

## Guiding rule

> **Lab observes. Adapters connect. I0 operates. Experiments provide evidence. Tests verify the code.**

This separation keeps technical work lightweight while preserving scientific traceability when a change can alter what the individual learns, remembers, perceives, chooses, predicts, feels, or does.

## Research workflow

Scientific contributions follow:

**Question / hypothesis -> RAI -> minimal plan -> prototype -> test -> results -> decision**

RAI means **Reuse, Adapt, Implement**.

Possible decisions are **retry**, **reject**, **integrate**, or **candidate I(n+1)**.

Negative and inconclusive results are kept when they provide reproducible information.

## Repository map

```text
individual-zero/
├── docs/
│   ├── architecture/
│   ├── research/
│   └── decisions/
├── src/
│   ├── lab/
│   ├── adapters/
│   └── i0/
├── experiments/
├── benchmarks/
└── tests/
```

- `src/lab/`: runtime, simulation, logging, metrics, seeds, artifact collection, reproduction tools.
- `src/adapters/`: integration layers between I0 interfaces and external projects.
- `src/i0/`: reference cognitive architecture and behavior.
- `experiments/`: scientific questions, RAI decisions, protocols, results, conclusions.
- `benchmarks/`: reusable scenarios, metrics, and comparison rules.
- `tests/`: software correctness, integration, compatibility, and regression tests.

## When is an experiment required?

An EXP is not a development ticket. Create or join one when work is intended to produce measurable knowledge, compare mechanisms, or justify a change in scientific reference behavior.

Documentation, tooling, CI, compatible adapter updates, behavior-preserving refactoring, clearly identified bug fixes, and equivalent performance optimizations normally require software tests, not a scientific EXP.

## Research axes

- **AXIS-ARCH**: architecture, integration, and global dynamics
- **AXIS-PERCEPTION**: perception, body, and world model
- **AXIS-MEMORY**: memory, learning, and consolidation
- **AXIS-REGULATION**: interoception, homeostasis, affect, and motivation
- **AXIS-ACTION**: action selection, agency, and control
- **AXIS-SELF**: self, metacognition, and continuity

See [RESEARCH_MAP.md](RESEARCH_MAP.md).

## Contributing

You do not need to understand the entire architecture before contributing. Start by identifying whether the change is technical, scientific, or architectural.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licensing

Individual Zero uses a split licensing model:

- **Source code and software scripts**: [Apache License 2.0](LICENSE)
- **Original documentation, research text, diagrams, and written experimental reports**: [CC BY 4.0](LICENSE-DOCUMENTATION), unless stated otherwise
- **Third-party components and datasets**: remain subject to their own licenses

## Responsible development

Openness supports independent review, but openness alone does not guarantee safety. The project should progress in stages, evaluate developed capabilities, keep responsibilities identifiable, and document deployment limits when they become relevant.

See [SECURITY.md](SECURITY.md).

## Current status

The repository is in its initial research bootstrap phase. Initial goals are:

1. establish the repository and contribution workflow;
2. build a minimal Lab;
3. define a minimal executable I0 baseline;
4. register only research questions actually being worked on;
5. run the first reproducible EXPs;
6. add shared benchmarks progressively;
7. iterate from evidence.

## Citation

Citation metadata is available in [CITATION.cff](CITATION.cff).

---

**Individual Zero** is not built by declaring one grand theory correct. It is built by asking small enough questions that experiments can answer them.
