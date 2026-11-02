# I2 native goal reappraisal after a resource disappears

This bounded engineering increment extends PR #896, issue #888.

Before this correction, the I2 subjective goal revision had a blind spot:
when the only offered drinking resource was exhausted after two actual,
nonrestoring attempts, the next capture did not include a drink affordance.
The code then failed to consider those past outcomes and retained the old
intention in suspended state rather than revising its goal.

The native actor now derives prior nonrestoration independently of *current
availability*, using two already committed, personally experienced bodily
before/after pairs. Only currently available candidates can receive value
adjustments in Competition; absence is not a fabricated negative reward.
A depleted drink action can therefore cause a goal reappraisal from
past failures while remaining honestly absent from physical affordances.
This does NOT claim permanent impossibility or that the new intention is
salvific. Exact journal replay checks the genesis and the resulting claim.

Negative checks: resource exhausted after beneficial drinking, no-learning
control with intact innate reflex, and no water available since birth without
any personal failure evidence. No I1 import, new owner, hidden world oracle,
extra motor authority, external M11, or comparison claim.

This branch is stacked on PR #896 and must be reparented onto the merged
main after #896's exact-head tests pass. No additional CI launch is
justified before that first boundary closes.
