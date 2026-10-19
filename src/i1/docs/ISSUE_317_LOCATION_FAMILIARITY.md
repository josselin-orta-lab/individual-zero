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


## Issue #317: observed frontier identity reset, 19 October 2026

In a sealed, physical dry-valley life (seed 1141, engine `2dc4aca7`), the same perceptually admissible frontier (8,7), from origin (8,8), was evaluated in 162 distinct world steps with **162 different Competition option IDs**. The evidence remained low but positive (~0.0207) and no exploration move crossed Competition. The original option ID included `:t<world_step>`, so the candidate accumulated no evidence across unchanged physical contexts. The tracked accumulator of each ephemeral frontier remained below threshold. This is a software continuity defect of the same class as the memory target defect fixed earlier in #317, now independently identified for generic new geographic sites.

Correction: `geographic_frontier` candidates use a stable key from the witnessed destination and current origin (`target.ref`) without an epoch. The fresh `source_t_monde` still validates the current Perception/Phase-1 target at the owner and Stage11 evaluator, and expiry remains real; after a different origin or physical visit the old option is invalidated, not granted an automatic command. Unchanged plans can retain evidence during non-adjudicated fallback. Any material plan change resets evidence through existing Competition, real winners retain residual effects, sleep may still win and Action Control retains final authority. TD, physics, I0, thresholds, exploration coefficients and original WAL are untouched.

Native generated-I1 regression `test_i1_frontier_continuity_317.py` exercises identical first-person frontier across steps, rejection of stale/visited targets, and persistent Competition evidence. An exact source-blob parity lock prevents unauthorized drift. New physical WAL and separate population survival/UC comparisons are required; software success is **not** population GO. The issue #317 verdict remains **NO-GO** until causal benefits of actual entity interactions influence subsequent decisions and held-out physical validation passes.


## Matched physical frontier-continuity result (19 October 2026)

**Exact latest engine** `370f4e99b3f80b931a0513b2bacae8f775163e1b` against
`2dc4aca73a1cabe0e01b23d5f3e3eef76d47b729` (the engine immediately
before frontier continuity). The CI runs completed successfully:
`39207102880` (full and structural), `39207099336` (eight standard-world
lives), `39207099289` (four corridor lives). Compare only paired births
with exactly matching preset, seed, individual ID, initial physiology, and
physics digest. All twelve independently recorded spatial audits report valid
WAL hash custody. Existing diagnostic seeds `1141/1142/2027/2028` are not
independent held-out proof.

Across these twelve *unequally completed* lives:

| Physical outcome | Before | Frontier-continuity revision |
|---|---:|---:|
| Actual lived steps | 3,087 | 3,012 |
| Deaths | 5 | 6 |
| Movement actions | 148 | 191 |
| Memory-guided physically applied movements | 12 | 9 |
| Out-of-sight multihop first steps | 2 | 0 |
| Full remote returns | 0 | 0 |
| Sleep steps | 2,738 | 2,641 |
| Drink actions | 14 | 11 |
| Eat actions | 19 | 18 |

Important **adverse pair** `memory-corridor/2028`: baseline returned from
`(9,8)` to `(8,8)` at step 25 and actually collected, ate, and drank
at steps 26-28, then survived to the horizon of 300. With stable frontier
identity, four *Competition-selected*, *Action-Control-admitted* exploration
moves occur at steps 10, 18, 26, 35, reaching `(12,8)`. Physical water and
food never increase; the individual dies at step 228 due to deprivation.
Memory proposals to previously sighted entities at `(8,8)` remain visible
in the WAL, but have no sufficient positive evidence to win. This is an
observed competing-capability regression, **not** proof that all geographic
exploration is harmful. In `dry-valley` and `blocked-route`, the same
fix unlocks movements previously never selected. The death difference
on only twelve seeds is a warning, not a population effect estimate.

### Narrow causal-temporal finding from lived entity interactions

The existing engine has a first-person water association pathway and
canonical Causal Model contracts; neither currently establishes a generic
entity-specific destination payoff in Stage11. Stage11 reads the TD
`memory_place_return:<sighting>` learned-action value, while Stage8's
return is from physically experienced *movement* after/before the next
decision. This is not a direct learned water/food/poison effect of the
destination.

