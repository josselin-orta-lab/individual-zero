# Task-scoped context routing for development agents

**Choose the scientific problem before choosing its files.** Start with [global research coordination](RESEARCH_COORDINATOR.md) and `python tools/research_coordinator.py recommend`. The task router is used only *after* selecting a justified intervention.

The repository root [`AGENTS.md`](../../AGENTS.md), generation-owned `AGENTS.md`, generation `engine.json`, and live source remain the authorities. The map at [`config/agent-context-map.json`](../../config/agent-context-map.json) is **only a navigational index**. It cannot register an engine, declare a mechanism active, launch a CI workflow, approve a scientific claim, or grant an I2 fixture motor authority.

## Two-minute workflow

From the repository root, without installing the engine:

```bash
python tools/agent_context.py routes
python tools/agent_context.py route --path src/i2/modules/lifecycle_external_witness.py
python tools/agent_context.py route --task 'I2 external witness' --format json
python tools/agent_context.py route --route i1-memory --generation I1
python tools/agent_context.py audit --json
```

Read the returned **authority** files first, then only the focused documents, code owners and tests. Inspect the current branch and exact HEAD before editing. The command never reads historic PR threads automatically and **never runs its suggested checks**.

If multiple changed paths resolve to different component owners, the router emits `AMBIGUOUS` and exits 2; select a route explicitly, or split the task into coherent sub-tasks. For text descriptions, keyword matching is a *hint*, not guaranteed semantic understanding. Prefer `--path` or `--route` when decisions are sensitive.

## Sources of truth, in precedence order

| Question | Where to verify |
| --- | --- |
| Which generation is active? | `config/engine-registry.json` at the live SHA |
| What can execute? | `src/iN/engine.json` plus actual live source, active constructors and entrypoints |
| What is allowed? | Accepted ADRs, generation-owned contracts and source invariants |
| Which files and tests are relevant? | This **navigation-only** context map, cross-checked with actual call sites |
| What passed on the exact SHA? | Local test output and/or GitHub CI results for that SHA |
| What is scientifically established? | Generation-owned evidence matrix, preregistration, traces and reviewed verdict |

A historical document never overrides current code or an accepted current contract. See [document authority classes](DOCUMENT_AUTHORITY.md) and [component ownership guide](COMPONENT_OWNERSHIP.md).

## Script and workflow custody

For scripts, the router reads the existing [`config/tool-inventory.json`](../../config/tool-inventory.json): `ACTIVE_CI_INFRASTRUCTURE` means an explicit infrastructure classification, **not permission to run**; `REVIEW_REQUIRED_NOT_PROVEN_OBSOLETE` preserves undecided historical custody. Unknown scripts and workflows remain unreviewed. The map supplies additional **advisory** classifications for a handful of current workflows, with a conservative default of `UNREVIEWED` for all others.

Do not run historical cohorts, heavy GitHub Actions or scientific benchmarks just because a script appears in a route. Inspect `.github/workflows/` and [`START_HERE.md`](START_HERE.md). Use the smallest meaningful local check before requesting the exact required CI. No routing result is scientific evidence.

## Updating the route map

Keep ownership declarations small and grounded in real paths. Add a route only when it identifies a stable intervention boundary, canonical documents, real owner paths, targeted tests and meaningful invariants. Prefer updating an existing route over creating redundant instructions. Ensure paths exist and the generation is correct. Run:

```bash
python tools/agent_context.py audit --json
python -m unittest discover -s tests -p test_agent_context.py -v
python tools/check_repo_navigation.py --scope entrypoints
```

The scoped [`agent-context-static`](../../.github/workflows/agent-context-static.yml) PR check runs only these navigation checks. It never instantiates an individual or performs science. Changes to engine contracts, actual runtime, behavioral modules or promotion still require their separate generation-specific checks and reviews.

## Handoff

Use the shared [handoff convention](AGENT_HANDOFF.md) and generate an *unverified* draft with:

```bash
python tools/agent_context.py handoff --route i2-witness --sha <exact-40-character-commit-sha>
```

Replace placeholders only with observed facts. Keep `NOT_RUN`, `NOT_OBSERVED` and `NOT_EVALUATED` where appropriate. No saved handoff becomes a new source of scientific authority.
