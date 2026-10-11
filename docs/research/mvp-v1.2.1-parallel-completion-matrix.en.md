# Agent B: MVP v1.2.1 parallel-completion matrix (initial, 2026-10-11)

**Normative source:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, frozen and unchanged.
**Baseline Agent A HEAD:** `3f32fd9afa6373d1536c0baf186d280942a79bdd`.
**Last verified software:** `6bfa9e7ecbbbb6d95b027714bbbbe2085400fff2`, CI #38135794852: 893/893 on both Python 3.11.17 and 3.12.15. This proof does not apply to Agent B commits.
**Scientific status:** Stage 9 NO-GO; no scientific acceptance inferred.

This is a **partial, evidence-conscious matrix**, not a certification of all 53 invariants. Status `partial` means functionality exists without demonstrated full integration, `blocked` means dependent on another owner, and `unverified` means no direct proof on Agent B SHA.

| Normative requirement | Causal owner | Status | Source | Tests | Validated SHA | Proof tier | Dependency | Remaining work |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15.1, DC-13, P-39/P-40/P-41, INV-14/36 | Metacognition & Health | partial | `src/i0/modules/sleep_pressure.py`, `sleep_health.py` | `tests/test_stage10_sleep_pressure.py` | `6bfa9e7ecbb` (baseline only) | unit | Agent B | Supply ordinary `dormir` through Competition; no energy double count |
| 15.2, INV-39/52/53 | Action Control, Goal Manager, Scheduler | absent | `src/i0/modules/action_control.py`, `src/lab/stage11_runtime.py` | no dedicated integrated Stage-10 test | none | none | Agent A runtime coordination | Admit sleep command, begin sleeping next step, suspend stagnation |
| 15.3-15.5, DC-13 | Perception, Action Control, WorldBody | partial (rule only) | `src/i0/modules/sleep_pressure.py` | `tests/test_stage10_sleep_pressure.py` | `6bfa9e7ecbb` (baseline only) | unit | Agent A runtime coordination | Reduced capture, reflex, wake, world advance and snapshot/replay |
| 15.6, INV-23/24/47 | Consolidation, Scheduler, history owners | partial: transaction contract only | `src/i0/modules/consolidation_transaction.py` | `tests/test_stage10_consolidation_transaction.py` | **unverified on Agent B SHA** | test authored, not executed | Agent B and scheduler coordination | Six real semantic passes, technical validation, complete owner rebase, atomic coordinated publication |
| DC-16, INV-23/25 | Causal Model, Procedural Memory | absent | `src/i0/modules/causal_model.py` | no consolidation-specific integrated tests | none | none | Agent B | Distinct provenance, hypothesis-only rules, deduplicated skill compilation |
| 16.1, 20.3 Stage 12 | Metacognition & Health | partial | `src/i0/modules/metacognition.py` | existing metacognition tests | baseline only | unit | Agent B | Stagnation, loops, entropy and bias detectors |
| 16.3, DC-07, INV-21/46 | Compute scheduler and Competition | partial | `src/lab/compute_budget.py`, `src/i0/modules/competition.py` | `tests/test_compute_budget.py` | baseline only | unit | Agent A interfaces | Exhaustive degraded-mode load/replay verification |
| DC-14, INV-29/48 | Lab supervision & safety | unverified | `src/lab/safety_protocol.py` | `tests/test_world_physics.py` | baseline only | existing partial tests | Agent B | Separate campaign close from diagnostic resumption |
| 20.3 Stage 13, INV-32/33 | Bench and campaign registry | blocked | `src/lab/stage9_scientific_preregistration.py` | `tests/test_stage9_scientific_preregistration.py` | baseline only | Stage-9 development diagnostics | Stages 10/11/12 and independent scientists | Register/freeze parameters before scientific campaign |
| 21.1 INV-01 through INV-53 | multiple owners | **audit incomplete** | `src/` | `tests/` | none on Agent B HEAD | none | multi-agent | Expand into per-invariant evidence, exact SHA and tests |
| 21.2 replay/isolation/interruption/load levels | scheduler, Lab and individual owners | partial | `src/lab/replay.py`, `snapshots.py` | `tests/test_replay.py`, `test_snapshots.py` | baseline only | technical | multi-agent | Integration and complete deterministic replays |

## First independent increment: contract, not false consolidation

The new `ConsolidationTransaction` records a stable identifier, causal cut point, frozen batch, private candidate, ordered six-pass checkpoints, interruption and restoration. `ConsolidationSlot` refuses a second transaction while one remains open (INV-47). The test pass executors intentionally manipulate **test-only lists**; they are **not** production implementations of the six normative passes.

