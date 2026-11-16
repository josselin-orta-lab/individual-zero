# I3 proposal-workflow rationalization: first tranche (16 November 2026)

**Baseline `main`:** `e33bc1ec4b0d5f1351f55b962f0aece606793b05`. This is **software-maintenance work only**, not a new experiment, World allocation, original-archive access, admissibility decision or new source pin for prior cohorts.

## Measured before and after

| Inventory | Before | Proposed active | Change |
| --- | ---: | ---: | ---: |
| YAML bytes | 111,686 | 71,236 | −40,450 (36.2%) |
| Lines | 2,324 | 1,516 | −808 |
| Declared jobs | 28 | 22 | −6 |
| Full actual I3 software jobs on an ordinary PR | 2 (3.11 and 3.12) | 2, unchanged | 0 |
| Historical permanently disabled one-shot job bodies | 6 (`if: false`) | 0 | Archived exactly |

The 6 retired job bodies accounted for **812 original lines**. A four-line explanatory comment replaces them. None had a `needs` consumer. Their removal **does not save 40,450 bytes of Git history**, because the original file is now intentionally retained byte-identically at [archive/i3/workflows](../../archive/i3/workflows/README.md). Nor does it imply billable runner savings: these six jobs were already disabled.

## Exactly what is retained

- The **complete** old file is pinned as original Git blob `370f34867330bce828d5de03135bb4f801917641` at `archive/i3/workflows/i3-proposal-checks-original-2026-11-16.yml` (outside the active GitHub workflow directory).
- The active header through `jobs:` is **identical** to that blob: PR target branches and paths; all six historically frozen `main`-push marker paths; read-only permissions; concurrency and cancellation rules.
- **Every one of the other 22 job definitions** remains byte-for-byte identical to the original. This includes source-exact I3 software checks (two Python versions), branch-gated engineering and the read-only original audits.
- The separate `i3-stage6-one-shot-20261115.yml` and `i3-stage7-persistence-one-shot-20261116.yml` workflows remain untouched and carry **no new execution authorization**.
- No test in `tests/i3/`, original data, frozen study plan, I3 Mind/World/Body/UC, I2 archive tree or I1 runtime is modified.

The extra [fail-closed static guard](../../tests/test_i3_workflow_archive.py) checks original Git blob identity, retired `if: false` gates, unmodified event header, byte identity of surviving jobs, and absence of a job that could become active on a historical main push. Its scope is exact; it does **not** certify the scientific adequacy of a research run.

## Required verification

- Run source-exact `agent-context-static.yml` PR CI, including `python -m unittest discover -s tests -p test_i3_workflow_archive.py -v`.
- Run the ordinary I3 software matrix on the PR HEAD: Python 3.11 **and** 3.12. Neither may be treated as a surrogate for the other.
- Confirm none of the six removed jobs appears as runnable work on the PR, and no `push` scientific transport was triggered.
- If a check fails, **do not** silently alter a retired original, source pin, run condition or allocation to force green. Record and review the cause.

## Deferred follow-up, not done in this tranche

The 21 remaining non-software jobs still use explicit research-branch gates. A later *separate* risk review may split them by contract and ownership, only after classifying actual run history, source-locked receipt dependencies, frozen original pointers and CI success criteria. No new blanket prefix permission, generalized `workflow_dispatch` or science job activation is proposed.

**Scientific context:** Stage6-light `beta_u_eff` primary ended 9/16 positive signs; Stage7 inherited G2 persistence 12/16 against the frozen 13/16 threshold. Both missed their primary sign concordance requirement. [Status and original receipts](../../src/i3/docs/STATUS.md) remain authoritative. This refactor changes no result and opens no cohort.
