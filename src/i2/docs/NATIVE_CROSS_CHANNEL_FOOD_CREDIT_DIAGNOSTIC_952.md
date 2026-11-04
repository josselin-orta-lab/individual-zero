# I2 P4: food restoration versus cross-channel harm

Research-only, 4 November 2026. Companion to issue #952 and PR #953. This dependent branch starts from exact #953 source head 15cd45e93fc59e0dc56e297c8aa2c49d3c43c3ae. No new PR or CI while #953 checks run.

## Scope of the finding

The current native function personally_observed_resource_outcomes counts a food action as a target-specific success when it restores food during hunger. This narrower count does not distinguish equal food restoration with versus without an actual integrity loss. At complete food saturation, a zero-food-gain action with integrity harm contributes neither target success nor target failure. This does NOT prove that all native learning ignores integrity: the generic G2 net-relief history and current bodily interoception may carry cross-channel consequences independently.

## Three purely read-only diagnostic controls

The new test_native_food_cross_channel_credit_diagnostic_952.py exercises synthetic recorded before/after physical row projections, without a new motor or research life:

1. Same food restoration with/without integrity loss gives identical target-specific positive count and learned target adjustment.
2. Saturated food with integrity loss gives no target-specific success or failure, rather than an inferred failed meal.
3. Learning OFF leaves this target-specific credit absent.

These tests are NOT_RUN while #953 exact-head CI is in progress. No new state owner, policy change, action veto, source-specific score, hidden future effect, or invented decision. Pure tests do not demonstrate a real-world behavior difference.

## Decision sequence

First inspect the four independent paid 64-tick harmful/harmless #953 life outcomes and cold audit. Preserve nulls and bodily harm. If actual choices fail to distinguish physical harm, consider a separate observational diagnostic of generic G2 outcomes, paid native scores, current needs and action timing before proposing any new learning rule. Do not retune #953 after results.

After #953 exact-head dual-Python PASS and merge, reconstruct this test-only slice on the merged main and open one focused PR for Python 3.11 and 3.12. Scientific P4, G3/H3 and independent M11 remain NOT_ESTABLISHED.
