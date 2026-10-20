# #317: interrupted spatial intention, motor authority and wake validation

Code base: PR #318, experimental change committed at `b5b1add2`, paired against previous correct motor baseline `0128f4a1`. This experiment is **not a scientific GO** until physical results and independent seeds confirm it.

## Root defect and physical witness

Authenticated actor-free corridor WAL, seed 1142, SHA `1446a78a`, demonstrates a remote return from (11,8) toward previously seen wood at (9,8) on world steps 71 and 86. Both first hops are physically applied to (10,8). On steps 72/87 Competition transfers exactly 0.25 to a **fresh motor candidate** for the next hop. Legitimate `dormir` beats this option, followed by several steps of sleep and a fresh different choice; no remote site arrival is observed.

A careful source audit revealed a distinct safety/invariant defect: the prior `continue_engaged_memory()` set `_engaged_option_id` for the *new unselected* motor candidate before it won Competition. Since `fallback_candidates()` prefers engaged options, the unselected next hop could potentially be chosen as a fallback even without threshold crossing. That is an unsafe architecture, regardless of whether these particular WALs triggered it.

## Experiment: separate held information from motor decision

- A validated one-hop continuation no longer engages a new motor option: `_interruptible_intention_id` is a distinct Competition-owned *informational* marker, not a proposal, priority, action or new owner of TD.
- The source motor option must have actually been chosen and applied and its next observed step confirmed by Stage11 exactly as before. No new motor trigger or route oracle is introduced.
- The next motor option is re-registered under its own identity and needs fresh Stage8 evidence, Competition threshold and Action Control admission. It is not returned as a fallback before crossing.
- An ordinary, **physically applied** `dormir` can suspend the marker without residual-decaying that one candidate. This does not carry forward an action. Dormant sleep has zero cognitive cycles; after waking, the option is only reused if the current phase-1 witnessed route offers and funds exactly that motor proposal. Candidate expiration, real goal or plan invalidation, site changes, disagreement, adverse learned evaluation and Competition capacity removal invalidate it.
- A competing non-sleep winner drops the special marker and follows ordinary residual. This provides natural interruption rather than indefinitely locked attention.
- A negative current Stage8 evidence clears the marker. The ordinary accumulator update still operates and may completely erase support; no fabricated positive evidence is added.
- The established Competition inertia applies to the temporarily held informational intention only while it remains valid. It remains less than the native threshold and can never alone admit movement. Sleep retains its own autonomously selected priority.
- M11 snapshots serialize the marker only when present; older snapshots are byte-for-byte unchanged. Restore verifies the marker corresponds to a live goal-neutral one-step witnessed memory proposal. Its Q/history is never modified.

## Falsification gates

Software tests must prove unselected fallback exclusion, legitimate sleep preservation, negative evidence cancellation, expiration, interrupt by non-sleep choices, identical deterministic snapshot, and unchanged non-memory behavior. CI and isolated physically applied corridor WAL must then demonstrate that the marker resumes at waking without *increasing* invalid/unsafe movement or mortality. A physical out-of-sight multihop **arrival**, not a resumed candidate, is the navigation goal. Repeat paired four-world seeds and withheld seeds; compare oscillations, UC, food and water, consolidation, survival, and cold M11.

**NO-GO** remains in effect for complete autonomous distant return or general survival. Do not close issue or merge PR based only on software tests or proposal counts.
