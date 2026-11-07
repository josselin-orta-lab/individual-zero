# Stage 1 ω: genome-v4 to Candidate-F first-contact wiring

Issue #1061. Baseline:
`6cd7ed3d6d91fdf971f28b9873031abdcb6ab86c`.

**OPT-IN COGNITIVE WIRING ONLY. NO LIVE DECISION POLICY.**

## Prerequisites

- #1125: the explicit-omega Candidate-F falsifier passes and shows capacity;
- #1126: personal post-contact histories can override the inherited first-contact
  disposition;
- #1127: omega is the final, symmetric genome-v4 gene, but current cognition is
  still omega-blind.

This slice removes the last laboratory injection of `omega=...` from the
individual-side interface.

## Adapter

`GenomicOmegaCandidateFMind` is an explicit experimental subclass of
`ReferenceBranchMemoryMind`.

At birth it:

1. receives an ordinary current v4 genome;
2. fixes `simulation_mode="candidate_f"`;
3. fixes `projection_accounting="event_local_quadratic4"`;
4. reads `genes["omega"]` once into `first_contact_omega`;
5. owns the ordinary paid `ReferenceBranchMemory`.

It does not override `decide`, `prepare_learning` or
`learn_from_outcome`.

The only new method,
`paid_water_first_contact(...)`, invokes the existing
`paid_water_one_future_opportunity_value` with:

- the adapter itself as the Candidate-F model;
- its **own** branch memory;
- `omega=self.first_contact_omega`.

There is no `omega` argument in the method API, so the caller cannot replace
the inherited value at evaluation time.

## Frozen equivalence gate

The adapter is compared against the already-frozen explicit-omega #1125
falsifier.

Use all:

- 6 omega arms;
- 80 states per arm;
- same personal memory;
- same explorer prefix;
- same continuation;
- same horizons;
- same Candidate-F projector.

Total: **480 state evaluations**.

For every state require exact equality of:

- funded/unfunded status;
- target-node choices;
- information value;
- trial advantage;
- water-revelation advantage;
- actual work;
- forecast-work ceiling.

A mismatch is a wiring failure. No tolerance or retuning is permitted because
both paths call the same existing kernel.

## Behavioral boundary

This is still not a live policy.

Reference `Mind` and `ReferenceBranchMemoryMind` remain omega-blind.

The adapter does not alter ordinary `decide`; therefore the inherited
disposition has no effect unless a future experimental first-contact decision
policy explicitly calls the paid adapter method.

Personal post-contact modules remain omega-free.

## Gate

Pass verdict:

`GENOMIC_OMEGA_WIRING_EXACTLY_REPRODUCES_FROZEN_EXPLICIT_OMEGA`.

A pass means the inherited gene is connected to the exact software mechanism
already falsified in #1125, without an external parameter injection.

It does **not** authorize:

- a live/world run;
- a `decide` override;
- ADR-0015 selection;
- reference adoption;
- I3 registration.

The next slice, if this passes, is the smallest opt-in decision-policy
integration that uses this method while preserving P1.3 repertoire, Competition
and Action Control. That policy must be software-tested before any fresh world
allocation.
