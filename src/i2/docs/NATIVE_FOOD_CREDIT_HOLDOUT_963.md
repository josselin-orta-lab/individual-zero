# P4 #963: prospective out-of-sample food-credit survival probe

**Frozen 4 November 2026, before running the eight new paid lives.**
This is a scenario-level prospective follow-up to discovery cohort
[#960](https://github.com/josselin-orta-lab/individual-zero/issues/960),
source-locked [PR #961](https://github.com/josselin-orta-lab/individual-zero/pull/961)
and [#963](https://github.com/josselin-orta-lab/individual-zero/issues/963).
Branch source: main `0f858a6fa516f6f8696f9ccc8eb6e4ce11c8ee4a`.
The validated **v19 runtime is unchanged**. These four new worlds were selected
after the discovery experiment: they are different physical conditions, **not**
randomly sampled statistical replication or untouched external confirmation.

## Four new matched environments (eight independently born paid lives)

Both experimental arms in each named world differ **only** in immutable,
birth-hashed `target_food_credit_enabled=True/False`; the rest of the
native cognitive package remains ON, including generic G2 outcome learning,
place-return, purpose follow-through, contextual movement credit, innate
current-body needs and critical last-resort protection.

Each arm starts at `camp`, food is physically located at `passage`,
water at `camp`, `berry_food_gain=35`, `drink_water_gain=40`,
food stock=1, and at most **96** real paid committed ticks with **950 UC**.
Sleep consolidation and evidence-tie-exploration are both OFF.
No scripted motors or omniscient resource information.

| World key | Born body (energy, food, water, integrity) | Born temperament (reward, threat, exploration, goal, affiliation) | Food integrity effect | Food / water refill periods | Water stock |
| --- | --- | --- | ---: | --- | ---: |
| `hungry_harmless` | 85, 18, 35, 100 | 0, .5, .3, 0, 0 | 0 | 8 / 8 | 2 |
| `mild_harm_threat` | 85, 35, 35, 100 | 0, .8, .15, 0, 0 | -4 | 8 / 8 | 2 |
| `severe_harm` | 85, 35, 35, 100 | 0, .5, .3, 0, 0 | -12 | 8 / 8 | 2 |
| `scarce_competing_needs` | 85, 18, 28, 100 | 0, .5, .3, 0, 0 | -8 | 32 / 16 | 1 |

This is a **fixed diagnostic panel**, not a balanced factorial experiment;
harm, temperament, hunger and scarcity vary **between worlds** and are not
separately identified as causal main effects. Matched ON/OFF comparisons
within a world are the only intended attribution. Prior #960 world's -8/0
conditions at 64 steps are *discovery*, never pooled into this panel.

## Readouts and stopping rules

For each independent born life, retain all physically admitted actions
and legitimate `NO_ACTION` abstentions, visited sites, real food/water offers,
actual meals and before/after body effects, including near- and zero-gain meals,
full-horizon and minimal food/water/integrity, last actual relief from a
personally eaten meal, true terminal and tick (if any), maximum horizon censor,
earned/spent UC and independent cold inspection replay. The native journal's
committed paid advice supplies food/rest/water value and evidence provenance
at the **first** pairwise motor divergence, alongside the current physical
body, needs and previous target-food success/failure count.

Primary measures: biological terminal-free committed steps, terminal event
rate, minimum food and integrity. Water minimum/terminal, hunger/injury
tradeoffs and UC are essential secondary measures. A food offer is only
credited at the physical food site and with available stock; water must be
at camp and stocked. An individual never actually offered food is
`NO_FOOD_EXPOSURE`, **not** a failure to value harmful food. Horizon ends
are **right-censored**, not proven survival beyond 96 ticks.

Engineering falsifier: at the first motor divergence within a physically
matched pair, both arms must still have the **same current body and prior
real motors** with at least one personally experienced food-target outcome,
else attribution to the target-credit switch fails. Once a motor diverges,
later physical and cognitive histories are confounded. No requirement that
OFF win, eat fewer times, improve integrity, visit the source, or survive.

## Interpretation and budget gate

If OFF reduces harmful food intake but loses necessary nourishment, worsens
terminal risk or inhibits harmless feeding in the new worlds, do not flip the
default. If it reduces injury without starvation across these selected
worlds, that supports further longitudinal work but is **not** evidence
of broadly natural learned harm avoidance or general survival GO.
No policy reweighting, hidden future food quality, generic neural
replacement, new reflex, forced exploration, or changed world physics
is allowed after reading outcomes.

One test-only PR (new research test and this document), one complete
exact-head Python 3.11/3.12 sharded workflow with 100% discovery/execution,
six generation-boundary controls and inert proposal result. Do not remove
existing longitudinal tests or trigger CI for each preparatory change.
Survival GO, P4 generalized causal learning, G3/H3 and independent M11
remain **NOT_ESTABLISHED**.
