# I1 development playbook

A change is acceptable only if it preserves autonomous, UC-priced, mortal and first-person cognition. Never write a target behavior and retroactively call it emergent.


## Capability-first integration policy (campaign #348, 2026-10-20)

Technical correctness, natural-engine activation, and scientific efficacy are **separate decisions**. Do not require an ecological survival advantage merely to merge a tested technical correction or to activate a safely integrated, architecture-consistent capability. Conversely, isolated research code in `main` is not an active capability.

**L1 SOFTWARE:** A targeted correction may merge after exact-HEAD CI, source/generated parity and relevant positive/negative tests, without survival claims. Record whether the code executes or remains dormant.

**L2 NATURAL CAPABILITY:** Activation needs a real `birth_i1` integration contract, observable full route from first-person input through evaluation, Competition, Action Control and applied effects (when applicable), UC accounting, M11 cold recovery or stateless reconstruction, invalidation/interruption and regression tests against existing goal options. Scientific benefit may remain `NOT_ESTABLISHED`; an unsafe or nonfunctional activation is BLOCKED. Avoid artificial action priorities, hardcoded food/water mappings or fabricated rewards.

**L3 SCIENCE:** Learning benefit, survival advantage and generalization remain independent empirical questions for prospective research. Record `GO`, `NO_GO`, `INCONCLUSIVE`, or `NOT_OBSERVED` without silently converting an L1/L2 pass into scientific proof. Previously defective-model cohorts are not acceptance oracles.

**Merge decision:** merge a passing L1-only improvement explicitly as *dormant*, or a passing L2 capability as *active*. A dormant component must have a follow-up activation issue and a disposition (activate/refactor/remove), never count as delivered cognition. A structural invariant failure blocks merge. Check exact-commit Python 3.11/3.12 CI; no need for new population/behavioral cohorts in integration-only PRs.

**Concurrency and ownership:** prioritize two new active development PRs at most; retain research branches as provenance instead of merging them wholesale. Each issue owns one scope, one PR, explicit dependencies, negative tests and a closing decision. Rebase onto latest `main` and avoid stacking unrelated runtime changes. Document owner, configuration/birth activation, software evidence, scientific uncertainty and remaining blockers in [CAPABILITY_INTEGRATION.md](CAPABILITY_INTEGRATION.md).

**Operating order:** #317/#326 intention continuity and revisitable choices; #327 independently considered local options; #328 lived place consequence relevance; #329 wake/needs/sleep arbitration. Every new motor step requires ordinary fresh arbitration even if the individual retains an intention.

## Before editing

1. Fetch current `main`, PR #251 → #252 → #253 → #254 dependencies, target HEAD and GitHub CI. Identify the active engine via `config/engine-registry.json`.
2. Read [THEORY.md](THEORY.md), [COGNITIVE_FLOW.md](COGNITIVE_FLOW.md), [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) and affected source. Separate intended mechanism from an unproven theory.
3. Write a falsifiable statement: observation → candidate mechanism → possible alternative explanations → negative test that can distinguish them.
4. Record the boundaries: physical state, subjective projection, technical journal, causal owners, UC, persistence and terminal state.

## Investigation and implementation

5. Capture the issue in a seeded living scenario when possible (see [WORLD_PRESETS.md](WORLD_PRESETS.md)). Preserve the individual's uncertainty, its own choices, and the fact of death. The observer is external and cannot feed back privileged data.
6. Track the full decision chain: bodily level → local perception → needs → goal → proposed plan → admission/competition → admitted command → physical change → experienced event → learning/consolidation.
7. Patch the *lowest real cause*, never force `manger`, `boire`, `dormir`, travel or a historically expected H1/H2 action. Avoid hidden danger or prebirth knowledge.
8. Test positive, negative and uncertainty cases. A plausible death is not automatically a failure; a hidden-knowledge leak, free UC or resurrected step is.
9. For M11: verify refusal on pending intent, identity mismatch, corrupt roster, bad publication and terminal state. No living rollback is available.
10. For Stage10: demonstrate nonempty actually published owner-specific forms when claiming consolidation improvements; verify provenance, UC and stable cold state separately.

## Proof and handoff

11. Run `python scripts/check_engine_repository.py --json`, `python scripts/check_engine_contracts.py --json`, I1 structural tests, smoke/full, owner and M11 suites, and artifact parity where affected. Check Python 3.11/3.12 on the exact pushed commit.
12. Attach world/seed, SHA, new evidence and limitations. Update [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) *only for evidence actually measured*, [STATUS.md](STATUS.md) for outstanding risks, and the code/doc references where mechanics changed.
13. Report clearly: code modified; tests passed/failed/not observed; observed live behavior; scientific gate; remaining unknowns. Do not merge dependent PRs out of order.

## Worked diagnostic: berries collected but not eaten

