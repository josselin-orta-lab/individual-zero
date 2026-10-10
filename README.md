# Individual Zero

**Individual Zero** is an open research project exploring a modular, reproducible architecture for an artificial individual capable of learning, adapting, and mobilizing knowledge in novel situations.

The project does not assume that human-inspired cognitive mechanisms are the answer. They are hypotheses to test. The goal is to build an architecture whose important mechanisms can be understood, observed, measured, challenged, and replaced.

## Start here

If this is your first visit:

1. read the short [project overview](docs/presentation/01-project-overview.md);
2. take the [repository tour](docs/presentation/02-repository-tour.md);
3. read [how the research workflow works](docs/presentation/03-research-workflow.md);
4. if you want to contribute, use the [first-hour contributor guide](docs/presentation/04-contributor-first-hour.md);
5. browse the [examples](examples/README.md) before creating a new Issue, EXP, benchmark, adapter, or ADR;
6. when you want to execute the current scaffold, follow [Running the bootstrap](docs/presentation/06-running-the-bootstrap.md).

The project documentation is intentionally layered: you should not need to understand the whole architecture before making a useful contribution.

## What is I0?

**I0** is the first integrated reference architecture of Individual Zero.

It is not a promise of AGI and it is not meant to be final. It is the smallest integrated baseline from which scientific questions can be tested reproducibly.

Future names such as **I1** or **I2** refer to architectural generations, not ordinary software releases.

## Guiding rule

> **Lab observes. Adapters connect. I0 operates. Experiments provide evidence. Tests verify the code.**

This separation keeps technical work lightweight while preserving scientific traceability when a change can alter what the individual learns, remembers, perceives, chooses, predicts, feels, or does.

## Research workflow

Scientific contributions follow:

**Question / hypothesis -> RAI -> minimal plan -> prototype -> test -> results -> decision**

RAI means **Reuse, Adapt, Implement**.

Possible decisions are:

- **retry**: the question remains useful, but the method or prototype needs revision;
- **reject**: the tested mechanism or hypothesis is not supported under the tested conditions;
- **integrate**: the result justifies a change to the current reference;
- **candidate I(n+1)**: the result suggests a broader architectural rupture worth investigating.

Negative and inconclusive results are kept when they provide reproducible information.

## Repository map

```text
individual-zero/
├── docs/
│   ├── presentation/
│   ├── architecture/
│   ├── research/
│   └── decisions/
├── examples/
├── src/
│   ├── lab/
│   ├── adapters/
│   └── i0/
├── experiments/
├── benchmarks/
└── tests/
```

- `docs/presentation/`: short onboarding documents for humans discovering the project.
- `docs/architecture/`: architecture descriptions, interfaces, and generation manifests.
- `docs/research/`: research method, terminology, RAI, and experiment guidance.
- `docs/decisions/`: shared architectural decisions recorded as ADRs.
- `examples/`: non-authoritative examples showing how the workflow is used.
- `src/lab/`: runtime, simulation, logging, metrics, seeds, artifact collection, reproduction tools.
- `src/adapters/`: integration layers between I0 interfaces and external projects.
- `src/i0/`: reference cognitive architecture and behavior.
- `experiments/`: scientific questions, RAI decisions, protocols, results, and conclusions.
- `benchmarks/`: reusable scenarios, metrics, and comparison rules.
- `tests/`: software correctness, integration, compatibility, and regression tests.

## When is an experiment required?

An EXP is not a development ticket.

Create or join one when work is intended to produce measurable knowledge about the system, compare mechanisms, or justify a change in scientific reference behavior.

Examples that normally require an EXP:

- a new learning strategy;
- a new memory or consolidation mechanism;
- a change in action selection, internal regulation, affect, or motivation;
- replacing a reference cognitive component with an external dependency;
- changing reference parameters with an expected behavioral effect;
- changing the global cycle or structural relationships between subsystems.

Documentation, tooling, CI, compatible adapter updates, behavior-preserving refactoring, clearly identified bug fixes, and equivalent performance optimizations normally require software tests, not a scientific EXP.

See [Experiments vs tests](docs/research/experiments-vs-tests.md) for concrete examples.

## Research axes

- **AXIS-ARCH**: architecture, integration, and global dynamics
- **AXIS-PERCEPTION**: perception, body, and world model
- **AXIS-MEMORY**: memory, learning, and consolidation
- **AXIS-REGULATION**: interoception, homeostasis, affect, and motivation
- **AXIS-ACTION**: action selection, agency, and control
- **AXIS-SELF**: self, metacognition, and continuity

See [RESEARCH_MAP.md](RESEARCH_MAP.md).

## Contributing

You do not need to understand the entire architecture before contributing.

For contribution permissions and public-release governance, see [repository governance](docs/governance/README.md).

Start by identifying whether the change is:

- **technical**: the software or infrastructure changes, but the scientific behavior is not expected to change;
- **scientific**: a hypothesis or behavioral change must be measured;
- **architectural**: experimental evidence supports a shared structural decision.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [contribution examples](examples/README.md).

## Licensing

Individual Zero uses a split licensing model:

- **Source code and software scripts**: [Apache License 2.0](LICENSE)
- **Original documentation, research text, diagrams, and written experimental reports**: [CC BY 4.0](LICENSE-DOCUMENTATION), unless stated otherwise
- **Third-party components and datasets**: remain subject to their own licenses

## Responsible development

Openness supports independent review, but openness alone does not guarantee safety.

The project should progress in stages, evaluate developed capabilities, keep responsibilities identifiable, and document deployment limits when they become relevant.

See [SECURITY.md](SECURITY.md).

## Current status

The repository is in its initial research bootstrap phase.

The following foundations now exist:

- repository and contribution workflow;
- neutral Lab execution loop;
- deterministic technical smoke scenario;
- structured JSONL run artifacts;
- minimal I0 execution contracts;
- executable BootstrapI0 with a deliberate no-op action boundary;
- automated unit tests and CI.

The current executable scaffold is **not yet a cognitive I0**. It is the research chassis required to test future mechanisms cleanly.

Next goals are:

1. identify the first genuinely measurable cognitive question;
2. perform RAI for the mechanism involved;
3. register the first real EXP;
4. implement the smallest mechanism needed to test it;
5. add shared benchmarks only when reuse becomes useful;
6. iterate from evidence.

See [Running the bootstrap](docs/presentation/06-running-the-bootstrap.md) and [Bootstrap runtime boundary](docs/architecture/BOOTSTRAP_RUNTIME.md).

The repository intentionally does **not** pre-create speculative experiments merely to make the project look busy.

## Citation

Citation metadata is available in [CITATION.cff](CITATION.cff).

---

**Individual Zero** is not built by declaring one grand theory correct. It is built by asking small enough questions that experiments can answer them.
