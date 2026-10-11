# Stage 11: life-snapshot journal receipts must be transactional

**Preimplementation software regression contract registered 2026-10-11.** The only normative authority is `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, specifically sections 17.4, 17.6–17.8, DC-08, INV-33/44/49. This is synthetic development verification, **not** a historical Golden, held-out evidence, Stage 9 scientific acceptance, or authorization to merge.

## Discovered failure boundaries

`SnapshotManager.take` stores the new `_StoredSnapshot` in `_snapshots` before recording `snapshot_taken`. If `HashChainedJournal.append` rejects that receipt, `take` raises but leaves a snapshot accessible through `record()` despite no successful causal audit event. `SnapshotManager.restore` currently records `snapshot_restored` **outside** its compensated multi-owner restore `try`, so a failed receipt can leave causal owners at the restored time even though `restore()` raises without a corresponding technical event. The helper `_write_journal` also increments its occurrence sequence **before** append, consuming an identifier on a failed write and potentially changing later replay bytes.

This protocol tests a **single atomic refusal at the technical journal API boundary**, not malicious Python code that mutates private buffers after append or persistently unavailable storage. `HashChainedJournal.append` itself provides all-or-nothing rejection of individual invalid appends; persistent receipt failure may leave a branch unable to continue and must not be misrepresented as successful recovery.

## Fixed implementation contract

1. Keep the exact existing success-path snapshot payload, SHA, deterministic snapshot ID, journal occurrence ID, event order and canonical bytes.
2. Increment `SnapshotManager._journal_sequence` **only after** the journal has accepted the receipt. If the append rejects before mutation, the next valid attempt must retain the expected occurrence sequence.
3. `take`: if `snapshot_taken` fails to append, remove the newly inserted snapshot or restore the previous value under the same deterministic snapshot ID. Do not return a record or leave a new unjournaled checkpoint addressable. Do not alter WorldBody, other causal owners or technical journal contents.
4. `restore`: include the `snapshot_restored` receipt in the same compensated transaction as restoring all causal owners. On a receipt failure, restore **all** owners from their full, pre-attempt causal states, in reverse canonical order, and rethrow the failure with no `snapshot_restored` occurrence. If compensation fails, retain the existing explicit critical error. Never roll back the technical journal itself.
5. Do not silently delete a valid earlier snapshot with identical deterministic ID, change the normative specification, alter historical reference fixtures, assign the individual an unobserved event or imply scientific acceptance.

## Frozen synthetic unit tests

- Create a `FakeOwner` and fresh `SnapshotManager`. Intercept only the `snapshot_taken` `journal.append` to raise a reproducible `RuntimeError` before modifying the journal. Assert the operation raises, no new snapshot can be looked up, no journal entry was added and `_journal_sequence` is unchanged. Retry without the fault: compare its snapshot record, bytes and journal chain against an independently instantiated clean manager.
- Take a genuine periodic snapshot of two owners `a` and `b`, mutate both current states, then intercept only `snapshot_restored` to raise before append. Verify the original states of **both** owners survive, the journal remains byte-identical/valid, no receipt is written and the sequence remains unchanged. A later genuine restore must succeed and yield the same journal bytes and snapshot ownership state as an independent manager with no failed attempt.
- Existing snapshot tamper, owner-mismatch, incompatible-late-owner and full Stage 11 snapshot/budget tests remain part of regression. Do not modify expected results to mask any negative finding.
- Report the exact code/test SHA, Python version, test counts, command and CI results separately from independent scientific campaigns.

**Stage 11 IN PROGRESS; Stage 9 scientific NO-GO. PR #25 stays Draft/open/unmerged.**
