# I3 Stage 2.1: effect-forecast sensitivity to TD replay content

**Prospective software-only negative-control contract, 10 November 2026.**
No new World, G0 individual, ecological cohort or biological source is opened by this work. Falsifier for [issue #1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276).

## Why this control is needed

The 24-pair first-realstate source (closed, original SHA verified) demonstrated **17/24** assigned units with changed learned TD values after priority-vs-random replay at the exact same lived state and count. The following new-source next-perception study (closed, independently audited) found **20/24** eligible different-memory selections, but only **1/24** different hypothetical next action. The two studies are distinct developmental samples, not a confirmatory pooled biological sample.

Crucially, the frozen P1.3 implementation's historical `Mind._td` replay changes only `values` and memory `buffer`. Its body-action one-step transition model is separately updated by `EffectsModel.observe` **once on the actual lived outcome** during paid base learning, before optional replay. The replay loop does *not* call `EffectsModel.observe`, and `Mind._read_plan_prediction` draws its action-effect mean from that same `EffectsModel`. Therefore, under **equal pre-replay learned state and actual TD replay count**, a memory-content intervention should produce **exactly unchanged one-step effect forecasts**, even when TD learned-value vectors differ.

This matters: scoring a one-step effect forecast with squared error on a later observed physiological delta is a legitimate *proper point-mean score* for this channel, but it **cannot** identify which memory-content replay selection improved prediction if the forecast channel never changes. A learned value residual is not automatically a calibrated forecast; an absolute TD-error reduction is not an independent observational target.

## Frozen no-World engineering falsifier

Run **48 fixed, synthetic first-person memory/effects cases** from `stage2_replay_content_local.synthetic_mind(0..47)`, with deterministic nonzero `EffectsModel.observe` histories. Compare exactly **three** original `Mind._td` updates on two detached copies of the **same** current source Mind: (P) original descending TD-error priority memory positions, (R) genuinely HMAC-selected random memory positions. The selector reuses the frozen stage-2.1 random-content selector with fixed synthetic life seeds/ordinals; no actual live action or World is generated. Inspect the same five ordinary action-effect prediction readouts for both clones and the learned TD residual at the **same fixed body**. Verify the source Mind's values/buffer/effects/map/history and RNG seal never change; no external CPU is booked as an organism debit. Zero-count replay is a required negative case.

**Predeclared structural acceptance:** all 48 TD replay cases have unchanged `EffectsModel.stats`, unchanged one-step action-effect means/uncertainties, no original Mind mutation, no World, and zero biology/selection claims. There must also be at least one differing selected-memory subset and learned value/residual readout, so invariance is not explained by *no intervention*. If the effects readout changes, fail instead of claiming a positive predictive-memory effect. Do not publish synthetic statistics as 48 independent biological lives or genuine funded cognition.

## Prequential scorer contract

The separate `PrequentialEffectAudit` is an **observer-only software component**, not part of `runtime/life.py`. It accepts two replay-only detached `Mind` models with identical original `EffectsModel.stats`, reference intrinsic weights and projection parameters; it commits a SHA-256 of two identical five-channel mean effect forecasts **after the real action is selected but before its outcome is observable**. A later factual matching action/body observation yields five-channel mean squared error. A terminal/no-next-observed window must be explicitly marked CENSORED with a fixed reason and **no** imputed zero score. Duplicate IDs, post-result substitutions, altered action keys, nonfinite Bodies, missing commitments and scores for unobserved counterfactual actions fail closed.

This scorer can measure how well the current **effects model** predicts *realized* changes, conditional on the executed action and the precise accounting boundary for the Body. It cannot rank replay contents when both predicted means are equal. It does not automatically obtain paid real cognition or an independently attested temporal data source by being a laboratory class. Any later live integration must add a real physically budgeted work receipt and original-before-outcome observation custody without letting the observer choose the action.

## Next scientifically meaningful design

**Mechanism stop condition:** do **not** expend another original-life cohort on P-v-R one-step effect-loss comparison under the unchanged P1.3 TD architecture. The predicted difference is structurally zero by design. Don't fabricate a positive signal by training the effect model differently between arms while claiming only replay content changed.

For a truly replay-sensitive proper score, predeclare a target that corresponds to the learned-value signal and is scored against **future first-person events not used to form the forecast**, such as a finite-horizon *realized discounted bodily distress* series with explicit terminal/censoring rules. Freeze each candidate predicted quantity before observing those events. State whether evaluation is on the actual live policy's subsequent trajectory, so off-policy alternative behavior cannot masquerade as an observed counterfactual survival outcome. In particular, separate observational value forecast calibration from the **causal benefit of learning for survival**. The latter still requires a new well-controlled prospective experimental design, independent ecological iid review, true energy/vigilance funding and no hidden World oracle.

No hand-coded water behavior, posthoc favorable-memory ranking, selection/reserve, Stage 2.2 registration or engine activation.
