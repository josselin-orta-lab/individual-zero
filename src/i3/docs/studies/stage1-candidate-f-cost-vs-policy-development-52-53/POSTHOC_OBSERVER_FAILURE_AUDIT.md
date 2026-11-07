# 52/53 post-hoc observer failure audit

**READ-ONLY AUDIT OF ARCHIVED ORIGINALS. ZERO NEW LIVES.**

Source: run `42422888044`, artifact `13593974371`, evidence commit
`60c5ae22c0b381865ec81678015c41efc1b9d975`.

## Exact failing state

Original: `life-11.json.gz`.

Identity:

`stable-53-g902:candidate_f_shadow_upper_cost_reference_controller_v1`.

The first and only trace step that has P1.3
`funding=NO_PROCESSING_BUDGET` with nonzero total decision work is step 177.

At that boundary:

```text
body before decision:
  [0.1384288541973714, 42.20257924678755, 43.99999999999957,
   100.0, 95.712]

Candidate-F shadow work:
  cycles=3
  memory_items=347
  simulated_steps=0
  replays=0

P1.3 reference-choice work:
  all zero

total physical decision work:
  exactly Candidate-F shadow work

body after total debit:
  [0.009028854197371372, 42.20257924678755, 43.99999999999957,
   100.0, 95.562]

P1.3 funding status:
  NO_PROCESSING_BUDGET

physical action:
  none

sequential settlement audit gap:
  0.0
```

The upper-cost receipt authenticates:

- `motor_authority=P1.3_REFERENCE_ONLY`;
- `candidate_motor_authority=false`;
- `settlement_authority=CUMULATIVE_V2_PHASE_START_BODY`;
- `total_work = candidate_shadow_work + reference_choice_work`.

Across all 286 decisions in that life, the upper-cost work-sum audit has zero
mismatches and maximum sequential-settlement gap
`1.4210854715202004e-14`.

## Why Stage-0 revision rejected it

The historical revision join performs:

```text
paid = funding != NO_PROCESSING_BUDGET
work = phases["decision"]["work"]

if not paid and any(work.values()):
    fail
```

That assumes the public funding status describes every computation in the
decision phase.

For the upper-cost control it describes only whether **P1.3**, the motor actor,
could buy its own processing block after paid shadow cognition.

The correct policy-specific validation is therefore:

```text
processing_work = reference_choice_work   # upper-cost control only
processing_work = total_decision_work     # ordinary policies

processing_paid <=> P1.3 funding != NO_PROCESSING_BUDGET
```

The total physical work must still remain independently authenticated by the
runtime/energy/upper-cost receipts.

## Endpoint semantics do not change

The R-depletion endpoint asks whether the individual could process the local
absence observation before later reacquisition.

In this control the individual whose behavior is under test is P1.3. Candidate-F
shadow cognition is a paid causal burden but has no motor or common-state
authority.

Therefore a step where the shadow was paid but P1.3 could not fund processing
must remain:

`processing_paid = false`.

It must **not** be reclassified as paid simply because total phase work is
nonzero.

## Required software correction

The correction must be narrow and fail-closed:

- detect only the explicit upper-cost receipt schema/policy;
- authenticate its P1.3-only motor authority;
- require total work to equal shadow + reference work;
- use `reference_choice_work` solely for the historical processing-base
  consistency check;
- retain total work for all physical billing/accounting;
- leave all ordinary-policy Stage-0 semantics byte-equivalent.

A regression test should reproduce the archived step-177 shape exactly:
nonzero shadow work, zero P1.3 work, public
`NO_PROCESSING_BUDGET`, no action, and successful revision-event join with
`processing_paid=false`.

No 52/53 original may be rerun to verify this fix.
