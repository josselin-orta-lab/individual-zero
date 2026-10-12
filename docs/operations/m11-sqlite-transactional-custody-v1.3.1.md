# M-11 Option A implementation: SQLite transactional I0 custody (phase 1)

**Status:** implementation in progress; **M-11 FAIL**, **M-12 not newly certified**. Do not use this component to restart a living Stage10/11 individual yet.

**Normative authority:** `docs/architecture/reference/en/mvp-specification-v1.3.1.md` §§4–5 and M-11/M-12. No specification change, Stage 9 scientific NO-GO unchanged. Operator acceptance is separate from CI.

## Why this change is necessary

The existing JSONL per-event WAL is a real improvement over the export-only crash window demonstrated by PR #63. However, writing one receipt with `fsync` does **not** atomically persist the entire current WorldBody, Scheduler, all active cognitive owners and the terminal status. In particular, a crash during an already applied physical transition cannot safely be handled by loading the most recent coherent journal prefix as a still-active life.

The intended target is **one local SQLite database owned by I0**, with its SQLite journaling set to WAL + `synchronous=FULL`, and *a separate permanent append-only causal occurrence table*. A SQLite WAL checkpoint is not deletion of I0's causal history. Oracle and EvaluationBench remain completely independent.

## Phase 1 delivered in this change

`lab.sqlite_life_store.SQLiteLifeLedger` is an **isolated transaction primitive**, not yet the active Stage10/11 persistence interface.

- Birth uses a new exclusive absolute database path; no existing identity is silently overwritten or imported.
- The `life_current` table contains **one current record only**, bound to immutable individual ID, strictly monotone generation, SHA-256 state checksum, causal count/head and lifecycle status. There is no API for selecting a former generation.
- `causal_occurrence` retains **all** canonical journal records, in exact order, with unique IDs, previous/event SHA-256 hashes and matching count/head, independent of temporary SQLite WAL checkpoints. The data can be exported as the normative canonical byte stream.
- A separate durable `pending_intent` fence is committed **before any potential external effect**. If the process dies before the corresponding atomic generation commit, the old current record cannot be reloaded into an active identity. A human may record a permanent `technical_halt` without manufacturing missing physical facts.
- `commit_generation` validates identity/lease, expected generation/head, the canonical event suffix, terminal death receipt/closure and proposed current state, then updates occurrences, current state, identity generation and terminal marker **inside one SQLite transaction**. The pending intent is removed in the same transaction.
- An uncertain SQL write, sync or commit outcome permanently poisons the in-process handle; it is not retried or compensated. After a process restart, `audit()` decides if the transaction actually committed; an unresolved intent is never interpreted as a successful active recovery.
- Test subprocesses inject real `os._exit` immediately after intent commit, after occurrence insertion, after current-state update, before commit, and after commit. Distinguish uncertain from durable outcomes. Both Python 3.11 and 3.12 will require verification.

All features intentionally avoid Oracle/Bench imports and never use a historic saved life snapshot as a rollback mechanism.

- A process-lifetime POSIX writer lease prevents two active processes from opening the same individual database. A separate read-only SQLite snapshot verifier can inspect ongoing WAL commits consistently without acquiring that writer lease.
- A stand-alone operator CLI, `python scripts/audit_i0_sqlite.py --db /absolute/i0.db --identity I0-ID --expect-generation 0`, checks only internal byte/hash/generation coherence and trusted anchors, not independent physical truth.
- `lab.sqlite_staged_world.prepare_mortal_world_effect` runs unchanged physical dynamics on a private copy under its own copied mortal-dispatch authority, without publishing anything to the public WorldBody. It is not yet an Action Control dispatcher and exposes no `publish` method.
## Phase 1b: registered runtime-custody inventory (development only)

The storage layer now accepts an **opt-in strict envelope** via
`lab.sqlite_runtime_custody.capture_registered_current_state`. It observes a
quiescent autonomous mortal instance, including `WorldBody`, the Scheduler
and every owner in the runtime's registered `causal_owners` roster. A registered
RNG stream owner is included without consuming a draw. Captures are detached,
and no physics, cognition, journal, Oracle or Bench is published or restored.

