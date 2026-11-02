# Individual Zero

**Open research into low-abstraction cognitive engines and emergent artificial individuality.**

> **At what point does a collection of mechanisms begin to behave as a single individual?**

This question drives Individual Zero.

Individual Zero is an open-source research initiative exploring how coherent, adaptive behavior might emerge from explicit mechanisms interacting within a unified artificial system.

Rather than starting with the outward appearance of intelligence, the project investigates its possible underlying conditions: how perception, internal regulation, emotion, memory, learning, decision-making, and self-modeling might influence one another over time.

The objective is not merely to imitate intelligent behavior, but to understand the conditions under which it might arise.

## The central hypothesis

Intelligence may not require a single central mechanism. It could emerge from the organization and interaction of simpler processes.

Drawing from **neuroscience, psychology, physiology, and software architecture**, Individual Zero explores this possibility through mechanisms that can be inspected, challenged, and experimentally compared. Human cognition provides questions and hypotheses, not a blueprint assumed to be correct.

The focus is on the whole system: not whether one module can remember, choose, or regulate, but whether their interactions can produce continuity, adaptation, and behavior that remains coherent across changing circumstances.

## Why low abstraction?

A low-abstraction cognitive engine exposes its mechanisms rather than concealing them behind a single claim of intelligence.

Internal state, inputs, decisions, costs, and consequences should be traceable. Researchers should be able to ask *what changed, why it changed, and whether that change mattered*.

This is a methodological choice, not an assertion that complex cognition can already be explained by the architecture. Making mechanisms explicit allows individual hypotheses to be tested and failures to be understood.

## Mechanisms under investigation

- **Perception and embodiment:** how an artificial system encounters a world through its own observations and actions.
- **Internal regulation and emotion:** how needs, physiological analogues, affect, and motivation may shape priorities.
- **Memory and learning:** how experiences are retained, consolidated, and used to change later behavior.
- **Decision-making and agency:** how competing possibilities lead to actions with consequences, and how those consequences can be attributed.
- **Self-modeling and continuity:** how a system might maintain and update representations of its own state and history.

These are **research directions, not claims of achieved capabilities**.

The interesting question lies in their interaction. Can an experience alter internal regulation, influence memory, change a future decision, and contribute to a persistent pattern of adaptive behavior? If so, under what conditions, and with what measurable limits?

## Research before conclusions

Individual Zero is designed as an observable, falsifiable, and reproducible research effort.

Hypotheses are translated into experiments. Implementations are tested against explicit constraints. Behavioral observations are separated from software correctness, and scientific conclusions must be supported by evidence rather than by a convincing demonstration.

Negative and inconclusive results are part of the record. A passing test does not establish general intelligence; successful behavior in one environment does not establish generalized autonomous learning.

**No claims of AGI. No claims of artificial consciousness. No definitive answers.**

Just hypotheses, experiments, and an architecture open to scrutiny.

Read the [research workflow](docs/presentation/03-research-workflow.md), [research map](RESEARCH_MAP.md), and [experiments versus software tests](docs/research/experiments-vs-tests.md) for the methodology.

## Where the project stands

The repository contains distinct architectural generations. They are research generations, not conventional product versions.

| Generation | Role |
| --- | --- |
| **I0** | Preserved historical reference. |
| **I1** | Currently registered active research engine, with its own runtime, laboratory, and evidence records. |
| **I2** | Independent experimental proposal and non-living prototypes; not registered as an active or born engine. |

The current implementation investigates embodied perception, internal regulation, memory, action, and continuity. It does **not** establish that a unified artificial individual has achieved generalized autonomous learning.

For the authoritative technical and scientific boundaries, see the [engine registry](config/engine-registry.json), [I1 evidence matrix](src/i1/docs/EVIDENCE_MATRIX.md), and [I2 research status](src/i2/docs/STATUS.md). Architectural progress, software validation, and scientific evidence are assessed separately.

## Published research

The research is public and open to examination.

1. **Architecture of an Artificial Individual - Version 2, Informed by Human Psychology and Physiology**  
   [https://doi.org/10.5281/zenodo.23070595](https://doi.org/10.5281/zenodo.23070595)
2. **Artificial individual - technical specification**  
   [https://doi.org/10.5281/zenodo.23091065](https://doi.org/10.5281/zenodo.23091065)
3. **Artificial individual - implementation analysis of the specification**  
   [https://doi.org/10.5281/zenodo.23224611](https://doi.org/10.5281/zenodo.23224611)

Repository citation metadata is available in [CITATION.cff](CITATION.cff).

## Explore the project

For a first look, start with the [project overview](docs/presentation/01-project-overview.md) and [repository tour](docs/presentation/02-repository-tour.md).

To understand the architecture and its limitations, read the [I1 research handbook](src/i1/docs/README.md), [Architecture Atlas](docs/architecture/ATLAS.md), and [generation map](docs/architecture/ENGINE_GENERATIONS.md).

To inspect or contribute to the research, use the [research workflow](docs/presentation/03-research-workflow.md), [experiment records](docs/research/README.md), [contribution guide](CONTRIBUTING.md), and [engineering start guide](docs/engineering/START_HERE.md).

## Open research and contributions

Individual Zero welcomes critical examination, reproducible experiments, alternative hypotheses, and technically grounded contributions. Understanding the entire architecture is not a prerequisite for investigating a focused question.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [repository governance](docs/governance/README.md) before proposing changes.

**Licensing:** source code and scripts use [Apache 2.0](LICENSE); original documentation and research materials use [CC BY 4.0](LICENSE-DOCUMENTATION), unless otherwise stated. Third-party materials retain their own licenses.

---

**The mechanisms are visible. What might emerge from them remains an open question.**
