# I3: Limits and a generalization scenario without imposed rules (verified against main e4eb3e8)

6 November 2026 · @Josselin

> **English translation of an owner-supplied research report.** The original
> French text is preserved byte-for-byte at
> `archive/i3/original-language-records-2026-11-09/src/i3/docs/GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md`.
> The report is a historical snapshot of `main` at `e4eb3e8`, not an
> assertion about the repository's current stage or adopted mechanisms.

## Executive summary

Direct verification of `main` (commit `e4eb3e8`, from PR #1058, with no
later commit at that time) confirms almost every figure and the code
description in the previous report. One conclusion changes: **P5e does
not demonstrate a Competition defect.** Most "lost" meals are explained by
absence of hunger, competing deficits, or alternative food plans.

- **What sustains survival in novel Worlds:** the learned-effects model
  (0/288 survivors when removed, versus 112/288) and the curiosity bonus
  (4/288 without it, versus 110/288).
- **What shows no measurable effect:** TD value (117/288), replay (119/288),
  prudence (105/288), and lineage selection (47/144 versus 42/144).
- **What prevents firm conclusions:** with n=4 independent populations, the
  two-sided exact test cannot fall below p=0.125 even if all four agree.
- **What changes in the development scenario:** "simplify Competition" is
  demoted to a lightweight audit. The priority remains replacing additive
  curiosity with information value expressed in predicted distress, then
  letting the individual decide how much to think.

## What was checked and corrected

This time the files were read directly from Git, rather than through issues:

- **Status and plan:** `src/i3/docs/STATUS.md`,
  `DEVELOPMENT_PLAN.md`, `P2_COST_AUDIT_RESULTS.md`.
- **Study results:** P3 and P5a `RESULTS.md`, P5b post-hoc
  `POSTHOC_SCORE_TERMS.md` and P5c `POSTHOC_ACTIVE_MORTALITY.md`.
- **Code:** `modules/mind.py` and `modules/genome.py`.
- **P5e originals:** the compressed file containing 24 lives.

At that snapshot, `main` had 192 commits since physical model v2 and none
after P5e.

| Claim in the earlier report | Status | Correction |
| --- | --- | --- |
| P2, P3, P4a, P4b, P5a, P5b, P5c figures | Confirmed | None |
| Code: distress D(h), curiosity β_u × u × relevance, prudence λ_r × u × (w_I · d_I + κ₀), veto at 10, Competition threshold 1.5, 30 genes | Confirmed in `mind.py` and `genome.py` | None |
| P4 reserve 1,200,000-1,200,199; future validation indices >=120 | Confirmed | None |
| P5e: "333 of 342 meal opportunities lost; Competition reverses the ranking" | **Incorrect** | In 333 cases another option already had a strictly higher raw score. The threshold changed the outcome only six times: three raw-top meals lost and three lower-scoring meals won |
| Limitation (g): "Competition thresholds present high hidden-rule risk" | **Overstated** | Only 6/342 deviations; low-to-medium risk |
| "Simplify Competition" as third priority | **Demoted** | Lightweight, low-priority audit |
| P5c: "809 waits versus 383" | Imprecise | 809 rest **or** wait actions (`dormir`/`attendre`) versus 383 during the first 12 steps |
| P5b post hoc: "exploration dominates choice" | Imprecise | 650, 4,587 and 837 describe scores that **change** when action-specific readout is blinded. Learned information thus reaches decisions mainly through the curiosity term; this does not measure curiosity's contribution to normal choices |
| Replay: "422,400 operations" | Imprecise | 391,323 physically paid replays in the normal arm; 422,400 in the discard-retention arm |
| Source access | Corrected | Git files read directly, not only issues and PRs |

## What the campaigns show

All campaigns were run on 5-6 November 2026. Constant status: I1 active,
I3 unregistered, P4 reserve sealed, no scientific GO.

