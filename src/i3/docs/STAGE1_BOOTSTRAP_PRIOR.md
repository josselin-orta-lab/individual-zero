# Stage 1 bootstrap prior A: zero-mean stake-projected ignorance

Issue #1061. Baseline before this slice:
`ffd903ca90e951d4841bbc2635ada927ce64355d`.

**SOFTWARE PRIMITIVE ONLY. NOT A LIVE POLICY. NO STUDY AUTHORIZATION.**

## Why this exists

The complete 50/51 diagnostic establishes two facts at once:

1. the reference-preserving frontier information mechanism can become positive
   in paid ordinary lives;
2. it does so only after the individual first acquires personally useful water
   experience under the current conservative unsupported-outcome semantics.

All seven positive-information lives activate exactly one step after first
positive water uptake. Five other candidate lives never experience water, never
activate the information mechanism and all die.

Therefore the next Stage-1 question is not whether the information arithmetic
works. It is how an individual can represent **possible consequences it has
never experienced yet** without receiving a designer-written favorable outcome.

## Hypothesis A

The first bounded hypothesis is a **zero-mean generic ignorance prior projected
onto the individual's own current stakes**.

It is deliberately not a prior that "water is good", "food is good" or
"exploration is useful".

Inputs are only:

- current first-person body;
- inherited distress thresholds `theta`;
- inherited distress powers `p`;
- inherited distress weights `w`;
- a paid CognitiveBudget.

There is no action, token, map, resource type, World, ecology, source density or
development-result input.

## Construction

For every currently distressed bodily channel, compute the analytic magnitude
of the direction that locally reduces the existing distress objective:

```text
g_c = w_c * p_c / theta_c
      * ((theta_c - body_c) / theta_c) ** (p_c - 1)
```

when `body_c < theta_c`, otherwise `g_c = 0`.

Normalize the resulting five-vector with its L2 norm. If the vector is zero,
there is no locally stake-relevant uncertainty and the primitive returns no
outcome hypotheses.

Otherwise form exactly two possible unsupported external effects:

```text
delta+ = +100 * unit(g)
delta- = -100 * unit(g)
P(delta+) = P(delta-) = 0.5
```

The radius 100 is not a fitted scale. It is the existing maximum admissible
single effect-delta magnitude in the Stage-1 forecast contract.

The two outcomes share one generic directly sensed-body signal. Hidden branch
identity is not observable; subsequent replanning may distinguish them only
because their predicted body states differ.

## What zero mean means

For every channel:

```text
E[external delta_c] = 0
```

exactly up to floating-point roundoff.

Thus the prior has no optimistic expected bodily reward and no pessimistic
expected punishment. Any positive value of information must arise because the
individual can condition later behavior on a bodily consequence that matters to
its own distress.

The sign symmetry also prevents embedding an instruction to move toward any
specific action or resource.

## Interpretation

This is a two-point quadrature, not a claim that physical effects literally
come in opposite pairs.

It asks a narrower computational question:

> If the individual knows only that an unsupported consequence could matter in
> either direction along the part of body space currently relevant to its own
> stakes, can conditional replanning create useful exploration without an
> additive curiosity reward?

Orthogonal bodily directions are ignored in this first-order approximation.
That is a falsifiable simplification, not hidden knowledge.

## Paid work

Constructing the prior costs one model cycle and 32 memory items.

The 32 items explicitly account for:

- 20 scalar reads: body, theta, p, w;
- 10 scalar branch-delta outputs;
- 2 branch probabilities.

No simulated step is claimed because this primitive only constructs the
hypotheses. Any later outcome projection/replanning must be separately paid by
the existing Stage-1 kernels.

The returned work object is an allowance receipt, not a physical settlement
receipt; ordinary runtime would still have to debit it if a future policy uses
the primitive.

## Explicit boundaries

This slice does not:

