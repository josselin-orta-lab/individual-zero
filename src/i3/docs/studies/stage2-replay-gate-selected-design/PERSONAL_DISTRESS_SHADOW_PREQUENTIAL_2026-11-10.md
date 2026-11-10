# I3 Stage 2.1: replay-sensitive, directly scored distress predictor (SHADOW ONLY)

**Prospectively specified 10 November 2026, before first candidate evaluation; zero new World births or biological cohorts.** Follows the complete [negative control](REPLAY_PREDICTIVE_NEGATIVE_CONTROL_2026-11-10.md) and [issue #1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276).

## The new falsifier

Existing P1.3 TD replay changes `values` and memory `buffer` but not the personally learned `EffectsModel`. In the 48-synthetic-control rehearsal, 48/48 priority-vs-random replay variants changed the learned value vectors but **0/48** changed ordinary one-step action-effect predictions. This makes a replay-content comparison based solely on those predictions structurally uninformative. A genuinely useful forecasting capability must respond to which personal memories were replayed and must be scored against an outcome that was **not** used to make its forecast, rather than a bootstrap of its own output.

**Hypothesis P1 (software mechanism only):** a separate, externally held, replay-trained direct-outcome prediction head can generate different *pre-outcome* forecasts of **next-step personally experienced intrinsic distress**, from two different sets of equally many personally recorded memory transitions, without modifying the living I3 Mind or imposing preferred actions.

**Null:** if the head is not sensitive to which prior memories it replayed, the two forecasts must remain identical at the same subsequently observed Body. A test with no replays or identical replayed memory indices must also give identical forecasts. The mechanism may fail. This is not a test of whether priority replay **survives better**.

## Frozen minimal candidate

Use the existing I3 individual's `Mind.feats`, `Mind.distress`, `d_max`, and genomically inherited `alpha` unmodified. No new genetically fixed preference, survival rule, water target, external reward, instruction to act, or World resource label is supplied. The shadow head is a 6-weight linear correction around the individual's current expected innate distress:

\[
\widehat y(b)=-D(\phi(b))+w^\top\phi(b).
\]

From a previously recorded personal memory `(abs_td_error, before_body, after_body, dead)`, the **direct observed target** is `-D(phi(after_body))` if alive or the individual's existing innate terminal penalty `-d_max` if dead. Apply `w <- w + alpha * (y - yhat) * phi(before) / ||phi(before)||^2`. This is supervised direct-outcome estimation from the individual's own experience, not extra innate guidance or TD bootstrapping. It is **action-agnostic** because the historical replay buffer does not store action identity; therefore any score describes the actual logged behavior distribution and cannot be used as an off-policy action-value oracle.

The source Mind remains unchanged. **Each head seals the eligible replay buffer when cloned from the pre-fork source and will train only through indices into exactly those stored historical memories.** An injected, replaced or appended future outcome, an index replayed twice or a total exceeding the existing one-fork cap fails before any update. Two heads cloned from one source receive identical `k=3` shadow replay updates, selected by original descending absolute TD-error memory order or genuine life/ordinal HMAC random content. All head CPU and memory work are external lab computation **not paid by the live Body**. The candidate must remain **outside** `runtime/life.py`, Action Competition and the active engine until a separate physical tariff, real-world observer neutrality and proper prospective sources are available.

## Prospective evaluation

Run **48 synthetic trials** using fixed personal-history fixtures 0..47 of `stage2_replay_content_local`. The *training source* consists only of the existing 12 `(before,after,dead)` memory tuples of each fixture. Frozen held-out *before-body* observations use indices >=12 and distinct synthetic next transitions generated **only after** two forecasts have been committed to an SHA-256 receipt by `PrequentialDistressAudit.freeze`.

The evaluator observes the actual next Body and terminal flag after the forecast seal; it computes the innate next reward directly from that observed outcome, never from learned TD weights, a World stock, a water location or a value bootstrap. The squared loss `(predicted_next_intrinsic_reward - observed_next_intrinsic_reward)^2` is a **proper score for a point prediction of the conditional mean**. All 48 forecast windows must be scored and none silently omitted; in later non-synthetic contexts, horizon/missing events require explicit right-censor receipts without zero imputation, while a genuinely *observed terminal* is scored as the individual's original terminal penalty.

**Primary structural readout:** count of the 48 trials with different pre-outcome forecasts after different replay-memory selection, with equal count, and zero differences on no-replay/identical-content controls. **Secondary exploratory** counts of synthetic held-out squared-error signs (P lower / R lower / tie), with no favorable-selection stopping and **no statistical survival/generalization claim**. The fixtures are deterministic, similar and not independent F0 ecological lives. A lower synthetic squared error does not establish effective memory selection, a future survival benefit, true paid cognitive efficiency, causal mediation or ecological transfer.

## Fail-closed contracts and next research decision

- Require strict same source Mind/genome and equal head update count before paired forecast; reject mixed source, unfunded/stale identity, repeated outcome and altered preoutcome seal.
- Reject malformed Body, nonfinite result, non-boolean death flag, ineligible/duplicate memory indices, invalid right-censor reason or replacing a missing forecast with a favorable invented score.
- Apply the current fixed inherited learning rate to shadow only. **Do not** tune the model on the 48 held-out results; any later changes require a new source and declared hypothesis.
- Zero World births and no physical cognitive debit are explicit report fields. No prospective scientific original sources are consumed.

**Gate after this experiment:** if prediction sensitivity exists, an engineering design may study separate *real physiological two-currency pricing* for creating/maintaining this head and using it only on first-person logged events. A live-use proposal must define whether and how it alters Action Competition; observer neutrality and an independent ecological frame must precede new scientific lives. Do not register I3, select/validate/reserve lineages, or activate Stage 2.2 on shadow outcomes.
