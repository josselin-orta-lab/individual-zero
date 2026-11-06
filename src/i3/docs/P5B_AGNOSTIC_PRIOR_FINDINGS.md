# I3 P5b: action-agnostic first-person effect prior, development findings

**Status: DEVELOPMENT-ONLY ENGINEERING FALSIFIER.** No P5b prospective
held-out study. I1 is active; I3 remains unregistered and the P4 reserve
is sealed. Research issues [#1035](https://github.com/josselin-orta-lab/individual-zero/issues/1035)
and [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026).

## Fixed control and nonprivileged information

A new `effect_readout="action_agnostic_prior"` mode is available
independently of the `learning_mode` parameter. It does not delete
effect records, change their lifetime paid learning, alter motor and
sensorimotor bookkeeping, bypass fitness or admission, or introduce
any world information. All simulated action steps use the **existing**
`EffectsModel` global `("*",)` observed outcome mean and its ordinary
uncertainty. The model is initially unknown (zero delta, maximum
uncertainty) and subsequently knows only the average bodily change
that this *same individual personally experienced*. No proposed action
label or edible-token identity is used in action forecasts.

This is a **partially informed empirical prior**. It retains generic
bodily information but intentionally destroys the correspondence
between action identity and action consequence. Crucially, it is NOT
a clean no-learning individual: learned source signs, learned sleep,
TD value, replay and spatial histories remain in place. Computation
is still executed, paid and accounted for by the original v2 model.
Actual expenditures may diverge because choices and time alive differ.

## Small paired development-only diagnostic

The existing [P5b development diagnostic](P5B_DEVELOPMENT_FINDINGS.md)
uses **six development worlds** indexed 20–25, G0 genome seeds 901/902,
120 physical steps, paired original-world/life seeds and observer-only
funding counters. The new mode adds 12 developer lives, for 84
development lives across 7 modes in this run. This does not open
any validation or reserve condition.

| 12 lives per mode | Full learned effects | Zero action predictions | Empirical action-agnostic prior |
| --- | ---: | ---: | ---: |
| Reached horizon alive (censored) | 8 | 8 | 8 |
| Total physical steps lived | 1370 | 1370 | 1370 |
| Physically inactive steps | **109** | **841** | **894** |
| No processing budget events | 109 | 840 | **891** |
| Admitted actions | 1261 | 529 | **476** |
| Offered choice options | 10585 | 4031 | 3518 |
| Paid cognitive energy | 756.5394 | 212.1354 | 183.5976 |

**A personal global-scale prediction did not restore normal activity or
decision funding**, and on this particular fixed development fixture it
was even less active than a zero-delta unknown prior. This is a useful
negative development diagnostic, not a survival disadvantage: exactly
8/12 lives reach the short horizon in all three modes.

What it rules out *on this fixture* is the simple claim that supplying
a nonzero learned body-change magnitude, while keeping the same interface,
is sufficient to repair the profound activity collapse induced by
masking action-specific predictions. It does not isolate whether the
specific information improves decision values, changes choices that
modify vigilance/energy, or is an architectural dependency.

The observed `no_processing_budget` events occur **downstream** of
choices and actual v2 body trajectories. They cannot be interpreted
as evidence that the initial set of options was empty or that the
control received less nominal cognitive budget. Neither intervention
subsidizes, rescues or forces a survival action.

## Verification and next scientific gate

[Preflight 42212861394](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42212861394)
passed **151 I3 tests on Python 3.11 and 3.12**, generation isolation,
paired development-only diagnostics, and raw uncompressed SHA-256
verification of **unchanged P4a/P4b/P5a original evidence**.
Tests require unknown pre-observation priors, identical readouts for
different proposed actions, exact grounding in existing personal global
observations, no changes to learned statistics during readout, no
unpaid or postmortem work and unchanged normal default behavior.

The next intervention should diagnose the earliest distinct
**first-person decision** before later fatigue becomes dominant,
retaining complete source, option and funding provenance. A stronger
control may separately test the *functional integrity* of a
minimal uninformed consequence predictor and the value of *correct
action-specific learning*. Do not design it using a validation cohort
or use results to tune the old P5a evidence. Before P5b held-out lives,
freeze an independent prospective source/schedule/analysis on
never-used validation indices **>=72**, preserve all 48 frozen G2
reference genotypes and report four independent population units'
limitations. Better yet, preregister more genuinely independent
lineages before making a generalization claim.

No scientific GO, no I3 activation, and no inference of acquired
individuality from this diagnostic.
