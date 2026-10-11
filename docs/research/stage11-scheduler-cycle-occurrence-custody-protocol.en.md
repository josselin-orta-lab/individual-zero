# Stage 11: Scheduler UC cycle-occurrence identity and safe re-entry

**Software investigation protocol registered on 2026-10-11 before any change to lifecycle behavior or execution of new tests.** Only normative source: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially S-11.2/S-11.3 (§16.3), Scheduler phase chronology (§4), rollback and exact replay (§17.1–17.6), INV-21/INV-22. This is neither a historical Golden nor an independent scientific experiment. **Stage 11 IN PROGRESS; Stage 9 scientific NO-GO.**

## Read-only source findings motivating this protocol

At source/test SHA `92cab509678e92dafa19e6854052c897bd835269`, `CycleComputeBudget.open_cycle(cycle)` first checks an exact positive integer, then resets `_consumed_cycle` and `_consumed_by_module` without knowing the world step or attempt identity. Calling it twice for the **same active logical occurrence** would therefore wipe charged UC and potentially let later modules perform more than the declared envelope during that occurrence. This is a static API-level concern, NOT proof that a current Individual Zero runtime executes that duplicate call.

A naive prohibition of numeric `cycle` repetition would be incorrect:
- `Stage1Runtime.run_step(cycle=1)` opens a **new world step** and then calls `compute_budget.open_cycle(1)`; successive world steps legitimately use the same numeric `1`.
- `Stage4Runtime` opens the budget at modulation phase 0 for successive cognitive cycles `1..c_max` of each world step, then starts again at `1` on the next step. No evidence from this static inspection says it double-opens one occurrence in ordinary execution.
- `DeterministicScheduler` distinguishes world steps, active `attempt_ref`, logical cycle and phase; rollback can create a **new attempt** after restoring causal owners while retaining the append-only journal.
- `CycleComputeBudget.export_causal_state` currently records `{config_version,cycle,consumed_cycle_uc,consumed_by_module}`, not world-step/attempt identity. The budget object alone therefore cannot distinguish a valid new step's `cycle=1` from an invalid duplicate open in the same step.

**No semantic or code fix is authorized by this document alone.** Before changing anything, identify the real call graph, simulate the two contrasting cases and design a causally versioned occurrence token or equivalent lifecycle authority. Do not use a global increment-only cycle ID when multiple steps restart at 1.

## Frozen development-only checks for a separate, future increment

1. Verify the direct owner API's present behavior using a clearly labeled **negative software diagnostic**: first `open_cycle(1)`, then an accepted 2-UC charge, then `open_cycle(1)` again in the same hypothetical occurrence. Record the exact before/after state. This must not be disguised as a test of normal-world execution or historical behavior.
2. Verify legitimate replay of **two or more actual world steps**, each with numeric `cycle=1`, including the physical step/attempt provenance, per-step 2-UC charge and zero UC carryover. Reproduce independent journaling and checkpoint schedules without synthetic charge events.
3. Verify distinct cognitive cycles `1..c_max` within one physical world step, including the protected-control reservation and per-cycle renewal, under normal and constrained budgets.
4. Verify the **same-world-step, same-attempt, same-cycle** double-open is rejected or controlled **before** erasing any accepted UC, while a new physical step with the same cycle number is still admitted. A rollback/new `attempt_ref` must be investigated separately and must preserve journal occurrence integrity and exactly replay owner state.
5. If a new occurrence identity is needed in causal owner state, **version it explicitly** and keep historic accepted snapshots, journals and old default fixtures byte-identical. Compare two runs only when world inputs, complete owner snapshots, restoration order and journal capture schedule match exactly. Never rewrite accepted hashes or count a new attempt as old work for free.
6. Keep normative P-43 counts, values, protected capacity, S_t publication, and Action Control safety authority unchanged. Do not add a hidden world-state oracle or infer danger learning from a technical Scheduler guard.
7. Execute targeted tests and show first divergence before a narrow code correction. Do not trigger a CI workflow until an actual independently testable source change exists; one quick workflow first, then one full campaign only when justified. Separate software diagnostic, integration, historical Golden and scientific held-out evidence.

## Boundaries and precedence

**Current status: INVESTIGATION NOT EXECUTED; NO FIX IN THIS PROTOCOL.** The registered cases are publicly inspectable development inputs, not independent held-out seeds or scientific claims. Any future code work must first confirm caller and snapshot compatibility and not regress the separate exact-type validation introduced at `92cab509...`. Changing `CycleComputeBudget.open_cycle` alone based solely on its previous cycle integer is **prohibited** because it would reject valid cross-world-step reuse.

PR #25 stays open/Draft/unmerged. No modifications to `main`, normative English v1.2.1, permissions, protections, repository visibility or frozen scientific results.
