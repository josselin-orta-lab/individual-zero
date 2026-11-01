# I2 G1-LAB: need × aversion competition research design

**Status: OWNER-ACCEPTED SCIENTIFIC FRAMING AND FACTORIAL DESIGN (ADR-0007); PARAMETER_FREEZE_PENDING; EXECUTION_NOT_AUTHORIZED; NOT_EXECUTED.**
**Date:** 1 November 2026. The owner accepted the conceptual scientific
analysis and experimental-control structure in
[ADR-0007](../../../decisions/ADR-0007-need-nutrition-aversion-scientific-design.md).
The candidate scoring equation and signal magnitudes/seeds/horizon still
require explicit, separate, prior-to-code parameter approval.
**Authority:** no G1-LIVE/G3/M11/engine birth or motor activation is conveyed.
This remains a bounded **prospective exploratory design**, NOT confirmatory
preregistration, evidence of natural motivation, or permission to run.

## 1. Frozen context and why a new model would be necessary

Reference source: `main=49bd5b339c6abbfeecfaddc52f3f1b9eeec8a44e`,
merged [PR #807](https://github.com/josselin-orta-lab/individual-zero/pull/807).
Read [ADR-0005](../../../decisions/ADR-0005-authorize-nonliving-integrated-g1-lab.md)
(non-living integration only) and
[ADR-0006](../../../decisions/ADR-0006-evidence-grounded-aversion-reappraisal.md)
(no time-based stale retry or assumption that social example is required).
The relevant existing source is
`src/i2/lab/integrated_loop.py` and
`src/i2/modules/chosen_outcome_study.py`.

Already demonstrated, NOT new findings:
- Energy 17 versus 60 changes the committed first-person energy evidence
  but NOT decisions or paid UC within either fixed or observational policy
  (PR #805): **energy is represented, not motivationally used**.
- PR #807 separates toy `metabolic_debit` from signed
  `food_energy_impulse`, with local rollback/replay.
- The cognitive chosen-only result nevertheless stores ONE
  `observed_net` scalar, which is neither an independent aversion nor
  a nutritional estimate. A negative food impulse is a toy *physical*
  energy effect, not proven pain, nausea or learned repulsion.
- Hidden recovery with no new chosen evidence remains unidentifiable;
  forced or time-triggered +9 revisit is an **artificial** comparator,
  not natural exploration.

**Scientific construct gap:** one scalar cannot distinguish a food that
supplies useful calories but is unpleasant from one that supplies none and
is pleasant. Consequently current G1-LAB cannot identify a competition
between learned aversion and energy need. This is not solved by renaming
the negative energy impulse 'aversion'.

## 2. Questions and discriminating predictions

**H-N (proposed):** once the SAME individual has actually observed
(a) a food's positive energy contribution and (b) a separately modeled
aversive sensory consequence, subsequently observed body energy can
alter paid action selection **without deleting the aversive memory**.

**H-A (proposed):** at otherwise comparable body states and learned
nutritional evidence, a previously experienced aversive sensory
consequence reduces selection of that action compared with a
nonaversive condition, without requiring a programmer-inserted veto.

**Information null (required):** if no chosen experience or new
perceptual cue distinguishes outcomes, neither the agent nor the
investigator may claim it learned hidden food safety. Rejection of
an action under no new evidence is not a standalone H2 failure.

**Null/failure results are legitimate:** if the candidate never eats,
dies before tasting, abstains throughout, or energy and aversion
contrasts do not affect behavior, record `NOT_ESTABLISHED`. Do not
adjust priors, training order, energy levels, effect magnitudes or
observation channels after seeing trajectories.

## 3. Minimum proposed environment, before any implementation

One **disposable, non-living SQLite owner** per independent simulated
subject, reused from the v5 G1-LAB transaction. No second body, UC,
cognition or witness service. Reuse the existing collect/eat/drink
affordances and the unforced paid Competition/Action Control cycle,
including veto, abstention, actual synthetic UC and modeled terminal.

Keep distinct, with different provenance:
- **Energy state / need:** `energy_t`, already available from the
  *previous committed* model state. A proposed generic deficit
  `D_t=max(0,100-energy_t)` is a researcher-defined toy drive proxy,
  NOT biological hunger or an independent subjective feeling.
- **Nutrition:** `nutrient_gain_t >= 0` attributable ONLY to a
  **chosen and executed simulated eating action**, issued as
  first-person outcome evidence no earlier than the next capture.
  This is NOT the current signed `food_energy_impulse`.
- **Aversive sensory input:** `aversive_signal_t >= 0` is an
  independent experimenter-specified **simulated sensory signal**
  after an actually chosen action. It must have no hidden prior
  exposure and does NOT prove pain, disgust or biological aversion.
- **Physical cost:** existing `metabolic_debit_t` stays separate.
  A new toy nutritional-energy world uses
  `E_(t+1)=clamp(E_t-metabolic_debit_t+nutrient_gain_t,0,100)`.
  The aversive signal is *not* secretly deducted from energy.
- **Memory:** maintain source-bound last actually chosen nutrition and
  aversive evidence as distinct items; NEVER infer the sensory
  signal from a signed energy net or read unchosen future states.

No example from a conspecific, direct social information or
stale-option revisit is included: social learning is a **different**
future experiment. No action-specific `EAT` command or additional
forced 'training' consumption is allowed.

## 4. Candidate decision mechanism, NOT YET PARAMETER-FROZEN OR AUTHORIZED

This is an explicitly **engineered low-level competition hypothesis**,
not an assertion that desire or consciousness emerges naturally.
For each action with previously and personally observed outcomes,
allow a generic bounded score contribution from need-conditioned
expected nutritional benefit, opposed by retained aversive memory.
The proposed *candidate* arithmetic, to be accepted or rejected
BEFORE any run, is:

```text
D_t = max(0, 100 - energy_t)
N_t(a) = last personally observed nutrient_gain for action a, else 0
A_t(a) = last personally observed aversive_signal for action a, else 0
need_contribution_t(a) = floor(D_t * N_t(a) / 100)
value_t(a) = unchanged_existing_prior(a)
             + need_contribution_t(a) - A_t(a)
```

No action semantic is special-cased; actions without firsthand
evidence receive no invented nutrition/aversion data. Use the **existing
paid Competition** to select or abstain. If this equation is accepted,
the exact dimensions, constants, clipping rule and possible score ties
must be locked *before* running. The researcher-designed formula
itself can explain any apparent response: it proves at most the
mechanistic coupling/ablation, **not natural motivational emergence**.
The original chosen-only +5 toy score is **not combined** with this
proposal as though it were learned biological reward.

## 5. Required ablations and negative controls (not yet run)

Minimal factorial comparison (candidate initial energies **17 and 60**,
informed by PR #805, so these data cannot claim confirmatory novelty)
crossed with a **nonaversive (0)** and **aversive (>0)** food sensory
signal at a common *positive* nutritional gain. Values of the latter
two signals, world duration, initial resource supply and max captures
must be published **before any implementation or observation**.
Avoid constructing constants to produce a desired EAT/non-EAT result.

At each cell, independently initialize and fund these arms equally:
1. **Full:** need-conditioned nutrition and experienced aversion.
2. **Need-off:** same received and retained nutrition/aversion evidence,
   but body need has **zero effect on valuation**.
3. **Aversion-off:** same sensory events/energy, but aversion has **zero
   effect on valuation**.
4. **Fixed baseline:** original fixed prior and no evidence-responsive
   valuation, retaining the same body, observations, UC and control.

No candidate ever knows its hidden sensory/nutritional schedule before
an actual chosen consequence. **Never force EAT after COLLECT.**
Record when usable eating evidence was never acquired: such an arm is
*uninformative*, not a failed or successful adaptation. Do not infer a
causal effect from unlike prior histories. Compare matched attained
history and common observation horizons when possible, and report all
selection/censoring differences when not.

Required measurements: every accessible affordance, prior body energy
evidence, each separately issued outcome, chosen action or abstention,
competing values with their actual source refs, sensory-memory
retention, energy and inventory transitions, all paid UC, veto/refusal,
simulated terminal and the earliest eligible post-exposure choice.
Do not choose the best seed/run. Initial finite deterministic seeds and
study stop limits are decision inputs to freeze, not adjustable knobs.

## 6. Fail-closed technical and scientific falsifiers

Reject implementation/reported inference if any of these occur:
- an unchosen `nutrient_gain` or aversive signal is read as personal
  experience; the current action's future consequences influence its
  current decision; or a social/hidden oracle is injected;
- the controller scripts the next EAT, or the `revisit_after=2,+9`
  heuristic silently enters the default policy;
- an aversive memory row is erased merely because low energy led to
  a risky choice;
- the full policy and a need-off ablation behave identically yet a
  hunger-driven change is claimed; likewise for the aversion-off
  control and an aversion-driven claim;
- action/body/cognition/UC do not share the same SQLite COMMIT,
  rollback leaves an effect, or local replay fails;
- a prior history is missing or arms truncate at different deaths,
  yet an equal-horizon causal benefit is asserted;
- behavior is explained entirely by the researcher-assigned equation
  but is described as an autonomous, natural learned drive;
- a test PASS, local mock witness or numeric body state is used to
  declare real G1-LIVE/M11/G3 approval.

The primary decision is **whether the mechanism is separately
identifiable from its ablations**, not maximizing survival or making
an individual eat. A zero effect or inability to acquire experience is
a scientifically informative **NO-GO/NOT_ESTABLISHED**.

## 7. Approved direction, remaining freeze and stop rule

**ADR-0007 records owner approval of the scientific analysis and the
four-arm factorial DESIGN IN PRINCIPLE. THIS DOCUMENT STILL DOES NOT
AUTHORIZE BEHAVIORAL IMPLEMENTATION OR EXPERIMENT EXECUTION.** Before
code or runs, explicitly freeze the aversive/nutritional signal
magnitudes, integer equation/clipping/ties, nonaversive versus aversive
world definitions, finite independent seed/run allocation, initial
resources, maximum captures, censoring rules and exact stop criterion,
and obtain a separately recorded owner decision for that complete
parameter-locked protocol. No constants should be retroactively
declared approved from the design acceptance.

After that separate authorization, only ONE bounded G1-LAB increment
may be considered, retaining all negative/null/harmful results.
No open-ended score, reward, threshold or heuristic search.

Existing approved ADRs remain normative. G1-LIVE issue #662 still
requires two truly independent architecture/science reviewers and
actual external M11; G0 custody #661 remains partial, G3 #664 remains
blocked. The experimental I2 engine stays `NOT_REGISTERED_NOT_EXECUTABLE`,
`NOT_BORN`, `motor_authority=NONE`. Any local terminal is not
an independently attested living death.
