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
