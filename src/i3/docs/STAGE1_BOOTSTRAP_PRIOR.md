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
