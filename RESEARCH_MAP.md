# Individual Zero Research Map

Research axes map scientific questions and related work. They do not define the code tree, Git branches, or permanent teams. One EXP may belong to several axes.

## Major axes

| ID | Axis | Indicative scope |
| --- | --- | --- |
| **AXIS-ARCH** | Architecture, integration, and global dynamics | execution cycle, coordination, temporality, relationships between subsystems |
| **AXIS-PERCEPTION** | Perception, body, and world model | vision, audition, proprioception, body representation, environment, predictions |
| **AXIS-MEMORY** | Memory, learning, and consolidation | working, episodic, semantic memory, plasticity, replay, sleep, consolidation |
| **AXIS-REGULATION** | Interoception, homeostasis, affect, and motivation | needs, internal states, regulation, values, emotions, motivation |
| **AXIS-ACTION** | Action selection, agency, and control | arbitration, planning, veto, motor control, exploration, agency |
| **AXIS-SELF** | Self, metacognition, and continuity | self-model, monitoring, reflection, identity, narrative, temporal continuity |

## Current research state

The active questions, evidence gaps, negative and unexecuted findings, I2 gates and intervention candidates are **not maintained in static tables on this page**. Empty planning templates previously shown here did not represent the real research backlog.

Agents should first read [the research coordination guide](docs/engineering/RESEARCH_COORDINATOR.md), whose [curated program](config/research-program.json) links reported findings to exact source Git blobs, research questions, reviews and blocking dependencies. From the repository root:

```bash
python tools/research_coordinator.py status
python tools/research_coordinator.py recommend --top 5
python tools/research_coordinator.py trace --id question:I1-L3
python tools/research_coordinator.py graph --mode knowledge
python tools/research_coordinator.py catalog --limit 20
```

The seed program covers only selected I1 and I2 research questions. It is **not** a census of all research, a live GitHub issue tracker, an independently verified scientific verdict or a permission to run a study. File names returned by the catalog are unreviewed candidates, not scientific evidence.

## Where evidence actually lives

- [I1 evidence matrix](src/i1/docs/EVIDENCE_MATRIX.md) distinguishes implementation, observed behavior and scientific limits.
- [I1 current status](src/i1/docs/STATUS.md) records the latest maintained local assessment; original protocols, traces and independent conclusions must still be inspected at their exact SHAs.
- [I2 proposal status](src/i2/docs/STATUS.md) and [the I1 → I2 gate decision](docs/architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md) describe the unpromoted generation and required scientific reviews.
- [Research records](docs/research/README.md), [formal EXP conventions](experiments/README.md) and [live GitHub issues](https://github.com/josselin-orta-lab/individual-zero/issues) provide broader historical and operational context.

An experiment, an architectural proposal and an accepted ADR answer different questions. No GitHub label, green software test or closed issue alone establishes a scientific result.

## Research governance and maintenance

A research contributor creates or updates the **original** preregistration, method, observations, control results and review decision first. The curated graph is then updated with precise source paths, pinned Git blob identities, falsifiable claims and scope limits. If a source changes, the affected recommendation remains blocked for review until it is reconciled. Negative or null evidence remains visible.

For an architectural candidate consult [accepted decisions](docs/decisions/) and [the generation-promotion process](docs/engineering/ENGINE_PROMOTION.md). For an external component apply [RAI](docs/research/rai.md) and the applicable license/provenance process. These decisions do not belong in a speculative empty global inventory.

The six research axes above remain cross-cutting themes rather than permanent agent teams or separate branches.
