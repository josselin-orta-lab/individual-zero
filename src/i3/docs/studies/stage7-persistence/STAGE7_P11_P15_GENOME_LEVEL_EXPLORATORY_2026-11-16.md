# Stage7 P11/P15: Genome-level, ancestry-aware exploratory analysis (2026-11-16)

> **Post-exposure, read-only diagnostic; not a new scientific experiment or pre-registration.** Stage7 source `06cfcf9cc9414e0f139b39a42d05177ddb813782`, [one-shot run #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125), [issue #1414](https://github.com/josselin-orta-lab/individual-zero/issues/1414). None of the 13/16 threshold, experimental seeds, generations, outcomes, or originals was modified. The frozen final verdict remains `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`: 12 positive/4 negative/0 zero population contrasts and overall mean +11.9036458333 lived steps, whereas 13/16 *strictly positive* and positive mean were both required.

## Audited inputs

Three **untouched** scientific GitHub Actions ZIP artifacts (hashes rechecked locally):

| Artifact | GitHub artifact ID | ZIP SHA256 |
|---|---:|---|
| Pre-exposure plan | 14213827437 | `8af2e4f4f9207997c6197c33e902f28672663d1e74de2a64e04fe568d4610ea3` |
| Scientific original lives | 14218795289 | `7391497d8664032c690b5d75cec3f98cabc8c589ea77fc946151d922d3a481b6` |
| `SCIENCE_RESULT.json` | 14217357887 | `a6e2b61208cbf65771ab8f8e101a3b7673552c4cdf656281dad38165f75e301c` |

A standalone offline Python analysis, **without importing the i3 engine or any living-world simulator**, read and independently rehashed **1,152 original compressed and uncompressed life records** for P11 and P15 across G1 and G2. It checked source and allocation pins, generation manifest seals, native identities/genotype hashes, complete six-world exposure for each slot, trace length, termination semantics (including death at the 400-step horizon), and settled funding. All 1,152 outcomes also match the prior independent derived extraction exactly for steps, terminal state, genome SHA256, drinking and feeding.

Design for this **subset**: 2 populations × 2 generations × 2 arms × 24 distinct offspring genome slots × 3 ecological families × 2 repeats = **1,152 native original lives**; 192 distinct genotype slots (96 at G2); 31 numeric genome parameters. A genotype (not each of its six life observations) is the unit for within-arm genotype association, and descendants sharing a parent are not genetically independent.

## G2 outcomes and parent-lineage concentration

| Population | Selected mean steps | Random-parent mean steps | Δ G2 mean steps | Distinct G1 parents of 24 G2 selected / random |
|---|---:|---:|---:|---:|
| P11 | 248.9792 | 279.3472 | **−30.3681** | 12 / 18 |
| P15 | 240.9097 | 258.7014 | **−17.7917** | 13 / 18 |

All 192 G1/G2 offspring parent-slot and parent-genome-hash links across the two populations and two arms match archived founders or previous-generation offspring. These links establish **transmitted genome ancestry**, not a causal hereditary survival effect.

## All 31 genomic predictors screened separately within 24 G2 genotypes per population/arm

Response: each genotype's average `steps_lived` across its six archived ecological opportunities. Correlations are Spearman ranks. Top gene is selected after exposure, and may be spurious. An exploratory permutation **max-statistic** reference used 5,000 phenotype-block permutations (analysis-only PRNG seed 1416; **not** Stage7 seeds), max absolute correlation across 31 genes in each of four groups (**124 correlations total**). Shared parental ancestry and post hoc choice of P11/P15 limit exchangeability; the reference probability is **not** a preregistered or valid confirmatory p-value.

| G2 group | Strongest observed gene | Spearman rho | Same gene in G1 rho | Exploratory max-over-124 reference | Parent-blocked nested CV skill |
|---|---|---:|---:|---:|---:|
| P11 selected | `p.food` | +0.421 | +0.388 | 0.978 | **−0.419** |
| P11 random_parent | `p.energy` | +0.625 | +0.127 | 0.155 | **−0.119** |
| P15 selected | `w.food` | **−0.672** | −0.175 | **0.054** | **+0.114** |
| P15 random_parent | `gamma3` | −0.617 | +0.176 | 0.179 | +0.041 |

**Parent-blocked nested CV:** choose the best of 31 genes using only the training descendant families; hold out **all offspring of one G1 parent** together, repeat over distinct parents; skill = 1 − squared prediction error / squared error of a training-only mean baseline. A negative score means worse prediction than the baseline. Even positive scores are internal, retrospective and lineage-dependent, not external tests. For P15 selected, the search selected `w.food` in 12/13 parental held-out folds. The apparently stronger post hoc `w.food`-only parent-blocked CV skill +0.351 was **not preselected** and should not be claimed as an unbiased validation.

Across G2 genotypes, the **G1 parent's six-world performance vs its G2 child's six-world performance** Spearman rho is just +0.030 for P11 selected and +0.027 for P15 selected (24 pairs each with repeated parent identities; nonindependent). This does not identify positive or negative inherited fitness.

## Is the candidate portable across ecological contexts?

For P15 selected, `w.food` vs genotype mean steps has rho **−0.530** in `stable`, **−0.486** in `depletion`, but just **−0.119** in `pulse`. The same G2 genomes' **rank order of persistence** is weakly shared between ecological families: stable/depletion +0.230, stable/pulse +0.094, depletion/pulse −0.033. Thus **the gene with the strongest overall association does not explain the observed pulse-specific deficit**. P15's two pulse repeats remain adverse as previously reported, but that observation is not tied causally to `w.food`.

P11 selected has much weaker maximum gene association (`p.food` rho +0.421); its parent-blocked predictor is worse than the null. Family rank concordance stable/depletion +0.183, stable/pulse +0.273, depletion/pulse +0.561. One native P11-selected stable repeat has a constant outcome over the 24 genotypes, making within-repeat rank rho undefined, not zero.

## What precisely is genetically transmitted?

Because every G2 genome and its recorded G1 parent genome are present, each **arm-level mean gene contrast** can be decomposed algebraically:

`selected-minus-random offspring gene mean = selected-minus-random chosen-parent gene mean + selected-minus-random average mutation change.`

| Population / gene | G2 descendant mean difference | Parent input contribution | Mutation increment contribution |
|---|---:|---:|---:|
| P11 `p.water` | −0.350172 | −0.278489 | −0.071683 |
| P15 `p.water` | −0.489611 | −0.449002 | −0.040610 |
| P15 `w.food` | +0.204290 | +0.112581 | +0.091709 |

These are **exact decompositions of observed encoded gene values**, not causal attributions of deaths. Although lower mean `p.water` in selected descendants is predominantly associated with the selected-parent input for both populations, its **within-selected-G2 genotype rank correlation with lived steps is weak**: P11 −0.102, P15 −0.248. Likewise, interpretation of `w.food` as a physiological mechanism requires a controlled intervention on genotype weights and independent evaluation. Recorded drinking actions are downstream of lived time: P11 selected vs random roughly 7.04 vs 6.85 drinks/100 *observed* steps; P15 9.04 vs 9.25. These ratios do not identify mediation or causal direction.

## Scientific disposition

- **Established:** all archived P11/P15 descendants have traceable inherited genome parameters and distinct G1 parents; 1,152 native lives have valid hashes and provenance; original population contrasts remain negative.
- **Exploratory candidate:** `w.food` in P15 selected predicts genotype-average persistence moderately within this campaign (rho −0.672; ancestry-blocked nested CV skill +0.114). A modest internal signal is not an independently validated mechanism; G1 association and `pulse`-specific association do not replicate its apparent strength.
- **No robust identified mechanism in P11:** 31-gene scan yields no convincing portable or parent-blocked predictive signal.
- **No identified transmitted *fitness* effect:** parent→offspring outcome rank correlations are near zero in the selected arms, and G1/G2 have different worlds. Source ancestry, gene shifts and post hoc phenotype correlations cannot distinguish stable inherited causal effects from campaign variability, shared-environment response, or selection-related chance.
- **Research decision:** `GENOME_INHERITANCE_VERIFIED; P15_W_FOOD_EXPLORATORY_CANDIDATE; P11_GENETIC_PREDICTOR_NOT_SUPPORTED; HERITABLE_SURVIVAL_MECHANISM_NOT_ESTABLISHED`.
- **No change:** frozen Stage7 negative outcome, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, I1 active, i3 not scientifically promoted; no new born lives, no reruns.

## Reproducibility

The accompanying offline Python script (`per_genome_ancestry_diagnostic.py`, SHA256 `1d8dd24c9e6ea3931fe3dffde240466df70ae3866728ebcaa7b59228ff607e12`) accepts **only** the three exact saved GitHub ZIPs and emits: per-life P11/P15 1,152-row CSV, 192-row genotype CSV, 124-row association scan, deterministic JSON summary. Requires Python, NumPy, pandas and SciPy. Example command after placing the exact three artifacts in a local directory:

```bash
python per_genome_ancestry_diagnostic.py --root /path/to/three/github-artifact-zips --out /path/to/read-only-output --permutations 5000
```

Original scientific ZIPs and original G0/G1/G2 lives are never changed. No `run_life`, World creation, mutation execution, or seed change occurs. Full original scientific retention currently has a finite expiration (GitHub metadata: 2027-02-14); retain provenance-aware copies for future reproduction. The script and CSV/JSON outputs are also delivered with the analysis conversation; review their SHA and archived source roots before reuse.

**Next falsifiable work without new cohorts:** predefine a *purely descriptive* ancestry-cluster sensitivity check with genotype-family rank changes and per-gene response plots, and document omitted variables. A fresh causal test of `w.food` or `p.water` would need separately authorized, prospectively registered genotype interventions with independently held-out World opportunities; do not reinterpret this one-shot run.

## Additional observed within-world survival thresholds (all original lives)

A key safeguard against overinterpreting single-gene effects is that some source-frozen World exposures **collapse many different genotypes to identical death steps**:

- **P11 / G2 / stable / repeat 0:** all **24 selected genotypes die at step 102**, all with recorded `zero_water`, **zero drinks**. The random-parent arm has **22 at step 102 and 2 censored at step 400**. Its apparent G2 deficit of **−24.8333 steps in this block** comes entirely from those two surviving random-parent genotypes relative to a common 102-step floor.
- **P15 / G2 / pulse / repeat 0:** all **24 selected genotypes die at step 95**, all with `zero_water`, **zero drinks**. The random-parent arm has **22 at step 95, 1 dead at 273, and 1 censored at 400**. The **−20.1250-step difference** in this block is entirely due to those two late random-parent trajectories.
- **P15 / G2 / pulse / repeat 1:** selected has **19/24 at step 124 and 0 censored at 400**; random-parent has **14/24 at step 124 and 5 censored at 400**. The arm difference here is **−50.5000 steps**, with a different discrete distribution.

These are **descriptive original outcomes**, not evidence of an engine fault or proof of a gene mechanism. Their discreteness shows that genotype-outcome associations are partly driven by rare survivors under context-specific bottlenecks and strongly cautions against extrapolating a smooth genetic fitness response. In the two zero-variance blocks no within-block genotype rank correlation can be estimated, regardless of genetic differences. They also do not replace the fixed six-world population estimator.
