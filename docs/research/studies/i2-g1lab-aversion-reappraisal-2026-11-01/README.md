# I2 G1-LAB: aversion, hidden recovery and evidence identifiability

**Date:** 1 November 2026. **Status:** owner-approved scientific interpretation, NOT a new experiment or independent scientific verdict. **Source:** [ADR-0006](../../../decisions/ADR-0006-evidence-grounded-aversion-reappraisal.md).

## Frozen experiment and exact provenance

The non-living G1-LAB model in [merged PR #801](https://github.com/josselin-orta-lab/individual-zero/pull/801) (`cb540875dc6949111b951362d948f57b7b5e19aa`) used three independently initialized arms and one deterministic world per regime, 24 model energy, 60 synthetic UC, eight captures, researcher priors C=3/E=4/D=1 and a historically post-hoc chosen-score offset +5. The third arm reused the **hand-coded** G2 revisit rule of two other chosen outcomes and bonus +9. [Protocol frozen before implementation](https://github.com/josselin-orta-lab/individual-zero/issues/662#issuecomment-6559888186); [original observed results](https://github.com/josselin-orta-lab/individual-zero/issues/662#issuecomment-6559926796). PR #800 (`175a78f877b2a0085d20c980f03968b2dbd58fec`) established fixed-prior and observational baselines.

Reproduction on exact PR #801 source: `PYTHONPATH=src python -m unittest discover -s tests/i2 -p test_g1_lab_frozen_revisit_recovery.py -v`. CI Python 3.11/3.12 PASS checks verify software, not biological or M11 authenticity.

| Regime | Chosen-only observational | Stale revisit comparator | Interpretation |
| --- | --- | --- | --- |
| Stable | CECECECE, energy 40, UC 36 | identical, and fixed baseline identical | NULL learned advantage |
| Permanently adverse | CECCCCCC, death capture 8, UC 38 | CECCE, death capture 5, UC 23 | Revisit added a damaging eating episode |
| Neutral | CEC_____, energy 13, UC 33 | identical | NULL revisit effect |
| Harmful reversal | CECECCCC, energy 8, alive at capture 8, UC 37 | CECECCEC, death capture 8, UC 37 | Revisit worsened modeled survival |
| Hidden recovery | CECCCCCC, death capture 8, UC 38 | CECCEECE, energy 24, alive at capture 8, UC 37 | Hand-coded revisit produced beneficial eating at captures 5, 6, 8 |

C=collect, E=eat, _=abstain. All energy and death values concern **toy simulated physiology**, not living bodies. Unequal terminal truncation prevents simple common-horizon causal comparisons.

## Corrected interpretation

The observational agent's **complete personal history is the same** in permanently adverse and hidden-recovery conditions, including actions, energy `[22,12,10,8,6,4,2,0]`, UC 38, resources/affordances and model death. From capture 5 onward, the hidden EAT payoff differs but EAT is never chosen. No newly encountered personal outcome, perceptual cue or social signal distinguishes these environments.

Thus the change in world law is **unidentifiable from this individual's available observations**. A no-retry policy is not evidence of *failed learning* about an invisible reversal. It can still be maladaptive in the hidden recovery world, and the modeled terminal is a negative outcome. This does **not** establish that avoidance is optimal, that an animal would never explore, or that memory is perfectly calibrated.

The +9 experimental bonus succeeds in recovery **only at a cost**: it is a researcher-specified exploration mechanism and worsens harm under adversity and harmful reversal. It is not emergent natural motivation.

## Biological boundary and references

The narrower scientific claim is that individual avoidance may persist in the absence of discriminating evidence, while social information is one possible reason for reappraisal, not a universal prerequisite. Hunger, context change, firsthand safe re-exposure and individual extinction are other possible mechanisms requiring separately falsifiable treatment.

- Galef, B. G., Jr. & Wigmore, S. W. (1983), *Transfer of information concerning distant foods: A laboratory investigation of the information-centre hypothesis*, Animal Behaviour 31, 748–758. https://doi.org/10.1016/S0003-3472(83)80232-2
- Galef, B. G., Jr. (1986), *Social interaction modifies learned aversions, sodium appetite, and both palatability and handling-time induced dietary preference in rats*, Journal of Comparative Psychology 100, 432–439. https://pubmed.ncbi.nlm.nih.gov/3802787/
- Conditioned taste aversion review (2018), https://pmc.ncbi.nlm.nih.gov/articles/PMC6051479/

These studies do NOT prove a universal rule that low-abstraction organisms need a social example before any reattempt.

## Research implication and gates

In future controlled designs, distinguish remembered harm, new observable evidence, physiological need/risk competition, and chosen subsequent confirmation. Compare with cue-absent controls, fallible or misleading social cues, and independently initialized no-learning comparators; predeclare provenance, UC and adverse outcomes. A cue should not be treated as unearned knowledge of a hidden payoff.

**No new experiment is authorized** by this retrospective analysis. G1-LIVE review (#662), G0 custody (#661), independent M11, no birth and G3 NOT_ESTABLISHED remain unchanged. No independent scientific peer review has occurred.
