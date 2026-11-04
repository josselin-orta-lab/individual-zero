# i2 P4 #967: one 128-tick life with competing body needs

**Frozen 4 November 2026 before running any of these six lives.** Scientific
contract [#967](https://github.com/josselin-orta-lab/individual-zero/issues/967)
and longevity [#906](https://github.com/josselin-orta-lab/individual-zero/issues/906).
This dependent branch begins at proposed #966 head
`e680196b6d33c8fadad1cdba4857b723639dcdc5`. Do NOT open a CI-triggering
PR before #966 exact-head Python 3.11/3.12 PASS and merge; transplant only
these new test/document files to merged main.

## Fixed born worlds

Three separate physical worlds, each paired with birth `target_food_credit_enabled`
ON and OFF. All six are independently born, learning ON, no source oracle,
no forced motor or episode reset, and up to 128 actual paid committed ticks
under the one born SQLite owner. Common: `Body(85,12,16,55)`,
`BirthTemperament(0,.5,.3,0,0)`, physically local food at passage,
water at camp, food/water stock 1/1, replenish 24/16, food gain +35,
ordinary water gain +12, 1000 UC, P2 spatial/purpose/return credit ON,
evidence-tie exploration and sleep consolidation OFF.

- `fragile_harmless`: food integrity delta 0, water remains +12.
- `fragile_harmful`: food integrity delta -12, water remains +12.
- `fragile_harmful_water_collapse`: food integrity delta -12,
  after 48 committed ticks water effect becomes 0 on any subsequently
  admitted ordinary drink. Quality is hidden until physical contact.

These selected worlds are **not randomized statistical replicates**. The
first two establish harmful/harmless context; the last pair tests a real
hidden exogenous quality change rather than a policy-scripted reversal.

## What will be measured

Full committed action/site chronology, honest NO_ACTION, offered local food
and water, actual before/after food and integrity for meals, physical water
gain for each admitted drink and first contact after the quality reversal,
last-resort goal ticks, minima/final body, actual terminal vs technical
right-censor at 128, UC, first paid value/evidence divergence between
birth-matched food-credit ON/OFF, and independent cold inspection audit.

A quality reversal **not contacted** must be labeled
`UNOBSERVED_CENSORED`, never learned. The stable-water and degraded-water
worlds may not physically differ before an actual chosen post-tick-48 drink.
A matched ON/OFF first motor divergence is interpretable only when its
preceding admitted motors, body and actually acquired food-target memory are
identical. Later bodily divergence is confounded; dying early is a real
negative survival outcome, not a failed technical test.

No runtime, cognitive weight, physics, admission, safety, UC, or owner
changes. No unchosen-counterfactual injection or artificial score. Full
Python 3.11 and 3.12 sharded tests and six boundaries once on a clean
merged-main branch after #966. No P4, G3/H3 or independent M11 scientific
promotion without separate longitudinal evidence.
