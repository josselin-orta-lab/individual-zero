# I2 native action-specific nonrestoration: physical attribution

Engineering correction to the lived failure branch #897, tracked by #888.

Before this change, native I2 selected the most critical reserve among food,
water and integrity, then classified **every action** as ineffective if it
failed to restore that one reserve. That is a causal category error: a drink
that does not relieve hunger is not evidence that drinking fails to hydrate,
and eating cannot be judged by whether dehydration gets worse.

This increment fixes the existing paid, birth-replayable policy. A native,
predeclared physical affordance maps to the reserve it can ordinarily
restore: drink -> water, eat -> food, sleep/wait -> integrity. It takes two
personally recorded before/after comparisons on the relevant reserve, and
the mapped reserve must be critical now (<=10) to trigger revision. The
recorded physical effect and before/after values remain the sole evidence,
not foreknowledge of food quality, water efficacy, or a hidden world phase.
If the resource has disappeared, prior real failures are still remembered.
An action whose affordance differs from the critical reserve is not falsely
declared ineffective.

When this evidence exists, the existing local first-person goal and paid
Competition can reconsider alternatives. No action is forced, no motor
permission minted, no extra owner/UC bypass created, and no external M11
or I1 comparison is claimed.

Focused tests: two nonrestoring eaten meals under critical food; two
nonrestoring drinks while food (not water) is critical; two nourishing
meals while water is critical. Retain previous thirsty-water and no-learning
negative controls. No scientific superiority or general autonomous survival
claim. See ADR-0009 and issue #888.
