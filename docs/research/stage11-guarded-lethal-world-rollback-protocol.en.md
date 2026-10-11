# Stage 11 real-world lethal rollback with guarded Scheduler occurrence

**Protocol registered on 2026-10-11 BEFORE the new fixture/test or its results.** Public deterministic software test, not scientific held-out or historical Golden. Normative English MVP specification v1.2.1 governs §17.6 lethal checkpoints, rollback, append-only journal, INV-27/28 and §16.3 P-43. Stage 9 remains SCIENTIFIC NO-GO; PR #25 remains open/Draft/unmerged.

## Previous evidence and missing scope

Source SHA `9ae6d033dc61804312f0ae7fe053cff13ef18dc1`, Stage11 versioned cycle-occurrence guard has already passed software tests and real Stage4 cognitive lethal rollback (Stage11 inherits Stage4 decision flow). What remains untested is a **full Stage11 instance containing Exploration and Global Modulation causal owners**, with the guard ON, that actually sends a geographic cognitive movement resulting in a physical lethal transition, restores the complete pre-send checkpoint and continues under a new attempt without learning a fictitious death.

## Predeclared public fixture

- Start from the existing deterministic public `build_public_route_runtime(layout_variant="junction_open", planning_uc=4, exploration_uc=4, survey_refresh=True, cycle_occurrence_guard=True)`. Its baseline 10-step physical route begins by moving from (2,2) east into (3,2); do not change its costs, rules or initial body.
- Instantiate a new Stage11Runtime using exactly the baseline world physics, independent initial state, stage-11 config, equipment, safety facts, and Action Control threshold. Change **only the explicit physical layout** to include a previously unknown *lethal_zone* at physical (3,2), and append a descriptive Stage11 config version suffix `+guarded-lethal-physical-dev-v1`. Do not add that physical truth to the individual's known safety facts; there are no scenario injections or oracle reads.
- Execute exactly **one** world step. Compare with a separately instantiated same-version independent replica with the same scheduling. Freeze inputs; do not extend the horizon to obtain a favorable result.
- Predeclared expectations: one physically confirmed lethal transition and one rollback; one append-only `snapshot_restored` receipt and one `lethal_rollback_completed`; alternative physical path or safe fallback must not revisit lethal (3,2); an actual new `attempt_ref` is allocated; no extra `t_monde` advancement for rolled-back branch; no rolled-back movement inside the autobiographical view or learned exploration/causal evidence; every cognitive cycle's `compute_budget.active_occurrence` matches actual (world step, active attempt, last cognitive cycle), and total charged UC respects budget; final journal verifies and independent runs reproduce journal bytes, owner causal states and checkpoint identities exactly.
- If the existing fixture selects a nonlethal first action, the negative finding must be retained. Do not change inputs or horizon post hoc to force a transition; register any corrected fixture separately before executing it.
- Separately assert historic default-off owner-state schema and fixture hash remain untouched; the opt-in guarded path legitimately produces different version/hash.
- Run one targeted quick CI and a complete Python 3.11/3.12/technical artifact campaign for exact SHA. Preserve failures, overrides and limitations separately. No staged science, independent operators, Goldens modification, `main` write or PR merge.

**If a genuine Stage11 bug is exposed**, reduce the first divergence to a deterministic fixture before any narrowly reasoned correction. Never hide a false-positive scientific success behind a green CI.