No `h_new` or Q/κ/precision/causal representation is published. The coordinator does not interpret the technical journal and cannot access WorldBody/oracle. Before integrating it, implement an actual memory-owned batch selector and six real passes, provide journal-backed post-cutpoint updates to each owner, privately prepare all rebased states and coordinate atomic commit from the Scheduler. A successful isolated contract test cannot close INV-23 or INV-24.

## Validation and GitHub Actions limitations

The stacked PR targets `i0/vnext-stages-10-12`, which is **not** in the current `.github/workflows/ci.yml` pull-request base filter. Do not assume applying `ci-unit` triggers anything. No unexecuted test is treated as green. Validate with `python -m unittest discover -s tests -p 'test_stage10_consolidation_transaction.py' -v`, then relevant neighbors, Python 3.12, and Python 3.11 before updating this matrix. Do not modify CI triggers or claim scientific results.

**Agent B exclusive files in this increment:** `src/i0/modules/consolidation_transaction.py`, `tests/test_stage10_consolidation_transaction.py`, this document. No Agent A file is changed.

## Agent B Stage-10 increment update, 2026-10-11 (software-only)

Agent B latest behavior-change SHA: `19f23c3ffd6f276e4a5e0b585ee5a094f358166a` (subsequent documentation-only commits may follow). This supplements the initial matrix above; earlier unverified statements refer to the initial checkpoint, **not** this updated work.

| Normative requirement | Owner / causal boundary | Status | Actual code and tests | Exact tested code / proof | Dependency | Remaining gate |
| --- | --- | --- | --- | --- | --- | --- |
| 15.6, P-42, INV-21 | Memory-authorized batch selection | partial | `src/i0/modules/consolidation_batch.py`; `tests/test_stage10_consolidation_batch.py` | `c36713dab0cf75f80db6585f707caa4a48dd8976`, unit-only isolated local, 13/13 | Agent B, then actual Memory owner | Authoritative Memory ledger; incremental bounded scanning when full scan exceeds UC |
| 15.6, P-42, 16.3, INV-21 | Stage-10 consolidation work ledger | partial | `src/i0/modules/consolidation_budget.py`; `tests/test_stage10_consolidation_budget.py` | `19f23c3ffd6f276e4a5e0b585ee5a094f358166a`, unit-only isolated local, 11/11 | Agent B, Scheduler integration with Agent A | Journal real sleep-step work charges and restrict work to actually admitted sleeping mode |
| 15.6, INV-23/24/47 | Private checkpoint transactions | partial | `src/i0/modules/consolidation_transaction.py`; `tests/test_stage10_consolidation_transaction.py` | exact Git blobs `d12c657fb17896d2b9e2d2c3014bcb1801688dda` and `9de0cf075b77e0d305e95e66eb4aa2a90ea9adb5`, unit-only isolated local, 11/11 | Agent B plus scheduler and owners | Six *real* passes, post-cut ordered rebases and one atomic publication |
| 20.3 Stage 10 behavioral acceptance | Competition, Action Control, Perception, WorldBody, Goal Manager | **unverified** | Stage-10 sleep rules exist but no full living sleep integration | no verified integrated SHA | Agent A / B coordinated | Real `dormir`, reduced perception, wake/intentions, full sleep world-step and journal replay |
| 20.3 Stage 12, INV-46/48 | Metacognition, Budget, Supervision | pending | no Stage-12 change in current Agent B increments | none | Stages 10, 11 | Detect/degrade/console/alignment tests |
| 20.3 Stage 13, INV-32/33 | Bench scientific campaign | blocked | no Stage-13 campaign change | none | Stages 1 through 12 and frozen registry | Preregistered independent campaign only after software prerequisites |

**Aggregate targeted local test run:** `PYTHONPATH=src:tests python -m unittest discover -s tests -p 'test_stage10_consolidation*.py' -q`, Python 3.13.5, **35/35 PASS, 0 FAIL, 0 skip**. Source/test files correspond to verified Git blobs, but `lab.determinism` was a separately copied local implementation. This is not a full checkout, native Python 3.11/3.12 CI, integrated replay or scientific acceptance.

**Explicit residual risk:** The current batch adapter debits the logical budget prior to scanning, but a batch larger than the one-step slot is refused rather than incrementally processed. A future true multi-step, cursor-based scan is required for finite progress with large Memory, without doing unpaid work. Candidate callbacks in the transaction are still unit-test fixtures; they are not six scientific or semantic consolidation passes.

**Noninterference:** no change to Agent A's Stage-11 paths, shared scheduler, journal, snapshot manager, shared world or CI trigger. Stage 9 scientific NO-GO is unchanged. No full INV-01..INV-53 certification is claimed.
