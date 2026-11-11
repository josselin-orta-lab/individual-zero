# ADR-0020: I3 becomes the owner-selected reference generation for development

**Date:** 11 November 2026. **Status:** ACCEPTED BY OWNER (direct instruction). **Scope:** architecture and development routing; not an active-runtime cutover or scientific outcome verdict. **Decision baseline:** `main` `1e5f494f80116461a4f6a190f99f46a1296baa04`.

## Context

The owner has explicitly decided that **I3 becomes the reference engine** and that autonomous development may continue **without repeated owner validation**. Previously the global registry exposed only one canonical concept, `active_generation=I1`, while I3's own independently executable research/lab path remained intentionally a proposal with no registered birth/runtime entrypoints. Confusing the desired reference architecture with an installed active runtime would silently invalidate the engine contract, I1's existing born identities and the evidence boundary.

Current facts on this exact baseline:

- I3 has its own [Mind/Competition/Action Control](../../src/i3/modules/mind.py), [five-channel BodyLaws and two-currency CognitiveBudget](../../src/i3/modules/body.py), [World](../../src/i3/modules/world.py), [genome](../../src/i3/modules/genome.py), [native bounded lab-life runner](../../src/i3/runtime/life.py), tests and G/R research custody.
- Its [engine contract](../../src/i3/engine.json) still declares `status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, empty entrypoints and no active owner/publication roster or attested M11 cold-recovery interface.
- The [active-surface manifest](../../src/i3/ACTIVE_SURFACE.json) reports `current_stage=2.1 replay gate`, `REPLAY_GATE_CAPACITY_SHOWN` **as a software capacity**, `i3_registered=false`, `fresh_lived_worlds_allowed=false`, `next_scientific_cohort_authorized=false`. The scientific Stage-2 verdict remains `NOT_ISSUED`; E3's exact software information-to-motor candidate is `CLOSED_NEGATIVE` on its frozen artificial cases.
- [ADR-0001](ADR-0001-strict-generation-autonomy.md) forbids importing I1 runtime, state, memory, M11 identity or postmortem continuation into a successor; [promotion contract](../engineering/ENGINE_PROMOTION.md) requires an independent technical runtime before activation. Original one-shot scientific cohorts and owner lifts have already been consumed.

## Options

1. **Change `active_generation` to I3 immediately. Rejected:** I3 lacks declared registered entrypoints, authenticated native persistence/identity and a passing production-cutover contract. A label-only switch would cause contradictory automated checks and risk I1 runtime/state custody.
2. **Keep I1 as the research reference indefinitely. Rejected:** violates the explicit owner's new architectural choice.
3. **Select I3 as canonical architectural/development reference, retaining I1 as active runtime until technical release. Accepted.** Distinguishes a direction decision from a scientific claim or operational cutover.

## Decision

1. The canonical [engine registry](../../config/engine-registry.json) now has **`reference_generation: "I3"`**. This is the owner-selected target **for new architecture, source-level development priorities, research questions and default agent routing**. I3's current policy/reference implementation *inside its generation* remains **P1.3 funded-v2**, under Stage 2.1.
2. **`active_generation: "I1"` remains unchanged**, as do the registered generation map and I1's running birth/M11/engine contracts. The new reference key is **not** itself an I3 runtime registration or an alias that dispatches execution to an unregistered experiment.
3. I3 stays `status=proposal` and `activation=NOT_REGISTERED_NOT_EXECUTABLE` until a separate **source-pinned technical promotion release** establishes the executable interfaces and fail-closed recovery. No I3 scientific or existing original is relabeled as active/confirmatory, and no older generation's state is migrated.
4. The owner **delegates routine I3 research engineering, scoped source modifications, zero-World software tests, diagnostic archival reduction, documentation and PR integration** to agents without intermediate approval. Autonomous execution is not permission to falsify independent evidence or turn a speculative candidate into a scientific GO.
5. **Existing source/index-scoped scientific World permissions are not silently extended.** The completed 80/81, B1, content, next-decision and other source-locked cohorts remain `CLOSED_NO_RETRY`, and scientific admission remains fail-closed under the current manifest and ADR-0017/0019. An agent may independently prepare new precommitted protocols and propose a replacement scoped admission release; this ADR does not itself mint any World index. No per-step owner review is required for these preparations.
6. For **technical active-engine promotion**, a follow-on source-specific release will be recorded when the *objective tests* are demonstrated. It must not depend on a discretionary repeated owner confirmation, but must have verifiable code/tests and no unsafe change to previously born I1 lives. A new scientific GO remains a separate evidence decision and is **not** a prerequisite for recording I3 as the chosen research reference.

## Technical release criteria, in dependency order

| Gate | Required proof | Status at selection |
| --- | --- | --- |
| R0 reference selection | Registry, ADR, agent/document routing and fail-closed checks distinguish reference vs active | **Owner accepted; implementation in this PR** |
| R1 native constructor/identity | Defined I3 birth, first-person observations, complete motor authority, irreversibility, unique life identity; never import another generation | **Local lab run exists; registered birth API unproven** |
| R2 generation-owned state and persistence | Durable I3-only M11 provenance, single-writer/atomic publication, terminal/uncertain state fail closed, cold recovery and anti-rollback evidence; no I1 shared storage | **NOT DEMONSTRATED** |
| R3 integrated costed execution | Consistent one-step World+Mind+Learning, charged energy/vigilance, death and inactivity, native effects; no hidden reward/control authority | **Lab capacity exists; production transition unvalidated** |
| R4 exact-source integration tests | Source-lock, failure injection, Python 3.11/3.12, generation isolation, no historical-state resurrection, smoke/full native session and independent source custody | **NOT DEMONSTRATED for active I3** |
| R5 controlled active runtime cutover | Dedicated I3 owner-ledger/entrypoint contract, registry change, startup checks, non-migration of I1 sessions, rollback only for deployment code and never an individual's live identity | **NOT AUTHORIZED BY THIS REFERENCE POINTER** |

No scientific population inference is implied by passing R0-R5. Stage 2.1's research and negative/uncertain evidence remain independent of runtime release decisions. Prioritize R1/R2 native lifecycle integrity **before** speculative new model heads or arbitrary survival policies. Reuse existing I3 modules; no replacement of Competition or ad hoc feeding/drinking scripts.

## Falsifiers and handoff

**Falsifier for reference-selection correctness:** a parser, agent, run harness or CI treating `reference_generation=I3` as permission to invoke `run_engine_checks`/born sessions or to change `active_generation` without an independently tested production contract. Any such path must fail closed.

**Smallest test:** registry boundary suite rejects switched/missing reference, mistaken I3 registration or unsafe I3 manifest activation, and continues to accept I1 as active and I3 as explicitly chosen reference. No World constructed. Do not claim an actual I3 birth from this decision.

**Next technical work:** source-pin a generation-owned birth/state/cold recovery adapter design, implement in an isolated I3 runtime without I1 dependencies, then test terminal/rollback and cost/motor equivalence before proposing a production cutover. Continue separate scientific Stage 2.1 disposition under the [post-E3 audit](../../src/i3/docs/STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md) and the [B1 family sensitivity](../../src/i3/docs/studies/stage2-replay-gate-selected-design/B1_POSTHOC_FAMILY_RISK_BOUND_SENSITIVITY_2026-11-11.md).

**Owner validation policy:** accepted architectural reference selection, no repeated signoff for bounded engineering. Technical release requires objective evidence rather than an invented owner receipt; new scientific World admission remains a separately authored exact source/index decision, not inferred from this ADR.
