# I3 R2: two-phase engineering step custody, not M11

**Date:** 11 November 2026. **Scope:** engineering-only, read-only replayable metadata and a fail-closed local intent/receipt ledger, without constructing a `World`, `Mind`, life or scientific cohort. Source baseline: I3 owner-selected development reference under [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md) and the [R1 birth-slot reservation](ENGINEERING_BIRTH_RESERVATION.md). Parent tracking [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

## R2 engineering question and falsifier

Can a *separately reserved, engineering-only* I3 birth identity publish a source-bound, monotonic one-step **PREPARED intent** before any motor, and then atomically settle one **POST_PAID_LEARNING** result in a local SQLite store, while refusing both accidental duplicate execution and recovery from a missing receipt? This is a state-owner storage/protocol question, **not** evidence of autonomous learning or physical M11.

A failure is: two concurrent writers preparing the same tick; a stale head progressing; the prior body's receipt being replaced; an unsealed motor being passed off as recoverable; a dead or horizon-censored session accepting a new step; a forged/foreign database or broken link accepted; or an external-generation/runtime import.

## Engineering interface

- `src/i3/runtime/engineering_step_ledger.py` is standard-library code except for its I3-local typed `birth_reservation` import. It requires a **previously consumed reservation**, matching its exact source/world/genome/seed identity. The ledger is isolated per engineering directory in `i3_engineering_steps.sqlite3`, with a dedicated SQLite application ID, strict schema, WAL, `synchronous=FULL`, and `BEGIN IMMEDIATE` single-writer transactions.
- `initialize(directory, reservation, horizon, initial_body)` consumes **no** new birth or World. It records a genesis head and one five-channel initial body. Initialization following reservation is not atomic across the two SQLite files: if interrupted, the slot is lost and requires a new isolated engineering workspace. It is not safe to reuse an old slot.
- `prepare(...expected_head, intent)` verifies that the preceding receipt's `body_after_paid_learning` equals the next step's `body_before`, the tick/decision-work/motor shape is valid, the sequence is new, and the session is open. It persists a **PREPARED** row *before* a motor. A one-time 256-bit seal token is returned only to the in-process caller; the DB stores its hash, never its plaintext. Do not serialize/log the token. `inspect` explicitly refuses any pending PREPARED entry. A crash losing the token must stop, never auto-retry a motor.
- `seal(...expected_head, seal_token, receipt)` only accepts the matching PREPARED row and explicit `POST_PAID_LEARNING` phase. It validates the two **reported** paid currencies, reconciles the E/V debit against the post-motor and post-learning bodies, requires death causes to match a zero vital channel and forbids postmortem cognition, stores the canonical receipt and hash-chain step atomically, clears the token hash and sets `OPEN`, `DEAD` or `CENSORED` (horizon). The caller's declaration is **not independent verification** that those computations happened or that the state is actually that of a born individual.
- `inspect(directory, reservation)` performs a read-only **complete chain validation** after closing and reopening SQLite, recomputing genesis and all committed entry digests, checking body continuity and terminal finality, refusing malformed input, foreign tables, gaps, duplicates and an unresolved PREPARED step.

## Demonstrated and missing properties

| Contract | Current result |
| --- | --- |
| Separate I3 engineering claim binds genesis | Locally checkable, subject to caller-supplied source hashes |
| Local duplicate/stale writer and tampered entry checks | Software tests present; full CI must be cited at exact PR source |
| Prepare-before-motor / seal-after-paid-learning protocol | Atomic storage protocol exists; **not yet wired to `Mind.decide`, `World.step` or real learning** |
| Crash after prepare, missing settled receipt | **Fail-closed** on cold inspect; cannot automatically recover or replay an uncertain action |
| Death/horizon tombstone | Ledger rejects further steps when record says `DEAD` / `CENSORED` |
| Full mutable Mind + World + RNG serialization or replay | **NOT IMPLEMENTED** |
| Authenticated M11, durable remote anchor, anti-rollback, proven single life continuation | **NOT ESTABLISHED**; local file replacement or rehash remains possible |
| New scientific World, Stage 2.2+, runtime activation | **FORBIDDEN / NOT PERFORMED** |

The ledger records a **syntactically valid asserted receipt**. It cannot verify a real motor, its actual energy/vigilance debit, personal learning, hidden World state, or post-crash equivalence without a separately integrated native session and externally checked provenance. A local SHA-256 chain plus WAL is not a signature or external monotonic witness. An attacker can replace the whole database, or both reservation and ledger databases. The in-process token blocks accidental recovery from PREPARED, but it is not an external transaction authority.

## Tests and next integration

`tests/i3/test_engineering_step_ledger.py` exercises local two-phase creation, unresolved intent, single-write thread race, wrong token, stale head, corrupted/missing/foreign ledger, altered receipt, wrong identity, wrong body, invalid payments, invalid death cause, irreversible terminal/horizon behavior and absence of motor/World imports. Existing birth-reservation tests remain relevant. A focused local Python 3 run with the I3 modules isolated from other engines completed **14 tests PASS** (ten new plus four legacy, no new World). Full PR-scoped Python 3.11 and 3.12 CI must still run and be checked for exact-source promotion.

**Next R2/R3:** connect the ledger behind a single native I3 stepped session that runs genuine `Mind.decide -> World.step -> prepaid learning -> POST_PAID_LEARNING` once and publishes its actual state and receipts before allowing the next motor. Define a versioned safe state codec or deterministic reconstruction with exact source and independent anti-rollback anchoring; test crash on both sides of every publication boundary and same-life cold-restart parity. If a motor cannot be conclusively settled, refuse continuation. Only after these checks is an I3 engine activation PR meaningful.

**Research authority unchanged:** P1.3 funded-v2, I3 Stage 2.1 scientific `NOT_ISSUED`, E3 source-specific `CLOSED_NEGATIVE`; no old cohort reused or new scientific World authorized by this engineering storage work.
