# I1 UC accounting and scheduler ownership

**Scope:** current I1 implementation at PR #254. UC is *logical work*, not physical energy, wall-clock time or a measure of intelligence. Values are configuration-dependent; never copy a historic campaign's numerical budget into a natural-I1 acceptance criterion.

## Two different budget ledgers

| Ledger | Owner and configuration | Lifetime / refusal |
| --- | --- | --- |
| Waking deliberation (P-43) | `src/i1/lab/compute_budget.py::CycleComputeBudget`, `ComputeBudgetConfig`; instantiated by `src/i1/runtime/stage4_runtime.py::Stage4Runtime.__init__` | `open_cycle(cycle, occurrence=...)` resets a cycle's counters; `charge(module, operation, count)` checks module envelope, cycle ceiling and protected reserve. Refusal returns `BudgetCharge(accepted=False, reason=...)` without debit. |
| Sleeping semantic work (P-42) | `src/i1/modules/consolidation_budget.py::ConsolidationWorkBudget`, `ConsolidationBudgetConfig`; used by `src/i1/runtime/stage10_runtime.py` | Explicit sleep `begin_period`/`begin_step`; charge checks the per-step slot then period capacity. A declined work charge cannot fund a semantic pass or a publication. |

**Do not sum these ledgers without an explicit measurement definition.** The separate `WorldPhysicsConfig.action_energy_costs` and `WorldBody.apply` govern bodily *energy*, not UC. Two cognitive cycles may happen in one physical world step, whereas sleeping work uses real simulated sleep steps.

## Waking charge path (reconstructed from the executable)

1. The Scheduler opens a world attempt; `Stage4Runtime.run_step` obtains a first-person capture and assesses bodily needs.
2. `Stage4Runtime._phase_hooks` opens each cognitive cycle using the Scheduler occurrence identity `(t_monde, attempt_ref, cycle)`. Whether repeated occurrences are rejected is controlled by `ComputeBudgetConfig.cycle_occurrence_guard`.
3. Producers call `Stage4Runtime._charge(module=..., operation=..., count=..., protected=...)`, which delegates to `CycleComputeBudget.charge` and writes a technical `compute_charge` event containing requested UC, admission and reason.
4. `CycleComputeBudget.charge` calculates `requested_uc = operation_costs[operation] * count`. It refuses excess over `module_envelopes[module]`, `cycle_ceiling`, or the ordinary-work ceiling `cycle_ceiling - protected_capacity` (for unprotected modules). It does not debit counters on refusal.
5. Non-protected refusal marks the cognitive cycle degraded; protected refusal raises an error. This changes scheduling outcomes, **not** the physics directly. `MinimalMetacognition.close_cycle` receives consumption, ceiling, degradation and protected capacity.
6. The command still needs the normal `ActionControl.admit`, dispatch and physical `WorldBody.apply`. Paying UC for a proposed plan never proves that an action happened.

The phase hooks are specifically `FREEZE`, `PRODUCTION`, `SELECTION`, `EVALUATION`, `ACCUMULATION_DECISION` and `CLOSURE`, in `src/i1/runtime/stage4_runtime.py::_phase_hooks`. Natural I1 also specializes hooks in `src/i1/runtime/stage11_runtime.py` and the Stage10 line; inspect method resolution before attributing a charge or producer to Stage4 alone.

## Costed operations to trace

Inspect the *configured* `operation_costs` for the actual birth. `Stage4Runtime._phase_hooks` explicitly charges `perception_publish`, `value_needs_cycle`, `goal_arbitrate`, `planning_build`, `bus_pour` (protected), `gatekeeper_select` (protected), `competition_register`, `competition_evaluate` (scaled by current registry size) and `control_admit` (protected). A no-op phase hook is **not** evidence that a cognitive mechanism has completed work.

For Stage10, `Stage10Config.validate` requires costs for `semantic_plan_build`, `replay_agenda_scan`, `pass_prepare`, `pass_validate`, `episode_scan`, `episode_replay`, `rule_extraction`, `skill_compilation`, `kappa_recalibration` and `index_maintenance` when live semantic policies are enabled. `stage10_runtime.py::_run_live_consolidation` gates actual candidate selection and charged passes; the existence of a valid budget does not guarantee eligible autobiographical episodes.

## Diagnosis: unexpected UC increase or starvation

1. Pin `git rev-parse HEAD`, birth config/digests and mode (WAL or M11). Hold world preset, identity configuration, steps and input conditions fixed.
2. Check if the reported series measures `requested_uc`, **accepted and debited** `consumed_cycle_uc`, or the distinct Stage10 `consumed_step_uc`/`consumed_period_uc`. Do not compare mixed denominators.
3. Inspect `compute_charge` technical events (module, operation, count, requested_uc, accepted, reason); map unexpected counts to `Stage4Runtime._phase_hooks`, Stage11 overrides and the exact candidate registry size.
4. Compare the configured module envelope, cycle ceiling and protected capacity with `CycleComputeBudget.charge`; distinguish `module_envelope`, `cycle_ceiling`, `protected_capacity` from skipped candidate production and action admission.
5. During sleep, inspect `stage10_consolidation_scan_checkpointed` and `stage10_consolidation_index_maintenance_charged` plus refused/deferred work. Charged scans are not owner publication.
6. Add a positive and a refusal/overflow test where applicable. Test two independent Scheduler occurrences rather than reopening one occurrence to obtain fresh UC.

## Tests and evidence level

Use `python tools/run_engine_checks.py --engine I1 --suite structure --execute --json` for currently registered structural suites, then `python scripts/test_i1_ci.py --mode smoke --seed 246 --junit reports/i1-smoke-contract.xml` and `--mode full --seed 247 --junit reports/i1-full-contract.xml`. When modifying generation/owner custody, also run `tests/i1/test_i1_m11_adversarial.py` and `tests/i1/test_i1_natural_m11_cold_recovery.py`. These commands/test paths exist in the PR HEAD; their success at a **new SHA** must be checked independently.

**NOT_OBSERVED:** `tools/inspect_i1_world_report.py` expressly does not expose UC or option competition from world-preset report JSON. No inference about energy efficiency, learning quality or scientific fitness follows from a green budget test.

See [COGNITIVE_FLOW.md](COGNITIVE_FLOW.md), [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md), [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) and [DEVELOPMENT_PLAYBOOK.md](DEVELOPMENT_PLAYBOOK.md).