| Campaign | Design | Verified outcome | Interpretation |
| --- | --- | --- | --- |
| Physical model v2 (#1004-#1007) | 16 development lives, horizon 400 | Survival 14/16 -> 8/16 | Reveals the real cost of thinking without retuning |
| G2e | Selected genomes, reserved seeds | 478/1,000 vs 364; revision 270/500 vs 163 | Revisable beliefs adopted |
| P2 | 36 lives, 12 Worlds, three ecologies | 31 deaths; 3,483 inactive steps out of 7,729 (45%); 0/7,729 exact matches with fixed probe tariff; funded reference 4/12, oracle 12/12 | Probes remain descriptive |
| P3 | 864 lives, four populations, three generations | G0 34 vs 34; G1 37 vs 50 (-13); G2 50 vs 45 (+3,+3,-1,0); selected arm spends more cognition (24,817 vs 20,856 energy) | Selection inconclusive |
| P4a | 288 lives, 24 validation Worlds | 47/144 vs 42/144 (-2,+9,-1,-1) | Evolutionary generalization not demonstrated |
| P4b | 576 lives | Retained learning 84/288 vs 0/288 when paid calculations are discarded; 144/144 distinct histories for identical genomes | Learning matters, but spending and activity differ |
| P5a | 1,152 lives, Worlds 48-71 | Normal 112; no effects 0; no TD 117; no replay 119; inactivity 19.80% vs 72.43% without effects | Effects model is vital; TD/replay show no measurable effect |
| P5b | 1,152 lives, Worlds 72-95 | Full 98; action-blind readout 0; global prior 0; sleep-blind 90; inactivity 19.56% vs 75.6% | Action-specific readout is essential |
| P5c | 1,152 lives, Worlds 96-119 | Normal 110; no curiosity 4; no prudence 105; neither 7; inactivity 18.65% vs 1.13% without curiosity | Curiosity sustains survival; prudence has no measurable effect |
| P5c post hoc | Original data | Deaths 178 vs 284, including thirst 146 vs 239; first 12 steps: resource commands 392 vs 132, rest/wait 383 vs 809 | Without curiosity, active thirst death, not paralysis |
| P5d | 24 development lives | Without curiosity: 761 waits vs 134, 193 moves vs 627; 11 vs 10 units collected, 0 vs 7 eaten; 125/125 steps with a paid meal offered, 0 chosen | Cause unidentified (complete scores unavailable) |
| P5e | 24 development lives with complete Competition recording | Normal: 342 opportunities, nine meals; threshold decisive six times; without curiosity: zero collection or meals, 717 waits, hence no observable meal opportunities | Competition follows raw scores; see below |

General statistical limitation: n=4 independent populations. The two-sided
exact test cannot attain p below 0.125 (p=0.375 after Holm adjustment).
The screen effects are substantial but not confirmatory.

## Revised interpretation of P5e: hunger, competing deficits and other plans

Of 342 opportunities to eat carried food, the individual was hungry in only
63. In most missed meals it selected another need or another food plan.
This is tradeoff between stakes, not evidence of defective Competition.

This is the report author's own post-hoc, descriptive analysis of archived
normal-arm originals (`p5e-original.json.gz`), without generating any new
life. Hunger is measured against each genome's food threshold θ_F.

| Step | Count | Explanation |
| --- | --- | --- |
| Meal opportunities (carried food, funded `manger` option) | 342 | None |
| Without hunger (food >= θ_F) | 279 | Eating gives no immediate relief; median food 53, median θ_F 44 |
| With hunger | 63 | None |
| Hungry and meal ranked first | 5 | None |
| Hungry but meal outranked | 58 | Winner: another food plan 27 times (eat elsewhere 17, collect then eat 10), sleep 22, explore 8, wait 1 |

Of these 58 cases, energy was below threshold in 57 and water in 44.
The winner prevailed on predicted distress alone in 43 cases, and due
to the bonus in only 15. The score margins are small: median 0.027 in
base value and 0.016 in bonus. Meal forecasting was still accurate:
positive predicted food gain in 97% of opportunities, median +10.3.

Two questions remain open:

- **P5d:** zero meals without curiosity (0/125 steps carrying food) remains
  unexplained. P5e observed no carried food in that arm.
- **Deferred meals:** postponement may become costly later. Does innate
  projection underestimate the risk of waiting? Only a preregistered test
  on new Worlds could answer.

## I3 limitations, supported by evidence

The main limitation is structural: the mechanism that rescues the individual
in new Worlds is a designer-added term (curiosity), not the individual's own
assessment of its stakes. Most other learning is tabular or inactive.

1. **Perception.** One-cell radius limits search: the systematic searcher
   survives in about 72% of development Worlds and its funded version in
   only 4/12 P2 Worlds. Unvisited boundary-adjacent cells remain "unknown"
   (G2c edge artifact). No hidden structure is inferred.
2. **World model.** Tabular effects per (action, token), falling back to
   action-level and then global estimates, with no transfer among tokens,
   locations or contexts. Global fallback alone yields 0/288 (P5b).
   Change is handled by a moving average: revisions occur more often but
   not faster, with median latency near 130 steps in G2e.
3. **Value and credit.** Linear TD over six features has no measurable
   effect (117 vs 112). Innate self-projection does most of the work.
   Delayed credit is not learned.
4. **Exploration.** Curiosity β_u × uncertainty × relevance is essential
   (110 vs 4), but it is a hand-crafted additive formula in different
   units from distress. Without it, the individual rests or waits near
   familiar places and dies of thirst (239/288 thirst deaths).
5. **Cost of thinking (v2).** Cycles, horizon and memory are fixed genes;
   the individual cannot choose how much to think. Inactivity is 19%
   normally, 45% in P2, and 72-76% with impaired predictions.
   In P3, the selected arm spends more cognition without a gain.
6. **Memory.** Fixed capacity, no explicit uncertainty over place beliefs;
   paid replay (391,323 operations in P5a) but no measured effect
   (119 vs 112).
7. **Mechanisms resembling hidden rules:**
   - **additive curiosity:** high risk, because it sustains survival;
   - **prudence:** medium risk, paid but no measurable effect;
   - **integrity veto at 10:** acceptable only as a physical body law;
   - **Competition thresholds:** low-to-medium risk, 6/342 differences;
   - **option types, BFS and frontier:** general procedures with a
     fixed repertoire.
8. **Method.** n=4 populations (p >= 0.125), three-generation lineage,
   unmatched probe costs (no exact match in 7,729 steps), energetic
   mediation not isolated (each ablation also changes spending),
   about 1 ms/step.
9. **Ecology.** Water, food, toxic tokens and three dynamics (stable,
   depletion, pulses), but no danger, seasons, delayed toxicity,
   obstacles or competitors.

## Guiding principle: one currency, predicted viability

Every added mechanism must contribute to one quantity: cumulative distress
the individual predicts for its own channels. The prediction includes the
energy and vigilance costs of the computation itself.

- **General mechanism:** estimates consequences for the individual's own
  stakes without steering toward a prescribed behavior. This includes
  inference, planning, memory, value of information and value of computation.
- **Hidden rule:** adds a term, threshold or weight that overrides predicted
  consequences without deriving from them, as additive curiosity does.
- **Also admissible:** generic, renaming-invariant heritable parameters
  (ADR-0014) selected only by individual persistence.
- **Excluded:** scripted actions, World-specific rewards, reward shaping,
  and oracle information.

Two research frameworks support this principle. Homeostatic RL
([Keramati and Gutkin 2014](https://elifesciences.org/articles/04811))
uses reduced deviation from set points as reward; I3's r=-D is close.
Active inference
([Pezzulo, Rigoli and Friston 2015](https://openaccess.city.ac.uk/id/eprint/16671/))
combines pragmatic and epistemic value under one objective. I3 lacks
curiosity **derived from** its evaluation instead of added afterward.
The proposal retains I3's explicit, inexpensive arithmetic rather than a
full variational formalism, costly under v2 and difficult to audit.

## Staged development scenario

One targeted change per gate, preregistered before any exposure, tested
with selected genomes (ADR-0015) on entirely new Worlds (indices >= 120;
P4 reserve sealed). Negative findings remain intact, and nothing is
retuned on a World that has already been opened.

1. **Stage 0: make experiments capable of deciding.**
   - Increase independent genetic populations to at least eight: unanimous
     directional results then give p near 0.008 versus 0.125 with four.
   - Preregister realized energy spending, inactive fraction, lived time.
   - Run "same genome, different histories, common challenge" (#1026).
   - Keep full Competition recording (P5e) as standard instrumentation.
   - Investigate P5d's absence of meals in an arm that actually carries food.
2. **Stage 1: information value in units of the stake.** This answers the
   repository's original priority ("explain active death without curiosity").
   - *Mechanism:* for exploratory options or unknown food, compute the
     expected reduction in predicted distress from what could be learned,
     average over outcomes supported by beliefs, then replan.
   - *Remove:* β_u, relevance and prudence. Urgency follows projection;
     risk follows predicted integrity-effect uncertainty
     ([Behrens et al. 2007](https://www.nature.com/articles/nn1954)).
   - *Cost:* two or three physically billed simulated branches.
   - *Gate:* survival non-inferiority and faster revision in family R.
   - *Ablations:* frozen projection (predicted to lower survival);
     zero-priced information value (predicted to increase spending).
3. **Stage 2: decide how much to think.**
   - *Mechanism:* value of computation
     ([Russell and Wefald 1991](https://doi.org/10.1016/0004-3702(91)90015-C);
     [Callaway et al. 2018](https://proceedings.mlr.press/r16/callaway18a.html)).
     Take an extra cycle only when expected viability improvement exceeds
     its cost, converted to distress by D itself. Replay becomes a
     computation like any other.
   - *Genes:* `n_base` and `h_max` become ceilings, not directives.
   - *Gate:* survival and inactivity fraction compared with fixed budget.
   - *Ablations:* zero perceived cost; random budget with equal mean.
4. **Stage 3: a World model that generalizes and detects change.** One
   gate per mechanism:
   - factorized effects based on generic perceived attributes, with
     shared priors;
   - online change-point detection
     ([Adams and MacKay 2007](https://arxiv.org/abs/0710.3742));
   - latent causes
     ([Gershman, Blei and Niv 2010](http://www.cs.columbia.edu/~blei/papers/GershmanBleiNiv2010.pdf)).

   Change probability feeds Stage-1 information value.
   *Gate:* revision latency. *Tests:* avoid a new token resembling a
   known toxin at first contact; fixed-change ablation.
5. **Stage 4: reusable value when needs change.**
   - *Mechanism:* successor features
     ([Barreto et al. 2017](https://arxiv.org/abs/1606.05312))
     over predicted bodily-channel changes, combined with **current**
     D. Reevaluate immediately when hunger overtakes thirst.
   - *Gate:* repeat P5a ablation; removing learned values should now
     reduce survival.
   - *Test:* delayed toxicity after 20-50 steps.
6. **Stage 5: a map for obstacles and larger Worlds.**
   - *Mechanism:* perceive adjacent edge/wall as impassable, eliminating
     the boundary artifact. Learn a topological map during life
     ([Behrens et al. 2018](https://www.cell.com/neuron/fulltext/S0896-6273(18)30856-0))
     and plan using the Stage-2 budget.
   - *Gate:* withheld family F1.
   - *Ablation:* current frontier. Keep perception radius unchanged.
7. **Stage 6: a lineage selecting how to learn.**
   - *Mechanism:* Baldwin effect
     ([Hinton and Nowlan 1987](https://www.complex-systems.com/abstracts/v01_i03_a06/);
     [Soltoggio, Stanley and Risi 2018](https://arxiv.org/abs/1703.10371)).
     Select generic learning parameters, never learned weights.
   - *Design:* at least eight populations, ten generations,
     recombination, random-parent control, multiple World families.
   - *Gate:* repeat P4a; selection wins in at least seven of eight
     populations.
   - *Control:* learning disabled.

**Lightweight cross-cutting Competition audit.** Thresholds changed the
outcome only 6/342 times in P5e. A small gate can test replacing them with
"highest predicted gain, with continuity justified by predicted switching
cost" without survival loss. Prudence, paid but not measurably effective,
should also be removed. The integrity veto remains only if classified as
a physical body law.

## World-family progression and generalization measurement

Complexity should come from Worlds, never from imposed individual rules.
Freeze each family and its seeds before evaluation. Families may be
generated progressively, as in
[POET](https://arxiv.org/abs/1901.01753), but never retuned after exposure.

| Family | Novelty | Capacity tested |
| --- | --- | --- |
| F0 (existing) | Stable, depletion, pulses | Current baseline |
| F1 | Obstacles, movement-cost terrain, maps 2-4 times larger | Cognitive map (Stage 5) |
| F2 | Seasons and periodic sources | Change detection and latent causes (Stage 3) |
| F3 | Hidden delayed toxicity and tokens sharing attributes | Delayed credit and transfer (Stages 3-4) |
| F4 | Moving danger regions that damage integrity | Cross-channel tradeoffs, risky information |
| F5 | Inventory as portable reserve | Long-horizon planning |
| F6 | Competing I3 individuals | Models of other agents (out of current scope) |

To measure generalization:

- **Disjoint families:** select on some World families, validate on entire
  held-out families.
- **Comparators:** equal initial opportunities (P2 doctrine), with actual
  spending measured as phenotype.
- **Probes:** descriptive until cost equivalence is demonstrated.
- **Criteria:** fixed-horizon survival as primary; revision latency,
  first drink and cognition per lived step as preregistered secondary
  measurements.

## Revised priorities and failure patterns to avoid

Competition auditing drops from third priority to last, because thresholds
decided only six of 342 outcomes in P5e.

1. Stage 0: statistical power, energetic effects, individuality, P5d.
2. Stage 1: predicted-distress information value instead of curiosity
   and prudence.
3. Stage 2: choosing how much to think.
4. Stage 3: change detection and latent causes, then factorized effects.
5. Stage 4: successor features.
6. Stage 5: family F1.
7. Stage 6: multi-family lineage.
8. Lightweight Competition audit and removal of prudence.

Avoid:

- **Disguised shaping:** bonus, threshold or weight to "make the individual
  drink or eat". P5e also shows that most uneaten meals were consistent
  with the individual's own stakes.
- **Per-World rules:** heuristics or options specialized to a family.
- **Oracle:** hidden stock, unseen sources or future scheduled changes.
- **Retuning:** change tariffs, genes or thresholds after World exposure,
  or open the sealed P4 reserve.
- **Forbidden heredity:** inherited maps, learned values or memories
  (ADR-0014).
- **Overinterpretation:** treating p=0.125 with n=4 as confirmation, or
  treating an oracle as an equal-cost upper bound.

## Uncertainties and caveats

The report's figures and code have now been verified at the cited snapshot.
Remaining uncertainty concerns interpretation and future results.

- **P5e reinterpretation:** post hoc on 12 development lives and two
  genomes, not confirmatory, and does not explain P5d.
- **Expected improvements:** Stages 1-6 are hypotheses from other
  frameworks applied to v2 physics. Every stage may fail and its adverse
  result must be kept.
- **Compute cost:** information value and metareasoning can consume all
  their benefit under v2. The gates should decide this, not an intuition.
- **Individuality:** divergent memory digests (144/144) do not yet prove
  stable behavioral differences under a common challenge.
- **Schedule:** the scenario assumes eight or more populations. At about
  1 ms/step, a full gate takes hours of computation; budget the experiment,
  never change behavior to satisfy the schedule.
