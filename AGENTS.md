# Instructions for development agents

This file governs **repository work**, never the mind, values or behavior of a born individual. Read only the context relevant to the task; do not reconstruct the project from hundreds of historical pull requests.

## Start in this order

**When selecting the next intervention (rather than executing a specified task)**, first consult [global research coordination](docs/engineering/RESEARCH_COORDINATOR.md) and run `python tools/research_coordinator.py recommend`. Review evidence gaps, dependencies, negative results, live issues/PRs and the exact SHA before choosing a scoped task. A recommendation is not permission to run experiments or to approve a generation. Use `python tools/research_coordinator.py trace --id <question-or-gate-id>` to inspect curated provenance and `python tools/research_coordinator.py catalog` to find sources not yet directly indexed. Both are read-only and do not establish scientific truth.

1. Read [the agent navigation map](docs/engineering/AGENT_NAVIGATION.md) and `config/engine-registry.json` to establish the **active generation**.
2. Read the chosen generation's `engine.json`, its `AGENTS.md` (if present), and its own `docs/README.md` and `docs/STATUS.md`.
3. Read [ADR-0001](docs/decisions/ADR-0001-strict-generation-autonomy.md) and only the contracts, tests and evidence relevant to the affected boundary.
4. Inspect **live** GitHub main/branch HEAD, open issues, dependent PRs and the checks for the **exact** commit. Dated reports are snapshots, not live branch state.

## Authority and evidence, never interchangeable

| Question | Primary authority |
| --- | --- |
| Which engine is active? | `config/engine-registry.json` |
| What can run? | Generation-owned `engine.json` **plus executable source** |
| What is architecturally allowed? | Accepted ADRs and generation contracts |
| What has been software-tested? | Tests and CI on a specific commit SHA |
| What has been observed or scientifically established? | Current generation's evidence index, preregistration, traces, controls and explicit scientific verdict |

If documentation conflicts with executable source, identify the discrepancy rather than inventing behavior. Historical studies cannot certify the current engine.

## Non-negotiable boundaries

- **I0** (`src/i0/`, `archive/i0/`) is frozen: do not rewrite its bytes during another generation's work.
- **I1** is active and owns `src/i1/lab/`, `runtime/`, `modules/`, born identity and authenticated M11 persistence. The existing generated `i1lab` namespace belongs to I1 and must not be renamed casually.
- **I2** is a **proposal with synthetic test fixtures**, not a registered, executable or born individual. Never give its test opinions motor or recovery authority.
- [ADR-0001](docs/decisions/ADR-0001-strict-generation-autonomy.md): generations own their own cognition, Lab/WorldBody, UC, state, M11 and contracts. Parent lineage is historical; no inherited live memory, old-runtime fallback, resurrection, or silent schema migration.
- First-person observations only, no hidden-world oracle, no forced actions, no free UC, no bypass of Action Control. Death is irreversible; uncertain or terminal M11 state cannot be restored.
- A green test or plausible survival is **not** a scientific GO.

## Change workflow and handoff

1. Record generation, task/issue, baseline SHA, intended files, dependency chain, invariants, expected behavioral impact and limits **before** editing.
2. Use a focused change. Distinguish documentation/technical fixes from behavioral changes requiring scientific justification. Keep proposals inert until promotion is explicitly authorized.
3. Verify the narrowest relevant static checks or software tests locally first. For I1 runtime changes, use the suites declared in `src/i1/engine.json` plus M11, generated-output parity and Python 3.11/3.12 CI **when affected**. For I2 fixtures use `src/i2/docs/TEST_PLAN.md`.
4. Avoid expensive repeated Actions runs for intermediate documentation commits; request heavy scientific / full CI only when required by the actual scope and promotion gates. Never skip mandatory checks to get a green badge.
5. Handoff: exact commit SHA; files changed; checks PASS / FAIL / NOT_RUN and reason; actual observed behavior; scientific gate; open issues and next independent step.

For documentation-only work use `python tools/check_repo_navigation.py --scope entrypoints` when available. It is a structural check, **not** a test of cognition.
