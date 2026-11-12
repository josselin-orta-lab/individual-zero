# Stage 2.1 post-hoc zero-change forecast comparator: analysis contract

**Post-hoc comparator, NOT a pre-registered scientific efficacy experiment.** Written after reviewing the exact 320-event receipt from the accepted [#1347 engineering CI](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43209682555), on main baseline `651676a0cd7b60045a5ebd5f52553e9732bbbee9`. This document freezes the **reanalysis mechanics** before creating the repository's reproducible read-only reducer. It does **not** claim that the zero-change comparator was selected before seeing these data.

## Motivation and fixed dataset

The [native-effect prequential observer](../../../lab/stage2_native_effect_reliability_observer.py) previously reported that observed squared error dropped from first unseen to later seen action keys. That mixes time, actions, physiology and ecology. The accepted CI receipt includes pre-outcome native five-channel predictions and genuinely subsequent post-paid-learning body deltas, so a **paired, post-hoc comparator** on exactly the same recorded facts is possible. Its purpose is to identify an inference limitation, not to certify generalization.

Use only the complete `I3_PREQUENTIAL_NATIVE_EFFECT_RELIABILITY=` JSON receipt in the **Python 3.11 exact-head job log** of [Actions #43209682555](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43209682555), source commit `7f32f33172c4773bf4c5630ff945f0b1df6dbb8e`, with matching aggregate report digest `86f7db8524783a249ec2e1363c3f149f94af1eed1dc09ba32724a9c9bade8373`. The corresponding 3.12 log has the same digest. Exactly four engineering units: dev-open-field / 840061, 840062 and dev-failing-well / 840061, 840062; horizon 80 each, 320 actual events. Do not alter observations, outcomes, populations or old forecast code; do not re-execute `World` or `run_life`.

Create one immutable **read-only derivative data file** containing the four ordered units, every event's immutable preoutcome forecast delta, actual subsequent delta, exact-key count and original preoutcome SHA, plus source CI reference/digest and event counts. Treat this file as a transcribed **derivative** of the public original log, not an independently witnessed source. Fail on any null action, terminal, missing forecast or missing target under this fixed-source claim; do not selectively remove events. Preserve five-channel precision as recorded.

## Analysis defined before reducer implementation (but after seeing primary outcome)

For each of the 320 event records, compute the five-channel squared loss of:
- **Native model:** mean of `(actual_delta[c] - forecast_delta[c])**2`, c=0..4.
- **Zero-change baseline:** mean of `actual_delta[c]**2`, same factual target and same event.
- **Paired gain:** `baseline_loss - native_loss`. Positive is better native prediction.
- **Within-event wins:** count native/baseline/tie at a strict absolute tolerance of 1e-12. These are descriptive counts of temporally autocorrelated events, not independent trial wins.
- **Source split:** `source_count_exact == 0` vs `> 0` solely as a description; not a causal estimate of learning or future calibration.
- **Unit-level table:** report all four unit mean native loss, baseline loss, paired gain and same-event counts. Then aggregate the four **equally sized 80-step units**, without treating 320 steps as independent for confidence intervals.

No new trial, seed, cutoff, target, cost tariff, action scoring, memory representation, model fitting, learner update, policy feedback, statistical margin, p-value or survival test. Include a sensitivity diagnostic for unequal unit weighting if needed, clearly secondary. The already inspected posthoc result suggests the aggregate improvement may concentrate in one trajectory; preserve that unfavorable heterogeneity, do not discard it or invent a significance level.

## Integrity and falsifiers

A deterministic, no-World reducer/test must validate exact source identity, four predeclared units and seed/world pairing, 80 unique ordered events per unit, all 320 all-assigned steps, valid 5-channel finite numeric forecast/outcome arrays, exact-key nonnegative counts, nonempty pre-outcome SHA, source-linked digest, and no added/fabricated data. Tests independently hand-calculate a few synthetic *unit tests* for the **pure reducer**, without invoking `World` or `run_life`; a simulated test vector is not a new scientific life. Full repository Python 3.11/3.12 CI and identical canonical statistical receipt are required before merging.

Possible outcomes are finite descriptive score differences, unit heterogeneity or data integrity failure. **Even a positive aggregate cannot establish marginal value of an optional calculation**, because the baseline is not an equal-work real computation fed into motor choice and does not produce factual alternative actions. Original Stage 2.1 `NOT_ISSUED`, embargo on scientific Worlds and original cohort sources, I3 reference/I1 active and E3 negative stop are unchanged.
