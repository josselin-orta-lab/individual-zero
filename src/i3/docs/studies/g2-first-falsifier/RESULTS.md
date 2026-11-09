# I3 G2: Result of the first falsifiable test

**Verdict: `G2_PASS_BEHAVIOURAL_AND_TECHNICAL`.** Executed once on
5 November 2026, on the preregistered code (commit `e25bf63`;
[protocol](../../G2_FIRST_FALSIFIER_PREREG.md)).
Full data: [result.json](result.json). This is a passed software gate and
behavioral falsifier, **not** scientific evidence of learning.

## Preregistered criteria

| World | Drank (required 8/10) | Alive at 300 steps | Deaths | First drink (median, range) | Drinks / meals (medians) | Sleep share (median) |
| --- | --- | --- | --- | --- | --- | --- |
| `g2-i1-foraging-like` | **10/10** | 9 | 1 (thirst) | step 7 (3-13) | 23.5 / 7 | 29% |
| `g2-i2-native-A-like` | **10/10** | 10 | 0 | step 5 (1-9) | 30 / 17 | 27% |
| `g2-i2-native-B-like` | **10/10** | 10 | 0 | step 3 (3-6) | 37.5 / 17 | 26% |

Engineering: 30/30 identical replays; **0.40 ms per step** on average
(1 ms limit); 7.6 seconds for 66 life executions.

Non-paired historical anchors from the 5 November diagnostic: I1
*foraging* (seed 7) died of thirst at step 106 after sleeping 82% of the
time; I2 World B died at step 111, stuck at the passage.

## Secondary observations (descriptive, without tuning)

**The separately reported midpoint genome dies of thirst in the foraging
World at step 106 without drinking.** At the first step, exploring east
(toward hidden water) and north tie. The random draw selects north. Nearest-
frontier exploration then follows the boundaries, moving away from water
until exhaustion. Failure under ignorance is legitimate, but the policy
covers space poorly.

**Genome 8 dies of thirst at step 267, after drinking twice.** Once hydrated,
it moves about twenty cells away from known water. Return begins at water
10.8 and energy 22, too late. Hypothesis: innate projection holds energy at
the end-of-trip level, so a long return that ends low-energy looks costly
forever and is deferred until thirst dominates.

## Limits

Ten generation-zero genomes and three frozen Worlds test only one architecture
capacity: leaving paralysis and reaching water. There is no paired I1/I2
comparison: I3 sees neighboring cell contents (unlike I2), pays for cognition,
and has neither nighttime nor inert objects. No learning is demonstrated.

## Historical next steps

1. **P1.1:** correct self-projection of energy/vigilance toward sleep
   restoration and improve spatial exploration, developing only on
   `lab/dev_worlds.py`; test on **new** reserved Worlds, never tune on G2.
2. **P2:** World-family generator and feasibility probe, then G3 gate with
   families frozen before evolution.

*English translation. Original preserved unchanged at
`archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2-first-falsifier/RESULTS.md`.*