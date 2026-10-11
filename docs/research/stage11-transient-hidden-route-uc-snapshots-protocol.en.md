# Stage 11: public 10-step observed-route / transient hidden danger / strict UC / snapshots

**Pre-execution, pre-implementation development protocol registered 2026-10-11.** Sole normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §4.6 external provenance, §14 exploration, §17.2–17.6 replay and snapshots, DC-07, DC-08, DC-11, INV-08, INV-33, INV-44. This is a PUBLIC software diagnostic, not a scientific held-out experiment, historical Golden, scientific acceptance or revision to Stage 9's NO-GO. Historical 8/10-step dead-end and survey-refresh results remain tied to their own SHAs.

## Question and frozen construction

Does the current **already implemented**, opt-in observed-frontier routing retain correct physical provenance, UC charging and deterministic replay when a world-only hazard appears and later disappears, across a full ten-step return-to-junction window? Can complete snapshots at the boundary of two distinct physical hazard states restore exactly without rewriting the journal? Do not implement a new routing mechanism or tune a configuration to obtain favorable movement.

Use the existing public `junction_open` layout, `build_public_route_runtime(..., survey_refresh=True)`, frozen E-v1, ordinary Simulation/Planning/Competition/Action Control, reference START_BODY and conventional world physics. No scripted individual action, hand-authored option, hidden map oracle, automatic safety fact, or direct cognition access to `WorldBody._danger_zones`. The only Lab interventions are **two scheduled, journaled world inputs**, both for location (3,2), not an initial physical fixture change:

- At world step 3, `set_danger_zone`, `sequence=0`, with `active=True` in the hazard variant, and `active=False` in the otherwise matched control. Both schedules must include this input.
- At world step 5, `set_danger_zone`, `sequence=0`, with `active=False` in both variants.

This makes the live danger physically present after step 3 through step 4, and absent after step 5. The individual is never told that this schedule exists. The control has the same external input times, operation names, source structure and sequence, but no active danger.

Run exactly **10 real physical steps**, without changing the route/survey novelty settings. In each variant independently run precisely these **versioned cognitive budgets**: (Planning logical UC, Exploration logical UC) = `(0,0)`, `(3,4)`, `(4,4)`, and `(4,0)`. The values 0, 3 and 4 are preexisting strict-public Planning envelopes, while Exploration 0/4 come from existing public fixtures. No speculative new budget is added.

## Prespecified measurements and negative gates

- Digest the complete public config including protocol name, variant, budget, input schedule, layout, physics/config/Equipment version; collect true world positions after step opening only from `perceptual_capture`, final actions from returned world-step results, actually applied route transits separately from reflexes, visited ledger, charged/rejected UC, and exactly logged `external_input_received` and `external_input_applied` at the two intended steps. Check `journal.verify()`.
- Compare the hazard and control conditions' **first two captured positions and actions**, before the world changes at step 3. These must be equal. Later behavioral equality is **not** required, because true physical harm can subsequently change the body's accessible state. Any hazard recognition is admissible only when justified by the individual's physically accessible history, never by the external schedule or Lab-only world truth.
- Lab-only truth checks immediately after physical steps 4 and 5: active at 4 only for hazard, absent after 5 in both. Record actual damage via `world_transition_experienced.effects.danger_zone_damage`, body integrity and current canonical safety status, without equating damage, threat signals, knowledge or scientific success.
- After step 4 and after step 5, `SnapshotManager.take(PERIODIC)` records complete causal owners (including WorldBody, Scenario, Exploration, cognitive owners and scheduler) at a closed-step boundary, using `t_monde` equal to that step, `cycle=0`, `attempt_ref=None`, and the versioned Stage-11 config. Before each capture, freeze owner states as the reference.
- Independent reexecution uses **exactly the same** input schedule, budget, number of physical steps **and snapshots at steps 4 and 5**. Compare full canonical journal bytes, head, snapshots' IDs/hashes, causal owner states, actions and Lab-scored results. Never compare timelines with different snapshot schedules or pass a restored/cancelled attempt back through the same journal occurrence namespace.
- Only **after** all ten steps and independent journal equality, restore the recorded 4/5 checkpoints for each independent runtime in the same order, compare all owner states byte-for-byte to the values held at capture time, verify snapshot integrity, confirm the WorldBody hazard truth in those restored snapshots, and compare the post-restore append-only journals between both runtimes. Do not execute the old physical step again after restoring in the same journal.
- Failure or zero routes under budgets 0 or 3 is an informative negative result, not an excuse to change thresholds. Do not call a failure to move autonomous rest or safety preemption. If any expected receipt, owner identity, chronology, capture ledger or chain diverges, record the first true divergence, FAIL the software gate, fix narrowly and rerun. Preserve exact results including negative trajectories.

## Fixed software acceptance versus scientific limits

The **software** gate requires the declared input provenance, initial hazard noninterference, bounded UC accounting, physical capture lineage, snapshots' complete ownership and exact independent reexecution. It does not require the individual to avoid an unknown hazard, independently infer the disappearance of a hazard, learn a causal fact, revisit a branch, or succeed in long-horizon planning. Those are empirical outcomes, not pass conditions.

Version this diagnostic separately; record input SHA-256 and output/journal SHA-256 for **every** variant/budget, tested source commit, Python patch, test counts, skipped jobs and limitations. Execute targeted tests before any full CI when possible. No forced CI reruns, workflow trigger changes, merging, normative spec edits, secret exposure or Stage 9 scientific reclassification.

**Stage 11 IN PROGRESS. Stage 9 SCIENTIFIC NO-GO. PR #25 stays open, Draft and unmerged.**
