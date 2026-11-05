# I2 P4 #984: need-contingent bounded exploration (native v23)

**Preregistered before this implementation, test, or born cohort** in [#984, comment 6638113655](https://github.com/josselin-orta-lab/individual-zero/issues/984#issuecomment-6638113655), on 4 November 2026. Code baseline is native v22 `main ed240f9bbaffe963cc8d978609ae39714832c07e`, after #983 independently verified opportunity diagnostics. This is **research only**, not a running I2 engine or G3/H3/M11 general survival demonstration.

## One new birth-locked hypothesis

The first-person organism cannot rank an **unknown** source by unobserved food quality, but it can know that its own recent *resource consumption attempts failed to restore an unmet need*. A single additional **default-OFF** immutable v23 genesis flag `need_failure_exploration` is accepted only for independently born `learning=True, spatial_world=True` native research individuals. Its exact value is stored in the existing single SQLite `native_genesis` hash and reverified in the independent cold cognitive/physical replay. No old-born migration, no second memory, motor authority or scheduler.

Current personally unsatisfied food/water pressure must be positive in the existing `assess_needs` model. For **each target channel separately**, the two most recent personally committed need-relevant `manger` (food) or `boire`/`boire_decouverte` (water) actions are failures only if neither raised its corresponding actual bodily reserve. Prior need was present at each attempt. Passive body decay, idle ticks, sleeping, unavailable/unselected resources, a single failure, and an observed restoration do not establish a double failure. This is target-specific, not a fictitious whole-body learned safe-site reward. A food-restoring meal with negative integrity is not relabeled a failed *food* restoration.

Provided there are at least two personal failures of either current need, a positive born exploration trait, no native `PREEMPT`/`CONSTRAIN` reflex, and exactly **one** currently **offered, adjacent, never personally visited** destination, the existing paid scores are examined **after** all v22 adjustments including innate novelty. No stacking on an existing credited innate novelty move. If the best paid score lies strictly between 0 and 1024 and the unknown movement has a positive score at most **4 below** the best, its value is set to best+1. The maximum increment is therefore **5 existing integer score units**. This constant is predeclared in #984 and not tuned to the chosen trajectories. This is a bounded, generic, symmetric competition *proposal*, not a motor order: existing Competition, Control, energy costs, UC, local adjacency and terminal state retain authority. The selected destination is UNKNOWN as to its future food supply, safety and success.

Only a genuinely modified score receives the provenance suffix `:personal-need-failure-adjacent-exploration`. Both runtime valuation and cold audit must reproduce exactly the same selected candidate, score and suffix using only the single owner's committed history. When flag OFF, v22 behavior must remain source-identical under the v23 genesis.

## Frozen first six-life falsifier, no guaranteed favorable outcome

`tests/i2/test_native_need_failure_exploration_v23_984.py` is an exploratory, unedited six-life 96-paid-step-or-death panel in unchanged camp-passage-source adjacency: birth E78/F46/W44/I94, temperament (0,.5,.3,0,0); passage food stock1/refill12/+**0** real food (non-restoring); hidden source food stock1/refill12/+**20** real food, hidden integrity injury source either **0** (world helpful-unknown) or **-12** (world harmful-unknown). Camp-only water stock2/refill10/+35; 1000 UC; standard metabolism, body repair and movement costs. Neither source quality nor remote stock is available as first-person knowledge until paid local contact.

Within **each** world independently born comparison arms:
1. Innate control: learning OFF, new factor OFF.
2. Existing learning control: learning ON, new factor OFF.
3. New v23 factor: learning ON, new factor ON.

All other experimental birth switches are identical: `spatial_world=True`, `origin_novelty_tie=True`, `target_food_credit_enabled=False`, `contextual_movement_credit=False`, `place_return_tie=False`, `evidence_tie_exploration=False`, `sleep_consolidation=False`, `purpose_followthrough=False`. There are no motor scripts or progress-dependent parameter changes. All births have their own SQLite identity and are independently cold audited after the genuine end/censor.

Read actual paid motors/NO_ACTION, prior same-world physical state until first divergence, exact observed failed meals, local food offers, distinct source *movement* versus source *meal*, original novelty and new failure-evidence ticks, injury and food gains, final/minimum four needs, cost, genuine death versus 96-tick technical censor. A harmless source that was never visited is **NO_ALTERNATIVE_EXPOSURE**. A harmful visited source may worsen survival. Evidence-tag presence alone is not behavioral rescue. A hunger score may dominate exploration despite failure: **NO_ELIGIBLE_SCORE_GAP** is legitimate. Death, starvation, null choices and harmful exploration are valid, non-discarded outcomes.

The independent pure negative tests cover 0/1/2 need-relevant failures and recent success, zero hunger, native urgent reflex, missing or multiple unknown neighbors, hidden-stock agnosticism, source-label permutation, out-of-range score gap, disabled mode, exact birth eligibility and digest tampering. Additional short born no-stock/harmful worlds can demonstrate no invented resource contact, **not** a guaranteed alternative strategy.

## Boundary and stopping decisions

This increment is a narrow behavioral research mechanism, not a new integrated planning system. **No site-specific safe-food bonus, omniscient map, source name advantage, guaranteed exploration, action admission override, physiology edit, G3/H3/M11 activation or I1 dependency**. A better source visit without a genuinely chosen resource meal is not a successful dietary switch. A positive single selected 3-site scenario is exploratory only; general survival requires longer independent lives, changed topologies, and demonstrated improvement over controls in both helpful and harmful unknown worlds.

**CI discipline**: one coherent source, tests and note PR, one ordinary exact-head complete Python 3.11+3.12 I2 test workflow with six static generation boundaries and inert-engine guard. Do not retune this frozen cohort from readouts. Preserve all null/negative outcomes and any true deaths.