- modify `reference_frontier_information_v1`;
- create `reference_information_v1`;
- change P1.3 or its genome;
- change the #1080 empirical frontier belief;
- reveal a resource modality;
- generate a motor command;
- read or mutate a map;
- import World/runtime;
- reopen development 44-51;
- authorize selection, validation or reserve exposure.

## Next composition problem

A future bootstrap integration must still distinguish two uncertainties:

1. **what modality an unseen resource observation exposes**;
2. **what bodily consequence an unsupported newly available action may have**.

This primitive addresses only the second item.

A clean next software slice may combine it with an explicit generic modality
prior and the existing #1081 revealed-plan arithmetic, but must keep nested
information semantics honest: merely seeing a water source reveals that
`boire` becomes available, not what drinking will do to the body.

No fresh world should be opened until that composition is explicit and tested.

Stage 2 remains blocked.


## Branch-local observed effect view

The first composition prerequisite is now
`modules/observed_effect_view.py::paid_simulate_after_observed_effect`.

After a subjective trial branch has explicitly revealed one bodily consequence,
this helper evaluates a future continuation through the existing P1.3
`simulate` algorithm while replacing the prediction for **that exact action
key only** with the observed delta and zero uncertainty.

The view is read-only. It does not update the real EffectsModel, TD values,
replay buffer, map, RNG, intention or observer state. It also deliberately does
not reproduce P1.3's action-level/global effect fallback update. Propagating one
hypothetical sample to other actions would claim more counterfactual learning
than the branch has actually observed.

Constructing the exact key/delta view costs one cycle plus seven memory items.
The subsequent plan simulation spends its ordinary P1.3 simulated work. A future
information comparison must include both in its common forecast ceiling.

This operation answers only:

> After this exact effect has been observed for this exact action, how would the
> existing P1.3 plan model value future reuse of that action?

It does not say the trial should occur, generate its outcome, execute an action
or read World.

The remaining nested bootstrap composition must therefore keep three moments
separate:

1. an unseen frontier may expose a resource modality;
2. trying the newly available but unsupported action incurs one of the #1088
   zero-mean possible effects;
3. only **after that observed trial effect** may this branch-local view use the
   effect for future replanning.

Collapsing steps 1 and 2 would turn resource observation into an oracle for its
bodily consequence. Collapsing steps 2 and 3 would remove the value of learning
from the trial.


## Nested value of trying one unsupported action

`modules/unknown_action_trial.py::paid_unknown_action_trial_value` composes the
zero-mean prior and branch-local observed-effect view without creating a live
policy.

The kernel separates three values under one common complete-work forecast:

1. **no trial**: best explicit continuation that never uses the unsupported
   exact action key;
2. **trial with frozen continuation**: execute the unsupported action once,
   average over the zero-mean effect branches, but require one common
   post-trial continuation chosen before observing the result;
3. **trial with informed continuation**: execute the same one trial, then let
   the directly sensed post-trial body choose the best post-trial continuation.

It reports two different quantities:

```text
information_value = informed trial - frozen trial
trial_advantage    = informed trial - no trial
```

This distinction is essential. Learning can be valuable while the experiment
itself is still too dangerous or costly to choose. Conversely, a favorable
trial advantage is not automatically evidence that information caused the
advantage.

Every trial matrix plan starts with the unsupported action. Within each
subjective branch, #1089 makes that exact branch effect the prediction for the
trial and any later exact reuse. Other action predictions remain unchanged
P1.3.

The common no-trial plan set is forbidden from containing the unsupported exact
key. It therefore cannot receive the unknown action for free.

### Observability and clipping

Conditional replanning groups branches by the generic signal and the directly
sensed post-trial body. If two different prior deltas clip to the same observable
body, they may not install different learned exact effects. The kernel fails
closed rather than letting an unclipped hidden branch identity leak through.

### Complete cost ceiling

The one forecast ceiling includes:

- the #1088 prior construction;
- matrix/preparation bookkeeping;
- every no-trial continuation;
- every prior-branch × post-trial continuation;
- one #1089 view for every trial matrix cell;
- all ordinary P1.3 simulation work;
- the final frozen/informed reduction.

