# Stage 1 — carried food: future-reuse characterization results

**Verdict under the frozen rule: `BOUND_NOT_CAUSAL`.** Representing up to eight
carried future uses never improves the meal's raw rank (0/27 at every `n`) and
leaves the raw-top-by-base count at 15/27. The one-reuse bound of #1102 does not
explain why carried-food information is decision-neutral. This direction is
closed for carried food.

Protocol: [STAGE1_CARRIED_FOOD_REUSE_CHARACTERIZATION.md](../../STAGE1_CARRIED_FOOD_REUSE_CHARACTERIZATION.md),
frozen at `254ac12`, Amendment 1 committed at `d160563` before any metric.
Executed once. Software only: **no World, no life, no study index**. Data:
[characterization.json](characterization.json). Label
`DESCRIPTIVE_NOT_COST_MATCHED` (as #1103).

## Frozen metrics (27-state #1103 grid)

| Carried units `n` (repeats `n−1`) | Positive information | Max information | Candidate raw-top by base | Meal base-rank improved | Meal total-rank improved | P1.3 chose meal |
| --- | --- | --- | --- | --- | --- | --- |
| Mixed 2 (1) | 18 | 0.126 | 15 | **0** | **0** | 24 |
| Mixed 3 (2) | 18 | 0.134 | 15 | **0** | **0** | 24 |
| Mixed 5 (4) | 18 | 0.139 | 15 | **0** | **0** | 24 |
| Mixed 9 (8) | 17 | 0.148 | 15 | **0** | **0** | 24 |
| Harmful 2–9 | 12 | 0.132 | 15 | 0 | 0 | 18 |
| One unit (control) | 0 | 0.0 | — | — | — | — |

`n = 2` reproduces the #1103 audit exactly. Information value saturates: eight
represented uses raise the maximum by 17% over one. Beyond the units the body
can use, eating more relieves nothing and the toxic branch keeps its cost.

**Paid kernel work** (mean per state, mixed history): `n = 2` 11 cycles, 29.7
simulated steps, 96 memory items. At `n = 9`: 3.55×, 4.78× and 4.5×. Every plan
cell is paid; none stops early.

## Amendment 1 (recorded before metrics)

The frozen stop rule "harmful history ⇒ zero information" fired on a new test.
The default bound, identical to #1102 on 24 compared cases, already gives
0.0373 in a hungry state where the two harmful branches disagree on the best
plan (eat a second unit vs stop). The corrected invariant is now tested:
information is positive only when branches disagree on the best plan, and zero
otherwise.

## Post-hoc description (not frozen; no decision drawn from it)

The frozen metrics count only *promotions* of the meal. Counting both
directions on the same deterministic audit:

| History | P1.3 eats, candidate meal not raw-top | P1.3 does not eat, candidate raw-top | Agree |
| --- | --- | --- | --- |
| Mixed (`n` = 2 and 9) | 9 | 0 | 18 |
| Harmful (`n` = 2 and 9) | 3 | 0 | 24 |

The disagreements are low-integrity states (integrity 20, or food 40 with
integrity 50). There P1.3 still eats an unknown carried food, carried by its
curiosity bonus, while the information-valued meal sits up to 2.1 below the
best competitor. The information mechanism is **more prudent** than P1.3, never
more exploratory. It cannot explain P5d's masked arm, which never ate, and it
does not reproduce curiosity's survival-carrying role (P5c).

## What this establishes

- With personal effect branches and a convex predicted-distress stake,
  information value is bounded by how much the best plan differs between
  branches. More represented future uses barely raise it.
- The same structure explains #1101 (water, exact explorer semantics: 0/80
  epistemic selections). Adding recurrence would not rescue it, which supports
  the owner's "do not patch recurrence" instruction with a measured reason.

## Limits

Synthetic states and fixtures, one seed, one genome (midpoint). No Competition
replay, no common cost ceiling between candidate and legacy scores, no survival
claim. Not a test of P5d states, which are not reconstructed.

## Next intervention

The open causal blocker remains **first contact**: before any personal
experience of a resource, information value is structurally too small to
justify a risky unsupported trial (radius-100 prior 0/80, #1101 0/80, here 0
promotions). See the decision note in
[STAGE1_FIRST_CONTACT_DECISION.md](../../STAGE1_FIRST_CONTACT_DECISION.md).
It requires an owner decision before any implementation.
