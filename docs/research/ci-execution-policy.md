# Minimal-cost GitHub Actions policy

The project uses **one** GitHub Actions workflow per branch (`.github/workflows/ci.yml`). This file changes CI orchestration only: no tests, historical diagnostic scripts, scientific evidence or normative implementation requirements are removed.

## Triggers and checks

- Ordinary Git pushes: **no CI jobs**. This avoids redundant push and PR runs.
- Draft PR updates: **no CI jobs**. Run local unit tests while the patch is under development.
- Review-ready PRs changing source code, tests, packaging, scripts, workflows or the English normative specification: **one light Linux/Python 3.12 job**, running `python -m unittest discover -s tests -q` and a three-cycle CLI smoke test.
- Documentation-only PRs, excluding the normative English specification: **no CI jobs**.
- A human requests the full archived reference checks by applying the **`ci-full` PR label** or using **Run workflow** in GitHub Actions (enabled by this workflow on the default branch). For PRs, remove and reapply the label to request a fresh run after further changes.
- Full runs preserve their original Python 3.11/3.12 matrix and all preexisting stage-specific reference replay, artifact, and safety validation steps. This can be important before integrating physical, determinism, invariants, learning, safety, provenance or scientific-evidence changes.

The quick job is capped at 5 minutes, each full job at 12 minutes. `concurrency.cancel-in-progress` cancels stale checks but separates the `ci-full` label request from normal PR edits. No schedule or new dependency cache is introduced because current `pyproject.toml` has no external runtime dependencies. Use local tests before pushing; archive actual held-out research data only under the independently witnessed scientific protocol.

## Status checks and release discipline

GitHub reported the repository's branches as *not protected*. The connector cannot independently read full branch protection details. Before requiring a job by name, confirm that skip conditions and path filters will not leave the branch's required checks pending: a **skipped workflow is not a successful test result**.

This budget policy assumes review through PRs: direct pushes to `main` no longer trigger an automatic post-push test. For critical code and protocol changes, request and inspect the manual full workflow before integrating, preserving failure evidence. Never interpret a passing software reference test as an independent Stage-9 held-out evaluation, INV-25 conclusion, or Golden. The unchanged English `docs/architecture/reference/en/mvp-specification-v1.2.1.md` remains normative.

All legacy development branches contain their own workflow snapshots. Coordinate policy propagation to those branches before assuming they benefit from the defaults on `main`.
