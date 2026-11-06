# I3 P5b: first readout-path development diagnostic (NOT scientific validation)

**Date:** 6 November 2026. **Status:** DEVELOPMENT ONLY.
No P5b held-out or reserve world has been opened.
I1 active, I3 an unregistered research proposal. Issue
[#1035](https://github.com/josselin-orta-lab/individual-zero/issues/1035).

## Technical motivation

The [prospective P5a screen](studies/p5a-paid-component-screen/RESULTS.md)
found 112/288 survivors in normal learning and 0/288 when
persistent learned action effects were discarded. The intervention
also raised inactivity to 72.43% and changed realized cognitive
spending. It did **not** distinguish learned information from
structural decision dependencies or energetic mediation.

P5b now preserves the **stored and actually paid** effect-learning
pipeline while masking selected *decision readouts*:
[exact mode definitions](P5B_EFFECT_READOUT_CONTRACT.md). An
observer-only diagnostic counts offered/scored resource, movement,
exploration and rest options, control rejections, funding failures
and admitted physical actions, without affecting decisions or billing.

## Reproducible development-only fixture

`PYTHONPATH=src python -m i3.lab.p5b_development_diagnostic --run-development`
on the exact tested source candidate. Pure
`--manifest` displays fixed development index 20–25
(seeds 2020–2025), three fixed ecological families, two independent
`generation_zero` engineering genomes (seeds 901, 902), and
paired life seeds 460020–460025. Exactly **12 120-step lives per
readout**, 72 lives total; these are **not** new validation or
independent evolutionary populations.

All six conditions reached horizon in 8/12 cases. The small
development fixture does not demonstrate a survival difference.

| Effect readout gate | Inactive steps / 1370 lived | Modeled cognitive energy paid | No processing budget events | Offered resource options |
| --- | ---: | ---: | ---: | ---: |
| `full` | **109** | 756.5394 | 109 | 1,588 |
| `blind_action_predictions` | **841** | 212.1354 | 840 | 310 |
| `blind_sleep_forecast` | **96** | 784.6928 | 96 | 1,507 |
| `blind_sources` | **200** | 649.7206 | 200 | 779 |
| `blind_predictions` (action, passive drift, sleep) | **715** | 287.4086 | 713 | 246 |
| `blind_all` (plus sources/veto) | **715** | 287.4086 | 713 | 246 |

The difference is **not** that all option proposals were lost:
for the action-prediction-blinded mode there were 4,031 offered
choices and 4,029 funded scored choices across the 12 lives. The
large rise in physical inactivity coincides with **840 steps
without processing budget**, versus 109 normal. This is a result
of the altered agent trajectory and body/vigilance funding, not
proof that prediction processing itself consumes more energy.

First difference in paired *physical actions* from the normal
mode, matched by genome/world/life seed:

| Gate | Matched pairs whose actions diverged /12 | Earliest first divergence |
| --- | ---: | ---: |
| Blind action predictions only | 12 | Step 4 |
| Blind learned sleep forecast only | 12 | Step 6 |
| Blind learned source signs only | 6 | Step 13 |
| Blind combined predictions | 12 | Step 2 |
| Blind all learned readouts | 12 | Step 2 |

The first-divergence step is the earliest among all 12 pairs,
**not** a median or population-wide causal effect. Paired lives
which subsequently terminate earlier are compared including their
truncated trajectories. Equal 8/12 end-of-horizon rates can coexist
with very different movement, option budgets and cognition.

`blind_action_predictions` uses a zero-delta unknown prior
and maximal uncertainty for simulated actions, while keeping
learned passive drift and sleep restoration. It **does not**
inject correct environmental dynamics or omniscient resource facts.
`blind_sleep_forecast` masks only learned sleep restoration;
ordinary action predictions and personally observed passive drift
remain. These are diagnostic readout masks, not a new optimal
uninformed agent. The observed control-path collapse may still
be partially mediated by changes in sleep/energy and source choice.

## Evidence gates and next steps

[GitHub CI run 42202272840](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42202272840):
**149 I3 tests passed on both Python 3.11 and Python 3.12**;
original P4a, P4b and P5a complete evidence JSON SHAs remained
unchanged; repository generation-isolation guard still reports
I1 active. CI executed only DEVELOPMENT-world lives, never
the new validation cohort or the reserve.

Next: design a genuinely **structurally comparable first-person
uninformed model** that can still generate and fund options
without inheriting P5a outcomes or privileged physics.
Focus on the earliest decision/energy divergence and
counterfactual financing before any new held-out experiment.
If a P5b scientific study becomes justified, freeze a separate
protocol, sample and exact source before using validation indices
>=72. Use independent genetic populations for inference,
publish actual paid work and negative outcomes, and keep
the P4 reserve sealed.

**No scientific GO, no claim that predictions alone improve
generalizable survival, and no new claims about individuality.**
