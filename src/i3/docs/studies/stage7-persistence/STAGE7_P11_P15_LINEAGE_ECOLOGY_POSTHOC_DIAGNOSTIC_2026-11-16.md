# Stage7 post hoc diagnosis: P11 and P15 inheritance versus campaign/ecology variation

**Date:** 2026-11-16. **Status:** exploratory, original-level, read-only. This report is not a new pre-registration or new scientific verdict. Frozen source `06cfcf9cc9414e0f139b39a42d05177ddb813782`, run [#43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125), prospective rule positive G2 selected-minus-random_parent in >=13/16 populations **and** positive overall mean. The published primary result remains **12+/4-/0 ties; +11.9036458333 lived steps; FAIL** (`PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`).

## Evidence and reproducible method

Data inspected: all recorded native-life outcomes in the scientific archive (#14218795289), including G1 and G2 original-level lived steps, terminal state and recorded drinking/feeding; the 24 offspring genome records per population/arm/generation in `SELECT_G1.json` and `SELECT_G2.json`; founder hashes in `FOUNDERS.json`. No new world or life was run.

Each generation's 24 genotypes is evaluated under three families (`stable`, `depletion`, `pulse`) and two repeats, creating 144 original lived-step observations per arm/population/generation. Decompose the G2 differences into **six 24-vs-24 blocks**. These blocks are descriptive strata, **not six independent confirmatory replication experiments**: genotypes reappear and the 16 population-level contrasts are the frozen inference units.

The exact parent-slot and parent-genome-hash linkage is correct for **192/192 parent-to-offspring mappings** across P11 and P15 in G1/G2, both arms. Each G2 genotype is thus demonstrably derived from the claimed parental lineage, with mutations recorded. This verifies inheritance of the genome representation, not heritability of a *fitness effect*.

## Original-level G2 contrasts by family and repeat, selected minus random_parent (mean lived steps)

| Population | Family | Repeat 0 | Repeat 1 | Both-repeat family mean |
|---|---|---:|---:|---:|
| P11 | stable | -24.8333 | -22.7917 | -23.8125 |
| P11 | depletion | +6.7917 | -78.1250 | -35.6667 |
| P11 | pulse | -50.6250 | -12.6250 | -31.6250 |
| P15 | stable | +9.3333 | -32.0000 | -11.3333 |
| P15 | depletion | -4.2083 | -9.2500 | -6.7292 |
| P15 | pulse | -20.1250 | -50.5000 | -35.3125 |

**Both populations: five negative blocks out of six.** P11 has a notably strong repeat contrast in depletion (repeat 0 positive +6.79, repeat 1 negative -78.13), showing that block-specific conditions or variability matter. P15's pulse disadvantage is negative in both repeats, but sizes differ (-20.13 vs -50.50); its stable repeat changes sign. As the same 24 genotypes are reused across all three families and repeats, these observations identify a robust *within-this-campaign descriptive pattern*, not independently replicated causal heritability.

## G1→G2 descriptive contrast changes (not direct cross-generation causal comparisons)

| Population | G1 selected-random | G2 selected-random | G2 censored selected/random |
|---|---:|---:|---:|
| P11 | -4.6389 | -30.3681 | 44/51 |
| P15 | +4.2361 | -17.7917 | 47/51 |

The different generation-specific worlds confound raw G1 vs G2 comparisons. These changes are hypothesis-generating only.

## Genotype observations

At G2, **P11 selected has 12 distinct parents for 24 descendants** compared with 18 among random-parent descendants. For **P15**, the counts are 13 versus 18. This is observable genetic concentration in the selected arm, not a tested explanation for mortality.

The 24 G2 genotypes per arm have different mean values for multiple recorded traits. In particular, relative to random_parent, the selected G2 genotype mean `p.water` is **-0.350172 (P11)** and **-0.489611 (P15)**. For `theta.water`, the differences are **+1.714914 (P11)** and **+4.265793 (P15)**; for `temperament.exploration`, **-0.175946 (P11)** and **-0.018416 (P15)**. These are descriptive differences in *encoded parameters*, not an established sign of physiological effect: the motor's actual sensitivity and interactions have not been manipulated or causally isolated. Do not interpret `p.water` as a directly measured water deficit.

Across G2 original lives, recorded mean drinking actions are approximately **17.53 selected vs 19.13 random_parent for P11** and **21.78 vs 23.92 for P15**. The dominant recorded death cause is `zero_water`. Behavior occurs downstream of genotype, environment, and survival duration, so comparing raw drinking counts is confounded by time-at-risk (individuals who die sooner can drink fewer times); no mediation claim follows.

## Determination and limits

1. **Established:** Actual parent-child genome lineage links (192/192) and mutations are present; selection changes the distribution/concentration of inherited genomes.
2. **Established in this campaign:** P11 is negative in every G2 ecological family and 5/6 repeat-by-family blocks; P15 is strongly negative in `pulse` in both repeats and 5/6 blocks overall.
3. **Not established:** These adverse persistence contrasts **cannot be attributed to a specific inherited mechanism, genotype parameter, or stable genotype-by-ecology causal interaction**. The single cohort, post hoc selection of negative populations, nested/reused genotypes, mutation stochasticity, and lack of a targeted independent genetic intervention prevent distinction from chance and campaign-specific response. Distinct `World` opportunities between G1 and G2 preclude direct heritability inference from the raw generation means.
4. **Scientific disposition:** `GENETIC_LINEAGE_CONFIRMED; NEGATIVE_EFFECT_CAUSE_UNIDENTIFIED; ECOLOGY_INTERACTION_CANDIDATE_NOT_PROVEN`. Do not claim that heritable disadvantage is demonstrated or that campaign variability is definitively the explanation either.

## Falsifiable next analysis (no new cohort authorized or executed)

Use the existing sealed offspring genome tables and original lives to publish a fully labeled sensitivity analysis: per-genotype mean duration over six worlds, family-by-genotype ranks, leave-one-repeat-out sign reversal, survival/hazard profiles and length-adjusted water-action rates, and ancestry diversity. For future *prospectively approved, separately pre-registered* work only, design cross-ecology replicated evaluation of identical descendant genotypes with randomized paired worlds, explicit mutation and parental controls, and a reserved holdout. Set new thresholds **before** births; never retrofit the Stage7 threshold, reuse the exhausted allocation, claim a confirmatory p-value from the 6 within-population blocks, or promote i3 based on this post hoc diagnostic.

Related: [Stage7 tracker #1414](https://github.com/josselin-orta-lab/individual-zero/issues/1414); [independent audit PR #1416](https://github.com/josselin-orta-lab/individual-zero/pull/1416). The PR remains draft; this report does not replace review of the exact audit CLI against untouched artifacts.
