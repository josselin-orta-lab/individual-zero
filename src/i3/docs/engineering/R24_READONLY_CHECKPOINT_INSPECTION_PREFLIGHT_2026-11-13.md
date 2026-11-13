# R2.4 / #1339: no-writer checkpoint inspection, source-frozen preflight (13 November 2026)

**Category:** software-only safety correction on the existing authority-v3 exact-state checkpoint probe. No World, Life, Mind, engine, source/index grant, credential, off-host deployment or Stage-2 scientific result.

## Baseline discrepancy and falsifiable hypothesis

[PR #1370](https://github.com/josselin-orta-lab/individual-zero/pull/1370) and its [result](R24_EXACT_STATE_CHECKPOINT_RESULTS_2026-11-13.md) say `capture_exact_checkpoint` is read-only. The current source first constructs `AuthorityStore(database, authority_id)`. Its **constructor executes `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=FULL` and `BEGIN IMMEDIATE`**, then checks and commits. The checkpoint does not update CAS rows, but its initializer opens a writer transaction and can alter journal mode or create a store on a race. Calling this an observational read path is too strong.

**Hypothesis:** a checkpoint probe can verify an existing v3 authority, exactly its full audit, histories and accepted nonce set, inside **one consistent read-only SQLite transaction** without invoking the writer-capable initializer. The SQLite URI **must require `mode=ro`**, `PRAGMA query_only=ON`, and an existing non-symlink regular database. It must never enable `immutable=1` because that can ignore real WAL commits. The verified view is an isolated internal engineering helper, not a public production off-host API.

## Precommitted adversarial matrix

| Case | Required result |
| --- | --- |
| Existing valid v3 state | Existing checkpoint shape/data unchanged; no writer initializer |
| Read connection | `PRAGMA query_only=1`, `INSERT` prohibited, no writer transaction or journal-mode update requested by inspector |
| No pre-existing file | Fail closed; never bootstrap a new authority DB |
| Malformed/foreign authority DB or wrong authority ID | Fail closed as before; no mutation |
| PREPARED pending state | Reject |
| Corrupt audit or altered nonce set | Reject when checked against separately retained newer checkpoint |
| Concurrent verify/commit after checkpoint capture | Stale checkpoint fails; no partial transactional mix of pre/post commits |
| SQLite full rollback while retained newer checkpoint survives | Reject |
| SQLite plus matching old public checkpoint rolled back | **Accepted negative**: `FAIL_INDEPENDENT_M11` |
| Actual independent operator/storage/key evidence | `NOT_RUN / NOT_ATTESTED` |

## Minimal change and stop rules

- Add `AuthorityStore.open_existing_verified_readonly(database, authority_id)` as a `contextmanager`: validate path and ID without invoking `__init__`, open SQLite `file:` URI in `mode=ro`, set `query_only=ON`, begin a deferred **read** transaction, run the same full `_check_audit`, yield the transaction and close it. No tables, schemas or protocol tokens added; existing authority v3 writer methods are unchanged. A read-only connection may still use SQLite's WAL/shared-memory machinery at the filesystem level; claim **no SQL write capability**, not zero OS I/O.
- Refactor the checkpoint capture to consume that verified connection, preserving a single transaction for audit/head/history/nonce reads. No changes to the accepted checkpoint record format or public checksum.
- Add tests that force the writer `AuthorityStore.__init__` to raise on capture, attempt a write within the read context, refuse absent/foreign state and exercise concurrent writer/read snapshots. Keep prior fault tests.
- Exact-source CI on Python 3.11 and 3.12, generation ownership, navigation and full prior I3 tests must PASS. Any error: stop and correct before merge. No tests may silently skip.
- No signed witness, key custody, off-host privilege separation or source attestation is introduced: this corrects only local probe behavior, not independent M11. Preserve `NOT_ISSUED`, `HOLD_NO_VERDICT`, P1.3 funded-v2, I3 reference and I1 active.
