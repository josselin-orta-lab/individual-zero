# Architecture: start here

**This is the architecture portal, not a second specification.** To understand the project quickly, open the [Architecture Atlas](ATLAS.md) first. It distinguishes executable I1, non-living I2 research, frozen I0 and historical references. The [global agent route](../engineering/AGENT_NAVIGATION.md) covers non-architecture tasks.

## Two-minute architecture navigation

| What you need | Read this | Verify in the owning source |
| --- | --- | --- |
| Understand the whole system and its causal handoffs | **[Architecture Atlas](ATLAS.md)** | [engine registry](../../config/engine-registry.json) |
| Choose the next justified research intervention | [Research coordinator](../engineering/RESEARCH_COORDINATOR.md) and [curated dossiers](../engineering/RESEARCH_DOSSIERS.md) | Original scientific records and current open review gates, not a software PASS |
| Locate which generation owns Lab, state, identity and runtime | [Engine generations](ENGINE_GENERATIONS.md) | each generation's `engine.json` and executable code |
| Modify an active I1 mechanism | [I1 handbook](../../src/i1/docs/README.md), [Stage ownership](../../src/i1/docs/STAGES_AND_INTERFACES.md) | [I1 engine contract](../../src/i1/engine.json), active callers and tests |
| Investigate I1 learning or scientific claims | [Evidence matrix](../../src/i1/docs/EVIDENCE_MATRIX.md) | dated experimental protocols and traces |
| Explore I2 without activating it | [I2 research handbook](../../src/i2/docs/README.md) | [I2 contract](../../src/i2/engine.json), synthetic tests, review gates |
| Evaluate a design or proposal | [Proposal and review index](proposals/README.md) | approved ADRs, open review, and original SHA |
| Find a versioned historical MVP theory or specification | [Versioned references](reference/README.md) | document-specific normative language, version and scope |
| Propose an independent new generation | [Generation review template](INDIVIDUAL_TEMPLATE.md) | [ADR-0001](../decisions/ADR-0001-strict-generation-autonomy.md) and [promotion process](../engineering/ENGINE_PROMOTION.md) |

## Status and authority

- **I0** is a frozen research reference with immutable archived bytes.
- **I1** is the active generation with its own Lab, cognition, identity, mortal M11 and tests. Its generated `i1lab` namespace belongs to I1 and must not be reused by a successor.
- **I2** contains only independently scoped **synthetic G2 research fixtures** and G1 proposals. It is **not registered, executable or born**; successful tests are not a scientific GO.

These are **orientation snapshots**. Trust, in order: current [registry](../../config/engine-registry.json) for activation; generation-owned engine contract and **real source** for execution; approved ADRs for architectural permission; exact-SHA CI for software verification; reviewed experimental evidence for scientific conclusions.

## Historical architecture references (read without promoting them)

- [Original I0 overview](I0_OVERVIEW.md) and [bootstrap runtime](BOOTSTRAP_RUNTIME.md): archived historical semantics, **not** current natural I1.
- [MVP v1.2.1 implementation map](IMPLEMENTATION_MAP_V1.2.1.md) and [Stage3](TECHNICAL_DECISIONS_STAGE3.md) / [Stage4](TECHNICAL_DECISIONS_STAGE4.md) technical decisions: dated implementation notes. Their old "current branch" statements refer to the historical checkout.
- [Versioned MVP and conceptual references](reference/README.md): keep their normative *historical* scope; superseded proposals cannot silently override active generations.
- [Dated research proposals](proposals/README.md): use their header and review state, not their filename, to determine whether they are accepted.

**Do not duplicate** detailed module behavior here. Place actual mechanisms, interfaces and evidence with the owning generation. The Atlas is a short cross-generation map with verified links. Changing an agent navigation link is documentation work; changing a living action, UC, mortality or M11 invariant requires software and scientific review.