A `i0-registered-current-state-v1` envelope pins sorted owner IDs, an owner
roster SHA-256, current journal count/head and lifecycle. The SQLite
`i0-sqlite-life-custody-v2` schema independently stores the roster hash in
`life_current.registered_roster_hash`. Birth requires an active genesis anchor;
later commits may neither add/drop registered owners nor replace the envelope
with an unregistered phase-one image. A read-only audit refuses a rehashed
state-only attempt to erase the strict contract. This is internal consistency,
not protection from an administrator who rewrites **both** the state and the
independent SQL contract field. Trusted external anchors still matter.

The standalone operator CLI includes `registered_owner_roster_hash` (or
`null` for phase-one toy records) and explicitly reports
`runtime_recovery_certified=false`. This is intentional: the registered
owner graph does **not** account for every unregistered mutable runtime-local
field, prove each owner's cold-start semantics, or atomically publish the
current runtime after a SQLite commit. In particular, it does not turn
Stage12's independent fsynced JSONL WAL into a single SQLite coordinator.

**Schema compatibility:** previous draft `i0-sqlite-life-custody-v1` databases
are not silently migrated/reopened by v2 code. Treat them as operator-controlled
historical development artifacts; there is no automatic legacy life restart.

Targeted tests now include Stage4/10/11/12 registered owner inventory,
explicit RNG state preservation, roster/anchor falsification and real subprocess
`os._exit` across terminal-death COMMIT boundaries. Passing these tests
is storage-layer evidence only. M-11 is still **FAIL**, and the separate
stacked draft PR #96 carries the M-19 terminal-order correction. No claim
of complete M-19 validation is made by this document.

## Critical missing integration gates before M-11 can become PASS

1. **Physical candidate preparation:** compute an unchanged, once-applied `WorldBody.apply` result in a private candidate, including failure-program indices, resources and lethal predicates. The public WorldBody must not be mutated before the database commit. The private candidate is discarded on precommit error, never used to "restore" an earlier published world.
2. **Full current-state custody:** include every versioned physical, RNG, scheduler, memory and cognition owner state, and prove coherent validation/cold-start restoration of that **same latest** generation. The current `_canonical_state` gate checks the minimum envelope only. It cannot certify all owners.
3. **Atomic publication:** stage causal events, cognitive updates, sleep and terminal markers privately; commit one complete coherent generation, then publish that same committed state to the public runtime without running the command twice. Current `HashChainedJournal.enable_durable_wal` is not a replacement for this coordinator and **must not** be used as a second independent commit point.
4. **Crash and recovery test matrix:** real subprocess exits before/after write, `fsync`, SQLite commit, physical candidate creation/publication and lethal terminal closure. Include disk full, interrupted I/O, WAL corruption/torn suffix, simultaneous writers, SQLite busy handling, crash after commit before in-memory publication, and replay prevention.
5. **Integration and acceptance:** unchanged physics parity, all six Stage10 passes with postcut ownership, Stage11 integrated flow, Stage12 diagnostics/operator stop, independent offline export/audit, Python 3.11 and 3.12 and measured latency/size on ≥600 genuinely applied development steps. Explicit operator receipt remains required.

### Safety boundary

**Do not wire this database directly around an existing `WorldBody.apply` call** that still mutates the live world before commit. A SQLite COMMIT does not retrospectively make such a mutation atomic. The staged-candidate and sole-current-identity recovery requirements are P0 design gates.

**Fallback until the gates pass:** old integrated runtime remains fail-closed on uncertainty; never resume an uncommitted/uncertain life from an older prefix. Stage 9 scientific NO-GO and historical artifacts remain unchanged.

### Phase 1 development check

```sh
python -m unittest discover -s tests -p 'test_sqlite_*.py' -v
```

The five `os._exit` process fault windows, monotone birth and terminal states, hash validation, and identity checks are technical regression tests **of the new storage primitive only**, not a full integrated M-11 result.
