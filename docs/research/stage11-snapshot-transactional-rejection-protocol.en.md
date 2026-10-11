# Stage 11 snapshot restoration: transactional refusal at the owner boundary

**Software-only regression contract, recorded 2026-10-11 before implementation.** Normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially exact complete causal-state restoration (S-01.5, S-13.1, DC-08, INV-33), technical journal append-only custody and fail-closed behavior. This is not held-out science, Golden reference replay or a Stage 9 status change.

## Existing failure surface

`SnapshotManager.restore` verifies the stored snapshot hash and the owner-ID set, then loops over each canonical state owner in sorted order. If an earlier owner accepts its replacement but a later owner rejects an incompatible snapshot, the runtime retains some already restored values and some newer values. This is a mixed-time causal state and cannot legitimately be resumed. An owner that mutates before raising makes the failure more severe. Current unit tests confirm valid restores, tampered-hash refusal and mismatched owner sets, but not multi-owner transactional refusal.

## Fixed implementation expectations

- Verify snapshot hash and exact owner set before altering any state, as currently.
- Before applying a validly hashed snapshot, capture and canonically validate complete current exported states of **all** target owners (the recovery point).
- Restore each owner from its frozen stored state through `restore_causal_state`, without bypassing ownership or rewriting the journal.
- On any owner failure, attempt to restore **all** owner states from the saved recovery point, including the owner that partially mutated before raising. Restore in reverse owner order; if every rollback succeeds, re-raise the original error with no `snapshot_restored` journal event. If rollback itself fails, throw an explicit critical error rather than claiming atomic recovery.
- Successful restore retains the prior journal behavior and deterministic owner ordering. No journals, evaluation traces or external physical observations are rolled back, and no extra cognitive action, physics transition or learned fact is fabricated.
- The generic manager must remain usable from Stages 1–11 and must not change normative specification or snapshot format.

## Frozen unit case

Take a verified periodic snapshot of two synthetic canonical owners, sorted by IDs `a` and `b`, at values 1 and 2. Move their current states to 11 and 22. Owner `a` successfully restores 1; owner `b` mutates to 2 then throws `ValueError` on that snapshot as incompatible, but permits restoring its genuine pre-attempt value 22. The manager must leave `a=11`, `b=22`, preserve the journal and rethrow `ValueError` without recording `snapshot_restored`. A normal positive restore remains unchanged.

**Before validation: UNVERIFIED. Stage 11 IN PROGRESS; Stage 9 scientific NO-GO. No full Python 3.11/Golden/held-out campaign, no PR merge.**
