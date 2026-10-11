# Stage 11: external scenario batch must fail closed on journal receipt failure

**Preimplementation software-only regression protocol, 2026-10-11.** The normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially sections 4.6, 17.4, 17.6, DC-08 and INV-33/44/49. This is a public development fixture, not hidden-seed science, a Golden, a Stage 9 acceptance or authorization to merge PR #25.

## Existing fault boundary

`InjectedScenario.apply_for_step` journals `external_input_received` before applying a physical input, but currently catches errors **only** from `WorldBody.apply_scenario_event`. The succeeding `external_input_applied` journal append runs outside the recovery `try`. If that append raises (for example a duplicate journal event ID or a narrowly injected append failure), the physical input may have changed WorldBody while the technical journal has no corresponding applied receipt, the scenario is not halted, and its cursor is not rewound. When the next input in a same-step batch fails at the initial `external_input_received` append, previously applied physical inputs may likewise remain. This is a software boundary omission, not an observed natural failure or a claim of hostile-code confinement.

## Frozen minimal correction

1. Retain the exact current success order and causal payloads: `external_input_received`, WorldBody application, `external_input_applied`, then advance scenario cursor and report the event as applied. Do not change successful canonical journal bytes, IDs, or time order.
2. Put both journal appends and WorldBody application under the **same compensated batch-failure boundary**. Before the first input of a due world step, the existing WorldBody recovery point is retained. On a failure from either receipt, restore the *entire* pre-batch WorldBody state, restore the scenario cursor to the first input for this world step, set the existing rejected/fail-stop marker, and emit the existing technical rejection/rollback records. Never invent an autobiographical physical observation or applied event for the failed input.
3. Distinguish a technical journal reception/receipt failure from a malformed external physical operation by using `reason="technical_journal_failure"` for only the new error path. Preserve the prior `reason` values and rejected-event bytes for unchanged WorldBody application failures. No exception reason should be interpreted as a learned safety fact.
4. If world recovery itself fails, the existing critical recovery failure must remain explicit and `world_recovered=False`. This gate assumes the journal can record the rejection after the narrowly injected append error; a persistently unavailable/corrupted journal remains an explicit critical failure, not an automatically recoverable execution.
5. Preserve the scheduler's `external_stop` semantics on rejection: no command, no world advancement, no Perception capture, no further advance of the halted scenario. Journal entries remain append-only; no rollback of technical events.

## Frozen tests

Use the existing public `junction_open` Stage11 runtime and a deterministic at-step-2 batch with a valid `set_danger_zone` and `set_position`. After step 1, save the *complete* WorldBody causal export, then inject a narrowly scoped `journal.append` failure for the **second** input's `external_input_applied` receipt. Require the first input's applied technical receipt to remain, the second to be absent, the second's `external_input_received` to be present, exactly one technical rejection and one explicit whole-batch rollback marker, full WorldBody equality to pre-step, scenario cursor rewind/halt, scheduler `external_stop`, no new Perception/command for step 2, and valid hash chain. Independently inject a failure when logging the second input's **received** event, after one prior successful event; demand the same whole-batch compensation and no synthetic receipt for the second event. Check that a run using the **same deterministic failure injection schedule** replays identically. Retain the existing successful-input and malformed-input tests without modifying their expected outputs.

## Validation boundaries

Before approval: require targeted tests, then the repository's Python 3.11/3.12 software CI on the **exact** code/test SHA; report test counts and failures honestly. A runner-less failure is not a code test. Full historical scientific Goldens and independent Stage 9 held-out campaigns remain separate. Keep the PR Draft and unmerged, `main` and the normative specification unchanged.

**Stage 11 IN PROGRESS. Stage 9 scientific NO-GO.**
