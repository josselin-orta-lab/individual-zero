# Stage 1 engineering gate: branch-decision settlement receipt repair

**PROSPECTIVELY FROZEN SOFTWARE/ENGINEERING PROTOCOL. SYNTHETIC FIXTURES ONLY.
NO 60/61 REPLAY.**

## Trigger

The one-shot Candidate-I DEVELOPMENT 60/61 transport opened the frozen panel
once and stopped after five completed lives while generating
`stable-60-g902:personal_relevance_candidate_h_v1`.

The archived failure is:

`CognitiveFundingError: cognitive work exceeds available energy/vigilance`

at:

`learn_from_outcome -> branch_memory.observe -> debit_cognition(before, decision_work)`.

60/61 are exposed and closed. This protocol must not reopen them or use their
partial trajectories as an acceptance set.

## Root engineering question

A branch-memory record removes the already-paid decision cognition from the
observed body delta. Therefore the pair:

`(decision_start_body, decision_work)`

must describe the **same settlement interval**.

Single-phase P1.3 paths already satisfy this naturally because
`self.last.before` is the body from which the whole decision work was funded.

Multi-phase Candidate-H/I can violate that identity: the final decision may
store a post-Stage-A body in `self.last.before` while
`_branch_decision_work` contains Stage A + Stage B. Re-debiting the total work
from that already-depleted body can fail even though the real decision was
correctly prepaid from the original body.

The repair must make the settlement anchor explicit. It must not lower,
forgive, reimburse or reprice cognition.

## Frozen repair semantics

Every branch-storing decision owns a transient settlement receipt containing:

- `decision_start_body`: the exact body from which the associated
  `decision_work` was physically funded;
- `decision_work`: the exact paid work over that interval.

For ordinary one-phase reference decisions this is the ordinary decision-start
body plus ordinary decision work.

For Candidate-H and Candidate-I multi-phase first-contact decisions it is the
pre-Stage-A body plus the complete Stage-A + Stage-B work.

The ordinary `self.last` tuple remains untouched and continues to serve the
existing TD/effect learning semantics. Branch-memory settlement must not
silently redefine ordinary learning.

The settlement receipt is transient, per-decision state. It is cleared on a
new decision and consumed/cleared during learning. It may never persist across
decisions or births.

## Frozen synthetic reproducer

Construct a no-World fixture with:

- original body `B0 = (1.0, 50.0, 50.0, 50.0, 1.0)`;
- Stage-A work `WA = CognitiveWork(cycles=10)`;
- Stage-B work `WB = CognitiveWork(cycles=5)`;
- total `WT = WA + WB`;
- `B1 = debit_cognition(B0, WA)`.

Under BodyLaws v2:

- `WT` is affordable from `B0`;
- `WT` is not affordable from `B1`.

The legacy mismatched pair `(B1, WT)` must reproduce
`CognitiveFundingError` without importing World/life or evidence.

The repaired pair `(B0, WT)` must be accepted and must produce the same
branch delta as sequentially removing WA then WB from the physical transition.

No numbers in this fixture may be changed after the first repair run.

## Rules

### B0 — custody

Before interpretation:

- Candidate-I runtime v2 remains PASS;
- composite-funding reducer remains PASS;
- the durable 60/61 failure receipt remains
  `ENGINEERING_FAILURE_NOT_A_DEATH`;
- no J1-J7 verdict is inferred from 60/61.

### B1 — exact synthetic reproduction

Before applying the repair, the frozen mismatched synthetic pair
`(B1, WT)` reproduces the same failure class:
`CognitiveFundingError`.

No World, runtime life or evidence branch is needed.

### B2 — exact settlement pairing

After repair, branch storage validates and removes decision cognition using only
an explicit same-interval pair `(decision_start_body, decision_work)`.

It is a defect if branch storage falls back to a body from a different phase
when an explicit total-work receipt exists.

### B3 — no cognition forgiveness

The work value is unchanged. The repair may not:

- replace total work by Stage-B-only work merely to make it affordable;
- clip a cognitive bill;
- reimburse energy/vigilance;
- skip STORE_WORK;
- move work after death.

### B4 — ordinary P1.3 identity

ReferenceBranchMemoryMind ordinary one-phase decisions retain exact prior
behavior:

- same action/param;
- same decision work;
- same learning allocation;
- same branch delta;
- same RNG/state;
- same stored record count.

### B5 — Candidate-H/I multi-phase alignment

For synthetic Candidate-H and Candidate-I decisions:

- settlement start is the pre-Stage-A body;
- settlement work is the complete decision work;
- `self.last.before` may remain a later phase body;
- learning completes without a false affordability failure;
- stored branch delta is identical to a manually reconciled body/work receipt.

### B6 — prepaid storage remains exact

STORE_WORK is still purchased in `prepare_learning` and verified in
`learn_from_outcome`.

The verification suballowance must execute exactly STORE_WORK and must not debit
the real body a second time.

### B7 — fail closed on stale/missing receipts

A branch store must not proceed when:

- the settlement receipt is missing for a decision that claims multi-phase
  total work;
- the receipt belongs to a previous decision;
- start body or work has invalid type/shape;
- the declared work is genuinely unaffordable from its declared start body.

### B8 — upper-cost shadow semantics unchanged

The existing Candidate-F upper-cost shadow path already stores an explicitly
aligned P1.3 `before` body plus P1.3-only work. It must remain unchanged in
meaning and continue to pass its existing tests.

### B9 — authority boundary

The repair gate is software-only:

- no World construction;
- no `runtime.life`;
- no P2 ecology generation;
- no evidence-branch fixture;
- no 60/61 reducer replay.

## Frozen verdict

If B0-B9 pass:

`BRANCH_DECISION_SETTLEMENT_REPAIR_PASS`

Otherwise:

`BRANCH_DECISION_SETTLEMENT_REPAIR_DEFECT`

A PASS repairs an engineering custody defect only. It does not retroactively
complete 60/61, produce J1-J7, authorize a retry, select omega or advance
Stage 2.

## Handoff after PASS

60/61 stay permanently closed.

After a PASS, the next scientific step must use **new conditions** and a newly
frozen protocol. The 60/61 partial originals may be retained as engineering
evidence only, never as calibration or acceptance data.
