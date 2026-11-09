# I3 G2: Preregistration of the first falsifiable test

**Filed on 5 November 2026, before executing any of the three test Worlds.**
Protocol `i3-g2-first-falsifier-v1`; executable
`src/i3/lab/first_falsifier.py`. The commit SHA containing this document and
its executor is the reference. Whatever the outcome, results are published in
a separate commit.

## Research question

Can the I3 core, with generation-zero genomes and no evolution, overcome
paralysis and reach water in the situations where I1 and I2 died of thirst in
the 5 November diagnostic, without situation-specific behavioral rules?

## Frozen conditions

| World | Reproduction | Geometry and resources |
| --- | --- | --- |
| `g2-i1-foraging-like` | I1 *foraging* preset (thirst death at step 106; water two cells away) | 30 x 30, birth (7,7); unlimited water (+40) at (9,7) and (10,9); `berry_a` (+10 food) at (8,7) x4 and (7,9) x3; `berry_b` (+5 food, -10 integrity) at (11,8) x3; body 70/45/42/85, vigilance 100 |
| `g2-i2-native-A-like` | I2 native World A (108 abstentions out of 128 in the diagnostic) | Camp, passage and source corridor; water at camp (+35, stock 2, +1 every ten steps); food at passage (+20, stock 1, +1 every eight steps); body 78/46/44/94, vigilance 100 |
| `g2-i2-native-B-like` | I2 native World B (thirst death while stuck at the passage) | Corridor with water and food only at the source (stock 2, +1 every eight steps); same initial body |

**Genomes:** `generation_zero(1)` through `generation_zero(10)`, one life
per genome per World, life seed 1000 + n, horizon 300 steps. The midpoint
genome is reported separately as a descriptive observation.

**Declared differences from the original conditions:** I3 sees the contents of
the four neighboring cells (like I1 but unlike I2). It has vigilance and pays
energy for cognition. These Worlds omit wood, stone and nighttime. The test
assesses I3 architecture; it is not a matched I1/I2 comparison.

## Criteria fixed before execution

1. **Behavior (primary):** in **each** of the three Worlds, at least **8/10
   lives** drink at least once before death or the horizon.
2. **Engineering:** replay all 30 lives once more and obtain identical trace
   heads; mean execution time <= **1 ms/step**.

## Verdicts

- `INVALID_EXPERIMENT`: any replay divergence.
- `G2_PASS_BEHAVIOURAL_AND_TECHNICAL`: both criteria hold. A software gate and
  behavioral falsifier have passed, **not** a scientific learning result.
- `G2_FAIL`: otherwise. Return to P1 design before starting a lineage.
  Tuning on these three test Worlds is prohibited.

## Declared development history

The core was developed only on `lab/dev_worlds.py` (14 x 14 open field and
six-cell corridor), which differs from the test geometry and numbers. The five
architecture corrections are documented in [SPECIFICATION.md](SPECIFICATION.md).
None of these three test Worlds was executed before filing the original.

*English translation. The original preregistration is preserved byte-for-byte
under `archive/i3/original-language-records-2026-11-09/src/i3/docs/G2_FIRST_FALSIFIER_PREREG.md`;
the frozen historical protocol and identifiers have not been altered.*