No branch may stop computation because it looks unfavorable and there is no
Stage-2 compute-selection rule.

This kernel still has no frontier modality model, action admission or motor
command. It answers the inner question only: if an unsupported action were
available here, is one trial plus adaptation worth more than not trying it?

A later frontier composition must first establish that the resource action is
observable/available from the frontier branch. Only then can this nested trial
calculation be attached. Seeing a water source remains distinct from knowing
what drinking will do.


## Frontier observation modality prior

The next independent uncertainty is **what kind of opportunity an unseen cell
will expose**, not what that opportunity will do to the body.

`modules/frontier_modality_prior.py::paid_frontier_modality_prior` extends the
same Laplace symmetry already used by P1.3 without consulting body need or
utility.

Resource presence remains exactly:

```text
p_resource = (resource_cells + 1) / (seen_passable_cells + 2)
```

Conditional on resource presence, the two existing first-person resource sensor
modalities receive a symmetric Dirichlet/Laplace prior:

```text
q_water = (water_incidences + 1)
          / (water_incidences + token_incidences + 2)

q_token = (token_incidences + 1)
          / (water_incidences + token_incidences + 2)
```

The three subjective observation classes are therefore:

- `NO_RESOURCE`: `1 - p_resource`;
- `WATER_MODALITY`: `p_resource * q_water`;
- `TOKEN_MODALITY`: `p_resource * q_token`.

At zero personal incidence the distribution is 0.5 / 0.25 / 0.25. This is not
a claim about environmental frequencies and is not fitted from development
50/51. It is the maximum-symmetry extension of P1.3's already existing
Beta(1,1) resource-presence prior to the two resource sensor classes already
present in its perception interface.

A personally seen mixed water+token cell contributes one incidence to each
modality and the two incidence counts are normalized. There is deliberately no
fourth mixed branch, keeping the Stage-1 two/three-branch approximation. This
means the modality model is categorical and does not represent joint
water+token discovery.

The prior reads only the individual's map. Relative positions and token names
do not affect probabilities. Edge cells do not enter counts but are still paid
to scan. No body channel, distress, action effect, action command or World fact
enters the distribution.

This prior therefore answers **what may become observable**. #1088/#1090 answer
a different question: **what might an unsupported newly available action do,
and is one trial plus adaptation worth it?**

A future frontier-bootstrap composition must keep those layers distinct.
Observing `WATER_MODALITY` can make `boire` available to the subjective
branch, but must not provide a favorable drinking effect. That effect remains
zero-mean and unknown until the nested trial model.


## Bounded three-leaf target composition

The source scenario limits Stage-1 subjective simulation to **two or three
branches**. Therefore the modality and effect priors must not be multiplied into
a generic six-leaf tree.

`modules/three_leaf_target_prior.py::paid_three_leaf_target_prior` performs a
target-specific composition that remains within three leaves.

For one target modality `m`:

```text
NO_TARGET_MODALITY               P = 1 - p(m)
TARGET_MODALITY_TRIAL_POSITIVE   P = p(m) * 0.5
TARGET_MODALITY_TRIAL_NEGATIVE   P = p(m) * 0.5
```

`p(m)` comes only from the first-person modality prior. The positive/negative
effect pair comes only from the zero-mean stake prior. Therefore:

- target identity changes only the observation probability;
- target identity cannot rotate the effect direction toward a favorable bodily
  channel;
- the full three-leaf expected external bodily effect remains exactly zero.

For a water-specific valuation, `NO_TARGET_MODALITY` aggregates
`NO_RESOURCE` plus `TOKEN_MODALITY`. Their individual probability masses are
retained in `non_target_probability_breakdown`.

This aggregation means only that **token-specific information receives no
credit in the water-only engineering valuation**. It does not claim that the
real individual would perceive a token and an empty cell identically, and it
does not remove token perception from runtime.

