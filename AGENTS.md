# Instructions for development agents

This file governs **repository work**, never the mind, values or behavior of a born individual. Read only the context relevant to the task; do not reconstruct the project from hundreds of historical pull requests.

## Start in this order

**When selecting the next intervention (rather than executing a specified task)**, first consult [global research coordination](docs/engineering/RESEARCH_COORDINATOR.md) and run `python tools/research_coordinator.py recommend`. Review evidence gaps, dependencies, negative results, live issues/PRs and the exact SHA before choosing a scoped task. A recommendation is not permission to run experiments or to approve a generation. Use `python tools/research_corpus.py report --top 8` to discover original protocols, findings and candidate links across the broader corpus (these are strictly unverified lexical hints). Before treating a candidate pairing as established, examine [curated research dossiers](docs/engineering/RESEARCH_DOSSIERS.md) using `python tools/research_dossiers.py gaps` or `show --id I1-A1C-TARGETED`. Dossiers keep missing original outcomes and independent reviews explicit. Use `python tools/research_coordinator.py trace --id <question-or-gate-id>` to inspect curated provenance and `python tools/research_coordinator.py catalog` to find sources not yet directly indexed. Both are read-only and do not establish scientific truth.

1. Read [the agent navigation map](docs/engineering/AGENT_NAVIGATION.md) and `config/engine-registry.json` to establish the **active generation**.
2. Read the chosen generation's `engine.json`, its `AGENTS.md` (if present), and its own `docs/README.md` and `docs/STATUS.md`.
3. Read [ADR-0001](docs/decisions/ADR-0001-strict-generation-autonomy.md) and only the contracts, tests and evidence relevant to the affected boundary.
4. Inspect **live** GitHub main/branch HEAD, open issues, dependent PRs and the checks for the **exact** commit. Dated reports are snapshots, not live branch state.

For location-oriented lookup use [test placement](tests/TEST_LAYOUT.md), [archive custody](archive/README.md), [research records](docs/research/README.md), and `python tools/repository_layout.py inventory --kind tests --match <topic>`. These navigation tools never move or promote source-pinned evidence.

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

## Scientific-prototype priority and drift reporting

Follow [ADR-0002](docs/decisions/ADR-0002-scientific-prototype-first.md), [ADR-0003](docs/decisions/ADR-0003-integrated-living-i2-milestone.md) and [ADR-0004](docs/decisions/ADR-0004-evidence-driven-development-and-g2-stop-rule.md) and [ADR-0008](docs/decisions/ADR-0008-remove-obsolete-i2-external-g1-review-gate.md), the project owner's explicit 1 November 2026 decisions. Prefer a **minimal integrated prototype that measures H1/H2/H3** over polishing G2 component guards for their own sake. Before each new intervention name the target question, falsifier, ablation/control, observable and the smallest runnable test. Record all negative/null outcomes, costs and what remains unobserved. **Signal DRIFT DETECTED** to the owner when work piles up complexity, repeated local proofs or CI without increasing end-to-end scientific information, and recommend a concrete correction. Request an arbitration if the scientific goal or safety authority must change. **I2 G2 STOP RULE:** PR #786 ends the open-ended synthetic-study campaign. Do not tune toy priors or add a synthetic owner/guard for its own sake. New G2-only tuning still requires a demonstrated scientific-validity defect or critical-path dependency. **ADR-0008 retires mandatory third-party G1 signoff:** implement the isolated I2 vertical prototype in #664 now, without waiting for two reviewers or G0 custody #661. Keep I1 active, the registry unchanged, exact-source evidence, bounded internal motor effects, true UC accounting and fail-closed M11 limitations. Never infer a scientific GO or authenticated anti-rollback from a toy witness.

## Change workflow and handoff

1. Record generation, task/issue, baseline SHA, intended files, dependency chain, invariants, expected behavioral impact and limits **before** editing.
2. Use a focused change. Distinguish documentation/technical fixes from behavioral changes requiring scientific justification. Keep proposals inert until promotion is explicitly authorized.
3. Verify the narrowest relevant static checks or software tests locally first. For I1 runtime changes, use the suites declared in `src/i1/engine.json` plus M11, generated-output parity and Python 3.11/3.12 CI **when affected**. For I2 fixtures use `src/i2/docs/TEST_PLAN.md`.
4. Avoid expensive repeated Actions runs for intermediate documentation commits; request heavy scientific / full CI only when required by the actual scope and promotion gates. Never skip mandatory checks to get a green badge.
5. Handoff: exact commit SHA; files changed; checks PASS / FAIL / NOT_RUN and reason; actual observed behavior; scientific status; open issues and next falsifiable step.

For documentation-only work use `python tools/check_repo_navigation.py --scope entrypoints` when available. It is a structural check, **not** a test of cognition.