**Do not** append a food-first action. Inspect whether collection changed inventory but not physiological food, whether inventory is perceptible, whether need pressure reached the Goal Manager, whether `manger` was a permissible candidate and whether competition or gatekeeper excluded it. Verify actual command and `ate` outcome separately, then that a lived effect updates the appropriate memories or models without an oracle. Reproduce with `oasis` or `foraging` and vary only predeclared physical conditions.

## Worked diagnostics by causal boundary

| Observation | First code entrypoint to inspect | Next distinguishing check |
| --- | --- | --- |
| Physiological need never motivates | `src/i1/modules/value_needs.py::assess` and `produce` | Capture body, deficit, weight, `p_min`, `GoalManager.arbitrate`; separate a below-setpoint value from a published proposal. |
| Proposed goal but no action | `src/i1/runtime/stage4_runtime.py::_phase_hooks` | Compare `option_registration`, `competition_cycle`, `ActionControl.admit`, `_dispatch_decision` and the real `WorldBody.apply` receipt; note UC refusals. |
| Lived event missing from memory | `src/i1/runtime/journal_views.py::JournalViews.commit_autobiographical` | Verify technical event, allowed policy fields, single-attempt refs, projected event, memory owner update and UC; never read hidden journal fields as experience. |
| No Stage10 owner change | `src/i1/runtime/stage10_runtime.py::_run_live_consolidation` and `_publish_live_consolidation` | Distinguish no pending episode, low pressure, refused scan charge, suspended transaction, rejected rebase, committed history and nonempty active owner diff. See [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md). |
| M11 cold recovery refused | `src/i1/runtime/m11_transactional_mortal.py::cold_recover` and `src/i1/runtime/sqlite_life_store.py::recover_current_bytes` | Audit identity, terminal status, pending intent, current-only committed hash, journal and owner roster; never replay from an older generation. |
| UC suddenly rises | `src/i1/lab/compute_budget.py::CycleComputeBudget.charge` | Separate accepted from requested UC and P-43 from P-42; review per-operation `count` and refusal reason in [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md). |
| Apparent hidden-world knowledge | `src/i1/runtime/world.py::capture_local` and `src/i1/runtime/journal_views.py` | Compare operator-only truth with actual first-person capture and allowed autobiographical fields; use canary-negative tests, never inject the operator frame into a live individual. |

These are **investigation entrypoints**, not claims that every field is exported by the standard world-preset report. `tools/inspect_i1_world_report.py` reports missing cognition as `NOT_OBSERVED`; add a reviewed passive observer before asserting the reason for any choice.

## Persistent state and lived evidence

For serialization, owner-roster, episode provenance, M11 cold reconstruction and private/public form distinction, follow [DATA_CONTRACTS_AND_CUSTODY.md](DATA_CONTRACTS_AND_CUSTODY.md). For an end-to-end read-only investigation, follow [LIVED_EVIDENCE_WALKTHROUGH.md](LIVED_EVIDENCE_WALKTHROUGH.md). The existing preset report does not expose UC or private cognitive owner decisions; do not assume they can be deduced from operator-only truth.

## Stop conditions

Stop and report a blocker for missing ground truth provenance, hidden observation injection, compromised mortality, noncanonical M11 commit, incorrect owner publication, unaccounted UC or test omission. Do not mask those failures with replaying a life, relaxing tests or calling an inconclusive trace a scientific success.

Registered smoke/full test vectors must pass a unique `--junit` path through `engine.json`; the CLI requires this option. See [TEST_PLAN.md](TEST_PLAN.md) before copying command lines into a shell.

## Diagnostic: a documentary CI fails but I1 executes normally

1. Pin the failed workflow **and exact head SHA**; identify the failing job and step. Do not infer that the natural I1 runtime failed merely because a generation-owned structural test was red.
2. Run `python scripts/check_i1_handbook.py --json` to identify missing canonical Markdown, broken links, missing quoted source paths, and invalid explicit `file.py::Class.method` references. The checker uses Python AST; it does not execute the engine or prove that a referenced symbol behaves correctly.
3. For a missing Python symbol, inspect its actual defining class/file in `src/i1/`. A module-level constant such as `PASSES` is not a callable; document its file and the constant separately rather than misrepresenting it as a method.
4. When testing a **negative fixture**, ensure the fixture itself is valid Markdown. Use literal backtick delimiters around the injected code span. Escaping a closing backtick with a backslash can make the extracted symbol `Sample.missing\\` instead of `Sample.missing`, invalidating the test rather than demonstrating a broken-reference detection.
5. Re-run `python -m unittest discover -s tests/i1 -p 'test_i1_handbook*.py' -v`, then `python tools/run_engine_checks.py --engine I1 --suite structure --execute --json`. Verify Python 3.11 and 3.12 on the *new* pushed SHA.
6. Report separately: validator status, natural-I1 tests, scientific evidence, and any still-open documentation references. A green documentation check validates links and declared names only.

**Negative test contract:** the fixture should contain a real temporary `Sample.existing` and intentionally reference `Sample.missing`. Assert both the reported path and the missing method. Avoid accepting an unrelated missing-directory error as proof that AST validation works.
