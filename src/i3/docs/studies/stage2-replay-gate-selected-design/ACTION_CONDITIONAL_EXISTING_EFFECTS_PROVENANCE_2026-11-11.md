# I3 Stage 2.1: provenance of an action-conditioned passive self-distress forecast

**Prospectively frozen SOFTWARE-only experiment, 11 November 2026.**
Baseline `main` `f6021034507665f19c314c3ff76b6f7a614e30e7`.
Issue [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) and
tariff [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283).
Prior independent technical evidence [#1292](https://github.com/josselin-orta-lab/individual-zero/pull/1292)
found, after equal counted calls and native cost, trained *action-agnostic*
direct-distress predictions had higher squared loss than paid-discard
on all three fixed engineering sources. Do NOT retune on, or rerun,
those completed source seeds.

## Source provenance restriction and causal distinction

The actual reference `Mind.buffer` stores only
`(abs(TD-error), before-body, after-body, dead)`: **no action label**.
Thus one CANNOT train an action-conditioned history from this buffer
alone; inventing tags, deriving actions from the future, assigning
the most recent chosen action to past transitions, or peeking into
a `World` is forbidden. However the *already-funded* native
`Mind.effects.stats` stores learned first-person mean body-deltas
indexed by **observed action and internal token**, including an
action-level fallback `(action, None)` and single-key actions.
This stored model is *already updated by normal prepaid reference
outcome learning*, not a new born individual's learning rule.

**H0**: a strictly read-only projection of native already-learned
action-level effects fails to respond specifically to the
already-chosen action, or produces an apparent response even when
there is no action-specific first-person evidence.

**H1 software capability**: the same frozen personal body and same
frozen effects state can yield two distinct action-conditioned
predictions **only** when the original Mind has separately observed
different effects for those real action labels. An unknown action
must fall back to its existing global-effect estimate, not a
new hard-coded behavior or resource identity. This test establishes
label sensitivity and source custody, **NOT** out-of-sample value,
action advantage, counterfactual outcome or survival.

## Frozen readout and targets

Use `Mind.effects.predict(key)` with **only the current action
already emitted by `Mind.decide`**, no candidate action suggestion,
score or motor control. Query the action-generalized model key
`(action,None)` for two-part action records, or `(action,)`
for single-part action records, based solely on the actual
presence of first-person observed model statistics; never pass a
World token/stock/position or a new action preference. For missing
action evidence, use the *existing* learned global `('*',)` fallback.
For actual inactivity (`action is None`) also use global and report
action-specific availability **false**.

Before an outcome, compute three **passive** forecasts from the
same current first-person `body` and innate `Mind.feats/distress`:
1. `action`: existing personally learned action-conditioned mean
   body-delta, clamped to [0,100] on each channel.
2. `global`: existing paid action-blind global mean delta `('*',)`,
   same clamping and innate distress.
3. `persistence`: the unchanged current body, i.e., zero delta.

The scalar point target (for a **future** prospective experiment only)
is the existing innate `-Mind.distress(Mind.feats(actual-next-body))`,
or `-d_max` if **actual** terminal. Squared loss is proper for that
scalar target. The predicted delta **does not** carry a death oracle;
terminal/death can only be known when scoring later. The native effect
model is updated after the I3 runtime's outcome-learning debit and
may use final post-learning body, whereas an external same-tick
`World.step` witness observes the earlier body. This **target timing
mismatch must be tracked** before claiming predictive utility.
No new reward function, manual action preference, or imagined future
resource is supplied.

## Fixed synthetic-only falsifier, first gate

No World, no scientific birth, no real engineering life opened. Use
a fixed internal synthetic reference genome `midpoint()` with
synthetically populated *EffectsModel* `observe` records:
- contrasting learned `attendre` vs `dormir` deltas at identical
  current body, with separate positive direct evidence; prove only
  the `action` readout varies with the **action label**, while global
  and persistence stay unchanged;
- action with no directly learned action-level model must have exact
  global fallback and explicitly `action_specific_history=false`;
- learned two-component keys (resource-actions) must use the native
  **action-generalized** `(action,None)`, never hidden item identity;
- identical mean action effects -> exact null contrast despite
  two different labels; terminal actual outcome -> adverse
  `-d_max`; invalid body/action/forged or wrong preselected action
  -> fail closed; prior-before hash, chosen action and scalar forecasts
  must be SHA frozen before synthetic outcome score and cannot be
  overwritten.
- `Mind.buffer` remains action-unlabelled; no changes to original
  `Mind`, `EffectsModel`, `World`, `runtime/life.py`,
  `BodyLaws`, P1.3 or genomes. The observer must not mutate
  learned statistics or live RNG.

Print fixed synthetic results as technical receipts, including
positive, fallback, null, terminal and invalid cases. Unit tests
must run on Python 3.11 and 3.12 with full I3 software suites and
owner/generation/navigation guards. No import from retired Stage 1.

## Gates and future authorized path

**Technical gate only**: pure provenance-consistent action sensitivity
with explicit fallback and source/no-future/tamper controls. The
`EffectsModel` training costs were genuinely paid *only when normal
run_life executes them in a previously authorized organism*; these
synthetic fake stats are NOT proof of a paid living history. The new
external scalar readout/hash are **UNPAID observer computations**;
this experiment cannot be reported as an endogenously funded
deployed cognitive capability. Nor is equal reading cost across
three passive readouts established. Do not re-label it as a
cost-matched predictive-utility comparison.

A later separate prospective engineering intervention would need
a new exact source protocol, a valid new-World authorization under
`ACTIVE_SURFACE.json`, an explicitly billed budget for the
readout and custody for **actual** next-Body outcomes, and
independent ecological framing. The manifest still reports
`fresh_lived_worlds_allowed=false`: **this PR opens none**.

**Verdict remains** `scientific_lives=0`,
`scientific_verdict=NOT_ISSUED`, I3 unregistered Stage 2.1,
no selection/validation/reserve, no Stage 2.2 or learned
behavioral activation, no survival improvement claim.
