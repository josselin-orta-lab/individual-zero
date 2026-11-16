# Baseline: agent context, documentation, test overlap and CI cost (16 November 2026)

This is a **measured maintenance baseline**, not a scientific finding, an engine promotion, a permission to restart a cohort, or a decision to discard historical evidence. It precedes any migration or deletion of retained repository documents, tests, and workflows.

## Exact snapshot and scope

- Source: `main` HEAD `9091387a24644865605520b4c42c3f997dce1e3d`; GitHub [recursive tree](https://api.github.com/repos/josselin-orta-lab/individual-zero/git/trees/main?recursive=1), `truncated=false` at the snapshot. PR #1417 changes are **not** included in the baseline.
- Inventory counts Git-tracked blobs only, not generated artifacts or tests executed. A document is a file whose suffix is `.md`, `.mdx`, `.rst`, or `.txt`. `archive/` is the archive exclusion used for the active-document count.
- Identical content is identified by matching Git blob SHA, **not** by filename. Equal names like `RESULTS.md` in different frozen studies are not duplicates by definition.
- Python test-file inventory includes `tests/`, `src/i1/tests/`, `src/i2/tests/`, `src/i3/tests/`, `tools/**/tests/`, and `archive/i0/tests/` for `*.py`. A file count is not a unittest-case count.

| Tracked inventory | Measured |
| --- | ---: |
| All files | 3,703 |
| Document files (including archive) | 1,193 (9,155,836 bytes) |
| Documents outside `archive/` | 1,172 (9,006,863 bytes) |
| `src/i3/docs/` document files | 379 (2,801,811 bytes) |
| `docs/engineering/` document files | 17 (118,643 bytes) |
| Python test files in the specified test locations | 918; 622 outside `archive/` |
| Exact duplicate document blob groups | **0** |
| Exact duplicate Python test blob groups | **0** |
| `.github/workflows/*.yml` / `*.yaml` | **71**, totaling 253,625 bytes |

The largest active status file, `src/i3/docs/STATUS.md`, is **252,350 Git bytes** (roughly 2,362 fetched lines and 133 Markdown headings). The ordinary I3 proposal workflow is **111,686 bytes / 2,324 lines**, or **44.0%** of all workflow-YAML bytes. These are navigation/maintenance load indicators, **not proof of duplicative or obsolete content**.

### Content-reuse screen, not a semantic-duplication verdict

A targeted **16-document** review covered I3 `STATUS`, `README`, `DEVELOPMENT_PLAN`, their dated pre-generalization counterparts, four Stage-2 audits, the three candidate-I custody-stress versions, and the engineering `AGENT_CONTEXT`, `AGENT_HANDOFF`, `AGENT_NAVIGATION` guides. After lowercasing and removing URLs/punctuation, we compared unique consecutive **seven-token shingles**. Pairwise *containment* is `shared shingles / min(shingles in each document)`. In this targeted sample, **highest containment was 1.9%** (I3 STATUS versus README), and **0 pairs reached 25%**. This detects literal/near-literal reuse only. It cannot detect paraphrase, conflicting instructions, copied facts in different words, or near-duplicate material in the other 1,177 documents.

The actionable documentation conflict is a **routing/function overlap**, not byte equality: `docs/engineering/AGENT_CONTEXT.md`, `AGENT_HANDOFF.md`, and `AGENT_NAVIGATION.md` already define agent routing, handoff, and startup conventions. Additions must extend those owners, not establish a fourth independent authority. Dated original protocols, outcomes, negative results, and custody indexes remain source-pinned.

## Observed GitHub Actions costs

Sample: latest 100 workflow runs returned by [Actions runs endpoint](https://api.github.com/repos/josselin-orta-lab/individual-zero/actions/runs?per_page=100), created between **2026-11-12 07:43:08 UTC** and **2026-11-16 10:38:35 UTC**. Duration for this summary is `updated_at - run_started_at` for **successful** runs only, and is the workflow wall/window proxy, **not CPU consumption, billable minutes, or cost in money**. The median is the conventional midpoint (mean of two central values for even sample sizes). Failed/cancelled runs are counted but excluded from successful-duration quantiles.

| Workflow family | Runs | Success | Cancelled | Failed | Median successful wall | P90 successful wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| I3 proposal software | 79 | 52 | 17 | 10 | **207.5 s** | 256 s |
| Agent context static | 7 | 7 | 0 | 0 | **17 s** | 23 s |
| I2 proposal-only safety | 5 | 2 | 3 | 0 | **1,567 s** | 1,573 s |
| Stage6 one-shot workflow-path failures | 7 | 0 | 0 | 7 | n/a | n/a |
| Stage6-light sealed engineering/science | 1 | 1 | 0 | 0 | **6,118 s** | n/a |
| Stage7 persistence one-shot | 1 | 1 | 0 | 0 | **8,671 s** | n/a |

The last two are **purpose-built one-shot scientific/engineering transports**, not routine CI and **not candidates for test-cost shortcuts**. An Actions SUCCESS does not establish a positive scientific hypothesis; verify frozen receipts and the formal verdict separately. Counts describe the sampled first page only, not the entire Actions history.

### Representative actual jobs and test counts

- [I3 PR checks #43837832547](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43837832547): 29 listed jobs, **27 SKIPPED**, two software jobs PASS. Python 3.11 job **161 s**, Python 3.12 job **258 s**; **419 job-seconds summed**. Logs: `Ran 1577 tests` in each version, plus `Ran 10 tests` for the common repository-boundary suite in each version. Skipped jobs are not 27 jobs worth of compute.
- [I2 PR safety #43829717223](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43829717223): Python 3.11 job **872 s**, Python 3.12 job **1,554 s**, **2,426 job-seconds summed**. Each version executed **877 discovered I2 test occurrences**, in exhaustive disjoint shards of 449 and 428, with zero skips/failures; the common repository-boundary suite ran 10 more tests per version. Job-seconds sum the two parallel runners and are **not** workflow elapsed time or a billing claim.
- [I2 PR safety #43768976909](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43768976909): 1,243 s and 1,543 s for the Python jobs, confirming substantial variability at the same workflow level.
- [Agent static #43850687637](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43850687637): **14 s** job, including **6 s** for the focused routing/metadata test step.

## Cross-suite and repeated-test screening

1. **Exact test-source identity:** zero repeated Git blob SHAs among the 918 Python test files in scope. This does **not** rule out equivalent assertions in differently written files.
2. **Expected version overlap:** ordinary I3 and I2 CI both run their complete suites on Python 3.11 **and** 3.12. The repeated *case IDs across versions* verify portability; do not cut one version merely to reduce minutes. I3 run #43837832547 logged **1,577 cases/version**; I2 #43829717223 logged **877 occurrences/version**.
3. **Shared repository boundary commands:** `python scripts/check_engine_repository.py --json` is present in I1, I2, I3, and agent-static workflow definitions; `python -m unittest discover -s tests -p test_engine_repository.py -v` appears in I1/I2/I3. These execute separately for their selected triggers. Editing the common structural guard can trigger both heavy I2 and I3 matrices. Any deduplication needs a path/authority and failure-boundary proof first.
4. **Other repeated lightweight checks:** `python tools/check_repo_navigation.py --scope entrypoints` appears in the agent-static and ordinary I3 workflows (I3 on Python 3.11 only). This is a measured command overlap, not yet a demonstrated bottleneck.
5. **Known repeated unittest IDs inside I2 discovery:** the [I2 shard scheduler](../../tools/i2_ci_shards.py) explicitly preserves repeated IDs **by occurrence index**. The Python 3.11 job log for #43829717223 visibly contains **at least seven repeated test-name pairs** in `test_feedback_transition_contract`; log parsing is incomplete and must **not** be used to drop IDs. Removing these would require a separate case-by-case equivalence proof and unchanged expected full-discovery cardinality.
6. **Stage7 preflight overlap is intentional:** the one-shot preflight runs `test_stage7_persistence_*.py`, which is also within the ordinary `tests/i3/test_*.py` discovery. The one-shot's frozen pre-exposure gate must not be elided because a separate PR run once passed.

No suite or workflow deletion is justified by these measurements. The expensive I2 suite is already sharded without dropping cases; see [prior I2 cost audit](I2_CI_COST_AUDIT_2026-11-04.md) and compare exact-SHA behavior before proposing further scheduling changes.

## Ranked, non-destructive follow-up

1. **P0, reduce agent cognitive load:** use the existing `AGENT_HANDOFF.md` as handoff authority, `AGENT_CONTEXT.md` for task routing, and `AGENT_NAVIGATION.md` for locations. A new quick-start guide should not duplicate them. Keep only a short live-status entrypoint plus links to frozen or dated records, without rewriting scientific history.
2. **P1, profile I2 without reducing coverage:** at the next ordinary source-exact CI, record per-module shard elapsed/CPU times, especially Python 3.12, number of original lives/cold audits, duplicate IDs by occurrence, and test counts. Compare with this baseline; do not dispatch new cohorts merely for a benchmark.
3. **P2, inspect overlapping shared guards:** map exact PR path triggers and check requirements before considering an isolated lightweight structural gate. Preserve both Python-version contracts, fail-closed ownership and promotion guards, and exact-head checks.
4. **P3, reduce I3 YAML navigation complexity only after trigger/custody review:** distinguish 27 SKIPPED experimental jobs from active runner cost. Preserve frozen one-shot/archival trigger paths and SHA-bound artifacts. No workflow triggers are changed here.
5. **P4, after full pairwise semantic review:** classify active, superseded and historical navigation paragraphs. Keep original protocols and negative results. Do not auto-delete by repeated filename, topic or shingle score.

## Reproduction and constraints

Requery the exact **commit**, not the floating `main` name, when reproducing this snapshot; the API example above is an endpoint illustration. For CI compare run IDs, `run_started_at`, `updated_at`, each run's `/jobs?per_page=100`, each actual job's `started_at`/`completed_at`, and the original test logs. Never conflate wall times, runner-seconds, case counts or scientific lives. The current source may advance; the measurements are historical, attached to the SHA and run IDs.

**No frozen protocols, scientific results, evidence archives, original research suites or CI triggers were moved, removed, regenerated or rerun to produce this audit.**
