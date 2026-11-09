# Stage 2.1 replay gate: supplied DEVELOPMENT pilot 68/69 results

**PRESERVED DESCRIPTIVE DEVELOPMENT EVIDENCE. NOT A STAGE-2.1 GATE RESULT.**

The uploaded package reports a sealed rehearsal PASS followed by 36/36
generated and reduced lives with zero invariant failures. These values are
preserved because they describe what the supplied implementation did, even
though the run is not canonical evidence for Stage 2.1.

## Reported per arm

| | FIXED (P1.3) | GATE | ZERO-PERCEIVED-COST |
| --- | ---: | ---: | ---: |
| Reached 400 steps | 5 | 5 | 6 |
| Mean steps lived | 261.3 | 250.1 | 261.2 |
| Replays per sleep step | 15.95 | **3.77** | 9.39 |
| Paid energy per lived step | 0.657 | **0.538** | 0.614 |
| Paid vigilance per lived step | 0.798 | **0.707** | 0.786 |
| Sleep fraction | 36.0% | 34.4% | 35.8% |
| Inactive fraction | 6.3% | 5.3% | 4.9% |
| Lives with a drink | 7 | 7 | 7 |

Reported paired observations against FIXED:

- GATE cheaper in energy in 10/12 blocks and vigilance in 10/12;
- GATE lifespan identical in 11/12, shorter in one;
- ZERO-PERCEIVED-COST energy cheaper in 11/12, vigilance in 7/12;
- one ZERO-PERCEIVED-COST life longer and one shorter.

The divergent block `pulse-68-g909` is notable: FIXED lived 362 steps and ate
five meals; both gate arms lived about 225-228 steps, ate none and died of
hunger. Four other blocks reportedly die of thirst at step 95 in every arm.

The package reports 220/2842 audited decisions (7.7%) where learned residuals
changed the decision, and a development RANDOM-EQUAL-MEAN value of
3.7725072604065826 replays per sleep step.

## Why these results are not promoted

1. The package's asserted ADR-0017 owner lift is not established in the
   repository history available to this integration.
2. The run used a non-conforming `r_hat` denominator relative to frozen #1212.
3. The software verdict that preceded the lived run is therefore also
   non-canonical.

These observations may motivate later design, but they must not set a
validation control or margin for a corrected Stage-2.1 experiment. A corrected
software falsifier comes first.
