# Individual Zero

**Open research in artificial intelligence, cognitive architectures, and autonomous learning for embodied artificial individuals.**

Individual Zero investigates whether an artificial individual in a simplified world and body can learn useful behavior from its own observations, needs, actions, and consequences, including in unfamiliar situations. The work explores perception, memory, learning, consolidation, motivation, action selection, and causal attribution without preloading a successful behavioral policy.

Human-inspired cognitive mechanisms are hypotheses to test, not assumptions to accept. The aim is an observable, falsifiable, and reproducible research architecture. A software test passing or an agent surviving a scenario is not, by itself, evidence of generalized autonomous learning.

## Start here

If this is your first visit:

1. Read the short [project overview](docs/presentation/01-project-overview.md) and [repository tour](docs/presentation/02-repository-tour.md).
2. Explore the [current I1 engineering handbook](src/i1/docs/README.md) and [evidence matrix](src/i1/docs/EVIDENCE_MATRIX.md).
3. Review the [I1-to-I2 scientific transition and gates](docs/architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md) before treating I2 as a running individual.
4. See the [research workflow](docs/presentation/03-research-workflow.md), [contributor guide](docs/presentation/04-contributor-first-hour.md), and [worked examples](examples/README.md).
5. For the historical I0 demonstration, see [Running the bootstrap](docs/presentation/06-running-the-bootstrap.md). That CLI is **not** the active natural-I1 engine.

The documentation is layered. You do not need to understand the complete architecture to inspect an experiment or contribute a focused change.

**For development agents:** understand the global research priorities through the [research coordinator](docs/engineering/RESEARCH_COORDINATOR.md), then inspect the [Architecture Atlas](docs/architecture/ATLAS.md), [AGENTS.md](AGENTS.md) and [two-minute navigation map](docs/engineering/AGENT_NAVIGATION.md) before editing. The registry, generation-owned contracts, code, software checks and scientific evidence answer different questions; historical reports do not override live HEAD.

## Architectural generations

I0, I1, and I2 are **architectural generations**, not ordinary software releases.

| Generation | Status (31 October 2026) | Entry point |
| --- | --- | --- |
| **I0** | Frozen historical reference; not the active research engine | [I0 archive and engine map](docs/architecture/ENGINE_GENERATIONS.md) |
| **I1** | **Active** artificial-individual research architecture with generation-owned Lab, runtime, tests, and evidence | [I1 handbook](src/i1/docs/README.md) |
| **I2** | **Proposal only**, unregistered and not an executable living individual; current source includes inert research fixtures | [I2 research proposal](docs/architecture/proposals/i2-continuity-and-learning-contract-2026-10-31.md) |

Each generation must be autonomous: a historical parent is a research lineage, **not** a runtime dependency. No successor may rely on an obsolete engine's live state, memory, owner, fallback mode, or resurrection path. See [ADR-0001](docs/decisions/ADR-0001-strict-generation-autonomy.md) and the [engine registry](config/engine-registry.json).

## Guiding rule

> **Each generation owns its own cognition and living-world boundary. Experiments provide evidence. Tests verify code.**

Scientific observations are kept distinct from software correctness, and historical generations remain available for isolated comparisons without being imported into a successor's runtime.

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
├── config/engine-registry.json
├── src/
│   ├── adapters/                 # external integration boundaries
│   ├── i0/                       # frozen historical engine
│   ├── i1/                       # active engine, Lab, runtime and handbook
│   └── i2/                       # unregistered, non-living research proposal
├── archive/i0/                   # preserved historical material
├── docs/
│   ├── presentation/             # onboarding
│   ├── architecture/             # models and generation proposals
│   ├── research/                 # protocols, results and limitations
│   ├── decisions/                # architecture decisions
│   └── engineering/              # technical operating procedures
├── experiments/
├── benchmarks/
├── tests/
└── tools/
```

- [I1 research handbook](src/i1/docs/README.md) holds the active generation's mechanism descriptions and evidence limits.
- [Architecture Atlas](docs/architecture/ATLAS.md) lets agents trace the I1 causal path, component owners, tests and scientific boundaries before editing.
- [Generation map](docs/architecture/ENGINE_GENERATIONS.md) explains engine ownership and archive boundaries.
- [Test placement](tests/TEST_LAYOUT.md), [archive custody](archive/README.md) and [research records](docs/research/README.md) provide physical navigation without promoting historical evidence.
- [Research documentation](docs/research/README.md) and `experiments/` record hypotheses, protocols, observations, uncertainty, and negative outcomes.
- [Engineering start guide](docs/engineering/START_HERE.md) explains current entrypoints. The older `individual-zero` CLI is a historical I0 bootstrap demo, not an I1 science run.

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

## Research status (31 October 2026)

**I1 is active; I0 is preserved; I2 is not activated.** I1 implements and tests mechanisms for first-person perception, bodily regulation, mortal world interaction, memory, learning, and authenticated persistence. Those implementation facts do **not** establish that the combined system learns naturally, efficiently, or autonomously across novel environments.

The pre-registered A1-C confirmatory study was a targeted **NO_GO**. General adaptive improvement at the L3 scientific gate remains **NOT_ESTABLISHED**. The A2-R cohort was **NOT_EXECUTED** (0/96). I2 work is limited to proposals and isolated, non-living research fixtures; no I2 birth or scientific promotion is authorized.

Start with the [I1 evidence matrix](src/i1/docs/EVIDENCE_MATRIX.md), the [I1-to-I2 decision and result limits](docs/architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md), and the [generation autonomy decision](docs/decisions/ADR-0001-strict-generation-autonomy.md). The project makes **no claim of AGI, consciousness, or demonstrated generalized autonomous learning**.

Software progress, behavioral observation, and scientific validation are deliberately reported separately.

## Citation

Citation metadata is available in [CITATION.cff](CITATION.cff).

---

**Individual Zero** is not built by declaring one grand theory correct. It is built by asking small enough questions that experiments can answer them.
