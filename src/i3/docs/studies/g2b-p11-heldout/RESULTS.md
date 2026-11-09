# I3 G2b: P1.1 versus P1 on held-out Worlds (result)

**Preregistered decision: `ADOPT_P1_1`.** One execution on
5 November 2026 ([protocol](../../G2B_P11_HELDOUT_PREREG.md), commit
`d88fc3d`). Data: [p1.json](p1.json), [p11.json](p11.json),
[g2-regression-p11.json](g2-regression-p11.json),
[verdict.json](verdict.json).

## Criteria

| World (30 genomes, 400 steps) | Drinkers P1 / P1.1 | Survivors P1 / P1.1 | Thirst deaths after drinking P1 / P1.1 | Distant source used P1 / P1.1 |
| --- | --- | --- | --- | --- |
| H1 hidden spring (water four cells away and unseen) | 9 / 9 | 1 / 0 | 0 / 0 | Not applicable |
| H2 round trip (water at origin, food ten cells away) | 30 / 29 | 29 / 28 | 1 / 0 | Not applicable |
| H3 dried spring (finite A, distant B 14 cells away) | 30 / 30 | 3 / 2 | 15 / 16 | 3 / 1 |

Non-inferiority (margin three) holds in all three Worlds; the H2 targeted
defect is not worse (1 -> 0); G2 regression passes (10/10 drinkers in each
World, and 7/10 foraging survivors versus 9/10 under P1); identical replays;
0.56 ms/step.

## Interpretation

**P1.1 makes no measurable difference.** Differences range from one to two
lives per 30 in either direction. The correction is adopted because it is
principled and non-inferior, not because it improves survival.

**The dominant defect is finding what lies out of sight.** With water four
cells away in H1, only 9/30 individuals find it and 29-30 die before step
400 (median 113). In H3, almost everyone drinks from the nearby source,
but when it runs dry, only 1-3 find the second spring: strategy revision,
the central challenge of ADR-0013, fails. Returning to a known spring
in H2 works (28-29 survivors out of 30).

## Historical consequence

No lineage should start with this poor unknown-space search; selection would
primarily select luck. Proposed P1.2 development-only work:

1. Estimate the feasible ceiling under this perception and energy economy
   with a systematic, non-oracle laboratory reference searcher.
2. Design spatially covering exploration with heritable generic heading
   persistence and search radius.
3. Verify on **new** held-out Worlds. H1-H3 must no longer be tuned against.

*English translation. Original preserved unchanged at
`archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2b-p11-heldout/RESULTS.md`.*