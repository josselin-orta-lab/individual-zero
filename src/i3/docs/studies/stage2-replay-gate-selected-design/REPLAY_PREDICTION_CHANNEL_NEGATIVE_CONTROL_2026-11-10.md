# I3 Stage 2.1: which prediction channel does replay memory content actually change?

**Software-only structural negative control, 10 November 2026. No World, life, ecological or biological inference.**

## Motivation

The recently completed [next first-person decision study](NEXT_DECISION_24_RESULTS_2026-11-10.md) observed a first genuine different-subset replay in **20/24** assigned new units but a different next hypothetical admitted action in only **1/24**. Its 19 shared-action TD residuals are self-bootstrapped quantities and **cannot** be advertised as calibrated predictive accuracy or proof of the usefulness of replayed memories.

Before introducing a new memory-value heuristic, we must distinguish the predictors already implemented:

- The **personally experienced physical-effects forecast**, via `Mind.effects.stats` and `Mind._read_plan_prediction(action)`, estimates an action's physiological transition from the individual's actual past outcomes.
- The **TD learned value channel**, via `Mind.values` and `Mind.value(k, phi, projection)`, estimates discounted self-distress/value including a residual over an innate physiological projection. The replay of an old episodic tuple calls `Mind._td` and updates this value matrix and its replay buffer.

**Hypothesis NC1:** changing only *which already experienced memory indices* are replayed at equal actual algorithmic replay count can change TD values, but **cannot change the already learned physical-effects model or corresponding one-step action-effect forecast**, because this replay path does not update `effects.stats`. A physical-effect prediction loss therefore cannot be used to attribute predictive improvement to this TD replay content selector without introducing some further learning mechanism.

## Fixed source and zero-World execution

Use exactly 48 fixed, existing legal synthetic Mind-memory fixtures from `stage2_replay_content_local.py`. Add the same small, deterministic *synthetic personally experienced* effect samples under the existing `Effects.observe` interface; no true hidden World law, stored World state or future physiological outcome is read. For each source Mind, copy it twice; use identical replay counts **k=3**, original priority vs life-seeded independent HMAC memory identity, actual existing `Mind._td` update on each clone. Do not mutate the source or its random generator. Validate the same model-work allowance and hypothetical physical tariffs for energy/vigilance, but **never claim a living organism was billed**. Compare, for each of 48 fixtures, pre- and post-replay `effects.stats` and action forecasts `attendre`, `dormir`, `boire`, `manger`. Separately compare TD learned matrix and evaluations on one fixed identical hypothetical Body.

**Frozen decisive checks:** all 48 source Minds remain unchanged, all 48 matched clones run three prepaid-capacity TD updates, all 48 effects forecasts match perfectly across content policies and original, while TD matrices may diverge. Record zero-difference TD cases without replacement or favorable stopping. If any replay content changes physical-effect forecast, NC1 is falsified and requires tracing an unexpected cross-channel mutation before further policy development.

**Non-inference:** equality of synthetic effect forecasts does not prove ecological predictive accuracy; different TD values are not necessarily meaningful memories. A hypothetical cognitive-cost tariff is not a debited World bill, and the experiment is not a biological survival or model utility study.

## Next admissible research, independent of owner validation

To evaluate **usefulness**, first define a comparable forecast target that is actually modified by replay and can be scored on truly future first-person observations with immutable *pre-outcome* forecasts, proper scoring, exposed vs censored counts, real action-selection/learning costs and no policy knowledge of the future. If one-step effect prediction does not depend on TD replay content, it is a **negative control**, not a survival-success metric. The design and missingness rules belong to [issue #1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276). There must be no arbitrary water rescue, hidden resource oracle, tuning after negative data or Stage 2.2 authorization.

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage2_replay_prediction_channel_negative_control.py' -v
PYTHONPATH=src python -m i3.lab.stage2_replay_prediction_channel_negative_control probe
```
