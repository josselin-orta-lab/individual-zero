# Stage 1 cost-reduced local information: development results

**COMPLETE DEVELOPMENT DIAGNOSTIC. ENGINEERING CONTINUATION RULE MET. STAGE 1 STILL NOT READY.**

Protocol: [prospective frozen design](PROTOCOL.md), issue #1061, PR #1075.
Executed once on 7 November 2026 UTC. No retry, replacement, horizon extension
or tuning on the earlier 44/45 panel or on the new 46/47 panel.

## Exact source and custody

- Pre-exposure runtime baseline: `3b09edfcc369059ea8e706d89ed8415ecfc31ff5`.
- Exact execution source: `cba7f01be7fdd7552d72ba3824a2f07251e38c28`.
- Source-files SHA-256: `816491f22e112016e70255ad4e0009e69653a8c15aba8dbcc9d992b048eca1c1`.
- Protocol SHA-256: `d9d8145db42c28108bcf5e3593a4957b7ec86152d89d991be89c4767fdca1025`.
- Actions run: `42359611338`; one-shot job: `128365089175`.
- Actions artifact: `13568698920`; ZIP SHA-256:
  `74fc93075a22254cf94490126b3e8853faa7a11745661af6da9e61f9c2786de3`.
- Original archive commit:
  `5f244f33e540e1832a6442cd21f5028fae6bc8bb`, tree
  `60a4a1bdfde378f5072fc93d6cd26e497590e2b2`, exactly 29 files.
- Archived `results.json` SHA-256:
  `823f000eeec3e6712b3edce1fb955cd779b9070873f37e78ed4d891919ca1f64`.

The committed `original/` directory contains registration, source snapshot,
complete case reductions, checksums and all 24 full `life-00.json.gz` through
`life-23.json.gz` originals. Every life was archived before reduction.
No engineering crash occurred.

## Frozen panel

Twelve matched pairs: stable/depletion/pulse, development indices 46 and 47,
G0 seeds 901/902, horizon 400. These development conditions are now exposed.
No selection, validation or reserve world was opened.

| Observation | P1.3 reference | local_information_v1 |
| --- | ---: | ---: |
| Lives alive at horizon 400 | 4/12 | **0/12** |
| Physical deaths | 8 | **12** |
| Death causes | 3 water, 5 food | **10 water, 2 food** |
| Total lived steps | 3877 | 1792 |
| Physical inactivity | 1138 (29.35%) | **403 (22.49%)** |
| Funded decisions | 2739 | **1389** |
| NO_FUNDED_SCORE | 0 | **19** |
| NO_PROCESSING_BUDGET | 1137 | **384** |
| Terminal processing-lock lives | 9 | **3** |
| Sleeping | 1012 | **1241** |
| Movement commands | 746 | **66** |
| Positive water uptake | 245 | **12** |
| Positive food uptake | 47 | **4** |
| Paid cognition energy / lived step | 0.476000 | **2.059937** |
| Paid cognition vigilance / lived step | 0.584084 | **3.166388** |
| Positive information increments >1e-12 | n/a | **0 / 8666 scored options** |
| Fully empirically supported information options | n/a | **8224 / 8666** |

All early deaths remain in the aggregates. Different trajectories mean the
per-step cost contrast is descriptive, not a cost-matched causal estimate.

## Prespecified engineering rule

The frozen rule was:

`candidate inactive_fraction <= 0.50 AND positive_water_uptakes > 0`.

It is **met**: 22.49% aggregate physical inactivity and 12 positive water
uptakes. This says only that the first panel's aggregate computational paralysis
is no longer the dominant bottleneck. It is not survival non-inferiority,
generalization, a Stage-1 pass or architecture promotion.

The earlier 44/45 diagnostic had 83.61% candidate inactivity, no positive
resource uptake, 43 NO_FUNDED_SCORE steps and 1146 NO_PROCESSING_BUDGET steps.
The new panel is on different development worlds, so the numerical change is
not a paired causal estimate of #1071-#1074. It nevertheless answers the new
prospectively frozen engineering question.

## Failure mode has shifted

The candidate still has **0/12 survivors**.

Stable and pulse are especially informative: all eight candidate lives remain
fully funded until death, yet none acquires water. Across those eight lives
there are 804 funded scoring decisions, only 48 movement commands, 707 sleeps,
and no scored `boire` option at all. The individual is therefore often able to
think, but does not reach a locally represented water action before dehydration.

Depletion differs. Candidate lives obtain all 12 positive water uptakes in this
family. Three of four later enter terminal processing lock; two reach the
predefined revision exposure but neither reacquires elsewhere. Thus residual
funding collapse remains real in depletion, but it no longer explains the whole
panel.

Candidate sleep dominates the complete panel: 1241/1792 lived steps (69.25%).
This is not passive inactivity. It is an executed action selected by the paid
policy.

## Information-value observation

None of the 8666 paid local information scores has a positive
`information_value` above 1e-12. This is not merely newborn ignorance:
8224/8666 (94.90%) have zero unsupported-history queries.

A separate read-only audit of the archived originals is recorded in
[POSTHOC_INFORMATION_ZERO_AUDIT.md](POSTHOC_INFORMATION_ZERO_AUDIT.md). It
shows that the zero increments coexist with substantial supported and distinct
payoff computation, and that the local policy strongly prefers sleep while
stable/pulse never expose a local drink option.

## Revision endpoint

Candidate revision receipts: 10 NO_EXPOSURE, 2 EXPOSED_NO_REACQUISITION,
0 REACQUIRED. Reference: 4 NO_EXPOSURE, 5 EXPOSED_NO_REACQUISITION,
3 REACQUIRED.

No successful-revision-only summary can rescue the candidate, and the two
candidate exposures do not establish internal belief revision.

## Decision

**local_information_v1 remains NOT READY for the Stage-1 gate. P1.3 remains the
reference.**

The useful conclusion is narrower than rejection of value of information:
#1071-#1074 removed the observed duplicate-work bottleneck far enough for the
candidate to keep choosing in most new lives, revealing a different limitation.
The local prototype does not assign informational value to unseen spatial
consequences and changes repertoire, memory partition and ignorance assumptions
relative to P1.3. It is therefore a software/mechanism falsifier, not the
one-mechanism Stage-1 comparison.

**DRIFT DETECTED:** do not spend the next intervention shaving unique rollouts
or adding more observer machinery. Do not tune the stationary prior or force
drinking. The next Stage-1 implementation should preserve the reference
repertoire/spatial state and isolate the information-value substitution much
more closely. Stage 2 remains separate: its question is how much unique
computation to buy, not how to repair a local repertoire that is fully funded
yet fails to seek water.

No activation, selection, validation, reserve exposure or general scientific GO.
Stage 0, #1026 and #1054 remain open.
