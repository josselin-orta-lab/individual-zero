# I2 G1: candidate single-owner WorldBody publication protocol

**Status: PROPOSED / REVIEW_REQUIRED / NOT_EXECUTED.** Prepared 2026-11-01 against `main` `5ec32e0e2da054d264dafcfc3474a7eb8064d63c`, for [#662](https://github.com/josselin-orta-lab/individual-zero/issues/662) and [#664](https://github.com/josselin-orta-lab/individual-zero/issues/664). This is a concrete design **option for independent architecture and science review**, not an accepted ADR, a functioning M11, a G3 implementation, a birth, a motor permission, or evidence that H1/H2/H3 work. I1 alone remains active. The current I2 SQLite v5 owner and witness ports are synthetic.

The [current-source G1 review packet](i2-g1-current-review-delta-2026-11-01.md) defines requirements S1-S8, crash cases C0-C11 and open decisions R1-R8. **That packet remains the scope of review; this candidate proposes one falsifiable implementation choice for R1-R4/R7, not a second set of scientific gates.** Follow [ADR-0001](../../decisions/ADR-0001-strict-generation-autonomy.md): no imports, fallbacks, memories, ownership or identities from I0/I1.

## Decision proposed for review, not accepted

Choose an **internal, deterministic WorldBody represented entirely by the same durable generation owner as the active I2 state**, and make any external observer a **read-only projection**. This avoids claiming exactly-once effects across a separate, nontransactional simulator or actuator. Every physical step is a state transition of the owner, with no independent `WorldBody.apply()` call before or after durable commit. A distinct **external latest-head service** attests which durable revision may become publicly observable and later serve as the next input. It is NOT a second state owner and cannot change body, UC or cognition.

Do not choose this model for a real external actuator without a separately reviewed **durable, hardware-enforced idempotency/fencing and effect-receipt protocol**. If physical effects can occur outside the owner and cannot be fenced, the required at-most-once property is **UNPROVEN**; stop at G1. Never hide this gap behind a re-read of SQLite or a local witness.

### Immutable identity and unique field ownership

| Group | Sole proposed authority / atomic payload | Unacceptable second owner |
| --- | --- | --- |
| Life/genesis and active generation | I2 generation owner: fresh `life_ref`, `genesis_ref`, schema, run identity, terminal flag | Importing I1 identity, silently converting old snapshots |
| WorldBody | Same owner: body, needs, inventory, resources, hazards, physics step, RNG state, deterministic environmental consequences | Mutable external Lab state or separate WorldBody file |
| Cognition and UC | Same owner: first-person capture issued from committed WorldBody, budget and debits, intention, current-step candidates/advice/veto, private learning/H2, journal | Parallel UC scheduler ledger, historical cognitive owner or saved winning motor option |
| Transaction and custody | Same owner: revision, `pending_attempt`, `state_digest`, `event_head`, irreversible terminal | Two mutable SQLite owners or operator file promoted to M11 |
| Independent witness | An **external** authority: epoch/fencing writer, monotonically attested `(life, genesis, revision, event_head, terminal)` plus signer/revocation/freshness | Operator HMAC file, synthetic challenge service, unverified cached claim |
| Public projection | Pure read-only view of an externally attested state digest; no state mutation or separate action execution | Consumer reading speculative/unanchored SQLite writes |

For G3 every field needs a canonical serialization, owned schema, mutation phase and parity/replay test. These are requirements for a **future** implementation; no living I2 owner or real witness exists today.

### Proposed order and linearization candidate

```text
current independently attested head + writer epoch
  -> acquire fenced writer / verify genesis and nonterminal
  -> read EXACT last publicly attested owner revision
  -> fresh first-person observation (no Lab oracle) and UC budget
  -> one private deterministic state transition:
       capture, paid cognition, intention, options, Competition/veto,
       one WorldBody transition, RNG, bodily consequence, H2, terminal
  -> local transaction COMMIT of entire generation and causal journal
       (not yet publicly observable; no external side effect)
  -> external compare-and-set(expected old head, new head, epoch)
       (proposed public-visible linearization point)
  -> only a fresh verified matching head authorizes read-only publication
       of this exact state and permits consideration of a NEXT step
```

**Prerequisite before any local COMMIT:** the independent service has already granted a unique writer epoch/fence for this life; stale writers must be unable to advance the external head. A mere expiring lease or local SQLite lock is insufficient across rollback or separate hosts. A candidate has an unforgeable **attempt identity** scoped to life/genesis, parent revision and writer epoch; the intended input claim, UC, physics inputs, RNG and output digest are fully bound to it.

**Exactly one physical transition in this proposed scope** means the WorldBody state has **one durable owner and no separate executor**. The local COMMIT fixes its candidate state, but readers and the next owner step must NOT observe it until the external CAS attests that exact revision and head. The CAS is therefore the proposed visibility point, not a way to make two disjoint state mutations atomic. Every public read must validate freshness and equality (revision, head, genesis, terminal, epoch); a cached `MATCHED` or double audit is not authorization.

A failed, delayed or lost-ack CAS is never retried as a physical action. A cold, independently verified latest-head read may classify the attempt, but does not authorize an I2 restart here. Until independent G1/G3 recovery rules and custody are proven, the only permitted local result is **`technical_halt`**, not guessing, replaying, undoing a terminal, recharging UC or selecting an older revision. In particular, **no G2 inspection ever becomes `resumption_authorized` or `motor_authority`**.

### Crash/counterexample obligations, mapped to the existing G1 packet

| Existing case(s) | Fault injection / concurrency conflict | Mandatory observable result (candidate expectation, not demonstrated) |
| --- | --- | --- |
| C0, C10 | Imported/duplicated genesis, pre-terminal copy restored after death | Independent identity/terminal fence rejects; no new birth or alive projection |
| C1, C2 | Captured affordance/goal, UC or veto changes before candidate is bound | No command carried forward; fresh capture/review and a complete, locally atomic debit or refusal |
| C3, C4 | Crash before local COMMIT or lost SQLite acknowledgment | No public effect or second step; cold check of EXACT attempt, never re-run WorldBody transition |
| C5 | Local COMMIT succeeded but external CAS failed or was never sent | New revision remains private; `technical_halt`, not a locally trusted advance |
| C6, C11 | External head newer, local branch older, coordinated directory rollback, bad signature or torn WAL | `STALE/FORK/UNKNOWN` refusal, never restore older life or continue |
| C7, C8 | CAS acknowledged or lost before publicly visible projection | Expose state only when attested head matches local bytes; no separate `apply`; uncertainty halts |
| C9 | Two writers with same parent head, one fenced late | Only independently fenced epoch can advance; old writer's local candidate cannot become visible |
| C10 | Terminal physically committed but attacker substitutes local/old signer records | Off-domain monotone terminal record blocks any further step or pre-terminal visibility |

Each row needs an **independent observer**, reproducible fault point, negative control and a demonstrable refusal. The completed SQLite v5 G2 tests cover none of the independent service, physical-effect or two-host claims above. Mark their future G3 executions `NOT_EXECUTED`.

### Discarded implementations and explicit unsolved questions

- **Rejected as sufficient:** a local WAL COMMIT alone; an operator-controlled lock+HMAC file; `read_verified_latest` on a mock; hash-chain consistency alone; time-based leases without fencing; retry after a timeout; two independent ledgers followed by a best-effort reconciliation.
- **Not covered:** irreversible effects on external devices, authority of a true signer/clock/nonce source, deployment trust boundaries, power-loss behavior of the storage medium, externally visible effects before anchor verification, birth certificate issuance, physical mortality instrumentation and G0 historical evidence recovery.
- **Open R1:** can WorldBody be *entirely* owned and projected without external mutable effects for the intended scientific world? If not, this candidate is insufficient.
- **Open R2/R3:** who implements the future owner, how are `pending_attempt`, rejected-cycle UC costs, current-state freshness and private vs visible revision represented with a single ledger?
- **Open R4/R7:** who actually operates and audits an independent monotone, non-equivocating witness, with fencing and terminal anti-rollback beyond the same operator's rollback domain?
- **Open R5/R6/R8:** what independent evidence links personal captures, intentions and admitted consequences to H2/H3 with no oracle leakage, and which preregistered tests disconfirm them? No outcome exists yet.

### Independent review and gating

A future **architecture reviewer** must either reject this candidate or specify a concrete ownership roster, single visibility point, key/fence trust domain and proofs against C0-C11, on an exact SHA. A **separate science reviewer** must evaluate first-person provenance, UC, H1-H3 observables and falsifying controls before accepting any experiment. Record objections and either `REVISE_G1` or `REJECT_G1`; only a documented independent verdict may use `ACCEPT_G1_ARCHITECTURE`. Merging this text grants **none** of these decisions.

**Next permissible step:** use this candidate as input to independent G1 reviews under #662/#664. **Do not** add a living constructor, runtime entrypoint, publication writer, WorldBody effect executor, registry entry, retry/recovery command, cohort or scientific promotion on the strength of this document alone. G3 remains `NOT_ESTABLISHED`.