The symmetric statement holds for a token-specific valuation.

If current distress is locally flat, the zero-mean effect prior returns no
stake-relevant uncertainty and the composition creates no trial leaves.

The composition pays:

1. the full first-person modality scan;
2. the zero-mean stake-prior construction;
3. one cycle plus 18 memory items for composition bookkeeping.

It does not simulate a plan, reveal a World fact, execute an action or mutate a
Mind.

### Why this is not yet the live frontier score

The three leaves establish the **probability/effect envelope** only. A later
kernel still has to model the temporal sequence correctly:

1. follow the existing explorer prefix;
2. observe whether the target modality became available;
3. if it did, decide from the individual's own predicted stakes whether one
   unsupported trial is worth taking;
4. only after the trial body's effect is observed may branch-local replanning
   reuse that effect.

The trial must not be automatic merely because the modality appeared. Otherwise
the composition would replace an explicit curiosity bonus with an implicit
"always sample the unknown resource" rule.

No fresh development allocation should be opened until that decision sequence
is represented and tested inside the same at-most-three-leaf envelope.


## Water-frontier optional-trial value

The first full three-leaf **decision sequence** is now implemented as a
software-only kernel in
`modules/water_frontier_optional_trial.py::paid_water_frontier_optional_trial_value`.

It remains water-specific to the already tested reference-frontier engineering
scope. No new runtime policy is introduced.

The kernel preserves the existing P1.3 explorer prefix and the #1082
sensorimotor binding that a newly revealed water cell is reached by one generic
movement before `boire`.

The stochastic leaves remain exactly those from the bounded prior:

1. no water target;
2. water then positive unsupported drink effect;
3. water then negative unsupported drink effect.

Critically, revealing water does **not** automatically execute `boire`.

At the water-observation node the individual compares:

```text
decline_trial_value

versus

expected_trial_informed_value
```

The trial value averages the two zero-mean effect branches. Only after the trial
effect becomes directly observable may the best post-trial continuation differ.

The kernel therefore reports:

- `ordinary_frontier_value`: best ordinary continuation after the existing
  explorer prefix, with unsupported `boire` forbidden;
- `trial_frozen_value`: one drink trial, but one common post-trial
  continuation chosen before observing its effect;
- `trial_informed_value`: the same trial with effect-conditioned
  post-trial replanning;
- `trial_information_value = informed - frozen`;
- `trial_advantage = informed - ordinary`;
- `frontier_expected_value`: the water-probability-weighted value after
  allowing the water node to decline or trial;
- `water_revelation_advantage = frontier_expected - ordinary`.

This separation means information can be valuable while the physical
experiment is still rejected. Conversely, if the trial is too dangerous, water
revelation need not create any positive exploration increment.

Ties at the water node remain explicit as both `DECLINE_TRIAL` and `TRIAL`;
the kernel contains no hidden tie preference.

All common continuations are forbidden from containing the unsupported drink
key. Post-trial plans may reuse it through the exact branch-local observed
effect view.

The complete forecast covers the three-leaf prior, bookkeeping, every ordinary
continuation, both effect branches times every post-trial continuation, the
branch-local effect views, ordinary P1.3 simulation work and reduction. When
local distress is flat, no effect branches exist and the ceiling correspondingly
omits them.

This remains a score kernel, not a live policy. It does not admit a motor action,
read World, change Competition, alter P1.3 state or authorize a development
allocation.

The next integration question is whether this bounded score can replace the
current water-frontier score inside the reference-preserving decision path
without changing any other option semantics or creating prohibitive cognitive
cost. That must be answered by software integration before another world is
opened.


### Adverse software characterization: zero-mean radius 100 does not initiate a trial

The predeclared synthetic falsifier that at least one plausible P1.3 state
should select the optional unsupported trial **failed**.

A bounded software sweep evaluated 80 combinations:

