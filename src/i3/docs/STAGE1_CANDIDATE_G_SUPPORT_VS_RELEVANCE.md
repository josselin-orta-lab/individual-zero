# Stage 1 Candidate-G: support versus decision relevance

Issue #1061. Baseline:
`975aaf479a4b2f029f3506a8daa283288733d783` (#1160).

**DECLARED BEFORE IMPLEMENTATION. SOFTWARE DIAGNOSTIC ONLY.**

No World, no life, no fresh study allocation, no runtime policy change, no
adoption. P1.3 remains reference. Development 56/57 are exposed evidence and
are not read by this diagnostic.

## Why

The frozen 56/57 pilot closed the Candidate-G live path. It nevertheless
separated two facts:

- decision-local Candidate-F projection is much cheaper than running Candidate-F
  broadly;
- Candidate-G still fails its continuation rule and remains behaviorally weak.

A structural ambiguity remains in Candidate-G itself.

The current activation rule switches **every option score in a decision** to
the Candidate-F projector as soon as a paid personal information path is
supported. It does this before the expensive information matrix has established
whether the epistemic trial is actually strictly advantageous.

The live evidence contains a concrete symptom: one exposed Candidate-G life had
112 information-active decisions and zero positive information options. That
observation motivates this diagnostic but supplies no fixture or threshold.

Question:

**Can mere support for an information path change ordinary option ordering in
states where the information trial is not strictly decision-relevant?**

## Frozen fixtures

Reuse the existing #1146 Candidate-G software grid exactly:

- midpoint genome;
- personal generic move/wait/sleep effects from
  `stage1_candidate_g_reference_recurrence_falsifier`;
- paid personal recurrence gaps 2/6/10;
- body base `(80,80,80,80,80)`;
- each of the five body channels independently set to
  `20, 30, 40, 50`;
- horizons `4, 6, 8, 12`;
- 80 states total;
- no genomic omega.

For the information kernel, use the canonical Candidate-F projector exactly as
in #1156. Do not change its cost, branches, prior or recurrence probability.

## Frozen ordinary plan set

In every state, independently score the same four already-known, generic plans:

1. `wait = (attendre)`;
2. `sleep = (dormir)`;
3. `move = (se_deplacer)`;
4. `move_wait = (se_deplacer, attendre)`.

These are not proposed actions for a live policy. They are a fixed laboratory
basis for asking whether the projector switch changes ordinary score ordering.

Score the entire four-plan set twice from the identical body:

- P1.3 reference simulation / `chunk_end`;
- canonical Candidate-F simulation / `event_local_quadratic4`.

Use fresh paid `CognitiveBudget` objects for every plan score. Report actual
work; do not reimburse or normalize it away.

## Frozen state classes

For each of the 80 states, first run the canonical personal-recurrence
information kernel.

A state is **strict epistemic selected** only when all are true:

- `TRIAL` is among `target_node_best_choices`;
- `trial_information_value > 1e-12`;
- `trial_advantage > 1e-12`.

Every other state is **support-only nonselected** for this diagnostic. The
personal recurrence support remains present in all states; the label means that
support exists but does not produce a strictly advantageous epistemic trial.

No class boundary may be changed after execution.

## Reported observables

For all states and separately for strict-selected versus support-only
nonselected:

- state count;
- reference top ordinary plan set;
- Candidate-F top ordinary plan set;
- whether the top set changes;
- number of unique-winner changes;
- winner counts by ordinary plan;
- maximum absolute change in any pairwise ordinary score gap;
- mean and maximum paid simulated steps for scoring the four plans in each arm.

Also report:

- strict epistemic selected count;
- support-only nonselected count;
- canonical kernel declined count;
- canonical kernel mean simulated work;
- exact state identities for every ordinary top-set change.

## Frozen interpretation

This diagnostic has **no promotion gate**.

Classify only:

### `SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT`

if at least one support-only nonselected state changes its ordinary top plan set
between P1.3 and Candidate-F projection.

### `NO_SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_ON_GRID`

if none does.

A positive classification means only that Candidate-G's support-triggered
projector switch can alter ordinary choice geometry even when its epistemic
trial is not strictly advantageous. It would justify designing a later
software-only relevance/fallback candidate.

A negative classification means this mechanism is not the ordinary-policy lever
on the frozen grid.

Neither classification authorizes:

- modifying R5 or reinterpreting #1160;
- tuning on 56/57;
- a new live panel;
- a Candidate-H implementation in the same slice;
- selection, validation, reserve, reference adoption or Stage 2.

## Boundaries

- no World import;
- no runtime/life import;
- no evidence-branch read;
- no hidden-world facts;
- no action-specific survival rule;
- no omega;
- no free or reimbursed cognition;
- no change to the reference projector or canonical Candidate-F projector.