An independent illustrative chain is present in the authenticated
`foraging/1141` WAL on `370f4e99`: step 18 physically collects
`berry_a` at `(9,8)`; step 19 eats, increasing observed food by
`9.8` after per-step metabolism; step 36 drinks at `(10,8)` and
observed water increases by `39.6`. A first-person lived water
outcome is published on step 37. Physical memory return commands to
`(10,8)` later occur at 64, 87, 103, 170 and 186. **This is evidence
of temporal coexistence, not demonstration that the earlier drinking
benefit caused those returns.** Crucially the `td_update_published`
for `memory_place_return:sighting:water_source:10:8` at step 36
contains `return_g=+1.4` for the *preceding* step-35 movement; it
cannot include the step-36 drinking benefit (Stage8 appends the
current action's reward afterward). Do not treat its positive value
as a learned entity affordance, and do not force an innate
`if thirsty: go to water` path.

**Next hypothesis to falsify:** a generic, provenance-checked link
between a physically encountered entity and a subsequent
independently witnessed interaction is needed before location
memory can safely represent utility, as distinct from TD value of
the motor action. An entity merely co-located with positive
physiology may not have caused it; simultaneous entities make
attribution particularly ambiguous. Require independent controls,
contradictions, and a later decision comparison before declaring
learning-based remote return. The frontier continuity code remains
provisionally useful but global scientific verdict is **NO-GO**.

## 19 October follow-up: causal-contact audit v2, no cognitive intervention

The full I1 CI on `ea229356` and the eight diagnostic world jobs were
successful (runs `39209718974` and `39209714587`). No physical engine
change is made in this follow-up.

The 12 paired physical WALs (`2dc4aca7` vs `370f4e99`) were re-read
against each world's authenticated spatial audit. The operator-side
read-only contact scan found 52 vs 47 physically certified `boire`,
`manger`, or `collecter` actions. Only 5 vs 11 actions had a single
co-located first-person sighting. Another 47 vs 36 actions had multiple
sightings at the interaction site. Benefit in physical telemetry was
observed for 14 vs 11 water increases, and 19 vs 18 food increases.
A learned later memory evaluation for one of the co-located entities was
observed for 5 vs 6 contacts. These are *associations*, not object-specific
causal learning. The populations are diagnostic and unequal mortal horizons.

The first version of `audit_i1_317_contact_causality.py` could be
misread as attributing a benefit to an entity merely co-located with an
action. Its reviewed v2 classification is more discriminating: `manger`
consumes carried inventory rather than an entity necessarily present
on the current cell; `boire` has no entity ID in the physical
command and remains environmental context evidence; `collecter`
has a recorded kind/quantity, which can be matched to a **unique
physically sighted entity type** but does not prove physiological utility.
Every candidate remains `entity_causal_benefit=not_established`.
Two additional adversarial tests now reject false direct credit from
ingestion and from a kind mismatch. No learned entity-value table or
specialized thirst/food navigation rule has been introduced.

For a future scientific GO, compare otherwise matched cohorts with and
without *real lived interaction evidence*, check later decisions and
actual motor admission, then replicate with fresh held-out seeds.
The non-scripted individual must remain free to choose or decline
an entity return; losses of hydration and one extra death after frontier
continuity remain unacceptable to ignore.

## Independent contact audit v3: temporal Q evidence and WAL snapshot

After the completed PASS of the full CI on `87e19c55` and eight successful
physical world jobs (runs `39211034260`, `39211029367`), an independent
review found two methodological risks in the passive contact auditor:

1. A learned memory Q evaluation **after** a contact does not prove that
   the associated TD value was learned **after** the contact. It could have
   been updated during an earlier movement. The v3 audit separately
   reports prior memory-signature TD updates and TD updates following a
   physically certified contact; neither is automatically credited to
   the entity's utility. The tests include both adversarial temporal cases.
2. A WAL might change between its cryptographic verification and later
   classification. The audit now reads original bytes once, seals a
   temporary immutable copy, authenticates that exact snapshot with
   the existing #314 verifier, then parses only the saved bytes. It
   reports the immutable source SHA-256 and checked journal head. Any
   count mismatch fails rather than inventing zeros.

This is **read-only instrumentation and test work**, not a new model of
physiological causality and not a cognitive improvement. The next
intervention must provide a separately identified, genuinely
experienced consequence and demonstrate its role in a later choice.
**NO-GO** remains the global verdict.


## 19 October: authenticated lived TD-to-memory decision bridge (sub-capability GO)

CI run `39213944546` at engine commit `e6644be17cba94479503572badb2eebb3964cd99` **PASS**.
It independently downloaded the *unchanged* foraging/1141 WAL originally
executed by `370f4e99`, authenticated its entire hash chain and classified
the exact sealed bytes (SHA-256
`0894b2a1420513e3a78d4b7b9692342fc1818343548ef8e3b9e0f16df399c22b`,
journal head `b31aa6c9c6aa7209ee9341510238d6b6c4c223bc1e777ce83f32109786aa0677`).
The archived classifier report is `i1-317-lived-td-memory-decision-proof`,
artifact ID `12169010479`. The new read-only
`certify_experience_to_memory_decision` has separately matched ordered
Action Control admissions, command hashes, physical World/Body transitions,
normal committed step closures, earlier entity-place sightings, option
registrations, evaluations and Competition crossing traces.

It certified **one** complete action-credit-and-decision bridge:

- Step 35: physical memory-guided arrival at (10,8), currently known
  `sighting:water_source:10:8`; the option was still unlearned.
- Step 36: physically applied drink, effect `drank=true`, water **+39.6**.
  The TD publication on this step (`return_g=+1.4`) credits the *previous
  memory movement*, not drinking.
- Step 37: TD publication of the previously applied drink
  (`return_g=+24.7`) lists the memory-return signature among updated
  eligibility traces. Other unrelated signatures also receive updates.
- Step 64: the *same* memory-return signature is evaluated with learned
  Q **+2.686204**, simulated evidence unavailable, intrinsic novelty **0**,
  option evidence **+0.241546**. Competition's recorded accumulator is
  **0.287576 -> 0.529123** against threshold **0.5**. Without this
  cycle's positive contribution, the recorded accumulator would not cross
  that threshold. The actual option wins, Action Control admits the command
  and World/Body confirms a movement into (10,8).

This is a **behaviorally certified TD action-value reuse** (local
crossing-dependence), not a policy-level randomized counterfactual and
**not** a proof that the entity itself was beneficial. The reward reached
the spatial option via TD eligibility traces; the causal contribution of
the source versus context remains unseparated. The destination is
adjacent/currently perceptible in the final action, so it does not prove
generalized *remote* returns. This is a **GO only for this narrow
sub-capability** and **NO-GO globally**, especially given the observed
frontier-continuity survival regression. The archive can be replayed
through `.github/workflows/i1-issue317-lived-td-bridge.yml` without
touching original WAL or a living individual. Independent held-out seeds,
counterfactual learning influence and multiple geographies remain open.

## Controlled TD eligibility ablation: pre-registered diagnostic

The laboratory-only script `tools/run_i1_317_td_counterfactual.py`
and workflow `.github/workflows/i1-issue317-td-credit-ablation.yml`
perform two separate mortal canonical I1 births under the same
`foraging/1141` world, physical rules, initial body, engine SHA, horizon,
and first-person observations. The reference life is checked against
historical journal head
`b31aa6c9c6aa7209ee9341510238d6b6c4c223bc1e777ce83f32109786aa0677`.
The experimental arm alters only one operator-side *eligibility-trace weight
update*, at step 37 for
`memory_place_return:sighting:water_source:10:8`, when the TD
transition is `i1_water_probe:boire -> primitive:dormir`.
The prior 36 physical world steps, published return G and TD delta,
remaining updated signatures and the natural trace decay must match
exactly. Each independent birth has its own authenticated WAL, source SHA,
final body, survival status and action distribution. The decision at step 64
is observed but never imposed, and there is no motor rollback, no copied
internal causal state and no oracle.
This is a *diagnostic* on a previously inspected seed, not held-out
population evidence. A difference may isolate the influence of a single
action-value credit; it cannot prove that a remembered entity caused the
drink's physiological benefit. Missing or contradictory observations fail
the experiment instead of publishing a false success. The global
scientific verdict stays **NO-GO**.
