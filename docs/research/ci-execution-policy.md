# GitHub Actions execution policy

**Status:** technical operating instructions. This is not a research protocol, a scientific result, INV-25 acceptance, or a Stage-9 Golden. The English normative specification `docs/architecture/reference/en/mvp-specification-v1.2.1.md` remains authoritative and unchanged.

## Cost control and triggers

The existing `.github/workflows/ci.yml` still contains all historical reference runs, scientific *diagnostics*, evidence uploads, Stage-9 300-step replay, and tests for Python 3.11 and 3.12. None has been deleted. Instead, the jobs have different conditions:

| Event | Runner jobs | Reason |
| --- | --- | --- |
| Push to any branch | **None** | Development commits must not automatically rerun the full campaign |
| Draft PR opened, synchronized or reopened | **None** | Drafts are intermediate work; run tests locally |
| Ready-for-review PR touching `src/**`, `tests/**`, `pyproject.toml`, CI/workflow configuration, Git attribute/ignore rules, scripts, packaging files or the English normative specification | **One lightweight `quick-checks` job on ubuntu-latest/Python 3.12** | All unittest checks plus a three-cycle CLI smoke test; no Stage-1–9 extended replay or artifact upload |
| Documentation-only PR, other than the English normative specification | **None** | Markdown editing does not require an executable validation |
| Explicit PR label `ci-unit` (on label application only) | **Unit and three-cycle smoke tests on Python 3.12** | Economical on-demand validation of draft development checkpoints |
| Explicit PR label `ci-full` (on label application only) | **Original exhaustive CI job on Python 3.11 + 3.12** | Human-requested cross-version validation and all software-reference diagnostics |
| Explicit `workflow_dispatch` | **Original exhaustive CI job on Python 3.11 + 3.12** | Manual Actions UI/API run, now available on the default branch |

PR targets are scoped to `main`, `i0/stage*`, `runtime/*` and `world/*`. The PR path filters are intentional. A `ci-full` label on a documentation-only PR cannot bypass the path filter. The manual workflow is now present on `main`: use **Actions > CI > Run workflow** and select the branch to validate. The `ci-full` label remains an alternative if that repository label is available or created in GitHub. To request a new full run later, remove and reapply that label. Similarly, apply `ci-unit` for a **single Python 3.12 unit/smoke run while the PR remains draft**, and remove it after the result is recorded; it does not enable routine draft checks. Merely leaving a label attached does not make later pushes run either job.

`concurrency.cancel-in-progress: true` replaces older PR-update jobs with the most recent check; explicit labeled unit and exhaustive runs each have their own concurrency group, so ordinary edits do not cancel operator-requested runs. Both jobs have bounded timeouts. The quick job runs on only one Python version; the full manual job retains both. There is no scheduled workflow and no push-triggered duplicate.

The `pyproject.toml` currently declares **no runtime dependencies**. Adding a persistent pip cache would mostly cache package-build downloads and may introduce cache upload/extraction overhead; the quick job deliberately avoids this extra step. Revisit caching if external dependencies become significant.

## Before integration

1. Run `python -m unittest discover -s tests -q` and `individual-zero --cycles 3 --seed 0 --run-id local-smoke --output /tmp/i0-local-smoke.jsonl` locally for code changes. If a local interpreter or checkout is unavailable, explicitly use the `ci-unit` label once on a draft PR rather than spending minutes on the full cross-version reference replay. Use isolated, synthetic local fixtures, never original held-out data.
2. Change the PR out of draft only when a reviewable patch is ready. A relevant PR event then runs the single lightweight CI gate.
3. For changes touching invariants, determinism, safety, physics, core world/runtime behavior, persistent evidence, or the Stage-9 scientific pipeline, deliberately request a **full CI** via `ci-full` or a manual dispatch before integrating. Do not interpret the quick green check as exhaustive regression coverage.
4. Inspect the results, including both Python versions and exact reference replay, before accepting critical changes. A failed or missing full run remains a blocker when full validation is scientifically or technically required.
5. For actual Stage-9 scientific acceptance, use the separate independent held-out operator runbook. Neither `quick-checks` nor `full-validation` proves independence, INV-25, or authorizes a Golden.

## Branch settings and caveats

At the time of the change, GitHub listed the inspected branches as **not protected**. The connector could not independently read detailed branch protection settings, and repository ruleset retrieval returned a plan limitation. Review GitHub's UI before introducing new required status checks: **a workflow skipped by `paths` can leave a required check pending**, and a skipped exhaustive job is **not** evidence that the job passed. If protection is enabled, require the *lightweight* `quick-unit-tests (Python 3.12)` check only where its trigger coverage matches the protected branch policy, and explicitly require documented manual full-validation before critical integration.

Removing automatic `push` checks means direct pushes to `main` no longer receive CI validation from this workflow after it is integrated there. Enforce reviewed PRs (or restore a lightweight main-branch post-merge smoke gate) if direct pushes become part of normal operations. The CI-cost policy has been propagated to `main` and all existing active Stage 1–9 branches; historic source and scientific artifacts were left unchanged. Subsequent stage branches must inherit the policy independently. After this propagation, the Stage-8-only CI base update was merged as a second parent into Stage 9, retaining the Stage-9 workflow and source tree.

This is an intentional quota-quality tradeoff. Preserve adverse and inconclusive outcomes; do not relax the normative specifications or scientific thresholds to satisfy a CI budget.
