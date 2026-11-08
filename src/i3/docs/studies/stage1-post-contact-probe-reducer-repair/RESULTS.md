# Candidate-I post-contact probe reducer repair: PASS

Protocol:
[STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md](../../STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md).

**SOFTWARE ONLY. ZERO FRESH LIVES. NO 66/67 REPLAY.**

Frozen verdict:

`POST_CONTACT_PROBE_REDUCER_REPAIR_PASS`

Authority:

- tested source: `78d09c98127fb55aebb5eca729fa4ce4795d007a`;
- GitHub Actions: `42533323063`;
- merged implementation:
  `4bcb2f28488f289625558960cd93c7c65c69b107`;
- Python 3.11 / 3.12: PASS;
- Python 3.11: **1031 tests** plus repository navigation.

## Q0-Q9

All frozen rules pass.

The synthetic reproducer preserves the exact pre-repair failure:

`ValueError: invalid Candidate-I post-contact processing receipt`.

The repaired reducer now has one Candidate-H processing-ownership definition,
used by both direct Candidate-H and Candidate-I
`POST_CONTACT_CANDIDATE_H`.

### Candidate-H complete finals

For nested/direct:

- `P1.3_FINAL`;
- `CANDIDATE_F_FINAL`.

Processing ownership remains Stage B, with existing complete funding, phase,
body and total-work authentication.

### Candidate-H PROBE_UNFUNDED

For nested/direct `PROBE_UNFUNDED`:

- only `NO_FUNDED_SCORE` and `NO_PROCESSING_BUDGET` are accepted as nested
  incomplete funding;
- Stage B must be exactly zero;
- Stage A + Stage B must equal total decision work;
- the Candidate-H body-after-cognition receipt must match runtime settlement;
- processing ownership is Stage A.

Consequently:

- nested `NO_FUNDED_SCORE` is processing-paid and must contain the existing
  paid base block;
- nested `NO_PROCESSING_BUDGET` is processing-unpaid and therefore Stage A is
  zero;
- no motor authority is admitted.

Total physical cognition is unchanged. No work is forgiven, moved or repriced.

## Regression custody

The PASS also preserves:

- composite funding R0-R6;
- multi-phase processing M0-M9;
- lifecycle custody v2 V0-V8;
- complete Candidate-I post-contact semantics;
- direct Candidate-H semantics.

Malformed nested funding, nonzero Stage B on `PROBE_UNFUNDED`, phase-total
mismatch, body mismatch, wrong post-contact source, omega use, unknown H route
and public/observer disagreement all fail closed.

## Scientific boundary

This PASS does not:

- retroactively admit the eleventh 66/67 original;
- complete 66/67;
- create J1-J7 evidence;
- authorize a 66/67 retry;
- change Candidate-I/H policy, omega/RMS, cost, physics or resource semantics;
- authorize selection, validation, reserve or Stage 2.

66/67 remain permanently exposed and closed.

## Handoff

Before another fresh Candidate-I DEVELOPMENT proposal, run a prospectively
frozen successor lifecycle stress using actual production Candidate-I
post-contact decisions.

That stress must force both legitimate nested Candidate-H
`PROBE_UNFUNDED` classes:

- `NO_PROCESSING_BUDGET`;
- `NO_FUNDED_SCORE`;

and pass the actual receipts through the repaired Stage-0 reducer.

No exposed original may be used as an acceptance fixture.
