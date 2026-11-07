# Stage 1 Candidate-F cost versus policy: complete 54/55 development result

**COMPLETE DEVELOPMENT DIAGNOSTIC. PRIMARY STRICT COUNTEREXAMPLE NOT OBSERVED. NOT A STAGE-1 GATE.**

Prospective protocol: PR #1144. One-shot execution: PR #1145.

## Exact custody

- protocol baseline: `954ea5f312024fb902dd43a6845341adc3f88f0f`;
- protocol merge: `eb79c7b50b8cfb1ef275441a2faaa87d1e69c904`;
- exact execution source: `a27e4c3ccebfcfec610b79f02f00fd2440d1b7dc`;
- source snapshot SHA-256:
  `07eba8421c7954310659f8eae59a8ce7868958ce21f2b5211ba7c7b73501ab85`;
- protocol SHA-256:
  `e1c8bd89e9e6cfa921fb0332bf9376e44181f649d19c896e7f736e888c1845c4`;
- Actions run: `42426687157`;
- one-shot job: `128566755373`;
- Actions artifact: `13595961603`;
- artifact digest:
  `sha256:38c5436cfb9158565d6507a0a19163552a77d92c4e5f037842431d275b07d3e0`;
- immutable evidence commit:
  `18bfda8bc680afc9df01d1d2ebb308b79efcbc70`;
- evidence tree:
  `74fc1756d29c71c806016f188fe8d4bb705c3b91`;
- archived files: **41**, including all 36 complete gzip lives.

All 36 preregistered lives completed. No retry, replacement seed, horizon
extension, selection, validation or reserve exposure occurred.

Development indices 54/55 are now exposed and closed for this mechanism.

## Frozen panel

Twelve matched three-arm opportunity blocks:

- F0 stable / depletion / pulse;
- development indices 54 and 55;
- G0 v4 seeds 901 and 902;
- horizon 400;
- arms: P1.3 reference, rejected Candidate-F+omega, and upper-cost P1.3-choice
  control.

The blocks and G0 seeds are not independent evolutionary populations. This is a
development causal falsifier, not confirmatory inference.

## Primary frozen falsifier

The preregistered continuation rule required at least one:

`UPPER_SURVIVES_CANDIDATE_DIES`.

Observed classification:

- UPPER_SURVIVES_CANDIDATE_DIES: **0**;
- CANDIDATE_SURVIVES_UPPER_DIES: 0;
- BOTH_SURVIVE: 0;
- BOTH_DIE: **12**.

Therefore the engineering continuation rule is **NOT MET**.

The result is exactly the preregistered interpretation:

`NO_STRICT_COUNTEREXAMPLE_IN_SMALL_OVERCHARGED_PANEL`.

Because the upper-cost arm deliberately pays Candidate-F shadow cognition **plus**
an additional P1.3 choice, this null result does **not** establish that
Candidate-F cognitive cost alone is sufficient for death. It also does not
establish that policy is irrelevant.

## Aggregate outcomes

| Observation | P1.3 reference | Candidate-F+omega | upper-cost P1.3 choice |
| --- | ---: | ---: | ---: |
| Alive at horizon | **4/12** | 0/12 | 0/12 |
| Total lived steps | **3450** | 1491 | 2395 |
| Water deaths | 5 | **11** | 8 |
| Food deaths | 3 | 1 | **4** |
| Positive water uptakes | **232** | 4 | 25 |
| Positive food uptakes | **54** | 1 | 8 |
| Moves | **831** | 79 | 216 |
| Sleeps | 1150 | 946 | **1212** |
| Physical inactivity | 14.81% | 26.96% | **36.24%** |
| Paid energy / lived step | 0.60876 | **2.06095** | 1.66955 |
| Paid vigilance / lived step | 0.75158 | **2.90923** | 2.11048 |

The per-lived-step costs are descriptive. Candidate and upper-cost trajectories
diverge, so their realized computation is not matched.

The upper-cost control has **868 NO_PROCESSING_BUDGET** steps. That is expected
to be possible after #1143: Candidate-F shadow cognition may already have been
paid before P1.3 lacks budget for its own processing block. All such decisions
retain the total physical bill in Stage-0 energy custody.

## Directional paired evidence

Although no upper-cost life reaches horizon, its lived time is longer than
Candidate-F in **7/12** matched blocks, shorter in 1/12 and tied in 4/12.

The four blocks where ordinary P1.3 survives are especially informative:

| Block | Reference steps | Candidate steps | Upper-cost steps | Ref water | Candidate water | Upper water |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable-55-g902 | 400 | 113 | 197 | 12 | 0 | 4 |
| depletion-54-g901 | 400 | 147 | 383 | 37 | 0 | 4 |
| depletion-55-g901 | 400 | 135 | 265 | 103 | 0 | 3 |
| pulse-54-g902 | 400 | 114 | 166 | 12 | 0 | 4 |

Thus, on every reference-survivor opportunity:

- Candidate-F dies with **zero positive water uptake**;
- upper-cost P1.3-choice obtains water;
- upper-cost P1.3-choice lives longer than Candidate-F;
- upper-cost still dies before horizon.

This is strong descriptive evidence that motor policy changes matter on these
opportunities. It is not a strict survival counterexample because the
upper-cost intervention is deliberately more expensive than Candidate-F.

Across all upper-cost lives, the Candidate-F shadow preferred a different
action from the actual P1.3 action on **510 / 2395 decisions**. The shadow also
registered 426 positive-information options across 1514 scored frontier options.
The motor-policy distinction is therefore operational, not merely nominal.

## Revision

Revision receipts:

- reference: 3 REACQUIRED, 2 EXPOSED_NO_REACQUISITION, 7 NO_EXPOSURE;
- Candidate-F: 0 REACQUIRED, 1 EXPOSED_NO_REACQUISITION, 11 NO_EXPOSURE;
- upper-cost: 0 REACQUIRED, 3 EXPOSED_NO_REACQUISITION, 9 NO_EXPOSURE.

No revision advantage is demonstrated for either experimental arm.

## Interpretation

The diagnostic supports a **both-mechanisms-are-plausible** reading:

1. Candidate-F's policy is behaviorally harmful relative to P1.3 on several
   matched opportunities. The upper-cost control restores some movement,
   resource acquisition and lived time despite paying even more computation.
2. Candidate-F-style cognition is physically severe. Paying the shadow plus
   P1.3's additional choice produces no survivors and 868 P1.3 processing
   shortfalls.

The experiment was intentionally unable to quantify mediation because its
control overcharges. The primary strict cost-sufficiency falsifier is therefore
null, while the secondary paired behavior strongly implicates policy.

**DRIFT DETECTED:** do not respond by tuning Candidate-F/omega, rerunning 54/55,
or reopening the failed ADR-0015 gate. Candidate-F remains rejected. A tighter
causal control, if pursued, must explicitly state how it avoids giving P1.3 free
cognition while matching physical cost more closely. Otherwise causal
decomposition should stop here and Stage 1 should return to architecture design.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked.
