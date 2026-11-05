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
- **I2** is an **unregistered proposal with synthetic fixtures AND an internally executable, locally born native SQLite research prototype** (three-site paid movement, embodied need competition, local resources and cold audit). It is **not an activated engine**, independent M11 custody or an established general adaptive individual. Never give research opinions external motor or recovery authority. Read [current I2 status](src/i2/docs/STATUS.md) before planning work.
- **I3** is a newly imported, **unregistered research proposal** ([ADR-0014](docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md)). It has independent proposal source, a local lab and original G2/G2b/G2c evidence. P1.1 remains the reference; P1.2 was rejected by its preregistered general non-inferiority gate and survives only as an alternative branch. Read [I3 status](src/i3/docs/STATUS.md), [I3 documentation index](src/i3/docs/README.md) and its original evidence before new work. **I1 remains active; do not activate I3 or reinterpret its negative results.**
- [ADR-0001](docs/decisions/ADR-0001-strict-generation-autonomy.md): generations own their own cognition, Lab/WorldBody, UC, state, M11 and contracts. Parent lineage is historical; no inherited live memory, old-runtime fallback, resurrection, or silent schema migration.
- First-person observations only, no hidden-world oracle, no forced actions or bypass of generation-owned motor authority. Cognition must be charged in the generation's declared economy (UC in existing I1/I2 contracts, vital currency in the I3 proposal); no cost-free cognitive shortcut. Death is irreversible; uncertain or terminal M11 state cannot be restored.
- A green test or plausible survival is **not** a scientific GO.

## Scientific-prototype priority and drift reporting

Follow [ADR-0002](docs/decisions/ADR-0002-scientific-prototype-first.md), [ADR-0003](docs/decisions/ADR-0003-integrated-living-i2-milestone.md) and [ADR-0004](docs/decisions/ADR-0004-evidence-driven-development-and-g2-stop-rule.md) and [ADR-0008](docs/decisions/ADR-0008-remove-obsolete-i2-external-g1-review-gate.md), the project owner's explicit 1 November 2026 decisions. Prefer a **minimal integrated prototype that measures H1/H2/H3** over polishing G2 component guards for their own sake. Before each new intervention name the target question, falsifier, ablation/control, observable and the smallest runnable test. Record all negative/null outcomes, costs and what remains unobserved. **Signal DRIFT DETECTED** to the owner when work piles up complexity, repeated local proofs or CI without increasing end-to-end scientific information, and recommend a concrete correction. Request an arbitration if the scientific goal or safety authority must change. **I2 G2 STOP RULE:** PR #786 ends the open-ended synthetic-study campaign. Do not tune toy priors or add a synthetic owner/guard for its own sake. New G2-only tuning still requires a demonstrated scientific-validity defect or critical-path dependency. **ADR-0008 retires mandatory third-party G1 signoff:** the isolated native vertical prototype from closed #664 already exists; extend it only for current, falsifiable P2/P3/P4 gaps, without waiting for two reviewers or G0 custody #661. Keep I1 active, the registry unchanged, exact-source evidence, bounded internal motor effects, true UC accounting and fail-closed M11 limitations. Never infer a scientific GO or authenticated anti-rollback from a toy witness.

## I2 methodological rule (ADR-0012)

For new I2 research interventions, follow [accepted ADR-0012](docs/decisions/ADR-0012-i2-scientific-development-methodology.md) and the [I2 scientific development method](src/i2/docs/SCIENTIFIC_DEVELOPMENT_METHOD.md), within the existing [P0-P5 roadmap](src/i2/docs/INTEGRATED_BEHAVIOR_ROADMAP.md). Prefer a continuing individual's experienced-evidence -> paid motor -> bodily outcome -> later revised choice, then challenge a meaningful behavioral result in prospectively frozen held-out conditions **before adding new cognitive score rules**. Distinguish technical, behavioral and scientific claims; record NO_EXPOSURE, null/adverse lives and actual costs. At milestones, check whether experimental flags/owners should converge rather than proliferate. Safety and scientific-validity corrections or missing physical test substrate are exceptions, not reasons to demand a new experiment for every docs/bug fix. No second method authority or activation gate is created.

**Approved Individual Zero research direction (ADR-0013):** [Lived autonomy and experimental restraint](docs/decisions/ADR-0013-lived-autonomy-and-experimental-restraint.md) defines what counts as appropriate architectural intervention. Developers build the physical, innate, first-person and paid-choice conditions for an individual's own fallible history, **not** a rescue script or guaranteed survival. Before "fixing" a poor choice, distinguish invalid physical/evidence/authority integration, a genuine behavioral gap and a legitimate individual error. The [I2 architecture and science plan](src/i2/docs/EMBODIED_AUTONOMY_RESEARCH_PLAN.md) refines P3/P4 with one-life strategy revision and controlled individuality without adding a competing roadmap, new module or experiment permission.

## Change workflow and handoff

1. Record generation, task/issue, baseline SHA, intended files, dependency chain, invariants, expected behavioral impact and limits **before** editing.
2. Use a focused change. Distinguish documentation/technical fixes from behavioral changes requiring scientific justification. Keep proposals inert until promotion is explicitly authorized.
3. Verify the narrowest relevant static checks or software tests locally first. For I1 runtime changes, use the suites declared in `src/i1/engine.json` plus M11, generated-output parity and Python 3.11/3.12 CI **when affected**. For I2 fixtures use `src/i2/docs/TEST_PLAN.md`. For I3 proposal changes, start with `src/i3/docs/README.md` and `src/i3/docs/TEST_PLAN.md`, run the focused `tests/i3/` suite and keep any new held-out study prospective and independently reported.
4. Avoid expensive repeated Actions runs for intermediate documentation commits; request heavy scientific / full CI only when required by the actual scope and promotion gates. Never skip mandatory checks to get a green badge.
5. Handoff: exact commit SHA; files changed; checks PASS / FAIL / NOT_RUN and reason; actual observed behavior; scientific status; open issues and next falsifiable step.

For documentation-only work use `python tools/check_repo_navigation.py --scope entrypoints` when available. It is a structural check, **not** a test of cognition.