- one bodily channel set to 20, 30, 40 or 50;
- the other four channels at 80;
- each of the five channels stressed in turn;
- horizons 4, 6, 8 and 12;
- ordinary learned movement/wait/sleep effects kept at the current P1.3-like
  magnitudes;
- the same ordinary wait/sleep continuation repertoire available before and
  after the trial.

Result:

- 80/80 cases evaluated;
- **0/80 selected the unknown drink trial**;
- at least one case had positive inner trial information value;
- best observed inner information value: about `2.38825e-5`;
- best total trial advantage remained negative: about `-0.0678657`.

Therefore the current zero-mean **radius-100** ignorance prior can represent
useful information, but under this realistic software grid its physical/cognitive
risk dominates before the first unsupported trial.

This is not a world-level or survival result. It is a software falsification of
the claim that the current prior is already sufficient to bootstrap the live
water-frontier candidate.

Do **not** integrate this kernel into runtime or open another development panel.

The next prior question should use information already available to the
individual rather than a designer-chosen smaller favorable radius. The 50/51
originals show that the five no-water candidate lives nevertheless recorded
95, 133, 127, 95 and 95 paid branch effects respectively, with 18 retained in
each ring. A generic action-agnostic empirical consequence distribution can
therefore be investigated without inventing water-specific knowledge or new
memory.

That investigation must remain distinct from the failed P5b global point prior:
its purpose would be to provide **uncertainty branches for an unsupported
action**, not to replace action-specific learned predictions with one global
mean.


## Prior B: recent action-agnostic empirical effect uncertainty

The adverse #1094 sweep shows that the maximally broad symmetric ±100 prior can
represent information yet still makes every tested first unsupported trial
unattractive. The next alternative therefore does not choose a smaller radius
by hand.

`ReferenceBranchMemory.recent_generic_effects` exposes a new paid read of the
existing ring:

- scan the same fixed 18-record memory already paid/stored by #1077;
- return only the last `WINDOW=3` bodily deltas;
- return **no action or token identity**;
- allocate no new memory and inherit nothing across births.

`modules/recent_generic_effect_prior.py::paid_recent_generic_effect_prior`
then compresses those recent personal effects into exactly two unsupported-
action hypotheses.

### Two samples

With exactly two recent effects, both are retained directly at probability
0.5 / 0.5.

### Three samples

With three recent effects:

1. compute all three squared Euclidean distances in five-channel bodily-delta
   space;
2. choose the closest pair, with chronological pair order resolving an exact
   distance tie;
3. average that pair into one branch with probability 2/3;
4. retain the remaining sample as the second branch with probability 1/3.

This deterministic 3 -> 2 compression preserves the empirical three-sample mean
exactly:

```text
(2/3) * mean(close_pair) + (1/3) * singleton
= mean(sample_1, sample_2, sample_3)
```

If fewer than two records exist, the result is
`INSUFFICIENT_GENERIC_SUPPORT`. If the two resulting branch deltas are
identical, the result is `NO_EMPIRICAL_DIVERSITY`; the code does not duplicate
one effect merely to satisfy a two-branch API.

### Why this is not the P5b global prior

P5b's action-agnostic point readout collapsed action identity into one prediction
and produced 0/288 survival in that ablation.

This new prior does something different:

- it is used only when the candidate action has **no personal support**;
- it preserves two explicit consequence branches rather than one global mean;
- existing exact/same-action predictions remain authoritative when available;
- it is a temporary uncertainty model for deciding whether an unsupported
  action is worth learning, not a replacement effect model.

### Why this is admissible after 50/51

The five 50/51 candidate lives that never experienced water still recorded
95, 133, 127, 95 and 95 paid branch effects respectively; all retained the full
18-record ring by death. So an action-agnostic empirical uncertainty model has
personal data available well before the missing water experience in those
closed lives.

That fact motivates this software mechanism but does not evaluate it on those
closed trajectories. No 50/51 decision is replayed or rescored here.

### Boundaries

The prior has:

