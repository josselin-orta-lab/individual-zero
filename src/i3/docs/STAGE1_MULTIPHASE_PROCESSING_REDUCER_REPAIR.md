# Stage 1 multi-phase processing reducer repair

**PROSPECTIVELY FROZEN SOFTWARE-ONLY REPAIR. NO WORLD. NO LIFE RUNNER.
NO 64/65 ACCEPTANCE FIXTURE.**

## Motivation

The one-shot Candidate-I 64/65 panel stopped after 35 admitted reductions. The
36th original completed normally but the Stage-0 revision join rejected one
valid sequential Candidate-H receipt.

The archived forensic shape is:

- a complete, paid Candidate-H Stage A;
- a zero-work P1.3 Stage B;
- public final funding `NO_PROCESSING_BUDGET`;
- total decision work = Stage A + Stage B, therefore nonzero.

R-depletion-v1 says the public processing flag belongs to the paid local
perception block of the final P1.3 controller. Earlier cognition remains charged
physically but must not masquerade as P1.3 processing.

This repair generalizes the ownership distinction already frozen for the
upper-cost control. It must not reinterpret 64/65 behavior.

## Scope

Allowed changes:

- `src/i3/lab/stage0_revision.py`;
- focused software tests / a dedicated synthetic characterization;
- documentation describing the reducer ownership rule.

Forbidden changes:

- Candidate-H or Candidate-I decision code;
- runtime/life;
- ResourceObserver;
- BodyLaws or cognitive prices;
- omega/RMS or any scientific score;
- P2 ecology/world generation;
- J1-J7;
- any 64/65 original, trace or result as an acceptance fixture.

No World, life runner or evidence branch may be imported by the repair gate.

## Ownership model

A revision row has two distinct quantities:

1. **total decision work**: every paid cognitive block physically charged in the
   decision phase;
2. **processing-owner work**: the block whose public funding status determines
   whether local P1.3 processing occurred for R-depletion-v1.

The repair must authenticate the processing owner, never infer it from the
amount of total work.

### Historical one-owner policies

Unchanged:

- processing-owner work = total decision work;
- `NO_PROCESSING_BUDGET` requires owner work zero;
- later funding statuses require the existing paid processing base.

### Upper-cost control

Unchanged:

- total work = shadow + reference choice;
- processing-owner work = `reference_choice_work`;
- paid shadow work never changes R-depletion processing status.

### Candidate-H complete final decisions

For routes `P1.3_FINAL` and `CANDIDATE_F_FINAL` only:

- authenticate `candidate_h_stage_a_work`;
- authenticate `candidate_h_stage_b_work`;
- authenticate `candidate_h_total_work`;
- require Stage A + Stage B = total = physical decision-phase work;
- require the declared Candidate-H body settlement to match the phase receipt;
- processing-owner work = **Stage B**.

Stage A remains fully charged in Stage-0 energy.

### Candidate-I complete first-contact finals

For routes `P1.3_BASE_FINAL` and `INFORMATION_FINAL` only:

- authenticate `candidate_i_stage_a_work`;
- authenticate `candidate_i_stage_b_work`;
- authenticate `candidate_i_total_work`;
- require Stage A + Stage B = total = physical decision-phase work;
- require the Candidate-I body settlement to match the phase receipt;
- processing-owner work = **Stage B**.

### Candidate-I post-contact

For `POST_CONTACT_CANDIDATE_H`:

- require `candidate_i_first_contact_omega_used is False`;
- use the authenticated Candidate-H Stage-A/Stage-B receipt above;
- processing-owner work = Candidate-H Stage B.

### Probe-unfunded composite status

The existing `NO_FUNDED_RELEVANCE_PROBE` normalization from #1172 is
unchanged. Its nested incomplete Stage-A status remains authoritative.

Do not broaden the accepted public status vocabulary.

## Frozen synthetic fixtures

The gate builds detached trace/ResourceObserver-shaped dictionaries only.

No fixture may call `run_life`, instantiate World, read P2 ecology or import an
evidence branch.

### S0 ordinary historical rows

Preserve:

- FUNDED with ordinary base work -> accepted, processing paid;
- NO_PROCESSING_BUDGET with zero total work -> accepted, processing unpaid;
- NO_PROCESSING_BUDGET with nonzero ordinary work -> rejected.

