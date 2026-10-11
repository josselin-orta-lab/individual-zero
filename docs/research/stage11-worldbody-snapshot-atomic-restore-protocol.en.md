# Stage 11: atomic WorldBody causal-state restoration

**Software-only regression protocol recorded on 2026-10-11 before the implementation and new tests.** The sole normative authority is `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §§17.2–17.6, DC-08, INV-33, and append-only journal custody. This public fixture is not a held-out scientific experiment, Golden acceptance, a change to Stage 9's NO-GO verdict, or permission to merge PR #25.

## Reproducible code gap and failure surface

Current `WorldBody.restore_causal_state` writes `_position`, `_body`, `_inventory`, `_resources`, topology collections, placed stones and action-failure schedules **while still parsing** the incoming snapshot. `physics_version` is checked at the very end. Thus a validly encoded but incompatible physics version, a malformed late topology row or a bad late action-failure schedule raises after some or all WorldBody owner fields have already changed. SnapshotManager's compensating multi-owner restore does not make direct owner calls transactional and cannot be the sole defense if the owner's restore leaves mixed state. The same method silently coerces coordinates and quantities (`int(1.9)`, `int(True)`, `int("2")`) and accepts duplicate resource rows, which cannot preserve an exact causal state.

## Frozen minimal implementation contract

1. Read and validate the complete prospective world/body state **without assigning to any live owner attribute**. Reject incompatible `physics_version` before touching any owner state. Commit all validated staged fields only after the last check. An exception leaves `export_causal_state()` exactly equal to the value before the call, including action-failure cursors and all dynamic physical collections.
2. For canonical owner-produced state, preserve the existing keys, arrays, hashable representations, causal bytes, action-failure replay and successful restoration behavior. No new field, schema revision, pseudo-observation, cognitive inference or journal entry is authorized.
3. Reject lossy or malformed **snapshot** representations: coordinates must be exact integers (not Boolean/fractional/text); bounded body fields must have finite binary64 values; inventory, resources and stone counts must use nonnegative exact integer quantities; resources must use declared kinds and unique (position,kind); topology positions must be canonical exact interior coordinates without duplicates; action-failure program primitive/schedule/index must be well typed, bounded and unique. Do not normalize a malformed source into a different physical history.
4. Preserve the currently legitimate states of WorldBody, including multiple resources at one site under distinct kinds, dynamic danger and lethal-zone changes, externally applied body values normalized into binary64 by the normal input boundary, and optionally absent `scenario_action_failures` for historical unprogrammed worlds. Body validation and world-grid boundaries remain normative, unchanged.
5. Do not change `WorldBody.apply_scenario_event`, the scheduler, `SnapshotManager`, action execution, journal event identities, physics constants, historical fixtures or the normative specification. Direct synthetic owner-state tests are **not** proof of a real-world hazard being perceived by the individual.

## Prespecified unit checks

- Build two otherwise independent WorldBody instances with matching configuration and a legitimate nontrivial physical state: inventory/resources, current position, active danger zone, placed stones or shelter, plus an external forced-action-failure schedule with a consumed cursor. Export this exact canonical owner state, independently restore it, and compare exact object equality and `canonical_causal_bytes` to ensure ordinary snapshots are unchanged.
- Make a *different* live state first; attempt to restore a snapshot with only `physics_version` altered. The call must raise, and the live exported causal state and canonical bytes must remain unchanged.
- Repeat with a valid snapshot whose late `resources`, `danger_zones`, `placed_stones`, or `scenario_action_failures` entry is malformed. Every reject must be atomic, even after successfully parsing earlier populated fields.
- Reject a physically impossible (fractional, Boolean, textual, out-of-grid) coordinate, a Boolean/non-integer/negative quantity, an unknown/duplicate resource, a NaN body field and an invalid/duplicate action-failure program. Check **no owner mutation** in each case and no silently coerced physical observations.
- After those failures a valid restore must still succeed. Existing Stage 2/11 unit tests, scenario rejection cases and snapshot replay must remain green.
- Record exact branch SHA, Python patch versions, commands, counts and CI outcomes. Do not call diagnostic reference replays scientific Goldens or update a held-out result.

**Status before execution: UNVERIFIED. Stage 11 IN PROGRESS; Stage 9 scientific NO-GO. PR #25 Draft/open/unmerged; `main` untouched.**
