# Architecture proposals: review and provenance index

**Index, not approval.** Entries below are dated design/research records. A document under `proposals/` is **not automatically accepted**, executable or the normative architecture of I1 or I2. Verify the exact dated header, accepted ADRs, live issue disposition and tested source at HEAD. Historical files must remain immutable unless correcting their provenance with an explicit review.

## Current I2 transition and unapproved G1 design

| Document | Kind and review boundary |
| --- | --- |
| [I1 → I2 transition and scientific gates](i2-transition-and-scientific-gates-2026-10-31.md) | **Approved research-transition decision**, **not** I2 birth, implementation, registration or scientific GO |
| [I2 continuity and learning contract](i2-continuity-and-learning-contract-2026-10-31.md) | **G1 proposal; independent review pending**. Hypotheses, ownership and negative tests |
| [I2 authority, COMMIT and external witness ADR candidate](i2-g1-authority-commit-and-independent-witness-adr-2026-10-31.md) | **PROPOSED / REVIEW_REQUIRED**. Not an accepted ADR. Dated source diagram may use superseded synthetic schemas |
| [I2 publication/crash boundaries](i2-publication-boundaries-g1-review-2026-10-31.md) | **Proposed G1 review** for future atomicity, external anchor and physical publication, not implemented living M11 |
| [I2 G1 current-source review delta (2026-11-01)](i2-g1-current-review-delta-2026-11-01.md) | **REVIEW_REQUIRED**, reconciles superseded fixture descriptions and supplies C0-C11 physical crash/fencing counterexamples and R1-R8 independent decisions; **not** an accepted ADR or G3 proof |
| [I2 G1 single-owner WorldBody publication candidate (2026-11-01)](i2-g1-single-owner-world-publication-candidate-2026-11-01.md) | **PROPOSED / REVIEW_REQUIRED**: one concrete R1-R4/R7 design alternative, public visibility/fencing boundary and C0-C11 falsification obligations, not accepted or executable |

I2's **live proposal software status** is owned by [`src/i2/docs/STATUS.md`](../../../src/i2/docs/STATUS.md) and [I2's engine contract](../../../src/i2/engine.json). An I2 synthetic G2 test cannot satisfy G1 architectural approval or G3 authenticated mortality and persistence.

## Historical I1 isolation and MVP migration material

| Document | Scope (do not treat as an active contract) |
| --- | --- |
| [I1 isolated fork, October 2026](i1-isolated-fork-2026-10-16.md) | Historical creation/isolation record; import paths and patch stages may be superseded by native I1 ownership |
| [MVP v1.3.3 migration and science gates](mvp-v1.3.3-migration-and-science-gates.md) | Historical implementation handoff and unfulfilled scientific gates |
| [MVP v1.3.2 DC05 food-safety delta](mvp-v1.3.2-dc05-food-safety-semantics-delta.md) | Dated targeted semantic proposal, not a broad new-generation mandate |

Authoritative specification versions live in the separate [reference index](../reference/README.md). A superseded MVP draft never overrules current source contracts.

## Historical Stage6/Stage12 and issue #110 design studies

These records are useful for provenance and counterexamples, but **not** the active I1 execution map:

- [Bounded progressive planning, Stage6](stage6-bounded-progressive-planning-addendum-issue110.fr.md) and [MVP clarification](stage6-progressive-planning-mvp-clarification-2026-10-14.fr.md)
- [Subjective goals and agency, Stage12](stage12-subjective-goal-agency-v1-issue110.fr.md) and [v1.3.2 adoption/migration checklist](stage12-v132-adoption-and-migration-checklist-issue110.md)
- [Spatial world reachability](stage12-ga-spatial-world-reachability-issue110.fr.md) and [external-obstacle/subgoal delta](stage12-ga-external-obstacle-subgoal-delta-issue110.fr.md)

## Rules for agent use

1. Check the **generation**, author/date, historical SHA, proposal state and whether a separate ADR has actually been accepted.
2. Compare the proposition with the actual [active registry](../../../config/engine-registry.json), [I1 implementation map](../../../src/i1/docs/STAGES_AND_INTERFACES.md) or [I2 research handbook](../../../src/i2/docs/README.md). Do not repair current runtime code based solely on an older proposal sketch.
3. Trace claims to their original tests and experimental data; explicitly label `NOT_TESTED`, `NOT_ESTABLISHED` or `REVIEW_REQUIRED`.
4. Keep successor generations independent, with **no fallback to obsolete engines, copied living memory, silent schema migration or synthetic motor authority**. Follow [ADR-0001](../../decisions/ADR-0001-strict-generation-autonomy.md).
5. To propose a new design, use the [independent-generation template](../INDIVIDUAL_TEMPLATE.md) and [promotion process](../../engineering/ENGINE_PROMOTION.md); update this index only when a real record is added or its reviewed status changes.

Return to the [Architecture Atlas](../ATLAS.md) for a task-oriented view. This index lists only the existing files, never invents a new implementation or experimental verdict.
