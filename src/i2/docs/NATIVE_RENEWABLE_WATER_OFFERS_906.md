# Native I2: born-timed recurring physical water offers (preliminary)

Issue #906, staged **after** the single-individual life extension in #907.
This is a small exogenous environment feature, **not** a renewed-water
learning benchmark or demonstration of natural longitudinal adaptation.

## Mechanics and invariants

A new optional immutable birth parameter, `water_restock_every`, fixes
the number of committed physical ticks between reappearances of ONE
ordinary water offer. 0 (default) preserves the prior finite old-water
world; positive 1..32 means one new drink opportunity after each
complete interval. The bound and existing birth water stock are hashed
with the rest of the born genesis v5. The current supply is calculated
from already committed physical history as:

`birth_stock + floor(committed_ticks / interval) - admitted_old_drinks`

(with zero additions if interval is zero). This recurrence is **the
physical world's accessibility**, not a learned prediction or a
replenishment of body hydration. Actually drinking still costs paid
cognition and an admitted physical action, with the birth-locked drink
effect; an empty or ineffective water offer grants no reward.

A new refill is exposed in the first-person capture only **after** its
physical threshold has been crossed by a completed action/abstention.
The capture includes causal evidence
`evidence:i2:native:water-offer-refilled:<physical_tick>` for completed
epochs only. The `learning` flag does not control refill scheduling.
Cold replay recomputes the offer and capture evidence from the SAME
native SQLite journal and immutable genesis. No second world scheduler,
motor owner, UC owner, or I1 runtime is introduced.

This initial bounded mechanism deliberately has no external weather,
multiple sites, sleep-dependent refill, quality inference, or learning
shortcut. The same old-water outcome parameter applies to each drink.
It is a prerequisite for repeated *real opportunities*, not yet
varying reward across context or evidence of adaptation.

## Acceptance criteria

- Life with at least 12 committed ticks observes replenishment only
  after ticks 3, 6, 9 etc., never in an earlier capture.
- Cognition may choose or ignore the offer; no enforced motor tape.
- A used old-water offer cannot be reused until physically renewed.
- Independent learning-on/off births share the same initial physiology
  and schedule; identical hidden world outcomes until observed.
- Mutation of birth refill cadence fails cold audit; invalid cadences
  including booleans, negatives, floats and >32 fail at birth.
- Default zero cadence preserves earlier finite-resource native tests.
- No claim of long-term natural learning, I1 comparability or
  independently witnessed M11. Dream-like replay stays deferred #902.

Next step: contextual variations in the *actual outcomes* of repeated
water encounters, and delayed longitudinal re-exposure measured in
matched independently born individuals.
