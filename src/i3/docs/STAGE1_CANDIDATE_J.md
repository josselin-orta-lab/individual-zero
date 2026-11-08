# Stage 1 Candidate-J: the last Stage-1 candidate

Issue #1061. Baseline: `effef78` (#1209). Governing decisions:
[ADR-0017](../../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md)
(execution custody) and
[ADR-0018](../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md) (Stage-1
closure).

**PROSPECTIVELY FROZEN BY OWNER DECISION. SOFTWARE FIRST. NO IMPLEMENTATION
COMMIT PRECEDES THIS DOCUMENT. NO LIVED EXECUTION WHILE THE ADR-0017 MORATORIUM
IS ACTIVE.**

## Why a last candidate, and why this one

Stage 1 asks whether stakes-based valuation can replace P1.3's additive
curiosity, relevance and prudence. No candidate has yet tested that question
cleanly:

- **Candidate-F** was rejected by its ADR-0015 gate (0/240) under a cost
  collapse.
- **Candidate-G** failed 56/57 in two modes: no value for exploration when
  unsupported, and Candidate-F-like costs when supported
  ([audit](studies/stage1-candidate-g-development-56-57/POSTHOC_FIRST_CONTACT_AUDIT.md)).
- **Candidate-I** removes the addends before first contact only. After first
  contact it routes through Candidate-H, whose fallback is complete P1.3 with
  curiosity and prudence. Its two-phase probe architecture also produced the
  custody defects that closed 58/59 to 66/67.
