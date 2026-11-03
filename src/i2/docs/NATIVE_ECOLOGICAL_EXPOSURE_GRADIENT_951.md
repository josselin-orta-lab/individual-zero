# I2 P3/P4: graded first-person exposure, without a new exploration rule

**Prospectively fixed on 4 November 2026, before any graded-world test run.**
This is a dependent, **NOT_RUN** research-only branch based on #950 exact head
`dd4a12034f7c2449badf125396832c58fb7a4806`. Do not open a CI-triggering
pull request before #950 passes Python 3.11/3.12 and merges. Reconstruct only
this new test and protocol from the new main at that time. Owners: [P3 #925](https://github.com/josselin-orta-lab/individual-zero/issues/925),
[P4 #906](https://github.com/josselin-orta-lab/individual-zero/issues/906),
[route ties #949](https://github.com/josselin-orta-lab/individual-zero/issues/949).
The approved [ADR-0012](../../../docs/decisions/ADR-0012-i2-scientific-development-methodology.md)
and [ADR-0013](../../../docs/decisions/ADR-0013-lived-autonomy-and-experimental-restraint.md)
require behavioral diagnosis before adding new score offsets.

## Research question and limitation

The already observed #947 96-step cohort reached `passage` but never `source`;
the movement choices `passage -> camp` and `passage -> source` were
repeated positive equal-top candidates, leading to genuine `AMBIGUOUS`
abstentions. Thus the two distinct hypotheses are:

1. **Physical exposure bottleneck:** the individual would be capable of
   autonomously using food when its current first-person observations
   actually offer it, but two-hop spatial access prevents exposure.
2. **Local arbitration bottleneck:** food is physically present, offered
   and locally observable, yet the individual still declines to eat
   because of its need state, valuations or other affordances.

A positive outcome in a nearer site is not a proof of spontaneous discovery,
general natural learning, ecology-spanning adaptability, or a reason to
call the longer-distance abstention a software bug. This graded placement
is **exploratory follow-up selected after seeing the #947 negative result**,
not a genuinely untouched held-out replication.

## Fixed three-context, two-arm protocol

Six **independently born**, uninterrupted research identities. Use identical
native code and competition, no new cognitive valuation or bonus. The sole
physical-world variation is where ordinary food is born, namely
`camp` (zero hops), `passage` (one hop), or `source` (two hops)
on the same paid P1 graph. Water remains at `camp`. Each context has an
independent learning OFF and ON birth with the same physical law, body,
temperament and finite currency. Learning ON retains the previously tested
P2 **bundle** of `place_return_tie`, `purpose_followthrough` and
`contextual_movement_credit`, while OFF disables that bundle. This is not
a single-factor learning ablation.

For each birth: body `(energy=85, food=35, water=35, integrity=100)`;
temperament `(reward=0, threat=0.5, exploration=0.3, goal=0, affiliation=0)`;
`uc=850`, horizon **64** physically paid decisions, food stock **1**, water
stock **2**, food/water replenish every **8 committed physical ticks**,
food gain **+35**, water gain **+40**, no sleep consolidation and no
evidence-tie-exploration. No external motor action, forced arrival,
altered action priority, death reset, continuation across separate births,
or future stock/quality in subjective evidence. Stop on true terminal,
otherwise label the technical horizon as right-censored.

## Primary and secondary observations

For every life, record **all committed actions and visited sites**, location
of each first-person `manger` offer, actual admitted `manger` tick and
its before/after bodily food, all water/food/energy trajectories, UC, actual
paid advice states and positive route ties, biological terminal vs technical
horizon, and independent cold replay. Predeclare disjoint interpretations:

- `FOOD_CONSUMED`: at least one physically paid meal at the birth site.
- `FOOD_OFFERED_NOT_CHOSEN`: the individual observed an accessible local
  meal but no meal motor was admitted.
- `FOOD_SITE_VISITED_NO_OFFER`: physically visited but food was not
  available at the time.
- `FOOD_SITE_NOT_VISITED`: no physical contact with the food site.

For `camp`, arrival at birth is **zero** hops and does not imply either
consumption or learned site usefulness. A physically exposed but ignored
meal is not the same as a failed exploration. A meal driven by innate
pressure rather than recalled experience cannot establish learning.
A negative or deceased life is valid research data.

## Technical falsifiers and interpretation stop rules

Reject the execution if a remote meal is offered, an offer lacks actual
stock, a meal is taken without fresh admission, resource outcomes or UC
change without a genuine action, subjective capture leaks hidden
water-replenishment history under #950, or cold audit disagrees. No
positive action assertion and no reward shaping after seeing outputs.
If food use occurs only at camp, classify near-access ability, not learning.
If food at passage is offered and ignored, inspect actual paid competition
rather than adjusting its tie policy. If none visits `source`, preserve
`NO_EXPOSURE` and the documented corridor ambiguity. If different
sites yield different outcomes, they represent environment-access
sensitivity, not independent scientific generalization.

Do not merge behavioral changes with this test-only slice. The existing
physical environment, born flags, score policies, Action Control and
immutable #933/#939/#941/#943/#947 results remain untouched. P3/P4,
scientific G3/H3 and independently authenticated M11 stay
**NOT_ESTABLISHED** unless separate evidence is obtained.
