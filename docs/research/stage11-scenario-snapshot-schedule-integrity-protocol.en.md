# Stage 11: injected scenario schedule integrity on snapshot restore

**Registered 2026-10-11 before this software change.** Deterministic unit-only protocol; not scientific evidence, held-out registration, Golden or runtime release. Normative English MVP v1.2.1, §§4.6, 17.6, S-01.5 and INV-33, requires the state of an injected external scenario to remain causal and reproducible across snapshots.

## Gap

The immutable configured `InjectedScenario` schedule is exported as `events` inside the complete causal state. The existing `restore_causal_state` checks the scenario identifier, version and cursor range, but does **not compare the stored events** to those of the live instance. A different schedule using the same identity and version could therefore be restored as if it represented the same causal future, violating exact replay. A Boolean cursor also passes the generic Python `isinstance(x, int)` test.

## Fixed gate

- Require the snapshot event schedule to equal the current `ScenarioEvent.as_dict()` sequence in full, after the existing deterministic sort, before touching `_next_index`. Do not use a prefix, event count, ID or version alone as equivalent to the schedule.
- Require an exact integer cursor (not Boolean) between 0 and the registered schedule length.
- Reject mismatched operations, world positions, payload values, changed event order or missing event schedule without advancing the cursor, changing WorldBody or producing an `external_input_applied` journal event.
- A valid unchanged schedule with an in-range cursor restores normally. No change to ordinary WorldBody scenario application, independent oracle restrictions or source normative specification.
- Distinguish the scenario schedule's immutable identity from actual world-state changes, which are independently held in the WorldBody causal snapshot. An external `set_position` input is not an individual movement or a learned geographic visit.

## Fixed isolated unit cases

Create one versioned schedule with `set_position` at step 2 and `set_danger_zone` at step 3. Round-trip the unchanged snapshot. Tamper `events[0].payload.position.x`, change operation, delete schedule, and replace cursor with `True`, keeping matching scenario ID/version. Each attempt must be refused without cursor mutation or an additional journal entry. A genuine in-range cursor remains restorable.

No full Python 3.11/Golden/Stage9 held-out campaign or PR merge is authorized. **Stage 11 IN PROGRESS; Stage 9 scientific NO-GO.**
