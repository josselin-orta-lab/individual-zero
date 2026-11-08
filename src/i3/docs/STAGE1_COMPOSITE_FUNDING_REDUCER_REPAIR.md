# Stage 1 engineering gate: composite decision-funding reducer repair

**PROSPECTIVELY FROZEN SOFTWARE/ENGINEERING PROTOCOL. SYNTHETIC FIXTURES ONLY.
NO 58/59 REPLAY.**

## Problem

The frozen Candidate-H 58/59 DEVELOPMENT transport opened Worlds once and then
stopped while reducing the Candidate-H original with:

`ValueError: resource processing status disagreement`.

The generic revision reducer currently assumes every public decision funding
string is one of the four historical P1.3 statuses:

- `NO_PROCESSING_BUDGET`;
- `NO_FUNDED_SCORE`;
- `NO_FUNDED_MOTOR`;
- `FUNDED`.

Candidate-H can instead emit the composite public status
`NO_FUNDED_RELEVANCE_PROBE` when Stage A is incomplete. Its receipt also
contains the underlying `candidate_h_probe_funding`, and its observer outcome
already reflects that underlying funding class.

This gate asks whether the reducer can normalize that composite receipt
fail-closed without changing the life, runtime or exposed evidence.

## Scope

Allowed:

- synthetic dictionaries shaped like revision trace/resource-observer rows;
- `stage0_revision.py` helper changes;
- adversarial unit tests.

Forbidden:

- opening or replaying 58/59;
- reading the Candidate-H original as an acceptance input;
- changing `runtime.life`, Candidate-H cognition, World physics or the
  resource observer merely to make the reducer pass;
- weakening custody joins.

## Frozen normalization

Historical funding statuses keep their exact existing meaning.

One additional public composite status is recognized:

`NO_FUNDED_RELEVANCE_PROBE`

It is valid only when the same trace row contains
`candidate_h_probe_funding` equal to one of:

- `NO_PROCESSING_BUDGET`;
- `NO_FUNDED_SCORE`.

The normalized processing class is that nested probe funding status.

No other composite or unknown funding string is accepted.

The sidecar's `decision_funding` must still equal the trace
`info.funding` byte-for-byte. The sidecar and trace observer
`decision_outcome` must both equal the historical outcome implied by the
normalized processing class.

## Frozen synthetic fixtures

At minimum:

1. historical `FUNDED` P1.3 row;
2. historical `NO_PROCESSING_BUDGET` row;
3. composite `NO_FUNDED_RELEVANCE_PROBE` with nested
   `NO_PROCESSING_BUDGET`;
4. composite `NO_FUNDED_RELEVANCE_PROBE` with nested
   `NO_FUNDED_SCORE`;
5. composite row with missing nested funding;
6. composite row with illegal nested `FUNDED` or `NO_FUNDED_MOTOR`;
7. unknown public composite status;
8. disagreement between normalized class and either observer outcome;
9. disagreement between sidecar and trace public funding;
10. contradiction between normalized paid/unpaid status and work.

The synthetic reproducer must demonstrate that the legacy reducer rejects
fixture 3 or 4 with the same class of `resource processing status disagreement`
before the repair is applied.

## Engineering rules

### R0 — historical behavior unchanged

All existing `test_stage0_revision.py` tests pass unchanged.

Historical P1.3 and upper-cost-control reduction outputs are unchanged.

### R1 — exact synthetic reproduction

A frozen synthetic Candidate-H row reproduces the pre-repair disagreement
without any World/life/evidence access.

### R2 — narrow normalization

After repair, only the declared Candidate-H composite status is normalized, and
only through the declared nested incomplete probe funding classes.

### R3 — processing-paid semantics

- normalized `NO_PROCESSING_BUDGET` means `processing_paid=False` and
  decision work must be all zero;
- normalized `NO_FUNDED_SCORE` means `processing_paid=True` and must satisfy
  the existing paid base-block work check;
- composite probe failure admits no motor action.

No new definition of reacquisition or physical uptake is introduced.

### R4 — fail closed

Fixtures 5-10 must raise `ValueError` before any revision endpoint is
interpreted.

### R5 — custody joins unchanged

Action, parameter, chosen option, death causes, positions, body phases,
decision/learning work, phase accounting and uptake checks remain exactly as
strict as before.

### R6 — authority boundary

The gate imports no World and runs no life. It does not fetch the 58/59 evidence
branch. The exposed Candidate-H original is not an acceptance fixture.

## Frozen verdict

If R0-R6 pass:

`COMPOSITE_FUNDING_REDUCER_REPAIR_PASS`

Otherwise:

`COMPOSITE_FUNDING_REDUCER_REPAIR_DEFECT`

A PASS repairs the engineering reduction path only. It does not retroactively
complete 58/59, authorize a retry, or create an H1-H6 verdict from the archived
partial panel.

## Handoff after PASS

If this reducer gate and the separately frozen Candidate-I integration gate
both PASS, the repository may propose a **fresh DEVELOPMENT protocol** on new
conditions. 58/59 remain exposed and closed forever.