- no target action argument;
- no token identity output;
- no body-need or distress input;
- no World or hidden-stock input;
- no designer-selected effect magnitude;
- exactly two branches when complete.

Its expected external delta may be nonzero because it is the empirical mean of
personally lived generic effects. That is a personal belief, not an injected
reward. The later body projection remains responsible for deciding whether
those possible consequences matter now.

This slice is not a live policy. The next question is whether replacing #1088
inside the three-leaf target composition with this empirical two-branch prior
can make an unsupported trial selectively worthwhile while still allowing
dangerous empirical priors to reject it.


## Prior C: recent personal RMS scale with exact zero mean

Two prior attempts delimit the problem more sharply:

- the fixed symmetric radius-100 prior kept zero mean but selected no optional
  trial in 80 realistic P1.3-like software states;
- the direct recent empirical prior selected many trials, but the selection was
  driven by transferred expected physical effect: maximum measured inner
  information value was zero, and an adverse recent history still selected the
  trial. That probe was rejected in #1096 and left unmerged.

The next prior keeps the useful part of personal experience, **scale**, while
discarding its mean and sign.

`modules/recent_rms_effect_prior.py::paid_recent_rms_zero_mean_effect_prior`
reads the same last two or three action-agnostic bodily deltas from the existing
paid branch-memory ring.

For each body channel:

```text
s_c = sqrt(mean_i(delta_i[c]^2))
```

It then constructs exactly two hypotheses:

```text
+s   with probability 0.5
-s   with probability 0.5
```

Therefore:

```text
E[delta_c] = 0
E[delta_c^2] = mean_i(personal_delta_i[c]^2)
```

for every channel.

This preserves the recent personal raw second moment exactly while transferring
no empirical mean.

### What personal experience contributes

The individual learns only an empirical magnitude of bodily uncertainty:

> consequences I have recently experienced have tended to move these bodily
> channels by roughly this much.

It does **not** infer that an unsupported action will behave like the average
known action, and it does not infer whether the unknown effect is beneficial or
harmful.

No action name, token identity, current need or distress gradient enters this
prior. Current bodily stakes matter later, when the existing projection decides
whether resolving that uncertainty is worth its risk and cognitive cost.

This differs from the original radius-100 prior in one dimension only:
uncertainty magnitude is now learned from the individual's own recent life
instead of being fixed at the largest admissible delta.

### Failure states

- fewer than two retained generic effects:
  `INSUFFICIENT_GENERIC_SUPPORT`;
- RMS zero on all five channels:
  `NO_EMPIRICAL_SCALE`.

Neither case fabricates two branches merely to satisfy a downstream API.

### Cost

The existing fixed branch-memory ring is scanned and paid normally. Scale
construction then pays two model cycles plus:

```text
5 * number_of_recent_samples + 12 memory items
```

for two or three samples.

This is an allowance receipt, not physical settlement. A future live caller
would still have to settle all work in the ordinary runtime.

### Next falsifier

This prior is not yet composed into frontier scoring.

Only after its software invariants pass should it replace the fixed ±100 prior
inside a **test-only** three-leaf water composition.

Promotion requires both:

1. at least one realistic state where the optional trial is selected **with
   strictly positive trial information value**;
2. at least one state where the trial is declined.

A harmful recent history must also remain rejectable. Failure of any of those
conditions blocks runtime integration and any new development panel.


## RMS three-leaf software probe

The zero-mean RMS prior is now composed with the first-person target-modality
probability in
`modules/rms_three_leaf_target_prior.py::paid_rms_three_leaf_target_prior`.

For one target modality:

```text
NO_TARGET                    P = 1 - p_target
TARGET + RMS positive effect P = p_target / 2
TARGET + RMS negative effect P = p_target / 2
```

The full three-leaf expected external bodily delta remains exactly zero.

The target composition also exposes an approximation that must stay visible:
the symmetric `+RMS / -RMS` pair preserves each channel's marginal recent raw
second moment, but represents them through one common-sign rank-one uncertainty
direction. It does not preserve the full empirical cross-channel covariance.