### S1 upper-cost rows

Preserve the existing authenticated shadow/reference split and all adversarial
fail-closed checks.

### S2 Candidate-H sequential no-processing

Synthetic exact logical shape:

- route `P1.3_FINAL`;
- Stage A complete and nonzero;
- Stage B zero;
- total = Stage A;
- public `NO_PROCESSING_BUDGET`;
- no action.

The legacy reducer must reject this synthetic shape. The repaired reducer must
accept it and emit `processing_paid=False`.

### S3 Candidate-H paid Stage B

Same authenticated shape with Stage B containing the normal paid processing
base and public later funding. Require `processing_paid=True`.

### S4 Candidate-I first-contact sequential no-processing

Build both `P1.3_BASE_FINAL` and `INFORMATION_FINAL` synthetic receipts with
nonzero Stage A, zero Stage B and public `NO_PROCESSING_BUDGET`.

Require acceptance with `processing_paid=False`.

### S5 Candidate-I post-contact sequential no-processing

Build `POST_CONTACT_CANDIDATE_H` with first-contact omega explicitly unused,
nonzero Candidate-H Stage A, zero Stage B and public
`NO_PROCESSING_BUDGET`.

Require acceptance with `processing_paid=False`.

## Frozen rules

### M0 — custody

- 64/65 remain exposed and closed;
- #1195 remains unmerged;
- no J1-J7 verdict exists;
- no archived 64/65 original is an acceptance input.

### M1 — exact legacy reproduction

The current reducer rejects S2 for exactly
`processing status contradicts paid base block`.

### M2 — total work remains physically authoritative

For every accepted multi-phase receipt:

- Stage A + Stage B = declared total;
- declared total = runtime decision-phase work;
- no work is hidden or reimbursed;
- Stage-0 energy semantics are unchanged.

### M3 — processing ownership is explicit

Only the authenticated owner block is tested against the public funding status:

- ordinary: total;
- upper-cost: reference choice;
- Candidate-H complete final: Stage B;
- Candidate-I complete first-contact final: Stage B;
- Candidate-I post-contact: Candidate-H Stage B.

No route/status fallback guessing.

### M4 — R-depletion-v1 semantics unchanged

For S2/S4/S5:

- `processing_paid=False`;
- earlier paid Stage A must not advance the paid-processing clock.

For S3 and equivalent later-funded Stage B:

- `processing_paid=True`.

### M5 — public motor authority unchanged

`NO_PROCESSING_BUDGET` and composite incomplete statuses admit no action.

`FUNDED` continues to require an admitted action under the existing reducer
contract.

### M6 — body and phase custody

Reject any receipt with:

- Stage A/B/total arithmetic mismatch;
- total/phase-work mismatch;
- declared post-cognition body disagreement;
- missing or malformed phase work;
- unsupported route;
- Candidate-I post-contact claiming first-contact omega use.

### M7 — status/outcome custody

Preserve exact agreement between:

- public info funding;
- resource-sidecar funding;
- observer outcome;
- resource-sidecar outcome.

Existing composite nested-status validation remains fail-closed.

### M8 — historical regressions

All current Stage-0 revision tests, upper-cost tests and composite-funding
R0-R6 tests remain green without weakening their negative controls.

### M9 — authority boundary

The repair:

- opens zero worlds;
- runs zero lives;
- changes no cognition or physics;
- cannot complete 64/65;
- cannot authorize a retry;
- cannot create J1-J7 evidence;
- cannot advance Stage 2.

## Frozen verdict

If M0-M9 all pass:

`MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS`

Otherwise:

`MULTIPHASE_PROCESSING_REDUCER_REPAIR_DEFECT`

Do not change the fixtures or rules after implementation begins merely to make
the gate pass.

## After PASS

A read-only forensic check may apply the repaired reducer to the already
archived 36th 64/65 original and confirm that the specific join no longer
throws. That confirmation is not an acceptance criterion and does not admit the
life into a J1-J7 aggregate.

Before another fresh Candidate-I panel is proposed, the lifecycle preflight must
gain an explicit synthetic case for **paid Stage A + Stage-B
NO_PROCESSING_BUDGET** reducer custody, so this boundary cannot again be left to
chance in a fresh world.