- **The shared prior has capacity** (#1170), but its recent-RMS scale makes the
  hope mostly energy/vigilance-shaped (water ≈ 0.4 × ω).

Pre-design sandbox computations (annex) add three observations, which are not
results:

1. **P1.3's `chunk_end` projector flips the sign of first-contact comparisons**
   near death, because death time is quantized at chunk ends. At ω = 0 and
   κ = 0.1, the trial advantage is +0.236 at water 25 and −0.254 at water 30.
   The event-based projectors agree with each other, are monotone, and give
   −0.089 and −0.066.
2. **Under an accurate projector, symmetric ignorance is aversive.** At ω = 0,
   a first trial is valued below waiting, the more so the needier the body
   (−0.148 at water 20, −0.011 at water 80). Convex distress with absorbing
   death makes a self-preserving evaluator avoid the unknown. Stakes alone
   cannot bootstrap first contact; only an inherited positive expectation can.
3. **With a capacity-relative scale, inherited hope becomes need-sensitive.** At
   κ = 0.1 and ω = 0.5, the perceived trial is worth +0.131 at water 20 and
   +0.024 at water 80, and exploration with the option to decline is worth
   +0.020 and +0.004. The drive appears when needs loom and fades when they do
   not.

Candidate-J is the smallest coherent design that follows: addend-free
everywhere, one decision phase, one accurate projector, and one inherited,
need-scaled prior shared by imagined and perceived first contact, as the owner
decided on 8 November 2026.

## Hypothesis

Designer exploration terms can be replaced if the individual evaluates the
unknown inside predicted distress, with an inherited expectation scaled to its
own body and an accurate projection, at bounded cost and in a single decision
phase.

## Mechanism

Everything not listed here is P1.3: repertoire, Competition, Action Control and
innate veto, learning, replay, presence beliefs.

1. **No designer addend in any route.** `score_addend_mode =
   "discard_both_bonus_terms"` in every decision, before and after any contact.
2. **One projector, one phase.** Every option of every decision is scored with
   `event_quadratic`, subject to J0 below; if J0 fails, the declared fallback is
   `event_local_quadratic4`. There is no detached probe, no rollback and no
   recomputed final decision.
3. **One shared first-contact prior.** When the individual has no personal
   observation of an action at the action level, so that the effects model
   would fall back to `("*",)`, that action's external effect has two
   equiprobable branches, `(ω + 1) × s` and `(ω − 1) × s`, on every channel,
   with `s = κ × 100`.
    - ω is the existing gene, unchanged.
    - κ is a new generic gene (genome v5), drawn last at generation 0 from
      U(0.05, 0.20) and set only by persistence. It names no action, token,
      place or channel.
4. **Perceived unknown action.** Its score is the mean of the two branch plan
   values, on the same plan length as every other option.
5. **Imagined trial at a frontier**, before contact. With `q` the existing
   personal Laplace resource-presence rate of newly seen cells (the
   frontier-modality primitive), the option's value is
   `(1 − q) × V(move) + q × max(V(move), mean over branches of V(move + trial))`.
   The `max` is the option to decline, so exploring is never valued below
   moving. No recurrence is required.
6. **After contact**, personal effects replace the prior: the frontier value
   becomes `q_m × max(V(move), V(move + known effect))` per modality, without
   any addend.

## Software falsifier (one execution)

**Fixtures**, all software, no World:

- P80: the #1170 perceived-water grid, with no drink effect;
- F108: the #1170 carried-food grid;
- K80: the #1146 bodies and horizons, with one unseen neighbor and **no
  recurrence**;
- the newborn fixture `(100, 80, 30, 80, 100)`;
- a satiated fixture `(80, 80, 80, 80, 80)`.

**Arms:** ω ∈ {−1, −0.5, 0, 0.25, 0.5, 1} × κ ∈ {0.05, 0.10, 0.20}. P1.3 with
its addends is reported as a descriptive anchor.

**Defect stops:**

- **J0 projector validity.** On the #1146 grid and P80, `event_quadratic` is
  checked against the canonical oracle: the same top option wherever the
  oracle's top-two gap exceeds 1e-3, and a maximum value error of 0.01. If this
  fails, J uses `event_local_quadratic4`, which is a declared fallback, not
  tuning.
- **J1 integrity.** No addend anywhere; renaming invariance; every computation
  paid; the number of plan evaluations is independent of ω and κ; no restore or
  rollback call exists.

**Reported:**

- **J2, theoretical prediction.** At ω = 0, no first trial and no pre-contact
  exploration is the top option in any state where the trial's channel is
  below threshold.
- **J4 cost.** Mean paid simulated steps per decision, against P1.3 on the same
  states.

**The question:**

- **J3 capacity.** Some ω > 0 makes the perceived first drink the top option in
  water-deficit P80 states, and pre-contact exploration the top option in
  water-deficit K80 states. The advantage must not increase as the deficit
  channel rises in at least 80% of ordered state pairs (need-sensitivity).

**Verdicts:**

| Verdict | Condition |
| --- | --- |
| `CANDIDATE_J_DEFECT` | J1 fails, or J0 fails for both projectors |
| `CANDIDATE_J_COST_WALL` | J4 exceeds 2.5 × P1.3 |
| `CANDIDATE_J_NO_CAPACITY` | J3 fails |
| `CANDIDATE_J_CAPACITY_SHOWN` | none of the above |

Any verdict other than CAPACITY_SHOWN closes Stage 1 under ADR-0018.

## Lived path, after the ADR-0017 lift only

- **One DEVELOPMENT pilot at 68/69.** 12 blocks and three arms: P1.3,
  Candidate-J native, Candidate-J ω := 0 on the same genomes. Two-phase
  execution and an exact-SHA sealed rehearsal, as ADR-0017 requires.
  Continuation is engineering-only: a complete panel, a non-funded decision
  fraction at most P1.3's plus 2 points, and paid cognitive energy per lived
  step at most 2 × P1.3. Behavior is reported, not ruled.
- **The Stage-1 gate.**
    - Worlds: family R-depletion-v1 ([Stage 0](STAGE0_REVISION.md)), validation
      indices ≥ 120, never opened.
    - Genomes: ADR-0015 selection (K = 40, m = 5) across at least eight
      independent populations.
    - Primary criterion: survival non-inferiority against P1.3, with the margin
      frozen before exposure.
    - Secondary: revision latency, cognitive cost per lived step, and the
      selected ω and κ, including their mass within 0.05 of either bound.

The current detached Stage-0 design reserves validation indices 120–167 and
records known historical allocation only through 119. This protocol does not
open those validation worlds; exact gate allocation remains a later
prospectively frozen decision.

## Declared expectations, before any execution

- J2 holds; it follows from convex distress with absorbing death.
- J3 holds at κ = 0.1 for ω ≥ 0.5; ω = 0.25 is marginal.
- J4 lands near 2 × P1.3: about 18–23 simulated steps per plan evaluation
  against 9.
- In lives, J tries perceived water quickly when ω is high. It explores more
  than P1.3 when needy and less when satiated.
- The main risk is worlds where water is far: there, `q × …` may stay too small
  and J dies where P1.3 also struggles.
- Under selection, ω is expected to rise, possibly saturating at +1.
- My estimate for the gate: a real chance, not the majority of chances.

## Not decided here

The non-inferiority margin, the population sampling and the compute ceiling are
frozen by the gate protocol, before exposure.

## Annex: pre-design sandbox (not a result)

Midpoint genome (θ = 60 everywhere), the #1146 personal effect memory,
horizon 14. Each branch is a one-step plan with a modified effect, so that all
compared plans have the same length. The plan-prediction read is overridden in
the sandbox only.

```python
import sys; sys.path.insert(0, "src")
from i3.modules.mind import Mind
from i3.modules.genome import midpoint
from i3.modules.body import CognitiveBudget, BodyLaws

m = Mind(midpoint(), 197); m.map = {}
for k, d in ((("se_deplacer",), (-2., -.2, -.4, 0., 0.)),
             (("attendre",), (-.35, -.2, -.4, .2, 0.)),
             (("dormir",), (3., -.35, -.4, 0., 4.))):
    m.effects.observe(k, d)
m._drift = m.drift()
m.simulation_mode, m.projection_accounting = "reference", "event_quadratic"

def v(body, delta):
    m._read_plan_prediction = lambda key: (delta, 0.0)
    return m.simulate(body, [("x",)], 14, CognitiveBudget(body, BodyLaws()))[0]

WAIT, TRY, MOVE = (-.35, -.2, -.4, .2, 0.), (-.5, -.2, -.4, 0., 0.), (-2., -.2, -.4, 0., 0.)
def branches(base, kappa, omega):
    return [tuple(x + (omega + sgn) * 100 * kappa for x in base) for sgn in (1, -1)]
def trial(body, kappa, omega):
    return sum(v(body, d) for d in branches(TRY, kappa, omega)) / 2 - v(body, WAIT)
def explore(body, kappa, omega, q=0.15):
    vm = v(body, MOVE)
    vt = sum(v(body, d) for d in branches(MOVE, kappa, omega)) / 2
    return (1 - q) * vm + q * max(vm, vt) - v(body, WAIT)

for water in (20., 30., 45., 55., 80.):
    b = (80., 80., water, 80., 80.)
    print(water, round(trial(b, .1, 0.), 3), round(trial(b, .1, .5), 3),
          round(explore(b, .1, .5), 3))
```

Expected output: water 20 → −0.148, +0.131, +0.020; water 80 → −0.011, +0.024,
+0.004. With `chunk_end` instead of `event_quadratic`, the ω = 0 column changes
sign between neighboring water levels.
