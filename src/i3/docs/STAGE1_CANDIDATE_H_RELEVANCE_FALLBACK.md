# Stage 1 Candidate-H: paid relevance-gated fallback

Issue #1061. Baseline:
`e17a3114ff124d95ee330f3dc2251009a31d1b43` (#1161).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ONLY.**

No World, no life, no fresh study allocation, no runtime policy integration, no
selection, validation, reserve exposure, reference adoption or Stage 2.

## Why

#1161 established:

`SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT`.

On the frozen #1146 grid, personal recurrence support exists in all 80 states,
but only 24 strictly select the epistemic trial. In the other 56 support-only
states, switching the whole decision to Candidate-F projection changes the
ordinary top set in 20 states and the unique winner in 4.

Candidate-G therefore switches projection too early. It treats **support for an
information path** as if support already established **current decision
relevance**.

The next question is strictly narrower:

**Can the individual pay to establish relevance first, then fall back to a full
P1.3 ordinary decision when the epistemic trial is not strictly advantageous?**

This is Candidate-H only as a laboratory mechanism. It is not a runtime mind.

## Scope: first-contact recurrence only

The live 56/57 pattern motivating this work included pre-contact
personal-recurrence activation. This slice therefore covers **first contact
only**:

- no personally learned `boire` effect;
- personal recurrence support from gaps 2/6/10;
- omega fixed to zero and not read;
- canonical Candidate-F projection for the relevance probe;
- no post-contact actionable-belief mechanism.

Post-contact relevance gating is a separate future question and cannot be
silently inferred from this result.

## Frozen fixtures

Reuse the exact #1146 80-state Candidate-G grid:

- midpoint genome;
- generic personally learned move/wait/sleep effects;
- recurrence gaps 2/6/10;
- base body `(80,80,80,80,80)`;
- each of five channels independently at `20,30,40,50`;
- horizons `4,6,8,12`.

The relevance probe is the canonical #1156 first-contact
`paid_water_personal_recurrence_value` under
`candidate_f/event_local_quadratic4`, with explicit personal recurrence and
`omega=0`.

It must reproduce the canonical kernel before Candidate-H can be interpreted:

- 80 evaluated;
- 24 strict epistemic selected;
- 56 support-only nonselected;
- 40 declines;
- mean simulated work 470.05;
- zero work-ceiling violations.

## Strict relevance rule

A state is **RELEVANT** only if all are true:

- `TRIAL` is in `target_node_best_choices`;
- `trial_information_value > 1e-12`;
- `trial_advantage > 1e-12`.

Otherwise it is **FALLBACK**.

The rule is frozen. Mere recurrence support, positive revelation value, or
nonzero information value is insufficient.

## Candidate-H two-stage mechanism

### Stage A: relevance probe

Starting from the fixture body, execute the exact canonical Candidate-F
first-contact kernel with a real `CognitiveBudget`.

The probe's actual work is paid. Its `body_after_computation` is the physical
starting body for Stage B when fallback is required.

The probe cannot authorize a motor command.

### Stage B1: relevant state

If Stage A is RELEVANT:

- no fallback computation is executed;
- Candidate-H reports `CANDIDATE_F_RELEVANT`;
- the canonical probe result is retained unchanged;
- this slice does not execute Competition or a motor action.

### Stage B2: fallback state

If Stage A is FALLBACK:

1. Start a fresh cognitive phase from Stage A's actual
   `body_after_computation`.
2. Score exactly the frozen ordinary plan basis from #1161:
   `wait`, `sleep`, `move`, `move_wait`.
3. Use P1.3 `reference/chunk_end` for **every** fallback plan.
4. Quote a common fallback forecast ceiling before scoring all four plans.
5. Score every fallback plan from the same forecast body after that ceiling.
6. Pay all actual reference simulations. No result from the Candidate-F probe
   is reused as an ordinary score.
7. Record combined Stage-A + Stage-B work and physical bill.

If Stage B cannot be funded, the state is
`FALLBACK_UNFUNDED`. It is never silently converted to a Candidate-F decision.

## Controls

For every FALLBACK state, compute two read-only controls:

### Same-body reference control

From the exact Stage-A `body_after_computation`, run the same P1.3 four-plan
fallback scorer on a fresh budget. Candidate-H fallback scores and top set must
be numerically identical to this control.

This checks implementation identity, not scientific benefit.

### Pre-probe P1.3 descriptive control

Score the four ordinary plans from the original fixture body under P1.3. Report
whether the paid relevance probe plus fallback changes the top set relative to
that pre-probe control.

This difference is allowed and descriptive because cognition itself is physical.
It must not be mislabeled projector contamination.

## Work accounting

Report separately:

- Stage-A work;
- Stage-B fallback work;
- combined work;
- energy/vigilance bill of each phase and combined;
- fallback funded/unfunded;
- fallback common forecast ceiling;
- final remaining body.

No free memoization, reimbursement or waived probe is allowed.

## Frozen software gate

Candidate-H passes this **first-contact software feasibility gate** only if all
are true:

### H0 canonical identity

The Stage-A kernel exactly reproduces 24 RELEVANT / 56 FALLBACK / 40 declines
and zero work-ceiling violations.

### H1 complete fallback funding

All **56/56** FALLBACK states can fund the complete four-plan P1.3 fallback.

### H2 fallback reference identity

For every funded FALLBACK state:

- every ordinary score matches the same-body P1.3 control within `1e-12`;
- the top set is exactly identical.

### H3 relevant-path preservation

All 24 RELEVANT states execute zero Stage-B fallback work and retain the
canonical Stage-A selected-state identity.

### H4 physical accounting

Every combined work receipt is exactly the sum of its phases, every bill is
finite/nonnegative, and no phase exceeds the available energy/vigilance.

### H5 authority boundaries

No omega read, no World instance/generation/capture, no runtime/life execution,
no motor authorization and no evidence-branch read.

Pass verdict:

`CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS`

Fail verdict:

`CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_FAIL`

No threshold may be changed after execution.

## Required descriptive outputs

In addition to H0-H5, report:

- mean/max combined simulated steps for RELEVANT and FALLBACK states;
- mean/max combined energy/vigilance bill;
- number of fallback top-set changes versus **pre-probe** P1.3;
- exact identities of those changes;
- how many of #1161's 20 support-only projector-drift states return to their
  pre-probe P1.3 top set;
- how many do not, due solely to the paid probe changing the body before
  fallback.

These outputs do not affect the frozen gate.

## Interpretation

A PASS means only that **support can be separated from relevance without
smuggling Candidate-F ordinary policy into non-relevant first-contact states**,
while paying the extra cognition.

A FAIL means this two-stage mechanism is not fundable or not reference-faithful
even in software. Do not rescue it with a free probe, body reimbursement,
changed threshold or selective fallback.

Even a PASS does not authorize:

- a runtime Candidate-H mind;
- post-contact generalization;
- a fresh World/life panel;
- reuse of 56/57;
- selection, validation, reserve, adoption or Stage 2.

P1.3 remains reference.
