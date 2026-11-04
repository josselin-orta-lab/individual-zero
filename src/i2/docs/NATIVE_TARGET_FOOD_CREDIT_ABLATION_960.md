# Native P4 #960: food-target credit ablation without reward shaping

**Prospective protocol fixed 4 November 2026 before running the new lives.**
Follow [#960](https://github.com/josselin-orta-lab/individual-zero/issues/960), #957 and
accepted ADR-0012/0013. Working branch starts from source-locked main
`8606330bbaee38623e5d94cb7c94b0da76cc7269`.

## Falsifiable research question

Previously experienced food restoration currently replaces the already computed
generic net-outcome food value with a target-specific association based on
restoring the food reserve only. Does retaining the **existing G2** score
instead (without adding a new score formula) change subsequent personally
paid food, rest and safety decisions in a harmful versus harmless environment?
The project may legitimately find no benefit, fewer helpful meals, no
discovery, or a detrimental effect.

## Minimal owner-preserving v19 intervention

New **research-only immutable genesis** version
`i2-native-paid-local-life-v19-target-food-credit-ablation` with
`target_food_credit_enabled` exact-bool born switch, default **True**.
The switch is stored in the only native SQLite genesis, included in its
digest, exposed to the same paid valuation path and independently reconstructed
from genesis and prior physical journal during cold audit. Rewriting the
flag invalidates the genesis. Older signed v18 lives are not migrated.

When False, only the positive/negative `manger` target-outcome score
**replacement** is skipped. In particular unchanged are: generic G2 learned
chosen-outcome relief, food and water physics, local stocks/replenishment,
current body and innate needs, `boire` target credit, optional place learning,
sleep or contextual movement logic, competition, fresh Action Control, paid UC,
and the independent `personally_nonrestoring_action` critical last-resort
gate. A repeatedly failed resource under physiological emergency must still
be clamped to nonpositive in the original urgent reflex.

## Four fixed independent native paid lives

2 × 2 born parameters: target food credit ON/OFF × food integrity penalty
-8.0/0.0. All **four** have learning ON, food at `passage`, water at
`camp`, initial body (energy 85, food 35, water 35, integrity 100),
temperament (reward 0, threat .5, exploration .3, goal 0, affiliation 0),
food/water stock 1/2 and replenishment periods both 8 committed ticks,
food gain 35, water gain 40, paid budget 850 UC, up to 64 committed
decisions, sleep consolidation OFF and evidence-tie-exploration OFF.
The existing P2 return/purpose/contextual movement effects are ON.
All physical laws and traits are matched across each pair except the
intended food harm; the single credit flag is the only learning contrast.

Every decision is autonomously proposed, valued, controlled and physically
admitted. No motor script, forced destination, hidden counterfactual quality,
hunger override, external reset or experimenter-induced food avoidance.

## Predeclared readouts and negative controls

For each born life: independent audit of actual committed native SQLite state
and cold reopen, full action/site timeline, local food-offer ticks, paid
food/rest valuations and evidence refs, all actually chosen meals with
before/after food and integrity, negligible (<5) and zero realized food gain,
UC, body and terminal vs technical horizon right-censoring. The first
choice divergence across food credit arms is recorded, even if absent.
Site-local offer checks and absence of remote refill subjective markers are
mandatory. Death and any null or worsening outcome are retained.

Pure source controls: default-True parity, immutable exact-bool birth and
digest tamper rejection, non-food and water scoring parity, target food
credit ON/OFF contrast, persistent emergency nonrestoration reflex, no
secondary owner or changes to physique. A life must not be described as
adaptive merely because the proposed component ablation eats less: first
inspect true starvation, injuries, need pressure, other bodily values,
and the first G2/target score difference.

## Acceptance, dependencies and limits

One coherent PR with code + test + this documentation; one exact-head
dual-version sharded Python 3.11/3.12 workflow, full discovered/executed
counts, six repository boundaries and inert assessment PASS. Never remove
or shorten existing research cohorts or run repeated CI for partial edits.
Technical tests prove only an isolated mechanism and journal integrity.
P4 causal learning, robust self-preservation, G3/H3 and independent M11
remain **NOT_ESTABLISHED** until separately demonstrated.
