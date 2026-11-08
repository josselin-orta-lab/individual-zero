# Stage 1 Candidate-H: post-contact relevance-gated fallback

Issue #1061. Baseline:
`9a06bcd3e68b1422a3f74687eaa926922ac198f9` (#1162).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ONLY.**

No World instance/generation/capture, no life, no evidence-branch read, no
runtime policy integration, no fresh study allocation, no selection,
validation, reserve exposure, reference adoption or Stage 2.

## Why

Candidate-H first-contact now passes its bounded software gate: support can be
paid first, relevance established, and all non-relevant states can fall back to
a fully paid P1.3 decision without retaining Candidate-F ordinary-policy drift.

The remaining ambiguity is **post-contact**. Once a drink effect has been
personally learned, Candidate-G currently:

1. computes the paid personal actionable frontier belief;
2. if that belief assigns any actionable-water probability `p_water > 0`,
   switches the entire decision to Candidate-F projection;
3. only then computes each frontier option's actual information value.

Thus post-contact activation still uses **support/actionability** as the trigger,
not demonstrated current decision relevance.

## Scope

This slice covers only a personally learned **beneficial drink effect** with
paid empirical branch support. Harmful/no-positive drink histories already
produce no actionable-water branch and therefore do not trigger the Candidate-F
post-contact path; they are authority controls, not Candidate-H fallback cases.

No recurrence proxy is used post-contact. No genomic omega is read.

## Frozen personal history

Reuse the established software fixture from
`tests/i3/test_reference_frontier_information_mind.py`, without constructing a
World:

- midpoint genome;
- personally learned:
  - wait `(0,-.2,-.4,.2,0)`;
  - move `(-2,-.2,-.4,0,0)`;
  - sleep `(3,-.35,-.4,.2,4)`;
  - drink `(-.5,-.2,+35,0,0)`;
- one retained personally seen water-bearing map cell at relative key `(9,9)`;
- one paid empirical generic drink branch `("boire", None)` with the same
  +35-water effect;
- no inherited or synthetic learned state.

The actionable belief must be
`COMPLETE_ACTIONABLE_PERSONAL_BELIEF`, expose an `ACTIONABLE_WATER` branch,
and read no omega or recurrence memory.

## Frozen body/horizon grid

Reuse the established #1101/#1146 80-state geometry:

- base body `(80,80,80,80,80)`;
- independently set each of the five channels to `20,30,40,50`;
- horizons `4,6,8,12`;
- 80 states total.

No state is selected from 56/57 or any live evidence.

## Frozen decision basis

One fixed frontier explorer basis is used:

`explore = (se_deplacer)`.

The post-contact frontier information outcome is exactly
`_water_outcomes(p_water, explore)` from the existing personal frontier path.

The same four ordinary plans used by #1161/#1162 are also scored:

1. `wait = (attendre)`;
2. `sleep = (dormir)`;
3. `move = (se_deplacer)`;
4. `move_wait = (se_deplacer, attendre)`.

This is a laboratory decision basis, not a motor policy.

## Stage A: paid post-contact relevance decision

For every state:

1. construct the personal-history Candidate-F model;
2. pay `paid_frontier_actionable_belief`;
3. derive `p_water` from that paid belief;
4. quote **one common Candidate-F forecast ceiling** covering:
   - the complete revealed-plan information matrix for the explorer;
   - all four ordinary plan scores;
5. use the single cognition-depleted forecast body implied by that ceiling;
6. compute:
   - frontier explorer `informed_value`;
   - frontier explorer `uninformed_value`;
   - information value;
   - all four ordinary Candidate-F scores.

Define two score sets under the **same Candidate-F geometry**:

- `WITH_INFORMATION`: explorer score = `informed_value`;
- `WITHOUT_INFORMATION`: explorer score = `uninformed_value`;
- ordinary scores identical in both sets.

## Frozen strict post-contact relevance rule

A state is **RELEVANT** only if all are true:

1. frontier `information_value > 1e-12`;
2. the top option set of `WITH_INFORMATION` differs from the top option set
   of `WITHOUT_INFORMATION`;
3. the explorer belongs to the `WITH_INFORMATION` top set.

Otherwise the state is **FALLBACK**.

Mere `p_water > 0`, positive information value without a top-set effect, or
an unchanged winner is not enough.

The rule is frozen before measurement.

## Stage B1: relevant state

If Stage A is RELEVANT:

- execute no fallback;
- retain the complete Candidate-F Stage-A score geometry;
- authorize no motor command in this software slice.

## Stage B2: fallback state

If Stage A is FALLBACK:

1. start from Stage A's **actual body after cognition**;
2. pay a complete P1.3 four-plan fallback over
   `wait/sleep/move/move_wait`;
3. score all four from one common P1.3 forecast body;
4. reuse no Candidate-F ordinary score;
5. record combined Stage-A + Stage-B work and physical bill.

If fallback cannot be fully funded, report `FALLBACK_UNFUNDED`; never retain
Candidate-F ordinary policy silently.

## Controls

For every funded fallback state:

### Same-body P1.3 control

Repeat the exact P1.3 four-plan scorer from the same Stage-A post-cognition body.
Candidate-H fallback scores/top set must be identical within `1e-12`.

### Pre-probe P1.3 descriptive control

Score the four ordinary plans from the original fixture body under P1.3.
Differences after the paid Stage-A cognition are descriptive physical-cost
effects, not projector contamination.

## Frozen software gate

Pass only if all are true.

### P0 personal-history/actionability identity

All 80 states use the frozen personal history, actionable-water belief is
complete with strict `0 < p_water < 1`, no omega/recurrence path is read, and
all Stage-A work stays within the common ceiling.

### P1 both relevance classes exist

At least one state is RELEVANT and at least one is FALLBACK. Otherwise this grid
cannot falsify the gated split.

### P2 complete fallback funding

Every FALLBACK state fully funds the complete P1.3 four-plan fallback.

### P3 fallback P1.3 identity

Every funded fallback state has score max error <= `1e-12` and identical top
set versus same-body P1.3.

### P4 relevant-path integrity

Every RELEVANT state executes zero fallback work, has strictly positive
information value and changes the Candidate-F top set exactly as required by the
frozen relevance rule.

### P5 exact physical accounting

Combined work equals Stage A + Stage B, all energy/vigilance bills are
finite/nonnegative, and the recomputed body after combined cognition equals the
reported body within `1e-12`.

### P6 authority boundaries

No World/life/evidence access, no omega, no recurrence proxy, no motor
authorization, no runtime registration.

Pass verdict:

`CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS`

Fail verdict:

`CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_FAIL`

No threshold or class definition may change after exposure.

## Descriptive outputs

Report:

- RELEVANT/FALLBACK counts;
- positive-information-but-FALLBACK count;
- top changes caused by information;
- fallback funded/unfunded;
- mean/max Stage-A and combined work/cost by class;
- fallback top changes versus pre-probe P1.3;
- exact state identities for all relevance decisions and pre-probe changes.

These do not alter P0-P6.

## Interpretation boundary

A PASS means only that post-contact actionability can be separated from current
decision relevance on this frozen personal-history grid, with all fallback
cognition physically paid.

A FAIL means stop this mechanism before runtime. Do not rescue it with a free
belief/probe, body reimbursement, altered relevance rule or selective fallback.

Even a PASS authorizes no runtime Candidate-H and no fresh live panel. Only if
both first-contact (#1162) and this post-contact gate pass may a **separate
unified runtime software-integration protocol** be proposed.

P1.3 remains reference. Candidate-G live remains closed. 56/57 remain exposed.
