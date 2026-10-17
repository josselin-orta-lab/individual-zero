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

## Charge-level contracts an agent can actually test

### P-43 waking cycle: exact admission semantics

`src/i1/lab/compute_budget.py::ComputeBudgetConfig.validate` requires integral non-negative `cycle_ceiling`, `protected_capacity`, module envelopes and operation costs; it refuses unknown modules, missing protected envelopes and invalid types. `CycleComputeBudget.open_cycle` clears counters on a **new** cycle, never carries spare UC forward. The optional `cycle_occurrence_guard` rejects reopening the same `(t_monde, attempt_ref, cycle)` identity when configured. Do not claim that guard is enabled solely because the implementation supports it: inspect the actual natural birth configuration.

`CycleComputeBudget.charge` checks, in order: (1) the module envelope, (2) the global cycle ceiling, then (3) the ordinary-work ceiling equal to `cycle_ceiling - protected_capacity`. A refused charge returns `accepted=False` with `reason` of `module_envelope`, `cycle_ceiling` or `protected_capacity`; **neither per-module nor total counters increment**. An accepted charge returns the cumulative counters. A zero `count` is legal on this waking ledger; P-42 sleep `count` must be at least one.

The `protected=True` argument to `src/i1/runtime/stage4_runtime.py::Stage4Runtime._charge` does **not** put a module into `ComputeBudgetConfig.protected_modules`. The configuration decides which debits consume protected capacity; the runtime argument determines whether refusal raises a `RuntimeError` (protected hook) or degrades/skips optional work. Check both before debugging a budget refusal. A capacity quote via `CycleComputeBudget.quote_operations` is **read-only**, not a reservation or a charge.

The actual `compute_charge` *technical journal* payload written by `Stage4Runtime._charge` is `module`, `operation`, `count`, `requested_uc`, `accepted` and `reason`. It does **not** contain `consumed_cycle_uc`: reconstruct accepted totals carefully from complete same-cycle events or inspect an authenticated owner snapshot. In `Stage4Runtime._phase_hooks`, perception publication charges `max(1, len(capture.visible_entities))` in cycle 1; competition evaluation charges `max(1, competition.registry_size)`. These are concrete sources of changes in consumption even without changing unit prices.

### P-42 sleep period: exact admission semantics

`src/i1/modules/consolidation_budget.py::ConsolidationWorkBudget` requires a unique `period_ref`, monotonically advancing **physical sleep** `world_step`, and separately bounded `step_slot_uc` and `period_capacity_uc`. `begin_period` resets the period ledger; `begin_step` resets only its step counter. A refused `charge(operation, count)` reports `step_slot` or `period_capacity` without debit. Work prices must be strictly positive; sleep work never inherits spare P-43 waking capacity.

The actual sleep entrypoint is `src/i1/runtime/stage10_runtime.py::Stage10Runtime._sleep_step`: it calls `begin_period` on entry and `begin_step` for admitted sleep, then attempts private work. `_run_live_consolidation` explicitly emits `stage10_consolidation_scan_checkpointed` and `stage10_consolidation_pass_checkpointed` with cumulative **P-42** counters after paid progress. `stage10_consolidation_work_deferred` identifies insufficient scan, agenda, plan, pass-completion or index-maintenance capacity. Lack of a scan or checkpoint may instead mean **no eligible episode or inadequate frozen pressure**, not exhaustion.

## Diagnostic decision table

| Symptom or observation | Compare these specific facts | Interpretation and distinguishing negative case |
| --- | --- | --- |
| Two runs use different UC despite identical cost tables | `compute_charge.count` for `perception_publish` and `competition_evaluate`; actual registered options and visible entities | Input work volume may differ. Same unit price does not imply same total. |
| Planning never produces a proposal | `planning_build` charge accepted, current `goal_for_planning` and `st_before_cycle`, `stage6_planning_result` | No frozen goal/`S_t` is different from P-43 refusal and from a failed simulator search. |
| Non-protected budget refusal | `compute_charge.accepted=false`, `reason`, subsequent `s_t_published` budget state | Optional work may be skipped/degraded; it was *requested* but not consumed. |
| Protected budget refusal | `bus_pour`, `gatekeeper_select` or `control_admit` hook plus matching `protected_modules` configuration | The protected hook raises rather than bypassing limits. An uncertain mortal step must not be retried. |
| Sleep enters, no semantic checkpoint appears | `stage10_sleep_entered`, frozen consolidation pressure, pending episodes, scanner cursor, charged work and `stage10_consolidation_work_deferred` | Distinguish no candidate, sleep interruption and lack of step/period UC before claiming failure of learning. |
| Charged passes but no active-owner state changes | `stage10_consolidation_pass_checkpointed`, `stage10_consolidation_publication_deferred`, `stage10_consolidation_committed` and detached owner hashes | Paid private work is not a publication. Even a committed history version may contain no nonempty advisory delta. |

**Reproducibility:** use two newly born independent identities under the *same declared world and birth configuration*. Record world steps, attempts, cycle or sleep period references, accepted charges and prices before comparing. Never rerun a dead individual or import privileged world layout into cognitive code. The standard preset report does not expose these UC events; use externally authorized, integrity-checked technical records or design an additional passive observer as described in [OBSERVABILITY.md](OBSERVABILITY.md).

**Tests to add for a UC code change:** positive exact debit, boundary debit, refusal without mutation, unknown operation/module, invalid integer type, reopened occurrence if enabled, protected-hook exception and P-42 repeated/nonconsecutive sleep step. Existing green smoke/full tests alone are not a quantitative calibration experiment. Document new assertions by exact file and SHA in [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md).
