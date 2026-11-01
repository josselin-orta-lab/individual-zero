# GitHub Actions workflow ownership and historical custody

This is a **routing and review guide**, not an authorization to run old experiments or a claim that a historical workflow is safe to delete. Always inspect current `.github/workflows/` at the **exact Git commit**; workflow triggers and referenced source may change.

## Current entrypoints

| Intent | Current workflow | Meaning |
| --- | --- | --- |
| Active I1 regression and its shared structure gate | [I1 current CI](../../.github/workflows/i1-current-ci.yml) | Software checks on the exact I1 PR HEAD; potentially expensive. Never scientific GO. |
| Reusable engine structure | [Engine structural](../../.github/workflows/engine-structural.yml) | Contract, registry and source ownership checks; callable and manually dispatchable, not proof of a living result. |
| Agent documents, architecture map and accepted decisions | [Agent context static](../../.github/workflows/agent-context-static.yml) | Existing lightweight navigation and source-pin checks, no intentional living run. |
| Inert I2 contracts and synthetic source changes | [I2 proposal safety](../../.github/workflows/i2-proposal-safety.yml) | Synthetic checks only. No WorldBody birth, motor authorization or promotion. |

**Do not** infer that every other YAML file is obsolete. The root directory also contains focused regressions, read-only scientific observers, manual laboratories, frozen-source comparisons and historical campaign launchers. Their names do not establish their current status.

## Representative historical and narrowly scoped routes

| Workflow | Observed trigger at 1 November 2026 | Conservative handling |
| --- | --- | --- |
| [I1 isolated fork](../../.github/workflows/i1-isolation.yml) | `workflow_dispatch` | I1-owned isolation and historical experimental-regression checks; no embedded I0 planning suite or frozen Lab restoration. |
| [I0 archive](../../.github/workflows/i0-archive-manual.yml) | `workflow_dispatch` | Historical I0 tests only, with original Lab and test paths reconstructed **inside a disposable CI checkout**; never a current I1 acceptance gate. |
| [I1 A2.38 confirmatory](../../.github/workflows/i1-a238-confirmatory.yml) | `workflow_dispatch` | Prior large cohort; preserve protocol and artifacts; do not rerun for repository maintenance. |
| [I1 A2.31 pairs](../../.github/workflows/i1-a231-science.yml) | `workflow_dispatch` | Historical prospective cohort; not ordinary code CI. |
| [I1 A0 six-world pilot](../../.github/workflows/i1-eco-a0.yml) | `workflow_dispatch` only, after the 1 November 2026 maintenance correction | Preserves operator-invoked six-world evidence, but never runs a birth as a side effect of changing the tool or workflow. |
| [I1 A1-C one-shot](../../.github/workflows/i1-eco-a1c-one-shot.yml) | `push` to `main` with workflow-path filter **and** a commit-marker job guard | Historical expensive one-shot protocol. Changing or relocating its YAML requires a separate explicit source/custody and trigger review. |
| [I1 S1 72-life](../../.github/workflows/i1-s1-main-72-life.yml) | Narrow historical-branch `push` and `workflow_dispatch` | Prior 72-life experiment; do not assume an old branch is dead or trigger it while tidying. |
| [I1 A2-R reward birth L1](../../.github/workflows/i1-a2r-reward-birth-l1.yml) | Focused `pull_request` paths plus `workflow_dispatch` | Research tooling regression contract, not a confirmatory cohort or I1 scientific result. |
| [I1 manual preset worlds](../../.github/workflows/i1-preset-worlds.yml) | `workflow_dispatch` with explicit inputs | Physical I1 laboratory. Run only with a justified experiment, not as a documentation check. |

These are **verified examples, not a census of all workflows**. An unlisted YAML remains `UNREVIEWED`. Determine its actual `on:` events, path filters, job-level conditions, sources, artifacts, dependencies, matrix size and run history before assigning ownership.

## Safe consolidation procedure

1. **Check current Git state and open PRs.** Do not change a workflow that an open PR is modifying or whose original experiment may still be awaiting review.
2. **Classify the trigger, separately from the job.** `workflow_dispatch` is manual, `pull_request` can run on a matching edit, and `push` can run even when a job later skips. Path filters, branch filters, marker guards and `if:` clauses must be inspected together. A green skipped job is not an executed scientific result.
3. **Trace custody.** Record the workflow's original Git blob SHA, source script/test paths, original EXP/preregistration, artifact references, historical CI run links and any exact-SHA source pins. Check original paths, imports and external retention before moving or deleting anything.
4. **Choose the least disruptive action.** Keep active checks; leave unreviewed campaigns intact; when historical custody is established, propose a reviewed in-place manual-only guard or preservation in `archive/` while keeping original YAML history discoverable. Never silently disable a necessary check or reproduce a cohort through cleanup.
5. **Verify proportionately.** Documentation-only changes use the agent static guard. Changes to workflow trigger semantics, engine safety checks or research launches need a dedicated review and focused checks. Preserve existing mandatory requirements; no new heavyweight runs solely to validate file organization.
6. **Handoff.** Name the exact Git SHA, workflow path, evidence/custody links, trigger before/after, relevant observed CI, scientific status (`NOT_EVALUATED` for navigation only) and unresolved risks.

**Priority:** finish the pending I1 test-placement PR and avoid new overlapping CI branches. Research navigation should accelerate the [minimal integrated living-I2 milestone](../decisions/ADR-0003-integrated-living-i2-milestone.md), not become another open-ended engineering campaign. See [script custody](SCRIPT_INVENTORY.md), [start guide](START_HERE.md) and [document authority](DOCUMENT_AUTHORITY.md).
