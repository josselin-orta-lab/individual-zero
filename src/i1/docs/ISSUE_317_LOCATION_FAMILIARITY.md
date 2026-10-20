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

## 19 October: paired physical TD-action credit ablation, diagnostic seed 1141

Independent physical evidence was recovered from the failed CI workflow
`39221582215`, artifact `12172506274`. The failure was in the
**operator-side comparison code**, after two 300-step lives ran: it
referenced non-existent trajectory key `source`, whereas the canonical
observer emits `action_source`. The two real WALs were preserved.

The control WAL contains 31,245 causal entries, SHA-256
`0894b2a1420513e3a78d4b7b9692342fc1818343548ef8e3b9e0f16df399c22b`
and final journal head
`b31aa6c9c6aa7209ee9341510238d6b6c4c223bc1e777ce83f32109786aa0677`,
identical to the prior pinned normal-life evidence. The ablated WAL has
24,390 entries, SHA-256
`5bc90b5d795c4f461aae8ec681f705c1dd6b40e8a9ee3d4783fedee92befca71`
and final recorded event hash
`f1ceb098f3afebde764b2542cb0d7fc3ab4c55c5715873d1939451f8a5e5362b`.
Both outputs deserve the completed independent WAL verification gate in
the repaired CI before being classified as finalized experimental reports.

A passive side-by-side scan shows identical motor/body trajectories until
step 63. At step 37, original and ablated TD publication both retain
`return_g=+24.7` and the same TD delta (+22.4847); only the
`memory_place_return:sighting:water_source:10:8` signature is excluded
from the ablated update. At step 64 the control evaluates Q=2.686204,
intrinsic novelty=0, option evidence=0.241546, crossing Competition
0.287576->0.529123 against threshold 0.5, then physically moves.
The experimental arm evaluates Q=0.242937, intrinsic novelty=0,
option evidence=0.022364; it does not cross Competition and physically
sleeps. **The first physical divergence is exactly world step 64.**

At horizon 300: both individuals survive; movement counts 16 vs 6,
sleep steps 252 vs 271, drinking actions 3 vs 3 and eating actions 4 vs 4;
accepted UC are 10,093 vs 6,740. The ablation makes a large behavioral
difference on this *already explored diagnostic seed*, but does not establish
population-level health improvements or any entity-specific causal affordance.

The schema fix `a34dcfa1`, adversarial schema regression `b742c163`,
and CI gate `9a5ad318` rerun the complete physical experiment and require
the independent proof chain. Until green, treat these findings as
**physical WAL observations, not a complete passing CI experiment**.
The global scientific verdict remains **NO-GO**.

## 19 October: independently completed TD-credit counterfactual

The corrected CI [run 39227788084](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39227788084)
is **SUCCESS** and emitted artifact `12175187205`, containing the independent
control and ablation mortal WAL plus `report.json`. Code pinned to
`9a5ad3184e872ee2c6ec9d15e6876ec16eeb6ced`.
Both WAL custody chains authenticated independently, control head
`b31aa6c9c6aa7209ee9341510238d6b6c4c223bc1e777ce83f32109786aa0677`,
ablation head `f1ceb098f3afebde764b2542cb0d7fc3ab4c55c5715873d1939451f8a5e5362b`,
each 300 physically lived steps and both alive at horizon.
The same credited TD reward (+24.7) and delta (+22.484721705494092)
were preserved on step 37 while only the designated memory action's
eligibility update was withheld. The first physical divergence was step
64: control Q=2.686204, evidence=0.241546, Competition crossed and its
admitted memory command physically applied; ablated Q=0.242937,
evidence=0.022364, no crossing, physical sleep. Both lives consumed
water 3 times and ate 4 times, but moved 16 versus 6 times and slept
252 versus 271 steps.

This supports a **single-world, single-seed intervention-specific
influence of past experienced TD credit on a future physical decision**.
It does not demonstrate causal affordance of the water entity, nor that
either motor policy is healthier, nor generality. The existing independent
held-out cohort is not an independent validation of this intervention.
New optional `--inspect-signature` in the researcher-only comparison tool
lets an observer read a *different* memory signature than the one
ablated; no decision or model state is changed by that diagnostic input.
This is groundwork for negative controls, not evidence that such
controls have yet been experimentally validated.
Global #317 scientific verdict remains **NO-GO**.

## Independent sealed TD-specificity negative control (19 October 2026)

