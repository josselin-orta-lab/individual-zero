# MVP v1.3.1 integrated audit: first corrective sequence (2026-10-11)

**Normative authority:** `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, section 9.  
**Baseline:** protected `main` at `9c9dd90f55614b9fe4c3c71d9a26b7f82f080017`.  
**Work branch:** `audit/v1.3.1-mortal-publication-guards-20261011`. No historic Stage10/11 approvals or Stage9 data changed.  
**Evidence scope:** source inspection of the integrated commit, PR #48–#59 patches, historical tracked tests and workflow definition. The new tests are added but **have not been executed locally** because the execution container cannot reach GitHub, and this connector cannot run a remote shell. CI is a separate validation gate. Do not treat an existing historical PASS as a fresh execution.

## Compliance matrix (individual check, normative criterion, linked test, evidence, limitation, assessment)

The criterion descriptions below refer to the precise English requirements in normative §9, not to alternate semantics.

| Criterion | Requirement from §9 (concise) | Source and relevant check | Current evidence / limitation | Assessment |
| --- | --- | --- | --- | --- |
| M-01 | One real transition and exactly one closure per admitted command | `stage2_runtime.py`, `scheduler.py`, `test_mortal_runtime_optin.py` | Fatal and regular closure tests exist; publication-error injection newly added; full failure matrix not rerun | PARTIAL |
| M-02 | Lethal zones/toxins/starvation/creatures/combined damage keep physical lethality | `world.py`, `test_world_physics.py`, `test_mortal_runtime_optin.py` | WorldBody lethal-zone and zero-integrity logic checked; full category-and-combination regression not reproduced | PARTIAL |
| M-03 | No postmortem step, reflex, cognition, learning, memory or consolidation | `mortal_execution.py`, `stage2_runtime.py`, `test_mortal_sleep_terminal.py` | Terminal status blocks steps; death during sleep tested historically; all Stage11 cognitive-path failures not injected | PARTIAL |
| M-04 | No mortal checkpoints, masks, retries, restores or physical compensation | `mortal_execution.py`, `snapshots.py`, `test_mortal_forward_only_world.py` | Forward-only protection and snapshot rejection covered; process-interruption recoverability unverified | PARTIAL |
| M-05 | Byte-identical nonlethal physical states versus baseline for matched commands/random states | `world.py`, `test_mortal_scenario_atomic.py` | 600-step fixture compares against independent WorldBody, not full legacy cognition parity | PARTIAL |
| M-06 | Preserve known-danger veto, reflex, competition and unknown-risk behavior | `action_control.py`, `test_mortal_runtime_optin.py`, Stage11 tests | Tests exist but no full with/without-instrumentation parity replay | PARTIAL |
| M-07 | Complete journal and distinct consolidated history, unchanged learning/provenance on nonlethal trajectories | `journal.py`, `journal_views.py`, `stage10_runtime.py`, `test_immutable_journal_export.py` | Complete in-memory log and independent histories are implemented; interrupted-current-state durability absent | PARTIAL |
| M-08 | Stage10 verified cut, full postcut updates, coherent publication after interruption | `consolidation_postcut_journal.py`, `consolidation_publication.py`, `test_stage10_postcut_journal.py` | Stage10 unit/provenance tests present; crash-injection and six-pass integrated replay not rerun | PARTIAL |
| M-09 | Prepublication input rejection; never undo committed physical changes | `injected_scenario.py`, `test_mortal_scenario_atomic.py` | Tests cover malformed input, post-publication receipt fault and fail-closed behavior | PARTIAL |
| M-10 | No Oracle/evaluation truth into perception, S_t, memory or consolidation | `oracle.py`, `stage2_runtime.py`, `test_standalone_exhaustive_journal.py` | Blocked-import autonomous tests and separated trace; transitive leakage/fault injections still incomplete | PARTIAL |
| M-11 | Persist current coherent nonterminal state after process failure, never revive dead identity | `journal_export.py`, `mortal_execution.py` | Explicit export fsync is not runtime WAL or atomic current-state persistence; restart recovery not demonstrated | NOT_TESTED |
| M-12 | Full append-only lossless history, verifiable prefixes/read-after-death | `journal.py`, `journal_export.py`, `test_immutable_journal_export.py` | Full in-RAM append-only and explicit immutable export checked; events after latest export may be lost on crash | PARTIAL |
| M-13 | Identity-distinct copies; dead/stopped copies cannot overwrite parents | `world.py`, `test_mortal_forward_only_world.py`, Stage5 copy tests | Independent world-copy check present; complete dead-identity persistence contract not exercised | PARTIAL |
| M-14 | Python3.11 reference, deterministic seeds/digests and operator smoke run | `.github/workflows/ci.yml`, reference tests | 3.11/3.12 full CI history reported for PR #59; operator acceptance and fresh post-change CI pending | PARTIAL |
| M-15 | Stage/scientific statuses independent, 600-step hypothesis and operator approval | normative §7, Stage11 protocol | Stage9 remains SCIENTIFIC NO-GO; 600-step software diagnostic not certification; operator approval pending | PARTIAL |
| M-16 | I0 standalone imports neither Oracle nor Bench; internal decisions/journal same as evaluated | `stage2_runtime.py`, `test_autonomous_reference_factories.py`, Stage11 probe | Autonomous no-service path exists; defaults intentionally legacy; complete parity test absent | PARTIAL |
| M-17 | Independent Oracle read/close without I0/world mutation | `oracle.py`, `test_oracle_bench.py` | Narrow truth protocol, capability, deepcopy and close tests; hostile reader audit missing | PARTIAL |
| M-18 | Standalone Bench reads approved observations and full export without runtime backchannel | `bench.py`, `test_bench_no_cognitive_imports.py`, `test_bench_exported_journal_audit.py` | Unit checks and lazy external journal verification exist | PARTIAL |
| M-19 | Standalone auditor rejects tampering/reorder/missing/duplicate/false provenance/postdeath | `independent_journal_audit.py`, `test_independent_journal_audit.py` | Negative tests present; trusted head/count needed against valid-prefix truncation; unexamined kinds reported | PARTIAL |
| M-20 | 600 genuine physical steps, complete externally auditable journal, no hidden Oracle | `stage11_autonomous_600_step_probe.py`, `test_stage11_autonomous_600_step_probe.py` | CI PR #59 recorded successful 600-step run; latest SHA had it; no independent new local run on this branch | PARTIAL |

No criterion is claimed PASS solely because a PR was merged. M-11 is **NOT_TESTED**, not FAIL: no credible process-kill/reload demonstration yet. Risk of losing post-export RAM events is real by design, not evidence of a specifically reproduced crash corruption.

## PR #48–#59 integrated scope review

| PR | Changed files reviewed | Integrated conclusion / remaining validation |
| --- | --- | --- |
| #48 | Normative EN/FR 1.3.1, indexes, initial audit | Normative target retained; requires engineering evidence |
| #49 | Stage2–11 construction paths and standalone safety | Explicit mortal mode present; publication and safety guards addressed in this branch |
| #50 | Stdlib journal auditor, CLI, tests, lazy package | Independent audit architecture exists; incomplete-event schemas may be reported as unexamined |
| #51 | Optional Oracle for Bench | Constructor separation present; independent parity not yet exercised |
| #52 | Separate EvaluationTrace and JournalViews | Separation at module level reviewed; dynamic import graphs need further verification |
| #53 | Oracle protocol/read copy/close | Read-only capability boundary present; hostile source not audited |
| #54 | Bench exported journal audit | Lazy independent auditor path present; negative fault checks not rerun |
| #55 | Stage10 cut/provenance audit | Cut and postcut consistency checks reviewed; semantic accuracy is not proven |
| #56 | Atomic never-overwrite export/fsync | Operator export correctly not advertised as per-event durability |
| #57 | Bench cognitive import removal | Bench runtime-level import separation present, audited export may lazy-load audit only |
| #58 | Stage5–11 factories | Opt-in flag propagated; legacy defaults intentionally preserved |
| #59 | 600-step probe/tests/CI | Surviving 600 steps with prefix receipts, no Oracle/Bench; distinct lethal-scenario coverage needed |

## Corrective work and residual risks

- **P1, verified gap:** `stage2_runtime.open_step` previously allowed a mortal scheduler opening to fail after it advanced the clock, leaving an active attempt but no `step_opened` receipt. It now halts the mortal execution permanently on this exception without restoring any life state. Added injected append-failure test.
- **P1, verified gap:** standalone `safety_block` set a blocked flag but `open_step` had no matching admission guard. It now refuses new steps, and direct mortal dispatch checks the same flag. Added safety-block terminal test.
- **P2, verified gap:** CI path filter omitted the current normative EN v1.3.1 while including v1.2.1; new path added.
- **P1, known limitation:** full `HashChainedJournal` resides in RAM during life; a sudden crash loses all events not explicitly exported. A durable append-only journal plus atomic current-state/terminal markers needs its own design and fault-injection tests. No historical restoration may be introduced. **No WAL is claimed implemented.**
- **P1, plausible risk:** `WorldBody.apply` mutates inventory or scheduled failure cursors before final result publication; exceptional paths must remain technical_halt with no re-execution, and journal/state divergence needs power-loss characterization.
- **P1, epistemic limit:** verified SHA-256 chain proves internal consistency conditional on trusted head/count, not external physical truth. Unknown event kinds are reported as unexamined.

## Reproduction / operator reception

1. Run `python -m unittest tests.test_mortal_publication_guards -v`, then relevant existing `test_mortal_runtime_optin`, `test_mortal_scenario_atomic`, `test_independent_journal_audit`, `test_mortal_sleep_terminal`, `test_immutable_journal_export` and autonomous factory tests. Refuse acceptance on any regression.
2. Run Python 3.11 and 3.12 quick/full integration gates as applicable. On Python 3.12 execute `python -m lab.stage11_autonomous_600_step_probe --steps 600` and retain JSON receipt, hash, count, prefixes and CI artifact. No rerun if source SHA and config identical to already validated PR #59.
3. Test an actual unknown lethal cell in a **new** mortal autonomous individual and export its entire journal postdeath. Require exactly one death, one applied physical transition for that terminal step, terminal event/closure and denial of every later step.
4. Run `python scripts/verify_i0_journal.py <path> --expected-head <trusted_sha> --expected-count <trusted_occurrences>` externally. Tamper, duplicate and reorder independent copies: all must explicitly fail.
5. Operator decides separately whether software migration is accepted. Stage9 SCIENTIFIC NO-GO remains. Final scientific validation remains deferred.

**Next lock:** design process-crash-safe append-only event publication coordinated with latest committed physical state. Establish fault injection at before/after durable append, physical mutation, terminal record and atomic current-state marker. Select fail-closed restart of the *current* identity only, never earlier-state replay/resurrection. No WAL deployment without verified crash semantics and operator approval on any normative ambiguity.
