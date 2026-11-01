# Minimal handoff between development agents

A handoff makes an intervention reproducible and understandable without mining historical pull requests. It is **not** a substitute for the current registry, source, contracts, tests or scientific evidence.

Create a starter template with `python tools/agent_context.py handoff --route <route-id> --sha <40-hex-SHA>`. The SHA must identify the *actual code used for the handoff*, not merely a branch name. If the exact SHA is unknown, leave it marked as required.

A usable handoff records:

1. The generation and route, exact baseline and resulting commit SHA, issue/PR and changed paths.
2. The original objective, impacted owners, direct dependencies, preserved invariants and actual changes.
3. Tests as `PASS`, `FAIL` or `NOT_RUN` with commands, environment and exact SHA; CI status must refer to the same SHA.
4. Observed behavior and traces as `OBSERVED` or `NOT_OBSERVED`, with precise artifacts and limitations.
5. Scientific gate as its actual separately reviewed verdict, or `NOT_EVALUATED`. A unit-test PASS is never a scientific GO.
6. Open risks, blockers, authorization boundaries and the next *independent* step.

For I2, a synthetic fixture, committed SQLite cycle or externally injected witness is not living runtime authority; describe G2 diagnostics without implying G3 activation. For I1, do not infer first-person learning or recovery semantics from green tests alone.

For a multi-agent effort, prefer one handoff per coherent route. If boundaries cross, explicitly enumerate each dependent route; do not silently collapse a cognition/persistence/observer change into a generic handoff. Keep historic work inspectable rather than rewriting old results.

For research-coordinator-driven work, include the question ID, targeted gate, blocking predecessors, proposed falsifying observation and source/issue status at the exact SHA. A gate stays unapproved unless separately reviewed. See [global research coordination](RESEARCH_COORDINATOR.md).

For research interventions, record which broader corpus candidates were reviewed versus left `NOT_REVIEWED` (see [corpus index](RESEARCH_CORPUS.md)). Also attach the relevant `trace` node identifiers, actual source paths and exact SHA, including negative/null results and any uncited documents subsequently reviewed. Filename hints and matching text markers never stand in for scientific evidence.

For a curated research dossier, record its ID, the actual reported assessment, exact source blob pins, protocol/cohort/endpoint identity, unresolved original-data and independent-review gaps, and the next falsification question. The [dossier register](RESEARCH_DOSSIERS.md) never substitutes for a signed scientific decision.
