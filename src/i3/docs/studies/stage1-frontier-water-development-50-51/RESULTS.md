# Stage 1 reference frontier-water: fresh 50/51 development result

**COMPLETE DEVELOPMENT DIAGNOSTIC. ENGINEERING CONTINUATION RULE MET. NOT A STAGE-1 SCIENTIFIC GATE.**

Prospective protocol: PR #1086. One-shot execution: PR #1087.

## Custody

- runtime baseline: `ed871a04e09a386f94f739f6c0701b87776c895f`
- prospective protocol merge: `cea413d5cde083096a2a6c21f23722db598c475e`
- exact execution source: `cfa51700b8efb5e33d43fb593cffc0cfb7a3d172`
- source snapshot SHA-256: `af39cfccdefe807d7cbe6dc2046a7a16b37c97931865e494cacae58f1d6df0ea`
- protocol SHA-256: `01fcd7bf03f7dc8b64b93e17ffa221740c1aca4081c1433f1c893bbee237576d`
- Actions run: `42365345012`
- one-shot job: `128382211402`
- artifact: `13571352088`
- artifact digest: `sha256:e2be82a2ffd568a7498aac1b0b45d3d43bb04cc2580afe40f9fe63bdb3985f28`
- immutable evidence commit: `7162a63caf8f3ddf396677e9c0ff1b47c5989058`
- evidence tree: `e8be4f1de8ad9a3f4bfb67a70049839ff25ccd46`
- archived files: **41**, including all 36 complete gzip lives
- archived `results.json` SHA-256:
  `2430d13e7e0bd1f1bfc4b488295d9f8e439ac1ff871e84e88862ef4ba35578b1`

All 36 preregistered lives completed. No retry, replacement, horizon extension,
selection, validation or reserve exposure occurred. Development indices 50/51
are now exposed for this mechanism.

## Frozen panel

Twelve matched three-arm blocks:

- stable / depletion / pulse;
- development indices 50 and 51;
- G0 seeds 901 and 902;
- horizon 400;
- arms: P1.3 reference, `reference_branch_memory_v1`,
  `reference_frontier_information_v1`.

The two G0 genotypes and repeated ecological blocks are **not independent
populations**. Results below are descriptive mechanism evidence only.

| Observation | P1.3 reference | storage-only | frontier-water |
| --- | ---: | ---: | ---: |
| Alive at horizon 400 | 3/12 | **6/12** | 2/12 |
| Physical deaths | 9 | 6 | **10** |
| Lived steps | 3183 | 3452 | 2704 |
| Physical inactivity | 20.70% | 18.89% | **1.11%** |
| NO_PROCESSING_BUDGET | 659 | 651 | **30** |
| Waiting actions | 410 | 465 | **1021** |
| Movement actions | 781 | 826 | **410** |
| Sleep actions | 972 | 1090 | 958 |
| Positive water uptakes | 230 | 289 | 200 |
| Positive food uptakes | 57 | 55 | 37 |
| Paid energy / lived step | 0.5591 | 0.5851 | **0.7612** |
| Paid vigilance / lived step | 0.6807 | 0.7274 | **1.0457** |
| Positive frontier-information lives | n/a | n/a | **7/12** |
| Positive frontier-information options | n/a | n/a | **121** |

The candidate engineering continuation rule was only:

`at least one candidate life has a positive frontier-information option`.

It is **met**: 7/12 candidate lives and 121 scored frontier options have positive
information value.

This is not survival non-inferiority, revision superiority, generalization or
architecture promotion.

## The mechanism genuinely becomes online

Five candidate lives never obtain a positive water experience. They have:

- 0 positive frontier-information options;
- 0 survivors;
- 567 total lived steps, mean 113.4;
- 0 water uptakes.

Seven candidate lives do obtain water and later show positive information.

In **all seven**, the first positive frontier-information score occurs exactly
**one step after the first positive water uptake**:

| Case | First water | First positive information | Lag |
| --- | ---: | ---: | ---: |
| stable-50-g902 | 24 | 25 | 1 |
| stable-51-g902 | 105 | 106 | 1 |
| depletion-50-g901 | 42 | 43 | 1 |
| depletion-50-g902 | 61 | 62 | 1 |
| depletion-51-g901 | 58 | 59 | 1 |
| pulse-51-g901 | 122 | 123 | 1 |
| pulse-51-g902 | 59 | 60 | 1 |

Therefore the implemented personal-support chain is functioning as designed:
experience is paid and stored, the water modality becomes actionable, and
frontier information can enter the next decision immediately.

The problem is **bootstrap before that first useful experience**, not failure to
activate after experience.

## Survival remains adverse

Candidate survivors are a strict subset of the control survivors on this panel.

Relative to P1.3 reference:
- survival gains: 0 blocks;
- survival losses: 1 block;
- ties: 11 blocks.

Relative to storage-only:
- survival gains: 0 blocks;
- survival losses: 4 blocks;
- ties: 8 blocks.

For lived time, candidate versus storage-only is longer in 2 blocks, shorter in
7 and tied in 3. These are paired descriptive counts, not independent-population
inference.

Candidate death causes are:
- 7 dehydration;
- 3 starvation.

The three starvation deaths all occur in lives where positive water-frontier
information exists. This is consistent with the explicit **water-only**
limitation, but does not explain the seven dehydration deaths.

## Funding paralysis is not the dominant failure

The candidate has only 30 NO_PROCESSING_BUDGET steps and 1.11% physical
inactivity, far below both controls.

Yet it waits 1021 times and moves only 410 times. Storage-only waits 465 times
and moves 826 times.

So this is not a return of the earlier local prototype's computational
paralysis. The individual usually completes a funded decision and actively
chooses waiting/resting behavior.

This reproduces, on the P1.3-preserving substrate, the older qualitative
failure mode already seen when additive curiosity was removed: insufficient
search before a useful source has been personally established.

## Cost

Candidate cognition is more expensive on the realized trajectories:

- energy per lived step: 0.7612 versus 0.5851 storage-only;
- vigilance per lived step: 1.0457 versus 0.7274 storage-only.

These are not cost-matched causal mediation estimates because trajectories
diverge.

The candidate is nevertheless usually fundable, so increased cost alone does
not explain its main failure on this panel.

## Revision endpoint

- reference: 1 REACQUIRED, 5 EXPOSED_NO_REACQUISITION, 6 NO_EXPOSURE;
- storage-only: 2 REACQUIRED, 5 EXPOSED_NO_REACQUISITION, 5 NO_EXPOSURE;
- candidate: 1 REACQUIRED, 4 EXPOSED_NO_REACQUISITION, 7 NO_EXPOSURE.

No revision superiority is demonstrated or evaluated as a gate.

## Decision

**The water-frontier value-of-information mechanism is real but incomplete.**

It can become positive in ordinary paid lives immediately after personal water
experience. That is a meaningful mechanistic advance over the earlier local
prototype, where all information increments were zero.

But the current conservative newborn semantics create a circular bootstrap:
before the individual has personally learned that water can improve its body,
water discovery has no actionable information value. Removing the old additive
curiosity at the same time therefore leaves some lives without a mechanism that
values acquiring the first such experience.

Do not tune 50/51, restore curiosity as a hidden bonus, invent water behind an
unseen cell, or move to Stage 2 to mask this result.

The next Stage-1 work should remain software/design only until the bootstrap
semantics are addressed generically. Unknown-food information also remains
incomplete and explains some, not all, adverse deaths.

P1.3 remains the reference. I3 remains unregistered. No scientific Stage-1 GO.
