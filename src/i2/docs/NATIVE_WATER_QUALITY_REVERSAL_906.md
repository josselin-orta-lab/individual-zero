# I2: born-locked reversal of actually experienced water quality

Research issue #906. This is a minimal **external-world change**, not a
new internal learning algorithm, source oracle, simulator or motor owner.

## Physical model

With recurring ordinary-water offers from PR #908, a native I2 birth may
optionally fix `water_quality_change_at` (integer 0..128, 0 means no
reversal), plus `water_quality_after_gain` (finite physical gain 0..100;
default 0). A positive reversal boundary requires a positive born
`water_restock_every`. The born quality of water is still determined by
`drink_water_gain` before that boundary. At the boundary, and only after
that many completed physical ticks, the effect of a **subsequently
admitted drink** becomes the second quality.

This quality schedule belongs to the actual deterministic external world,
is immutable from birth and is included in the new genesis v6 hash. It is
**not communicated to the individual**. The first-person observation
continues to report only whether the old-water offer is present and
records physical consequences of *actions actually chosen*. A reversal
alone adds no evidence and does not alter the body.

The same one-owner SQLite transaction implements action choice, safety,
physics, current knowledge and later reward evidence. Cold replay
independently recalculates every admitted water effect from the born
external schedule and the prior committed physical ticks. Synthetic UC
and physiological costs remain paid, and a veto still advances time.

## Acceptance

- No quality forecast, hidden result or fabricated extra water in a
  subjective capture.
- Earlier water attempts are evaluated using the actually experienced
  old quality, and post-boundary attempts use only their actual physical
  outcomes. No forcing I2 to drink or forcing its next choice.
- Two separately born learning ON/OFF individuals share the same
  physical offers, birth conditions and external quality reversal.
- False birth data and invalid quality-change values fail cold audit
  or birth validation; absent change defaults to the previous physics.
- This is a **single, bounded reversal** with deterministic timing,
  not evidence that memory produces generalized longitudinal adaptation.

Next scientific gate: a multi-encounter, matched, sufficiently long life
with repeated resource quality reversals and actual re-exposure. Record
behavioral delays, mistakes and costs; do not interpret exploration
arising innately as proof against experiential learning. Do not reopen
dream replay (#902).
