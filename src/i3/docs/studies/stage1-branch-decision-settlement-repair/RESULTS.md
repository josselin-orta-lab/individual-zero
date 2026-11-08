# Branch-decision settlement repair: software PASS

Protocol:
[STAGE1_BRANCH_DECISION_SETTLEMENT_REPAIR.md](../../STAGE1_BRANCH_DECISION_SETTLEMENT_REPAIR.md).

**SOFTWARE/ENGINEERING ONLY. ZERO WORLD/LIFE.**

Frozen verdict:

`BRANCH_DECISION_SETTLEMENT_REPAIR_PASS`

Confirmed on implementation head
`7362628afab7f7231e17a9dac278a58d6297a845` by GitHub Actions run
`42505811626` under Python 3.11 and 3.12. Python 3.11 ran 941 I3 tests plus
the repository navigation check successfully.

Merged repair commit:
`5ee25b3b0f39050321b0b5c6147bdae0e3e68ec5`.

## Frozen rules

All B0-B9 pass:

- B0 custody / no 60/61 verdict: PASS;
- B1 exact synthetic reproduction: PASS;
- B2 exact settlement pairing: PASS;
- B3 no cognition forgiveness: PASS;
- B4 ordinary P1.3 identity: PASS;
- B5 Candidate-H/I multi-phase alignment: PASS;
- B6 prepaid STORE_WORK exactness: PASS;
- B7 missing/stale receipt fail-closed: PASS;
- B8 upper-cost shadow semantics unchanged: PASS;
- B9 authority boundary: PASS.

The gate also reports:

`legacy_mismatch_reproduced = true`.

The old failure is therefore reproducible without a World. The frozen synthetic
pair deliberately makes complete Stage-A+Stage-B work affordable from the true
decision start body but unaffordable when incorrectly re-debited from the
already Stage-A-depleted body.

## Repair

Branch-memory custody now carries one transient per-decision settlement pair:

`(decision_start_body, decision_work)`.

The body and work always describe the same already-paid decision interval.

For ordinary one-phase reference decisions this is the ordinary start body and
ordinary decision work.

For Candidate-H and Candidate-I multi-phase first-contact decisions this is the
pre-Stage-A body and complete Stage-A + Stage-B work.

`self.last` remains unchanged and retains its existing TD/effect-learning
meaning. The repair therefore does not redefine ordinary learning.

The settlement receipt is cleared at the next decision and consumed atomically
when learning prepares branch storage. A missing or stale receipt cannot become
branch-learning authority.

## What did not change

The repair does **not**:

- reduce Stage-A + Stage-B work to Stage-B-only work;
- clip a cognitive cost;
- reimburse energy or vigilance;
- move cognition after death;
- change Candidate-H/I scores, relevance or motor rules;
- change the Candidate-F upper-cost shadow's local P1.3 receipt semantics.

STORE_WORK remains separately prepaid and exactly verified.

## 60/61 remains closed

The PASS does not repair the already exposed panel retrospectively.

60/61 remain permanently closed after five completed lives and the archived
`ENGINEERING_FAILURE_NOT_A_DEATH`. No J1-J7 verdict exists and no retry,
resume, replacement seed or reduction of the partial lives is authorized.

A new lived comparison must use fresh conditions prospectively frozen after
this result.