The separate CI workflow [#39234321213](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39234321213)
is **SUCCESS**. It independently reauthenticated both existing paired
mortal WALs from physical run `39231424425` using the #314 cryptographic
verifier, compared their immutable SHA-256 and journal heads to the
paired source report, certified 300 physically applied/closed world
steps per arm and reproduced the first physical divergence at step **64**
(control moved, ablation slept). New reusable read-only
`tools/audit_i1_317_td_credit_specificity.py` and five adversarial tests
`tests/i1/test_i1_td_credit_specificity_317.py` enforce the evidence
boundary: an absent or invalid Q is never converted to zero, mismatched
pre-decision evaluation counts fail, and unrelated Q contamination is
reported. The archival CI report is artifact `12177573671`.

Before and including the first divergent physical world step the
auditor compared **383 non-target learned-Q observations** matched
across the two WALs, finding **zero different values**. The targeted
`memory_place_return:sighting:water_source:10:8` learned-Q differs
already at step **58**, again at **64**, but no physical divergence occurs
before step **64**. At that step the control crossed Competition and
physically moved; the ablation did not cross and physically slept.
Differences in option-level normalized Competition evidence and number
of evaluations after a divergent decision must be distinguished from
changes to Q weights or benefits attributed to other entities.
The audit thus supports a targeted **learned-action-credit effect**
on this one deterministic life, not an object-affordance map or a
population estimate.

Scientific scope: **GO for the narrow within-life intervention-specific
effect and negative-control Q isolation; NO-GO globally**.
Do not merge/close #318/#317 before held-out seeds, several geographies,
survival/cost guardrails, and a separately justified causal interpretation
of entity interaction consequences.

## 19 October: independent twenty-life population, physiological wake recursion

The pre-registered population on unchanged canonical I1 engine
`28dfa62d6cf05ebecd1d2767769aa6ae53224616` has completed
successfully: [run #39243776617](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39243776617),
report artifact `12182895902`. All 20 original mortal WAL chains, fixed
birth identities, exact preset/physics digest and matching Git SHA were
independently authenticated by the aggregate job. This was an
*observation-only* study, not paired with an alternate cognitive engine.

Results: **15 deaths among 20 births**, 4,658 lived steps, 4,058
physically executed sleep actions (**87.1189%**), 284 movements, 8 drinks,
20 eating actions, 230 consolidation commits and 199,452 accepted UC.
By world, deaths: blocked-route 4/4, dry-valley 4/4, foraging 4/4,
memory-corridor 2/4, oasis 1/4. Across 3,729 registered memory-place
proposals only six crossed Competition; four yielded genuinely applied
memory-guided movements, all in a single oasis life. A single first
out-of-perception multihop motor step was proven, but **zero completed
remote returns**. 48 physical consumption/collection contacts were
certified, none established a complete strict lived-benefit → TD-memory
→ later physical decision bridge in this cohort. The narrow positive
intervention on old diagnostic seed 1141 cannot be extrapolated.

A further operator-only scan of all twenty WALs exposed a recurrent
specific failure mode in Stage10 wake/Competition, also relevant to
open issue #292: **1,391 wake events marked `alert`**, of which
**1,357** were followed by an *ordinary newly chosen* physical `dormir`
action in the same world step; **1,340** also physically slept on the
next step, according to the source WAL action tables. **2,100 sleep
actions occurred with water zero**, and **3,755 while energy was at least
99**. Reduced capture reports physiological critical channels, wakes
are real, and fresh normal cognition can voluntarily return to sleep,
as opposed to staying in a blocked sleep state. Thus an existing
alert does not guarantee competition against an alternative action.

The permanent regression tool
`tools/audit_i1_317_vital_wake_recursion.py`, synthetic adversarial tests
and `.github/workflows/i1-issue317-vital-wake-recursion.yml` now
independently reauthenticate all twenty original WAL files and distinguish
an actual alarm, resulting competition threshold crossing and committed
physical action. The dedicated audit's GO gate is **not** assumed before
the run succeeds. No sleep refractory rule, compulsory food/water
command, sleep-weight retuning, World modification or I0 edit has been
made. Research next must isolate *why* Stage10 reports repeated alarm
and whether free Competition can find any physically experienced
vital-need action under critical conditions, using matched birth
variants and risk controls. A waking alert is a physiological
observation, **not** world-map knowledge or an instruction to act.

**Scientific verdict: NO-GO globally**, PR draft and issue open.

## 19 October: 10%-critical biological wake proposal, paired operator-side falsification

User-approved design: water, food and integrity **at or below 10 out of 100**
must be able to interrupt ordinary sleep, and eventually any **future**
consolidation-coma. This is **not** an instruction to infer where a resource is
or force an action. Canonical I1 already uses real reduced perception and
alerts before 10 for water and integrity (`water <=15`,
`integrity <=25`, `food <=10`), but in the sealed 20-life cohort often
selects `dormir` again after waking. Lowering those canonical wake thresholds
to 10 would actually *weaken* protection, so they are preserved.

The **research-only** experiment
`tools/run_i1_317_critical_wake_guard.py` is explicitly bounded to three
worlds (oasis, foraging, memory-corridor) times two fresh seeds
(9601, 9631), with two independently mortal, WAL-custodied births for
each pair. It suppresses only the Stage10 intrinsic sleep **contribution**
during *ordinary waking evaluation* when the actual fresh first-person
`capture.body` reports **water, food or integrity <=10**.
It leaves Q(dormir), all learned values, intrinsic fatigue/cognitive
state, consolidation, Competition thresholds and registration, Action
Control, wake rules, physical energy/needs decay, irreversibility and I0
unchanged; an individual can still freely choose `dormir` on TD evidence.
No food/water command or destination is supplied. Before the first guarded
step, paired physical action, body and journal custody must agree; each arm
has independently verifiable WAL.

Workflow `.github/workflows/i1-issue317-critical-wake-10pct.yml` and
adversarial threshold tests
`tests/i1/test_i1_317_critical_wake_guard.py` collect re-sleep,
physically accepted movements, hydration, meals, deaths, consolidated
batches and accepted UC. Runs on this experimental code **are not a
production safety certification or implementation of coma**. No global
GO or causal-entity utility follows merely from fewer sleep actions.
Require actual CI and paired biological outcomes first; keep #317 open.

## 19 October evening: real paired 10% protection outcomes and coma capacity gate

From the GitHub Actions artifacts of the six-pair experimental design,
four **complete paired mortal-life reports** are available: oasis/9601,
foraging/9601, foraging/9631 and memory-corridor/9631. All are technical
reports from real generated I1 births with separate WAL (not a claim that
the entire workflow has passed). The first operator-only removal of the
intrinsic sleep bonus at directly observed <=10% vital channels happens
at step 164 for oasis/9601, and step 82 for the other three observed
pairs, precisely when the first motor divergence occurs.

Across these four pairs, canonical vs critical-intrinsic-guard:

| Birth | Canonical horizon/status | Guard horizon/status | Sleep actions | Guard sleep actions | Canonical/guard consolidated batches |
| --- | --- | --- | ---: | ---: | --- |
| oasis/9601 | 300 / active | 299 / dead | 216 | 96 | 17 / 17 |
| foraging/9601 | 228 / dead | 203 / dead | 208 | 61 | 8 / 8 |
| foraging/9631 | 230 / dead | 225 / dead | 215 | 66 | 10 / 10 |
| memory-corridor/9631 | 228 / dead | 228 / dead | 207 | 60 | 9 / 9 |

Thus lower sleep preference demonstrably changes the actor's choices,
but **does not establish a survival improvement**. It frequently increases
movement or waking `attendre` and costs more UC, while consolidation
batch count stays unchanged in the four reported pairs. In oasis/9601
the native control survives 300 steps but the altered actor dies at 299.
Two pairs and the final aggregate workflow status have not been declared
successful at this writing. The original canonical I1 sleep thresholds
remain water <=15, food <=10, integrity <=25; the experimental >=critical
condition is **a separate wake-deliberation scoring ablation**, not a
reduction of early warnings and not an implemented coma.

To evaluate the proposed *maximum pending consolidation objects* without
inventing protection, `tools/audit_i1_317_consolidation_capacity.py` now
reads each of the 20 original, pre-registered, independently authenticated
mortal WALs. It counts actually closed autobiographical episode IDs and
only those episode IDs listed in fully matched atomic Stage10 consolidation
publications. It tests capacities 16/32/64/128 with a half-capacity
recovery observation, carrying actual first-crossing water, food,
integrity and energy. Synthetic adversarial tests reject missing
physical closure, fabricated objects, duplicate batch references and
false coma claims. The matching workflow
`.github/workflows/i1-issue317-consolidation-capacity.yml` has been
triggered; **its results are not yet established**.

This capacity audit does **not** simulate a coma or allow a shortcut
around a stalled/alert-interrupted Stage10 consolidator. A future coma
must show actual positive consolidation throughput while unconscious,
real reversible wake at or before the critical body state, and an
acceptable survival/consolidation/UC trade-off in matched mortal
worlds. Until then, the global issue remains **NO-GO**.

## 19 October: human-inspired two-process sleep calibration, matched physical protocol

The user's scientific priority is now a **human-inspired balance**, not a
fixed forced sleep percentage: homeostatic fatigue rises with real waking
work and drops with actual sleep; the physically observed night phase
modulates sleep desire; personally experienced TD values remain relevant;
semantic consolidation remains real, priced work during admitted sleep,
not a perpetual demand for more sleep. This is an engineering analogy to
two-process sleep regulation, **not** a claim of human biological timing.

A six-pair diagnostic ablation on the existing engine (critical sleep
intrinsic suppression at body <=10; original native earlier warnings
preserved) has now delivered complete physical reports for all six
world/seed pairs. Canonical control versus ablated: **3/6 vs 4/6
deaths**, 1,330 vs 647 sleep actions, 357 vs 23 alert-wake-to-sleep
decisions, **105 vs 105 consolidation commits**, and 63,635 vs 109,055
accepted cognitive UC. The ablation altered behavior strongly but
**did not improve survival or consolidation**. One oasis control survives
to horizon 300 while the ablated life dies at step 299. Therefore do
not merge the abrupt suppression as a production sleep feature.

The next experiment is now predeclared in
`tools/run_i1_317_two_process_sleep.py`, tests
`tests/i1/test_i1_317_two_process_sleep.py` and workflow
`.github/workflows/i1-issue317-two-process-sleep.yml`. It runs
**8 independently matched world/seed triplets** (24 mortal births),
four presets `oasis`, `foraging`, `dry-valley`,
`memory-corridor` × two new seeds 9761/9791. Native I1 is compared
with two frozen, operator-only Stage10 birth configurations:

| Dimension | Native | Homeostatic | Circadian |
|---|---:|---:|---:|
| awake fatigue gain | 0.70 | 0.20 | 0.12 |
| fatigue recovery per real sleep | 0.30 | 0.36 | 0.34 |
| fatigue weight | 0.65 | 0.62 | 0.58 |
| consolidation pressure weight | 0.25 | 0.05 | 0.03 |
| night contribution | 0.20 | 0.27 | 0.42 |
| intrinsic sleep evidence weight | 0.90 | 0.82 | 0.85 |
| pending-episode normalization | 8 | 32 | 32 |
| memory occupancy normalization | 2 | 4 | 4 |

None change body needs, world resources, sleep energy gain, learned
TD action value, Action Control, Competition thresholds, awake goal
arbitration, semantic algorithm, expensive consolidation budgets, wake
alerts (food <=10, water <=15, integrity <=25, energy <=10), death
irreversibility, I0 or previously sealed WAL. The designs are research
candidates, **not yet selected calibration**. Separate hash-authenticated
WAL and observer records include actual day/night asleep fractions,
bout durations, physical movement, resource intake, consolidation
objects and backlog, deaths, alert re-sleep and accepted UC.

The older capacity shadow audit initially failed because its verifier
incorrectly rejected a final *physically applied* mortal world step
with `step_closed.outcome=dead`. This is not rollback; death is a
valid final outcome. A precise correction and synthetic regression
test preserve this event and forbid post-death continuation, with
rerun pending. A safe consolidation coma remains unimplemented and
its value cannot be inferred from backlog threshold crossings.

Scientific verdict **NO-GO** pending completed and audited living
experiments. Never equate less sleeping with better surviving.

## 19 October: two-process trial stop investigation

The first full two-process trial (run `39288096522`) produced six technically
completed triplets and failed two (`oasis/9791`, `foraging/9791`) with
`ValueError: sleep entry requires actually applied ordinary admitted dormir`.
This is a **mortal session/admission contract failure**, not a death and not
evidence of improved or worsened physiology. Do not include stopped arms
in mortality comparisons or silently retry a stopped birth.

In Stage10, `_run_step_with_mortal_guard` records entry to sleeping mode
after a physically applied `dormir` decision, and the
`sleep_session.record_applied_sleep_decision` gate verifies ordinary
Action Control provenance and motive `sleep_pressure`. With alternative
sleep coefficients, the failing case needs exact real admission/option and
session state before any contract change. Read-only enhanced capture in
`tools/run_i1_317_two_process_sleep.py` (commit `ff427796`)
retains the stopped WAL's SHA, admitted primitive, motive type, option,
sleep session and mortal status, never rolls back or repeats the action.
Trial rerun `39292705542` is pending. Neither I0 nor production I1
was changed. Global `NO-GO` remains.

## 19 October: physically confirmed motive/admission mismatch and bounded fix

Independent archived experiment reports from Actions run `39292705542`
(`oasis/9791`, homeostatic, world step **51**; `foraging/9791`,
circadian, world step **95**) identify the immediate failure:
`last_applied_decision.motive_type=active_goal`, goal `recover_energy`,
`prepared_source=decision`, `admission_ok=true`, primitive `dormir`.
The same physically archived event sequences record an actual Competition
threshold crossing, the ordinary `command_admitted` receipt and a
`step_closed` with one physical command and one world advance.
`SleepSession` nevertheless rejected the entry solely because its older
gate required the motive type `sleep_pressure`. It is not a rogue action.

The narrowly scoped correction removes **only** motive identity as an
independent sleep-admission criterion. Stage4 must still select the option
through Competition, obtain Action Control admission and physically execute
the exact command. Stage10 checks the applied decision option, prepared
reference and selected plan agree; SleepSession retains chronological,
non-reentrant, admitted-primitive and `execution_status=applied` checks.
Synthetic tests reject reflex/fallback, unadmitted, mismatched, non-dormir
and non-applied candidates. The real I1 CI and fresh 24-life matched
experiment must establish the *actual* effect. No weights, rewards,
physiology, thresholds, wake rules, I0 or M11 rules are modified.

The previous two stopped individuals remain definitively technically
halted. Their WAL bytes and world steps must **never** be replayed or
extended. Subsequent CI launches independently born individuals under a
new source SHA with separate immutable WAL, not a resurrection of either
stopped life. Six previously completed triplets under the old SHA must
not be mixed with future, newly born results. Global verdict remains
**NO-GO** pending prospective authentic WAL validation, survival and
consolidation/UC comparison.

## 19 October: preregistered recovery-sensitive natural awakening, 2×2 factorial

Reinspection of the 24 independently verified WAL from the successful
two-process cohort (run `39297909539`, independent verifier
`39299436471`) gives a more precise diagnosis. Native I1 froze
`p_cons=1` at **626/659 physical sleep entries**. The eight native
lives recorded **587 alert wakes, 71 maximum-duration wakes and only
one natural-end wake**. Recovery-reduced variants still suffered frequent
alert wakes, with no population survival benefit and substantially fewer
physically committed memory objects. These are observations, **not**
proof that recalculation is better.

**Architectural distinction:** `SleepSession` currently passes the
last *waking-step-frozen* `sleep_pressure` to DC-13 on every sleeping
step. `SleepHealth` decreases fatigue only after physically applied
`dormir`, but the natural-end test never incorporates that recovery
within the same bout. Frozen memory pressure and the DC-13 alert,
reflex, dated-intention, maximum-duration precedence remain legitimate;
the scalar used only for natural end may be physiologically stale.

New research-only candidate
`tools/run_i1_317_wake_recovery_factorial.py` uses **two independent
factorial dimensions** at fresh birth:

- Actual fatigue-recovery-aware natural-end pressure: keep frozen prior
  consolidation demand and prior day/night phase, replace only the
  accumulated decrease in the already-owned F_cog within a sleep bout.
  A pure, monotone, bounded validator rejects nonphysical fatigue and
  contradictory pressure. First sleeping step preserves native pressure.
  It never reads privileged WorldBody state, new Memory episodes or TD,
  and never sends a motor command.
- Higher natural-end threshold only: 0.10 native versus 0.35 research
  candidate. Neither water/food/integrity/energy alert threshold nor the
  maximal 6 sleeping steps is modified.

The four independent arms are **canonical**, **recovered_fatigue**,
**natural_threshold**, **recovered_and_threshold**. Fixed preregistration:
four worlds `oasis`, `foraging`, `dry-valley`,
`memory-corridor` × new seeds **11117, 11239**, each a separate
mortal physical life with native 300-step limit and its own WAL.
Exactly **32** lives required. All retain the native frozen
`fatigue_gain=0.7`, `sleep_fatigue_recovery=0.3`,
`w_F=0.65`, `w_C=0.25`, `w_N=0.20`,
`intrinsic_weight=0.9`, and genuine charged consolidation. No coma
or forced vital action is introduced.

The experiment is deliberately **diagnostic**, not a candidate for
automatic model promotion. A safe replacement would also require a
state-owning and cold-restorable causal implementation, independent
WAL/UC attestation, and beneficial survival-plus-consolidation outcomes
across previously unseen births. Recovery pressure is recalculated in a
non-persistent research adapter attached at the individual's birth;
**no I1 production sleep owner or M11 restore contract is changed**.
Changing natural-end pressure is an intervention, not a direct assertion
of natural human sleep. Also, an alarm wake can legitimately be followed
by an independent ordinary decision to sleep again, and no priority
override is allowed. Death is irreversible; technical stops are
excluded from survival comparisons, never retried in place.

Workflow: `.github/workflows/i1-issue317-wake-recovery-factorial.yml`.
Every run must pass isolated adversarial tests, independent mortal WAL
authentication, and the exact frozen native-birth parameter checks.
**Global NO-GO maintained** until all 32 physical lives complete
and an independent population audit validates any prospective effects.

## 19 October: 32-life recovery-aware natural wake factorial, complete birth reports

All eight source run `39302574668` jobs completed successfully at the
locked `9f19100e276a16edaefd17e26a1092ef98391c38`; each includes four
separate physical WAL and a fully filled birth report. Four independent
treatments were **not** promoted to production. The following counts have
been calculated from all eight original archived reports and should
be interpreted as *provisional* until the second verifier certifies each
original WAL:

| Birth arm (8 each) | Deaths | Lived steps | `dormir` | Consolidated objects | Accepted logical UC | Natural ends |
|---|---:|---:|---:|---:|---:|---:|
| Native I1 | 6 | 1921 | 1685 | 314 | 84625 | 1 |
| Recomputed real fatigue only | 6 | 1919 | 1642 | 314 | 86246 | 21 |
| Natural threshold 0.35 only | 6 | 1914 | 1606 | 303 | 90618 | 32 |
| Recovery and threshold together | 6 | 1914 | 1584 | 307 | 94498 | 115 |

The recovery-only arm creates 41 more awake actions and 20 more
natural-end events, but **no extra `boire` or `manger`** and two fewer
physical steps survived in total. Across each four-arm cohort, exactly
3 `boire` actions and 8 `manger` actions occurred, despite greatly
different wake dynamics. At eight matched pairs, no evidence supports
claiming an improvement in survival or food/water agency. The greater
natural-end count is *not* itself a fitness improvement. The combined
arm adds 9,873 logical UC versus native, yields 7 fewer consolidated
objects, and gains no survivors. Treat the apparent trade-off as an
observation, not an optimized solution.

Independent, fail-closed second verification has been implemented at
`tools/audit_i1_317_wake_recovery_cohort.py`, adversarial tests at
`tests/i1/test_i1_317_wake_recovery_cohort.py`, and GitHub workflow
`.github/workflows/i1-issue317-wake-recovery-cohort-audit.yml`.
It enforces exactly eight preregistered groups, original exact engine
SHA, 32 unique WAL hashes, fully authenticated event chains, real
body transitions and death boundaries, verified wake reasons, charged
UC, exact atomic consolidation and vital wake policy. It deliberately
reports `experimental_recovery_scalar_itself_WAL_proven=false`:
the experimental research-only wrapper never wrote the recomputed
pressure scalar into its WAL, so causal interpretation must not
pretend this magnitude is independently authenticated.
No technically halted life can be revived or retried in place.

**Next architectural hypothesis:** native I1 already attempts to wake
under bodily alerts; additional voluntary wake opportunities do not
by themselves generate enough *first-person* effective survival actions.
The next valid experiment must examine per-step goal selection,
registered choices, learned value and Action Control evidence for
`boire`/`manger` versus `dormir`, without installing an innate
resource-location oracle or a compulsory vital reflex. Longer memory
consolidation must remain genuine, atomic and UC-paid, and coma remains
unimplemented. Global `NO-GO` remains until reproducible independent
causal evidence and safety guardrails are satisfied.

## 19 October: decision-chain explanation from eight canonical sealed lives

The previously launched factorial has now been independently certified:
[Actions 39304778688](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39304778688)
SUCCESS, **32 unique original physical WAL**, with no revived births and
no fabricated proof for the unjournaled recovery-pressure scalar.
The canonical I1 and physical memory workflows on commit `03371be9`
are also green. The scientific verdict remains `NO-GO`.

A new read-only scan of the **eight canonical lives** in that exact
cohort, using their original archived WAL and no engine interventions,
isolated **1,201 physically witnessed waking captures** with current
water at or below the native 15% wake alert. In 902, the active goal
remained `drink`; 741 had at least one previously personally sighted
water-source place, but only 162 critical captures had a currently
proposed water-place return. On those 162 occurrences, none of the
registered water-place candidates physically crossed Competition's
threshold. These are *per-step* counts, not 1,201 independent deaths
or causal trials; the same observations may persist over many steps.

Architecture review distinguishes at least three causes:
1. The active goal `drink` does not install an effect prediction or
   a water location oracle. Water-probe options require first-person
   local source visibility or previously experienced positive water
   change and a currently passable, perceived adjacent source.
2. Spatial place memory is goal-neutral: even a genuinely sighted
   `water_source` yields only a revisitable place option and at most
   a small entity-familiarity intrinsic signal. It does **not** infer
   thirst relief. Stage8/Competition must still value and choose its
   one-hop action under actual personal evidence.
3. No proposed location is guaranteed to be locally traversable,
   within the bounded witnessed eight-hop route graph, still valid,
   or already known from a successful water interaction. Distinguish
   these limitations from loss of learned physiological effect.

The previous 32-life factorial leaves survival unchanged even when
awake decisions increase. Adding an innate emergency action or making
every water-memory proposal an automatic winner would falsify the
epistemic architecture. The correct next study is a causal funnel
audit: *fresh captured need → already witnessed place → personally
observed bodily effect (if any) → genuine route proposal → funded
Competition registration → actual threshold crossing → Action Control
admission → physical movement and outcome*. Include negative cases,
out-of-view resources, post-death locks and false-success exclusion.

New executable external evidence work:
`tools/audit_i1_317_vital_memory_decision_chain.py`,
`tests/i1/test_i1_317_vital_memory_decision_chain.py` and
`.github/workflows/i1-issue317-vital-memory-decision-chain.yml`.
The verifier requires exactly eight preregistered canonical independent
source WAL, original SHA and world digests; independently verifies each
real applied step and journal before interpreting retrospective event
chains. It rejects unobserved water-source return targets, crossing
without registration, application without Competition crossing and
nonphysical progress. Its output is **diagnostic only**, not promotion,
and does not equate a sighted source with known water usefulness.

No canonical I1 weights/thresholds, food-first contracts, action
enforcement, I0, world physics, TD or consolidation owners are changed.
No coma introduced. Maintain draft PR and `NO-GO` until reliable
interventional, held-out evidence justifies any architecture change.

## 19 October: experimental first-person learned site value, 2x2 design

The sealed, independent vital-decision funnel run `39306632481`
completed **PASS** at engine SHA `4d1f001f`. For eight original
canonical lives, 1,201 waking captures with water at/below 15 were
authenticated; 902 had a `drink` goal, 741 had an earlier personally
witnessed water-source location, 419 were after an *admitted observed
positive* `boire` outcome and 162 offered a valid water-site memory
proposal, which never crossed the normal Competition threshold.
Counts are repeated steps, not independent births.

A further important mechanism was found in the archived
`memory-corridor/11239` WAL: personal water at (8,8) physically rose
after `boire` at step 1 and the subsequent first-person followup at
step 2. I1 moved through the corridor. By step 20, the
`i1_place_memory_recalled` candidate list retained stone/wood/berry
locations but excluded that personally useful water position. Spatial
memory itself was not erased: limited generic candidate selection and
valuation of goal-neutral place returns must be tested independently.
Being a `water_source` merely seen does not prove useful, permanent,
safe or reachable.

Research-only, pre-registered `tools/run_i1_317_lived_place_factorial.py`
crosses two small interventions: (i) paid expanded spatial candidate
retrieval *only during a genuine active drink goal* when the subject
already has an admitted positive first-person `boire` followed by
observed water rise at that exact source coordinate; (ii) a bounded
0.10 maximum advisory on the same source-place option through the
normal Stage8 evaluation API. Neither creates a primitive nor
alters motor admission, Competition threshold, innate knowledge,
TD/Q, physiology, food/drink reflex or source-map truth. The
existing spatial route search must still find actually surveyed
passable hops; no extra unreadable geometry is supplied.

Four arms: **canonical, recall_only, value_only,
recall_and_value**, across new seeds **13127,13219** and
`oasis`, `foraging`, `memory-corridor`, for **24 separate
irreversible births**, horizon 300 each. The original world, need
policy, sleep and consolidation parameters are unchanged.
A second `geographic_route_search` is explicitly charged to
Planning when the expanded candidate search is used; rejected
credit cancels that path. This operator-only adapter is NOT an
M11 cold-restorable cognitive owner, so even a positive physical
outcome would not justify deploying it unchanged. Worldstep/WAL
certification, a first motor divergence, mortal survival, water
actions, true consolidation and UC must all be examined on
independent fresh lives before any promotion.

Adversarial unit tests reject type-only utility, absent/negative
`boire` effects and invalid candidates. Workflow:
`.github/workflows/i1-issue317-lived-place-factorial.yml`,
run `39308197811`. The eight previous historical WAL remain sealed,
not re-executed. **Global NO-GO, PR draft**, no I0 change.

## 19 October: all 24 first-person water-place factorial births complete

The prospective run `39308197811` has **six successful birth groups**
(3 worlds × 2 fresh seeds × 4 independent mortal arms), frozen
source `5ce9604893a83615d3b84e8506709732286939c7`.
All 24 archived original reports are technically complete. These
report-only totals precede an independent physical WAL re-verification:

| Arm | Dead / 6 | Lived steps | `boire` | Moves | Consolidated objects | Accepted UC |
|---|---:|---:|---:|---:|---:|---:|
| Canonical | 2 | 1706 | 13 | 111 | 688 | 50501 |
| Re-rank only | 2 | 1706 | 13 | 112 | 689 | 50596 |
| Small learned-value advisory only | 2 | 1706 | 13 | 111 | 688 | 50501 |
| Both | 2 | 1706 | 13 | 112 | 689 | 50596 |

The research-only report counters were zero for effective rank changes
across all 24 lives; the optional value adapter was invoked five times,
but did not improve drinking or survival. Small physical differences
for the retrieval arms can arise from **extra charged Planning UC**
even when the candidate list does not change. Treat them as a
cognitive-cost confound, not evidence of improved place recall.

Additional analysis of archived WAL found genuinely identical physical
and journal trajectories for multiple paired arms. This is possible
for independently born deterministic individuals under matching inputs
and **must not be falsely described as shared identities or replayed
life**. Per-arm WAL provenance must be certified individually; unique
WAL file paths, not necessarily unique content hashes, are required.

Independent fail-closed verifier
`tools/audit_i1_317_lived_place_cohort.py` plus negative tests
`tests/i1/test_i1_317_lived_place_cohort.py` and Actions
`.github/workflows/i1-issue317-lived-place-cohort-audit.yml`
have been committed. They reauthenticate original WAL chain, real
physical actions, post-death boundaries, personal positive `boire`
followups, Stage8/Competition scores and actual memory-route crossings.
The adapter's unjournaled counter `rank_changes` **cannot**
independently certify that an intervention took effect; verifier
does not use it to certify a benefit or claim GO.

**Scientific decision: NO-GO.** The present experiment has not
established a route-recovery benefit, a drinking benefit or a
survival benefit. Before further changes, isolate whether
`find_spatial_returns` yields the same three candidates after
the expanded paid call, and whether a small learned advisory
can approach Competition's physical threshold on actual
critical-needs steps. No I0, canonical engine, M11 cold
restoration, TD or first-person requirement changed.

## 19 October: proven value effect is not proven motor effect

The 24 original WAL from the matched experienced-place factorial were
independently authenticated by [Actions 39311156884](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39311156884):
all 24 existing physical paths and their irreversible death/UC/consolidation
boundaries passed. The six arms grouped by treatment have exactly 4
survivors/6 and 13 `boire` commands each. The two paid expanded-recall
arms add 95 accepted UC on aggregate and one movement, with no
independently attested ranking change.

A closer candidate-aligned, read-only comparison of the original
WAL across matched steps/cycles/options shows the advisory value
intervention changed only **three** first-person learned water-place
evaluation records (two in `oasis/13219`, one in
`foraging/13219`). It did not produce a new threshold-crossing
outcome or a new physical drink command. Two recall-only groups have
distinct *first physical action divergences*, `oasis/13127` at
world step **110** (`se_deplacer` vs `dormir`) and
`memory-corridor/13127` at **203** (`attendre` vs `dormir`).
The research-only `rank_changes` counters remain zero.
These findings must not be interpreted as successful beneficial
recall: spending UC alone can alter the future cognitive budget
and so the action, without changing the intended candidates.

A prospective-independent verifier is now provided in
`tools/audit_i1_317_place_competition_margins.py`, negative tests
`tests/i1/test_i1_317_place_competition_margins.py` and workflow
`.github/workflows/i1-issue317-place-competition-margins.yml`.
It reauthenticates the 24 already-lived WAL first; then aligns
identical site-specific options by worldstep, cycle, option-ref,
scores actual Competition evidence and threshold fractions,
and compares applied motor streams. Nonjournaled experimental
invocation counters are *not* promoted to independent physical proof.

The observed problem now decomposes into:
- A location can be personally observed and physically associated
  with the individual's measured improvement, yet not be returned
  by the bounded current survey graph or offered candidate list.
- When a candidate is emitted, it may have small/zero legitimate
  Stage8/TD evidence and remain below Competition's actual threshold.
- A change in UC budget can cause an unrelated motor difference
  without proving either memory relevance or learned agency.

Scientific status remains **NO-GO**. Avoid a further weight-boost
sweep or source-type oracle. First establish that an intervention
actually changes eligible, personally grounded candidate availability
at the correct read boundary *and* is affordable with no confound,
before any new birth calibration. No canonical I1, I0, world physics,
mortal custody or M11 change is endorsed.

## 19 October: cap-exhaustion falsification and preregistered no-op guard

[Certified sealed Competition margin audit 39312722073](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39312722073)
completed PASS, with physically identical candidate comparisons.
Across the 24 original mortal WAL, learned-place value changed two
exact same-candidate score records (oasis/13219 and foraging/13219)
without any changed threshold crossing. Paid expanded recall
introduced 26 step-level motor differences in two matched lives,
but **zero candidate-only opportunities** and no water/survival gain.

Direct inspection of the six canonical source WAL counted 130
post-personal-positive-water `i1_place_memory_recalled` events that
actually saturated the original **three-candidate** limit. In **all
130** the positive site was either already the individual's current
cell or was present among the three offered candidates. Therefore
these physical observations **falsify** the initial conjecture that
the limit itself excluded a personally useful *offsite* water source
in this cohort. Do not confuse being on an experienced water cell
with needing a navigational return to that same cell. This is not a
claim about unsurveyed or future locations.

The previous expanded search spent an extra genuine Planning UC on
numerous calls where the outcome provably could not change. To test
that cost effect separately, the new research-only two-arm study
`tools/run_i1_317_place_noop_guard.py` uses:
(1) native canonical I1 unchanged and (2) previously explored
expanded recall but with an admissible **no-op gate** before the
SECOND paid spatial search. The second call is skipped if the
first, already-paid search has fewer than its capacity; or if the
full prefix contains all personally supported nonlocal water
sites and already ranks them first. Only a positive personally
observed `boire` followup from the private owner can qualify;
a visually labeled `water_source` alone never qualifies.

This is tested prospectively in **12 fresh irreversible lives**
over `oasis`, `foraging`, `memory-corridor` and locked new
seeds **14083**, **14107**, at 300 world steps max, with
normal budgets, physics, TD, consolidation, Competition,
Action Control and mortal custody. Test/workflow:
`tests/i1/test_i1_317_place_noop_guard.py`,
`.github/workflows/i1-issue317-place-noop-guard.yml`.
It is a transient laboratory wrapper, not an M11-compatible owner
and not eligible for integration without authenticated new WAL
and a demonstrated survival/learning benefit.

Original 24 WAL remain sealed; no restart, rollback, resurrection,
new motor authority, innate resource value, forced consumption
or coma. **Global NO-GO.**

## 19 October: 12 new mortal no-op guard lives, physical result

The matched fresh-birth run [39315789674](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39315789674)
completed **six SUCCESS jobs**, all 12 birth reports. Reports:
both arms have **four survivors of six**, **1,656 physical world
steps**, **seven `boire` commands** and **382 objects consolidated**.
Native accepted 91,940 logical UC; guarded recall 92,083, an
increase of 143. The lab wrapper reports 331 avoided searches,
215 potentially useful extra searches and 215 ranking changes
(all 215 in `memory-corridor/14107`). Such wrapper counters
are not original WAL-proven and do not establish a better action.

Direct independent inspection of the two original
`memory-corridor/14107` WAL: the guarded individual physically
proposed a known water-place route **215 times across 95 world
steps** that baseline omitted. All 215 Competition evaluations had
**evidence exactly zero**, **accumulator exactly zero** and
**threshold exactly 0.5**; *none crossed*. Applied physical commands,
water consumption, survival and consolidation remained identical,
even though UC usage and internal recalled candidates changed.
In other cohorts the guard was behaviorally identical to native.

This separates memory access and motor decision much more precisely:
the same individually learned water-positive destination can be
retrieved and offered, but Stage8 remains at zero intrinsic value for
an entity-place already personally reached. Normal Stage8 Q/TD
evidence here did not overcome that zero. It would be scientifically
wrong to "fix" this by forcing return to a resource label or
making the option a Competition winner.

The new independent audit
`tools/audit_i1_317_noop_guard_cohort.py`, negative tests
`tests/i1/test_i1_317_noop_guard_cohort.py`, and workflow
`.github/workflows/i1-issue317-noop-guard-cohort-audit.yml`
read, verify and compare original 12 WAL before trusting any
life outcome. Original records remain unaltered; no retries in place.
Next hypothesis is an *entirely experiential* Stage8 location
relevance signal based solely on admitted positive `boire` followup
and active thirst goal. Such a signal cannot be an oracle, a
guaranteed benefit, a bypass of Competition/Action Control, or a
free UC calculation. It must be isolated from paid-retrieval
confounds and validated with fresh paired mortal lives before
production consideration. Current research wrapper is not
cold-restorable through M11.

**Scientific NO-GO maintained.** No I0, canonical I1 owner,
physical simulation, thresholds, food-first reflex or coma is changed.

## 19 October: fresh matched experiential goal relevance, stage-8-only research

[Independent original 12-life verification `39318131046`](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39318131046)
is green, along with I1 and physical-memory CI at `667cce96`.
The 215 personally observed, fully offered water-site candidates in
`memory-corridor/14107` scored zero evidence against threshold 0.5,
without a single command change. Neither extra retrieval nor source
type as a label establishes a useful motor.

To isolate the next mechanism, new, preregistered
`tools/run_i1_317_experiential_place_relevance.py` and
`tests/i1/test_i1_317_experiential_place_relevance.py` run
**two physically independent mortal arms** in **three worlds**
(`oasis`, `foraging`, `memory-corridor`) × **three previously
unused seeds** (15121, 15173, 15313), **18 separate lives** at up to
300 steps each. Both arms use the *same already tested guarded spatial
retrieval* and equal ordinary Stage8/Planning charges. The only
difference is a bounded Stage8 extra *association-based relevance*
for a genuine currently offered, observed-and-visited site where
that individual performed a physically admitted `boire`, then
personally observed an increase in their bodily water. The present
first-person frozen water reading must be <=30%; the Stage6/Stage8
motor prediction is untouched. Relevance is capped at 0.45 and
discounted by memory confidence and witnessed route length. This
is neither a model of future water gain nor a site-type oracle.

No changes to native physiology, sleep, world physics,
Competition thresholds, TD/Q memory, Action Control,
M11 owner state, or I0. The experimental wrapper is not yet
cold-restorable and **cannot be promoted unchanged**.
Competition still requires its normal accumulator crossing and
Action Control still admits the single real motor. A favorable
result must be defended by authentic WAL, true executed return,
subsequent drinking, consolidation, survival and matched UC.

Workflow:
`.github/workflows/i1-issue317-experiential-place-relevance.yml`,
run `39322396991`; at the time of this entry the nine
fresh independent birth groups were beginning, with no
survival outcome available. Prior 12 and 24-life WAL remain
sealed. Global **NO-GO**, PR #318 stays draft.

## 19 October: complete 18-life experiential-site result and independent authentication

All nine preregistered matched-birth jobs in Actions run `39322396991`
completed SUCCESS under exact source `43e1fa82e8034c20708d9edf380b41a5bf30502b`.
The **18 original birth reports** (three worlds × seeds 15121/15173/15313
× two independently mortal arms) give this *provisional* comparison
pending the new independent 18-WAL audit:

| Arm (9 lives) | Deaths | 300-step survivors | Lived steps | `boire` | Moves | Consolidated objects | Accepted UC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Same guarded recall, control | 4 | 5 | 2446 | 9 | 265 | 572 | 103579 |
| Same recall + Stage8 positive lived-site relevance | 4 | 5 | 2446 | 15 | 277 | 787 | 94314 |

Exactly **three** independent `memory-corridor` births changed behavior.
All 3 changed from one `boire` to three, from four movements to
eight, and had more genuine memory objects consolidated, with lower
UC cost. The other six pairs remained identical. Population
survival did **not** improve, and n=9 is not sufficient for promotion.

A precise event-chain example: `memory-corridor/15173` at
world step 132 both arms propose a first-person remembered
water source at (8,8). Control returns evidence 0 and ultimately
applies `attendre`. Experimental Stage8 uses a previous
physically admitted `boire` at (8,8) followed by a measured bodily
water increase, frozen present water, current drink goal, confidence
and route length. This raises Competition evidence from zero to
approximately 0.213; the option crosses the **unchanged** 0.5
threshold during cycle 3. At this crossing, a different concurrently
offered site on the **same destination cell** (`berry_a`) has
exactly the same motor hop and is the option actually admitted by
Action Control. I1 physically moves west from (12,8) to (8,8)
over world steps 132-135 and then physically executes `boire` on
step 136, with `drank=True`. Never attribute the crossing to a
specific winning option unless its actual admission ref matches.
The observed useful return is a real motor outcome, not a forced
navigation order, but the attribution is partially shared because
multiple remembered entities occupy the destination cell.

An important qualification: original owner `stage11_runtime.py`
already exposes the private `_stage11_prospective_capture`
with frozen water and position before Phase1. The lab adapter
uses that first-person capture, not unseen world truth. Original
per-step accepted UC are equal before first motor divergence in
the `memory-corridor/15173` pair. Fewer future UC can result
from the changed subsequent physical trajectory and planning
load, and must NOT be credited as an isolated computational
optimization.

The next verifier, `tools/audit_i1_317_experiential_place_cohort.py`,
`tests/i1/test_i1_317_experiential_place_cohort.py` and
`.github/workflows/i1-issue317-experiential-place-cohort-audit.yml`,
checks each sealed WAL, journal hash chain, physical attempts,
first-person learned positive sites, Stage8 WAL-visible signals,
competition score and threshold, exact admission option and
matched first-motor divergence. Research-only counters are never
used as the sole proof. Until successful independent audit,
this is a **report-based preliminary benefit** only.

No forced eating/drinking/navigation, no resource-type oracle,
no change to Action Control, TD/Q or motor thresholds, no
I0 or canonical I1 implementation changes, and no coma.
The experiment's mutable lab wrapper lacks M11 cold
restoration; a native persistent owner and independent
held-out population validation would be required for promotion.
**Global scientific verdict NO-GO; PR remains draft.**

## 19 October: 18 original mortal WAL certified, independent held-out replication

[Independent 18-life WAL certification #39323693952](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39323693952)
is SUCCESS. Its sealed `independent-experiential.json` attests
all **18** original WAL paths, **30** genuine Stage8 experiential
signals, **15** threshold crossings, and **three of nine** matched
pairs with a real first motor divergence under equal accepted UC
before that divergence. All three were in the original
`memory-corridor` and moved west towards a site (8,8) containing
**both** a personally beneficial water source and berry_a.
Normal Competition selected a motor candidate which could be
the berry place option rather than the water place option.
Every paired life in oasis or foraging was unchanged.
Deaths remain **4/9** in both experimental arms: no survival gain.
The per-arm authentic WAL aggregates were: control 2446 physical
steps, 9 `boire`, 572 objects consolidated, 103579 UC;
treated 2446 steps, 15 `boire`, 787 objects consolidated,
94314 UC. These results prove a narrow first-person,
motor-mediated capability but not general survival improvement
or a standalone water-driven motor choice.

Prospective validation is frozen before observing new outcomes:
- Research algorithm exactly as in
  `tools/run_i1_317_experiential_place_relevance.py`
  and historical source `43e1fa82`; copied to
  `tools/run_i1_317_experiential_place_heldout.py`
  without changing confidence discount, water<=30,
  maximum learned evidence 0.45, Competition, Action Control,
  physiology, Q/TD, or paid retrieval.
- Four world presets: `oasis`, `foraging`,
  `memory-corridor` and the new fixed
  `water-isolated-corridor`. The fourth duplicates the
  original corridor's birth, needs, water at (8,8),
  surveyable passable corridor, obstacles and all other
  resource counts but places berry_a at **(10,8)** instead
  of **(8,8)**. Berry and water locations are disjoint.
  No actor is given this mapping; it remains Lab world truth.
- Four entirely new seeds: **16127, 16249, 16381, 16513**;
  two independently born mortal arms `guard_control` and
  `guard_experiential` per world/seed. Thus **32 new
  independent mortal lives**, max 300 physical steps each,
  with separate immutable WAL. No past seed or life is
  retried, rolled back, or resurrected.
- Negative unit tests ensure no unearned value from an entity
  label, bad personally observed delta, unseen future resource,
  or changed site co-location.
- Outcome GO criteria require physically authenticated new WAL,
  repeated first-person conditional Stage8 value evidence,
  unchanged score thresholds and UC before motor divergence,
  an **actual admitted decision option** with the learned
  water site's referent (not just same-cell berry), then
  actual movement, subsequent `boire` and observed water
  change, without unacceptable losses in survival,
  consolidation or compute cost. If mixed, report NO-GO.

Workflow:
`.github/workflows/i1-issue317-experiential-place-heldout.yml`
run `39324485459` launches the 16 matched new pairs.
This remains a laboratory intervention, not an M11 native
persistent owner: **NO-GO** and PR #318 **draft** pending
held-out attestation and native cold-restore contract.

## 19 October: completed held-out 32-life birth reports, dissociated water/berry site

The new preregistered held-out run
[39324485459](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39324485459)
completed all **16** matched job groups successfully, yielding
**32 independent mortal WAL** at exact experiment source
`4536cd2dda53e470ef577aa14ea98ab9ec05fc50`.
Aggregates from the 16 original **birth reports** (pending independent
original WAL verification, no promotion):

| Arm (16 lives) | Deaths | Lived steps | `boire` | Moves | Actual consolidated objects | Accepted UC |
|---|---:|---:|---:|---:|---:|---:|
| Matched guarded-control | 9 | 4209 | 17 | 514 | 1047 | 192226 |
| Same retrieval + lived-site relevance | 9 | 4209 | 21 | 518 | 1182 | 183022 |

**Held-out positive result in the separated-water-and-berry corridor**:
seeds 16127 and 16249 show **1 to 3 physically reported `boire`
commands** per life, **81 to 150** and **84 to 150** actual
consolidated objects, respectively, with water at (8,8)
and berries only at (10,8). The former berry-colocation
confound cannot alone account for these paired effects.
However, held-out seeds **16381** and **16513** die without
a single positive first-person water-source experience, so
neither variant has a learned association to apply. Six other
non-corridor-world pairs with no intervention effect likewise
remain largely equal. Survival overall stays 7/16 in both
groups. The benefit is conditional, not population survival GO.

All motor-choice claims must be verified by the **actual** winning
Action Control `option_ref`, not inferred from simultaneous
Competition threshold crossings. Independent source verification:
`tools/audit_i1_317_experiential_place_heldout.py`,
`tests/i1/test_i1_317_experiential_place_heldout_audit.py`,
`.github/workflows/i1-issue317-experiential-place-heldout-audit.yml`.
The first audit workflow was launched before all original artifacts
were present and failed closed on a missing archive; this did
**not** indicate invalid physical birth and no original life was
restarted. Updated workflow waits for original run completion
before retrieving all 16 sealed pairs.

CI correctness: the new fixed world preset was initially absent
from the strict expected preset set in `test_world_presets.py`,
and `main` I1 smoke CI correctly failed. Commit `e5154f12`
registered the new world in the test inventory without altering
the world or any cognitive engine. General CI must pass afresh.

No coma, forced resource visit, motor override, source-type
oracle, I0 change, cold-recovery promise, sleep-policy
retune or mortal replay. **PR draft / scientific NO-GO maintained**.

## 19 October: independent audit reconciles Phase-1 proposal and later goal

The held-out 32-life independent audit initially failed closed at
`association with no current perceived thirst and drink goal`. The
source WAL in `water-isolated-corridor/16249`, step 134, cycle 1,
revealed a time-order distinction, **not** a forged motor:
the place proposal was stamped with `goal:eat:food:128:2`
from the frozen planning snapshot, while the logged
`active_goal_changed` had ALREADY switched the genuinely active
GoalManager owner to `goal:drink:water:134:1` before the subsequent
Stage8 experiential evaluation. The first-person observed water was
28.8, within the <=30 research gate. The original experimental
wrapper used the contemporaneous GoalManager, not the earlier
planning label.

The independent verifier is corrected in `1cb8c5b8` to follow the
*ordered original WAL GoalManager transitions* and certify
the active `drink` goal at the **actual Stage8 signal event**,
while retaining the earlier Planning label as explicit provenance.
Any mismatch must be backed by the exact same-step, same-cycle
`active_goal_changed` receipt; absent, malformed or mismatched
GoalManager transitions still fail closed. Adversarial negative test
`d02ecbb2` rejects relevance evaluated while live goal remains
`eat`. The physical original WAL have NOT been modified or replayed.

The first population verifier failure (`39325349276`) was due to
missing artifacts before the 16th birth finished; the next
(`39325485619`) was this overly strict earlier Planning goal
assumption. Both were **auditor failures**, not new birth failures.
Rerun of the independent verifier and general I1 CI is required
before declaring the 32-life evidence fully certified.
Global NO-GO and non-promotion remain in place.

## 19 October: native stateless Stage8 relevance, opt-in M11 contract prototype

The held-out 32-life certification succeeded in
[Actions 39326459271](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39326459271).
The original 32 archived WAL are authenticated and the Phase-1/Stage8
GoalManager switch is reconstructed from actual ordered WAL events.
No birth was replayed. Global scientific result remains **NO-GO**:
7 survivors/16 per arm, despite extra hydration and consolidations.

The next software architecture is now **implemented but not promoted**:
`src/i1/modules/experienced_place_relevance.py` is a pure
first-person, goal-conditioned, Stage8 evidence evaluator with no
mutable state owner of its own. It derives relevant place evidence from
the existing `I1LivedWaterOwner` owner, which M11 already includes
in the current committed owner graph and installs only using the
authentic cold-owner capability. The same site must be associated with
a previously applied `boire` and an admitted, physically observed
positive followup at the same coordinates. The current need, site
confidence and route length bound its contribution to 0.45.
It never infers effects from a resource-type label, predicts water
gain from movement, raises the Competition threshold, changes TD/Q,
chooses a motor, or supplies WorldBody state not in Perception.

The candidate is only installed when constructing an explicit research
`I1Runtime(..., i1_experienced_place_enabled=True)` on a separate
mortal birth. Both public ordinary entrypoints `birth_i1` and
`birth_i1_m11` have no such parameter and remain **OFF**.
In M11, the *opted-in* contract, relevance ceiling and water threshold
enter the birth constructor SHA; same-identity cold recovery with a
different opt-in setting is refused. Historical OFF fingerprints are
unchanged. The dedicated CI
`.github/workflows/i1-issue317-experiential-native-m11.yml` runs
pure guard tests, a fresh opt-in current-generation M11 cold-recovery
two-step journal parity test and the pre-existing natural M11 test.
These certify software integration for current generation, **not**
full observational parity after an arbitrary learned water-history
checkpoint, nor a proven long-horizon behavioral gain from this new
native implementation.

A full promotion still requires: a matched physical validation
using the native opt-in instead of the laboratory monkeypatch, real
water-effect histories surviving a cold restart and producing the
same Stage8 scores, full original WAL/UC certification, no systemic
survival regression, and transparent first-person effect attribution.
The software parity gate currently approves this opt-in source
diff **only through exact pinned Git blob SHA1**, not by granting
an open path exemption. After any source change the pins must be
explicitly re-reviewed.

No I0 change, no involuntary `boire`/`manger`, no coma, no
historical restore, no default policy change. PR #318 remains draft;
scientific **NO-GO** remains valid.

## 19 October: native opt-in physical replication with independent births

Native-source integration reached a software-only milestone:
[dedicated M11 workflow `39327980676`](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39327980676)
**SUCCESS**. The native no-new-owner Stage8 evaluator is instantiated
only at an explicitly separate experimental birth. Cold recovery of a
two-step current-generation native opt-in I1 produced the same canonical
journal head as uninterrupted execution, while changing the opt-in
at cold-birth failed the immutable M11 constructor fingerprint.

Next prospective physical experiment:
`tools/run_i1_317_native_experiential_cohort.py` compares two
new mortal arms, `guard_control` and `guard_experiential`,
across `memory-corridor` and `water-isolated-corridor`,
with new seeds **18121, 18233, 18367, 18481**. Exactly **16**
separate, never-before-run I1 lives, 300 steps each, with original
WAL. Both arms have the same tested guarded place-retrieval
research routine and charges. The second activates **native**
`I1Runtime(i1_experienced_place_enabled=True)` and the first
keeps it false. There is **no old laboratory Stage8 value
wrapper** in the new script; real Competition and Action Control
retain every action decision.

Initial attempts with seeds 17123/17257/17383/17491 aborted at
construction because calling I1Runtime directly omitted the ordinary
Stage12 diagnostic/occupancy UC constructor defaults supplied by
`birth_i1`. None produced a physically executed born life;
the new seeds above prevent ambiguity or reused identities.
New workflow:
`.github/workflows/i1-issue317-native-experiential-births.yml`,
run `39328430028`. Report-only comparisons require a second
independent original-WAL audit before any scientific inference.

Even if new lives improve, this does **not** establish natural
human sleep or population survival. More importantly, cold parity
has so far been tested for two initial steps, not a truly learned,
multi-step first-person water state after a cold restart.
Global **NO-GO**, no canonical I1 enablement, no I0 changes,
no forced drinking or movements, no coma or life rollback.

## 19 October: first real learned-water M11 cold recovery, typed-body fix

The new independent M11 software test
`tests/i1/test_i1_317_experiential_native_lived_m11.py`
creates **two new opt-in M11 mortal lives** from identical birth
parameters in a contained thirsty `water-isolated-corridor`:
body water 20 on the first-person visible source at (8,8).
It NEVER sets a command, overrides Stage8, injects learned
examples, imports a prior world or rewinds a historical generation.
Both actors physically run until their own real `boire`
is followed by a paid, positively observed next-capture
`i1_water_lived_outcome_admitted`, then attest exact
owner state in both SQLite current generations. A separate
continuous individual proceeds normally while the other process
is closed and cold-restored by authentic current-state M11.
Next five genuine physical steps must match exact journal heads,
step identities, life states and living water-owner evidence.

The initial run [39329416260](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39329416260)
correctly **FAILED** closed, notwithstanding a valid
already authenticated I1 water-owner state. Read-only diagnostic
runs isolated the mismatch to **WorldBody.body.integrity**:
the original SQLite physically committed generation contained
integer `85` while WorldBody's generic historical fixture
restore converted it to float `85.0`. Those values compare equal
arithmetically but differ under strict M11 canonical causal bytes.
No real physics or first-person association differed.

Commit `8105bcad` repairs only the **unexecuted detached
M11 cold staging**: after validating source WorldBody snapshot,
rebuild `BodyState` with exactly the authenticated int/float
types, validate physiological bounds, then require exact
canonical full-world bytes BEFORE publishing. Live WorldBody
restore remains prohibited and final M11 bitwise world+owners
gate remains intact. The source parity approval for M11 is
re-pinned exactly at reviewed Git blob SHA in `d01cafe0`.
The dedicated [actual learned-water M11 workflow
39329829122](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39329829122)
is **SUCCESS**, after genuine positive first-person experience.
This is cold recovery of a current, active generation, NOT
resurrection or continuation from an earlier chosen generation.

The separate 16-life native physical prospective campaign
[39328430028](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39328430028)
has eight independently born matched pairs and its dedicated
[original WAL independent auditor
39328630695](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39328630695)
returned **SUCCESS**. Any reported population efficacy must
be read from that auditor's certified figures, not inferred
from software parity alone. No canonical activation, no I0
change or compulsory water reflex. **Global NO-GO** pending
population survival benefit and final I1 full CI.

## 20 October: native population attestation and sleep-alert reentry investigation

The native research cohort's original 16 WAL are independently certified
by [workflow 39328630695](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39328630695)
under physical experiment source `22560d09dbe242b722f07c151781cf261faaccef`.
Certified totals over eight independent matched births per arm:

| Arm | Survive / 8 | Applied boire | Consolidated objects | Accepted UC | Personally earned Stage8 signals |
|---|---:|---:|---:|---:|---:|
| Guarded control | 5 | 12 | 648 | 92435 | 0 |
| Guarded retrieval + native learned relevance | 5 | 14 | 716 | 88906 | 5 |

Four real threshold crossings occurred in the experimental arm.
The learned water-site `option_ref` was actually accepted by Action
Control on world step **133** in `water-isolated-corridor/18367`
after the baseline would have waited. The six other non-divergent
birth pairs provide no evidence of a universal survival effect.
Keep the global NO-GO.

A new problem independent of learned spatial route relevance has emerged
from the **same already-sealed** control WAL. In
`memory-corridor/18233`, I1 died after 228 steps without any
physically experienced `boire`; water reached zero while actual
physical decisions continued choosing `dormir`. Detailed original
WAL inspection found **79 distinct wake events with reason
`alert` that were followed in the SAME WORLD STEP by another
ordinary Competition/Action Control decision `dormir`**.
These are *not* 79 uninterrupted sleep steps or 79 forced wakes.
They are newly deliberated actions, mostly under full 100% energy,
low water and a frozen intrinsic sleep pressure of about 0.9.
`memory-corridor/18367` shows a similar phenomenon.

The reduced perception bodily alert truly WAKES I1, but waking
does not automatically reduce actual F_cog nor the prior
consolidation backlog. Subsequent ordinary Competition can again
select sleep with high pressure and no immediate fatigue recovery.
This is a candidate explanation for failure to obtain the very first
beneficial water observation. It is *not* evidence I1 knew where
the missing water was or that drinking should be hardwired.

New research-only read-only auditor
`tools/audit_i1_318_alert_sleep_reentry.py`,
adversarial tests
`tests/i1/test_i1_318_alert_sleep_reentry.py`, and workflow
`.github/workflows/i1-issue318-alert-sleep-audit.yml`
independently certify the original 16 WAL before counting
newly admitted sleep after alert, frozen P40 pressure, the
actually observed body and competing active GoalManager.
No original birth is rerun; no M11, canonical sleep coefficient,
consolidation pressure, default wake policy, I0 or Action Control
has been changed.

Next controlled hypothesis: make an alert wake an explicit
**temporary eligibility restriction of the sleep candidate only**
while the same personally sensed serious physiological alert
persists. Such a restriction must remain within Competition, preserve
the other alternatives, avoid motor forcing, require a versioned
opt-in born contract and current-generation M11 continuity, and
be measured in NEW mortal lives against matched control. No GO
until the audit verifies the original physical failure mode.
