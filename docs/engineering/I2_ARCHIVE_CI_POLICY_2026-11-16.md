# I2 archived-research CI policy · 16 November 2026

**Scope:** software/agent infrastructure maintenance after [ADR-0023](../decisions/ADR-0023-i2-archived-in-place-i3-context-focus.md). This changes **when** historical I2 tests run; it changes **no tests, I2 source, living identity, protocol, sample, receipt or scientific result**.

## Baseline and measured reason

At source baseline `main` `4a2e32de49bb7ab8a501b9f3f07cd7f31e92239c`, the preserved I2 proposal workflow automatically ran on pull requests changing `src/i2/**`, `tests/i2/**` and even shared static guard files. The [measured CI baseline](AGENT_CONTEXT_CI_REDUNDANCY_BASELINE_2026-11-16.md) found a median successful workflow wall time of **1,567 seconds** for its two successful runs in the 100-run sample (Nov 12–16). One [representative successful run](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43829717223) executed **877 test occurrences on each of Python 3.11 and 3.12**, with the two full shards per version disjoint and no discarded occurrences. These are historical measurements, **not** a projection of billable savings or evidence that any case is unnecessary.

Under the [I2 historical archive portal](../../archive/i2/README.md), both `src/i2/` and `tests/i2/` are preserved **at their original paths and exact Git tree hashes**. Normal PR maintenance is not supposed to change either tree. Re-running the whole expensive matrix on attempted edits to a protected archive, or on modifications to a common static policy, was disproportionate.

## New two-tier contract

| Path/event | Mandatory verification | Does it run original I2 suite? |
| --- | --- | --- |
| PR touches `src/i2/**`, `tests/i2/**`, I2 archive manifest/portal or archival guard | `agent-context-static.yml`, including `tools/check_i2_archive.py --json` and negative tests | **No.** Any tree drift fails closed. |
| PR touches `scripts/check_engine_repository.py`, `tests/test_engine_repository.py`, `tools/assess_engine_proposal.py`, `tools/i2_ci_shards.py` or the old I2 workflow | Same automatic static CI, including original repository-boundary unittests | **No.** Shared policy remains covered without I1 birth or historical I2 full matrix. |
| Operator explicitly starts `workflow_dispatch` for `i2-proposal-safety.yml` | Original 3.11/3.12 full I2 software suite, sharded as before, source checked out at `github.sha` | **Yes, manually only.** This does not authorize an I2 research cohort. |
| PR touches actual `src/i1/**` or `tests/i1/**` | Existing registered-I1 workflow unchanged | No change to I1 checks. |
| PR touches only the shared repository tests/guard | `agent-context-static.yml` runs the repository-boundary suite; `i3-proposal-checks.yml` no longer starts a full I3 matrix for these shared static paths | Neither full I2 nor full I3 test matrices start from the shared policy change alone. |
| I3-owned source, tests or a change to its own workflow | Existing full I3 software matrices for Python 3.11 and 3.12; frozen one-shot conditions unchanged | No I2 suite triggered. |

A reviewer cannot turn an I2 source/test change green by merely dispatching the old matrix: the mandatory **automatic** archive tree guard must still pass. The old manually triggered suite cannot update the archive manifest, activate I2, or create scientific evidence. Any proposal to reopen I2 requires a **new explicit archival decision**, preservation of original SHAs and separate provenance.

## Implementation and checks

- `.github/workflows/i2-proposal-safety.yml` now has **only** `workflow_dispatch`, preserving the full original 877-case-per-version historical test discovery and the independent proposal assessment. Its checkout is pinned to `github.sha` for the selected dispatch ref, not a now-absent PR head.
- `.github/workflows/agent-context-static.yml` watches all frozen I2 paths and the shared guard/tooling paths, runs the I2 archive guard and executes `tests/test_engine_repository.py` as a lightweight structural boundary suite.
- `tests/test_engine_repository.py` asserts that the archived matrix has no automatic PR trigger, still supports manual source-exact 3.11/3.12 verification, and that the static workflow covers every protected path and command. Original I1 trigger exclusions and live-workflow paths remain guarded. It also checks that I3's own source/test paths retain the 3.11/3.12 matrices while these shared static files do not trigger them.
- The historical [I2 portal](../../archive/i2/README.md) links to this policy. No file from the pinned `src/i2/` or `tests/i2/` tree is modified.

**Measured impact:** the *automatic* I2 full matrix now launches **zero** times for matching PR changes because it has no `pull_request` trigger; its former 1,567-second median runtime remains available on manual dispatch. The static gate still consumes its ordinary (previously measured 17-second median) runtime plus the newly added structural tests; shared-only changes also avoid unnecessary I3 software matrices; **the actual post-change duration must be observed on this PR**. No fabricated runner-minute saving or scientific verdict is inferred.

## Safe scientific boundary

I1 remains active, I3 the owner-selected unregistered reference. I2 remains `ARCHIVED_IN_PLACE`, never promoted or reanimated. Original I2 tests are **retained and executable only on explicit manual CI**. All historical negative, null and positive outcomes and exact-source evidence remain unchanged. A successful archival policy check is **not** a scientific result or a release permission.