This PR does **not** bind that prior into production cognition. Tests inject it
only into the existing optional water-trial arithmetic from #1094.

The prospective software promotion criteria are:

1. at least one realistic P1.3-like state selects `TRIAL` with strictly
   positive `trial_information_value`;
2. at least one state declines the trial;
3. a high-magnitude personal uncertainty history still permits rejection;
4. the composed prior remains exactly zero mean.

A pass would establish only that personally learned uncertainty scale can, in
principle, create **selective epistemic experimentation** without an additive
curiosity bonus. It would not establish survival benefit or authorize a fresh
development world.


## One future matching opportunity without current-source persistence

The persistence-free #1099 probe establishes that observing the immediate body
after an unsupported drink trial has zero information value under the ordinary
wait/sleep continuation set, even across 160 competing-need states.

The missing quantity is therefore not another effect prior. It is whether the
learned action effect can matter at a **future matching opportunity**.

`modules/water_future_opportunity.py::paid_water_one_future_opportunity_value`
tests the smallest bounded representation of that idea.

It does not assume the currently revealed source remains after the first drink.
Instead it represents one generic future one-cell water opportunity with the
same current first-person water-modality probability already supplied by the
frontier prior.

For each learned RMS effect branch `i` and ordinary continuation `j`:

```text
O_ij = current water trial + ordinary continuation j

R_ij = current water trial
       + one generic future move
       + future boire
       + ordinary continuation j
```

The future `boire` uses the exact effect learned in branch `i`.

Let `p` be the current first-person probability that one generic future cell
offers water.

If no future opportunity appears, only `O` plans exist. If it appears, the
individual may choose between ordinary and reuse plans.

Availability is analytically marginalized rather than expanded into another
simulated subjective outcome:

```text
informed =
  sum_i q_i * [
      (1-p) * max_j O_ij
      + p * max(max_j O_ij, max_j R_ij)
  ]

frozen =
  (1-p) * max_j sum_i q_i O_ij
  + p * max(
      max_j sum_i q_i O_ij,
      max_j sum_i q_i R_ij
    )

information_value = informed - frozen
```

The informed policy knows the learned effect branch after the current trial.
The frozen comparator may still observe whether a future action opportunity
exists, but cannot condition its action choice on the unknown effect.

Therefore `information_value >= 0` is the value of learning the action effect,
not the expected physical payoff of the future action added as a separate
curiosity bonus.

### Branch and cost discipline

The subjective Stage-1 envelope remains:

1. no initial water target;
2. water + RMS-positive effect;
3. water + RMS-negative effect.

The future availability event is not an additional simulated effect branch.
However all ordinary and future-reuse plan cells are actually simulated and
charged before comparison. There is no early stop or value-of-computation rule.

The future opportunity probability is frozen during this calculation. The
kernel does not recursively update the map or run another frontier prior after
the hypothetical observation.

### Explicit limitations

This remains a one-opportunity approximation:

- it represents one future matching opportunity only;
- the future opportunity is one generic movement away;
- it uses the current first-person water-modality probability rather than a
  learned temporal hazard;
- it does not claim the current source persists;
- it does not recursively value subsequent information.

Those restrictions keep Stage 1 bounded and auditable. More general recurrence,
change detection or latent ecological causes remain later-stage questions.

No runtime policy or scientific world is authorized by this kernel.


## Carried unknown food: information without ecological recurrence

The water work isolates an important limitation: information about an action
effect matters only if the individual represents a future opportunity to use
that learned effect. Exact P1.3 water exploration does not provide such an
opportunity cleanly without additional ecological recurrence assumptions.

The owner scenario also explicitly names an **unknown food** case. Carried food
provides a cleaner Stage-1 falsifier because its future opportunity is already
inside first-person inventory.

`modules/carried_food_information.py::paid_carried_unknown_food_information_value`
uses:

- one internal carried token identity;
- the individual's current count of that token;
- existing paid `ReferenceBranchMemory`;
- the current P1.3 simulator and cognitive budget.

No World/source state is read.

### Subjective effect branches

The branch memory is queried for:

```text
("manger", token)
```

Existing precedence is unchanged:

1. latest exact-token support, if present;
2. otherwise latest same-action `manger` support from other personally eaten
   tokens;
3. no global/cross-action fallback.

One retained effect is duplicated into two identical half-weight branches only
to satisfy the existing 2-branch kernel shape. Because both branches are
identical, this creates no information.

Two or three support rows retain equal empirical probabilities.

### Inventory-bounded future opportunity

One carried unit is the current trial.

If `inventory_count == 1`, there is no represented repeat opportunity:

```text
information_value = 0
option_score = expected value of one trial
```

If at least two units are carried, the kernel models exactly one possible
repeat, regardless of larger inventory:

```text
STOP_i   = eat one unit under effect branch i, then stop/bootstrap
REPEAT_i = eat one unit, observe effect i, eat one further carried unit
           under the learned same effect, then stop/bootstrap
```

The informed value is:

```text
sum_i q_i * max(STOP_i, REPEAT_i)
```

The frozen comparator, which cannot condition repeat choice on the observed
effect, is:

```text
max(
  sum_i q_i STOP_i,
  sum_i q_i REPEAT_i
)
```

and:

```text
information_value = informed - frozen
```

This is ordinary expected predicted-distress return. There is no additive
curiosity term.

### Why this case is scientifically useful

A safe-versus-toxic personal food history can make information useful:

- after a benign first bite, eating the second unit may be rational;
- after an integrity-damaging first bite, stopping may be rational.

The urgency and risk then arise from the individual's current bodily projection
and its own empirical effect distribution.

The kernel does **not** command `manger`. It returns only an option score.
A future live policy would still have to compare that score against every other
P1.3 option under one common decision-work forecast and unchanged
Competition/Action Control.

This is also a direct software route back to #1054's unresolved carried-food
case without rewriting P5d evidence.

No scientific study or runtime policy is authorized by this slice.


## Carried-food raw-rank audit (#1103) and future-reuse characterization

The #1103 audit placed the #1102 score beside actual P1.3 witnesses on 27
synthetic states: information positive in 18, **meal rank improved in 0**, P1.3
already eats in 24. A frozen follow-up added opt-in `max_future_repeats`
(default 1 is #1102 exactly) and represented 1, 2, 4 and 8 carried future uses:
still **0/27 improvements**, raw-top fixed at 15/27, information saturating
(0.126 → 0.148) while paid kernel work grows ×3.6–4.8. Verdict
`BOUND_NOT_CAUSAL`: [results](studies/stage1-carried-food-reuse/RESULTS.md).

Harmful personal histories can carry genuine information when their branches
disagree on the best plan (Amendment 1); "harmful ⇒ zero" held only for the
earlier test states.

Information value is bounded by how much the best plan differs between imagined
effects, not by how often it is reused. First contact is the remaining Stage-1
blocker: [decision note](STAGE1_FIRST_CONTACT_DECISION.md).


## ω: inherited expectation toward the unknown (owner decision A)

`paid_recent_rms_zero_mean_effect_prior(..., omega=0.0)`, threaded through the
RMS three-leaf composition and the one-future-opportunity water kernel. The two
hypotheses become `(ω+1)·s` and `(ω−1)·s`: mean `ω·s` on every channel, spread
`s` unchanged, `ω = 0` exactly the zero-mean prior. Paid work does not depend
on ω.

The frozen falsifier passed R0–R3 on the #1101 grid
([results](studies/stage1-omega-software-falsifier/RESULTS.md)), but showed that
the P1.3 projection rewards plan length. Absolute trial and revelation
advantages from this kernel family must be re-read after a bootstrap-consistency
fix.

