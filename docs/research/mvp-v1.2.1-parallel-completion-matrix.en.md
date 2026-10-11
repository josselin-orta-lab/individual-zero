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
