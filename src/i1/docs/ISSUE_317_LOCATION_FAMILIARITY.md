# Issue #317: separating spatial familiarity from learned usefulness

**Experimental architecture correction.** This is not a survival guarantee or a scientific GO.

## Evidence motivating the change

The untouched held-out matched cohort (seeds 3011, 3023, 3041, 3067, 3083, 3109, 3121, 3137) produced, on each of the previously pinned engines, 1,103 registered out-of-perception multi-hop proposals, none crossing Competition and none carrying relevant learned Stage8 value. Meanwhile, 238 physically certified memory actions accompany 261 reversals over 281 physical movements, many oscillating between only two known cells. The original WALs are immutable: [audit run #39200154369](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39200154369). These numbers establish an important failure mode, not the behavioural effectiveness of a prospective repair.

The Stage11 memory evaluator previously provided the same positive intrinsic motivation to return to a sighted place even if its location was physically visited already. More confident/frequent observation could make a familiar location more attractive purely due to recognition, independently of learning a beneficial consequence. This is an architectural conflation of *spatial information novelty* and *learned utility*.

## Correction and scope

Stage11 now consults only GeographicExploration's own recorded first-person physical visit ledger (constant-time `has_recorded_site(target.observed_position)`) while evaluating an already valid and funded memory option. If the individual has **personally visited that location**, informational novelty of that *location* is exactly zero. An as-yet-unvisited previously sighted location retains its existing confidence-weighted intrinsic interest unchanged. This is **generic across entities**. There is no innate relation between water and thirst, berry and hunger, or any object and an outcome.

Stage8's original, truly learned/simulated evidence passes through unchanged, even for revisited sites. The memories, their confidence, route proofs, TD updates, Competition thresholds, motor vetoes, physiological parameters, death and M11 state are untouched. This does **not** classify sites as beneficial or dangerous, nor prevent a learned positive value from overcoming zero spatial novelty.

The existing paid memory evaluation already has access to Exploration's owner; no extra world read, map oracle, phase-1 prediction, new UC charge, memory state, mutable cache or serialized field has been introduced. The Stage8 evaluation signal records whether its site interest was previously visited, enabling physically verifiable attribution.

## Falsification gates

- Generated current I1 unit test: identical result for water, berries, wood and unknown objects; *first* observed site retains previous intrinsic interest, a witnessed previous visit removes **only** location interest, learned extrinsic Stage8 value still contributes.
- CI, parity, M11 cold recovery, all four native preset worlds, corridor motor and authenticated WALs.
- Compare 1141/1142/2027/2028 development worlds first, without changing parameters based on held-out seeds 3011..3137.
- After the code is frozen, validate against **new independent** seeds. Count remotely unseen first hops and complete returns separately, physical swings and actual UC, consolidation, sleep, drinks, death, TD and actual entity interactions.
- If useful learned returns disappear, any vital need degrades or oscillations persist from apparently positive TD, audit temporal credit attribution rather than forcing coefficients or lowering the Competition threshold.

No merge or issue closure until scientific robustness is demonstrated; I0 and PR #316 remain untouched.


## 19 October 2026: independent WAL comparison and TD-credit diagnosis

**Scientific verdict: NO-GO globally.** Matched births, same 300-step requested horizon (mortal lives stop on death), old code `b56b4c053a2d` in the four standard worlds and `eef98704569e` in memory-corridor versus `a657a2542935`. The different baseline SHAs reflect the pre-familiarity code lineage, not a claim that one code SHA covered all worlds. Provenance in the sealed per-life report, WAL journal head, and verified hash chains. Compare only the identical world/seed/birth pair. The old 1141/1142/2027/2028 seeds are development diagnostics, not final held-out validation.

Across the twelve paired lives (3,087 lived steps on each side): movement actions 174 -> 148; A-B-A reversals among successive movement actions 34 -> 13; physically certified memory moves 31 -> 12; remote first hops 4 -> 2; sleep steps 2,661 -> 2,738; drinks 16 -> 14; eats 24 -> 19; deaths 5 -> 5. In corridor seed 1142, the prior revision had three physically certified full remote journeys after sleep; the new revision produced zero. This is a **loss of demonstrated capability on this diagnostic cohort** despite lower local reversal count. A-B-A is not inherently pathological, and fewer moves is not itself better cognition.

Charged UC across all twelve lives: 94,413 -> 102,475 accepted (+8.5%), with zero rejected in both sets. Planning: 28,454 -> 33,108; Competition: 28,908 -> 31,447. No blanket resource efficiency improvement can be claimed.

### Learning interpretation, not an innate object-affordance map

The Stage8 runtime reads the **actual** before/after physiology following the applied action and computes `ValueAndNeeds.reward_between` as reduction in weighted distance from physiological setpoints. Hence a negative change in a body variable *can* have positive value if the variable was above its setpoint. In the twelve current physically certified memory movements, twelve next-decision TD publications carry a positive one-step return `G` between +1.4 and +2.2. The underlying authenticated `World/Body` transitions are all **movement only**, with a common immediate physical delta (energy -2.0, food -0.2, water -0.4, integrity 0). No water consumption, food consumption, entity interaction, or directly beneficial destination effect occurred *in those movement steps*. These TD values are not invented and can validly encode contextual homeostatic action value; **they do not establish causal usefulness of the remembered entity**. Across the twelve publications, 72 non-memory signatures were also listed as updated in the eligibility-trace fields. TD trace propagation therefore requires separate assessment from direct entity credit.

`tools/audit_i1_317_loop_diagnostic.py` now has read-only `audit_memory_td_credit`, invoked *after* independent WAL authentication, and reports a separate classification of physical action credit vs unproven entity affordance. It verifies the memory signature, admitted Action Control command/hash, ordered physically committed transition and closure, observed position and body, decision spacing, and reward publication. It rejects ambiguous, missing or out-of-order proofs and never fabricates unavailable metrics or changes any cognitive state. Synthetic adversarial regression tests in `tests/i1/test_i1_spatial_wal_audit_314.py` check false positives.

### Architectural consequence and next falsification gate

The current `memory_place_return:<entity_id>` signature follows the remembered entity-place, yet the reward is on the movement action and eligibility traces. It must not be reinterpreted as learned water, food, toxicity or other object-specific affordance. Before changing TD or Stage11 again, design controlled counterfactual experiences to distinguish contextual homeostasis, neutral movement, genuine interaction effects and delayed utility, then measure whether the *resulting learned value* causally changes a later memory-guided choice. Preserve Stage8's normal online TD, deaths, Competition, Action Control, M11 and I0 while doing so.

Do not merge PR #318 or close #317 based on the reduced A-B-A count. Independent reserved seeds, certified useful returns, survival/UC guardrails, M11 cold restore and CI remain required.


## 19 October: first-person encounter chronology correction (pending physical GO)

Source audit found a distinct potential defect in the 19 October familiarity
change: a cell can have been visited **before** an entity is first seen there.
A location-visited flag alone then zeroes informational novelty even though
I1 has never revisited that newly sighted entity-place. The owner already
holds `PlaceMemory.first_seen_step` and `reached_step`, each born from real
Perception; the Stage11 evaluator now consults this existing owner record.
Only a physical arrival after that first sighting exhausts *encounter-site*
novelty. An inconsistent or stale memory is unscored, never granted a new bonus.
This distinction neither creates a causal experience nor increases novelty
for previously reached entities; TD/simulation values stay unchanged. No
new M11 state, owner, world fact, sensory prior or tuned threshold was added.

This is a **software counterexample**, not a proven explanation for the
observed oscillations: in the twelve previously inspected development WALs,
none of the first entity sightings had an older recorded visit at the same
site. A new physical counterexample and matched holdout population are still
required before scientific GO.
