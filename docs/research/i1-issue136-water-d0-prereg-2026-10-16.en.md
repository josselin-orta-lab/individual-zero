# A2.33-I136/D0: I1 water acquisition and transfer, preregistered baseline diagnostic

**Registered:** 2026-10-16, before writing/running the dedicated D0 executor.  
**Source frozen for comparison:** I1 experimental PR #219 head `ebe91baf0f8493f3f4d17fa6357bce3b4a736036`, descended from immutable I0 main `8ce8711b2d5f86b184d66fcee1d95a3e39f30836`.  
**Issue:** #136. **Outcome permitted:** diagnosis of existing I1, NOT proof of first-person water learning, held-out generalization or Stage12 acceptance. I0/WorldBody/M11/spec are unchanged.  
**Historical context:** #135 demonstrated real drinking only with extra **prebirth external** exact-model transitions. A2.31 active I1 had 8/8 hidden-lethal deaths ON versus 0/8 OFF. A2.32 found learning unproven, and its runner deviated from registered body settings. Those historical cohorts do not count toward this D0 sample.

## Code-grounded mechanism to falsify

At the registered SHA, experimental I1's active partial model only handles `MOVE_E` and `COLLECT_B`, has `source_scope=external_lab`, freezes its deltas at birth and, when exact Stage6 produces no option, offers a supplementary proposal only for `goal_type == "eat"`. The inherited exact `FrozenTableEquipment` is an offline-born immutable table. No authenticated `observation-before -> applied-action -> subsequent first-person observation` flow refits this equipment in the active I1 runtime. A future learner must NOT be inferred merely from event counts or from the existence of autobiographical episodes.

**D0 hypothesis:** switching the *existing* I1 partial food model ON does not create a water-directed proposal or in-life update of either equipment artifact. Any incidental drinking by exact Stage6, exploratory behavior or default drives is reported separately. A new model must be registered, implemented and prospectively assessed in another phase before a first-person water-learning claim is meaningful.

## Fixed D0 study allocation (prospective, diagnostic only)

- **4 water layouts x 4 index variants x 2 I1 mortal births = 32 distinct lives / 16 matched pairs.** Layouts: water on current birth cell (`local`); visibly adjacent north (`north`); visibly adjacent east (`east`); water two steps south (`south2`, not initially adjacent). All use separate WorldBody, I1 identity, journal and WAL. Order ON/OFF alternates with index parity. No inter-life continuity, transferred memories, shared journals, artificial resurrections or operator-provided commands.
- Normal WorldBody physics with unchanged 32x32 geometry and mortal conditions; `enable_geography=True`; no berry/creature/obstacle/danger resources in these diagnostic water worlds. Start body `energy=65+(index%2)`, `food=80`, `water=20+index`, `integrity=100`. For every arm, use the same fixed inherited Stage11 exact equipment. All births use the development-only fatigue/sleep profile from A2.31: `fatigue_gain=0`, `night_weight=0`, `consolidation_weight=0`. No other cognitive threshold or horizon adjustments.
- The ON arm has the explicitly opted-in existing active I1 partial model. Fit its birth artifact from 8 genuinely physical external `MOVE_E` and 8 external `COLLECT_B` transitions in independent **training-only** WorldBody instances, never from a scored life. The OFF arm excludes it. This training is NEVER first-person acquisition. Train nothing on water or `boire`. Never read held-out world truth to produce model inputs or commands.
- **At most 8 real WorldBody steps per life**, stop at death, block, technical halt or exception. Do not manufacture the missing steps. Python 3.11 and 3.12 re-run the same cohort, NOT independent scientific replicas. Preserve every negative/noncompletion result.
- Model ON and OFF comparisons concern *current I1* on different, authentically independent births; this is not a controlled test of a future on-life learner. The public scenario specification is available to the external scorer only. No Oracle, Bench or hidden-truth data enter cognition.

## Predefined endpoints and interpretation

For each life retain source SHA, experiment/world/life IDs, layout and birth body, exact equipment digest at birth and after, sealed model corpus digest if ON, ordered admitted/applied physical commands, before/after visible water, final mortal status, actual time steps, journal bytes/hash and durable WAL audit, `i1_partial_preaction_forecast` and `i1_partial_instrumental_option_proposed` evidence, `stage6_planning_result` status, `stage12_goal_progress_followup` outcomes, and accepted/refused `i1_partial_model_forecast` UC charge receipts. Count all nonapplied/blocked steps and missing followup outcomes explicitly.

A **drinking event** requires a physically applied `boire` action plus measured water increase on that real step. An admitted/proposed/forecast-only `boire` does NOT count. A lived **water model acquisition** requires authenticated pre-action capture, real applied command, admissible subsequent visible outcome, an individual-owned first-person model state transition, durability/M11 recovery and later causal use, within the **same** life. Neither frozen E nor imported external model training qualifies.

D0 contract checks (software/diagnostic, not Stage GO):
1. **No water-origin I1 partial proposal**: zero model-origin `boire` or water-goal proposals across these 32 lives (if nonzero, examine as contract regression).
2. **No hidden refit**: each life retains the same exact equipment and partial-model birth digests (if changed without explicit lived custody, investigate).
3. **Integrity**: 32 independent mortal records, no post-death actions, WAL/journal verified and no Oracle/Bench input; any violation is HARD NO-GO.
4. **Accounting**: publish ON/OFF water successes, physical steps, unexpected deaths, failures, accepted/refused UC and model-origin actions, with denominators including all births, whether successful or not. No scientific benefit threshold is asserted for these deliberately low-powered diagnostic cohorts.

**Explicit unknown:** These water positions alone do not test unseen-world transfer by a newly learned model. A D0 pass establishes only wiring and limitations; it cannot close #136.

## Required next registered experiment D1 (NOT performed by D0)

Build a separate I1-only **first-person equipment acquisition owner** from authenticated per-life captures and applied transitions, with explicit source identity, observable/unknown components, uncertainty, UC costs, M11 cold-recovery state custody and default-OFF opt-in. Preserve Stage9/DC-05, a single Action Control dispatcher and immutable I0. Preregister, *before tuning*, multiple independent learning lives versus frozen-E controls, disjoint held-out water-location families, delayed followups, mortality/hidden lethality controls, UC opportunity costs, and causal proof that a lived update preceded a changed decision. Prevent using one life to train another, or scoring held-out outcomes in a living model. A matched protocol with no improvement may refute the mechanism; no improvement must be honestly `NOT_DEMONSTRATED`. A favorable cohort would still need 600 genuine stage-relevant physical development steps, longer-horizon persistence, independent raw-artifact audit and explicit operator acceptance, never automatic Stage9/Stage12 GO.

**Decision register before data:** #136 remains OPEN, scientific acceptance PENDING. The D0 executor and workflow must be committed after this preregistration, preserving its commit SHA.
