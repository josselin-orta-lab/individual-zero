# I2 / G1: reviewer handoff for the smallest living scientific loop

**Prepared 1 November 2026. Candidate baseline to inspect: main commit
`2221b42f9012acb1292700b3ec29ee5974bbf372`. This is a short review request, NOT independent review,
G1 approval, a born individual, or G3/G4 scientific evidence.** Re-pin the
exact SHA at the moment each reviewer begins and state any intervening changes.
I1 alone remains active; I2 is proposal-only with no executable entrypoints.

**Owner direction:** [ADR-0004](../../decisions/ADR-0004-evidence-driven-development-and-g2-stop-rule.md)
ends the open-ended G2 campaign and puts independent G1 review before
further living implementation. Review on the **current** unified SQLite
v5 source, not the deleted v1-v4 synthetic owners. Original detail lives
in [the source-current review delta](i2-g1-current-review-delta-2026-11-01.md)
(S1-S8, R1-R8, C0-C11) and
[the single-owner publication candidate](i2-g1-single-owner-world-publication-candidate-2026-11-01.md).

## A concrete minimal candidate, not an approved architecture

For the first experimental world **choose a wholly internal deterministic
WorldBody**, with all physical fields stored in the **same** durable I2
generation owner as UC, capture, cognition, H2, RNG, action status, journal,
attempt, genesis and absorbing terminal. An external public view is a
**pure read-only projection**, not a separately mutable body nor an
external actuator. This removes the external-effect double-apply path for
this narrow laboratory world; it does **not** prove fencing, trust,
anti-rollback, an independent M11 witness or physical causality.

The proposed publication sequence for reviewer assessment:

1. Verify a genuinely external latest-head and terminal witness, unique
   fenced writer epoch and exact local canonical state S(t). No stale,
   unanchored or terminal state may make a fresh observation.
2. Generate first-person O(t) from **public attested S(t) only**, including
   verified consequences of earlier admissions. Past H2 update and full
   UC charge occur in the same generation transaction.
3. Rebuild today's available actions and intention semantics, run paid
   Competition, recheck freshness, veto and actual motor admission.
   **Review/advice is not motor admission**.
4. Compute **one** deterministic internal state transition using that
   admitted action, body, inventory, RNG and current physics. No
   separate WorldBody executor, no researcher-forced secondary action and
   no read of this step's hidden result by cognition. A null action
   still records its actual UC and non-admission.
5. Commit a single canonical owner revision and causal record privately,
   then request external CAS(expected previous head, next head, epoch).
   **CAS is the proposed visibility point**, not a claim of distributed
   state mutation atomicity. Only an authenticated, fresh matching
   latest-head read may expose S(t+1).
6. At O(t+1), and **never before**, the individual may observe the
   previous action's consequence and update learning. A terminal
   S(t+1) must have no later cognitive step or postmortem learning.

After an uncertain COMMIT, CAS, witness, signer, fork or publication,
**technical_halt without retry, second effect, refunded UC, resumption,
or old-copy recovery**, until a separately accepted recovery contract
exists. For an external robot, networked actuator or separately mutable
physics, this candidate is **insufficient**; require another independent
idempotent effect protocol and new review before any use.

## Narrow decisions needed from TWO genuinely independent reviewers

| Reviewer | Must decide on current-SHA evidence | Do not accept as a substitute |
| --- | --- | --- |
| Architecture (R1-R5/R7) | Single mutable owner including real UC and body; CAS as public linearization; private/outcome visibility barrier; externally governed monotone/fenced M11 signer; terminal/identity protection; classification of uncertain writes and C0-C11 with explicit `technical_halt` | SQLite WAL alone; operator HMAC; injected latest-head test double; same-domain signer or a green G2 CI |
| Science (R5/R6/R8) | First-person O(t) -> admitted action -> bodily effect -> later O(t+1) provenance; H1 continuity without inherited commands; H2 collect/eat delayed consequence; H3 competition without hardcoded food priority; ablated independently born comparator; failure, abstention and mortality observables | Toy priors, experimentally forced consumption, same-step feedback, unchosen counterfactual, paired synthetic episodes or favorable eight-step trajectory |

**Independent review format:** reviewer identity and independence, role,
exact commit and files examined, date, chosen alternative and rejected
alternatives, C0-C11 dispositions, specific missing proofs, and individual
verdict `ACCEPT_G1_ARCHITECTURE`, `REVISE_G1` or `REJECT_G1`.
The joint gate remains **REVIEW_REQUIRED** until *both* appropriate reviews
exist and any necessary revisions have been explicitly resolved. Neither
this packet nor its author can sign off on its own design.

**Explicit current blockers:** no independently governed non-equivocating
witness/epoch/fence, no living single-owner body/UC/physics/terminal,
no verified O(t+1) causal issuance, no independent scientific reviewer.
G0 evidence custody remains PARTIAL (#661). All future physical failure
injectors C0-C11 remain NOT_EXECUTED on I2.

## First implementation increment AFTER G1 is accepted (issue #664)

Implement **one vertical experimental path**, not a family of new owners:

- A fresh I2 identity and canonical generation owner: life/genesis, needs,
  inventory, resources, RNG, real UC account, intention, action admission,
  H2/memory, event head, pending attempt, physiological terminal.
- Minimum actions: collect one resource, eat if accessible, drink/neutral
  option, abstain on no funded/safe candidate. The independent safety
  decision cannot be inherited; no action gets hardcoded priority.
- A wholly owned deterministic WorldBody transition and read-only,
  independently attested public observation; a successor action cannot
  read the newly computed outcome until the next personal capture.
- Exact first-person provenance to a later learned decision; compare a
  learning-disabled I2 with a new independent genesis under the same
  physical laws and initial resources. Preserve actual UC, survival,
  null/negative and adverse outcome traces.
- C0-C11 adversarial proof of independent witness, no double effects,
  stale writer refusal, irreversible death and no resurrection **before**
  the system is eligible for G3 acceptance.

No I1 code, live identity, memory, Q or runtime dependency may enter I2.
The first gated implementation should fail visibly if a component is
absent; **do not fill gaps with simulated M11 or operator privilege**.
No automatic activation on software PASS.

## Pilot falsifiers, not a confirmatory protocol

**H1:** intention's semantic continuity fails if a stale command or
previous veto/admission survives goal change, sleep or resource loss.

**H2:** no learned causal contribution is demonstrated if collect/eat
appears identically with learning disabled, if learning changes no later
*admitted* choice, if hidden/unchosen or withheld outcomes update memory,
or if roles reverse and the same preference remains indefinitely.

**H3:** no autonomous arbitration is demonstrated if need, exploration or
food priority is imposed by the controller; record changes in available
actions, abstention and UC to avoid selection bias.

**Stop/revise:** terminal resurrection, fork, double application, a
same-cycle hidden outcome in H2, unauthorized motor action, missing
independent witness, or unavailable G0/independent G1 evidence all
preclude scientific GO. G4 confirmatory cohorts need separately frozen
N, H, seeds, endpoints, censoring and an independent reviewed statistical
protocol (#663); **no such study is approved or run here**.

**One-sentence deliverable to the owner:** a precise signed/attributed
G1 verdict and the smallest unresolved proof, or a documented REVISE_G1
with the exact reason. More G2 fixture PRs do not resolve it.
