# I3 P4a: independent held-out G2 lineage validation, original result

**Status: TECHNICAL VALIDATION COMPLETE; NO GENERALIZABLE ADVANTAGE
DEMONSTRATED, NO SCIENTIFIC GO.** P4b learning and individuality controls
are **NOT_RUN**.

P4a was [preregistered](../../P4A_HELDOUT_PREREG.md) in merged PR #1020
**before** the first held-out world was opened. Exact implementation:
`01132efef08edb23143c4618d1a2491b23026eb4`. Fixed schedule digest:
`7d5785eca2f65b1562c2dca22bc4bd65f930250e8a0b032df18a030b22b38289`.
All 48 G2 genotypes were taken without mutation or reselection from the
previously frozen P3 artifact (canonical digest
`4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b`).

An initial [run 42185413666](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42185413666)
failed **in software preflight before any validation life** because a negative
authorization test inherited the workflow's approved-run variables. The
subsequent [run 42185484483](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42185484483)
changed **only the CI test invocation** to isolate those variables,
not the frozen scientific executable, schedule, genomes, sample size or
outcome tests. This is the first and only executed P4a experimental cohort.
Its original artifact is `i3-p4a-original-heldout-first-run`; a separate
post-run [archive workflow](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42185915350)
preserved the full data. Its first packaging attempt failed on relative
checksum paths and is retained in run #42185856935; it did **not** rerun lives.

## Unfiltered technical custody

| Registered endpoint | Observed |
| --- | ---: |
| Independent populations | 4 |
| Fixed G2 genotypes | 48 / 48 |
| Distinct never-before-used validation worlds | 24 / 24 |
| Complete P4a life receipts | **288 / 288** |
| Deaths | **199 / 288** |
| Censored alive at 400 steps | **89 / 288** |
| Distinct evidence heads | 288 |
| World hashes | 24 |
| Different engine source hashes within experiment | 0 |
| P3 selection worlds reopened | 0 |
| P4 reserve worlds opened | 0 |
| P4b interventions executed | 0 |

Original uncompressed full evidence:
[`validation-full.json.gz`](validation-full.json.gz) (gzip archival copy).
Plain [summary](validation-summary.json); [checksum receipts](ORIGINAL_SHA256SUMS.txt).
Uncompressed original JSON SHA-256:
`44adb1192d1aea87cf5d96a547f794de6f7fe33a566a5de90747a34429e8e8d6`.
Canonical internal evidence digest:
`3fe21087283eeafb8e9b0fc2522b238ea700611029a7f02b1edf3b89b2a3b3c5`.
No adverse life was discarded, truncated, or changed into a censoring outcome.
Physical mortality reasons: 183 `zero_water` and 16 `zero_food`,
with no fabricated failure attributed to funding or world transitions.

## Primary endpoint: surviving to 400 physical steps

Both arms contain 144 **new held-out** lives, six frozen G2 genotypes in each
population/arm, on the same six fresh worlds per population. Each of the four
populations is one independent experimental unit; 288 lives are repeated
measurements, **not** 288 independent populations.

| Independent population | Selected / 36 | Random-parent / 36 | Difference in survivors |
| --- | ---: | ---: | ---: |
| 0 | 6 | 8 | **-2** |
| 1 | 13 | 4 | **+9** |
| 2 | 13 | 14 | **-1** |
| 3 | 15 | 16 | **-1** |
| **Total, not an independent-unit test** | **47 / 144** | **42 / 144** | **+5 / 144** |

Selected-parent survival: **32.64%**; random-parent: **29.17%**.
Aggregate descriptive difference **+3.47 percentage points**. But the four
paired population differences are **[-2, +9, -1, -1]**. The mean difference
is **+1.25 lives per 36-life population**, sample SD **5.188 lives**.
Using the *preregistered* exploratory two-sided t interval, df=3,
t-critical 3.182, the 95% interval is **[-7.01, +9.51] survivors per
population**, equivalent to approximately **[-19.46, +26.40] percentage
points**. This spans large potential harm and benefit. With only n=4
populations and a strongly asymmetric single positive response, the t
approximation is fragile; **do not interpret it as confirmation**.

Three of four independent populations favor **random** parenting. The
entire overall positive difference comes from population 1. P4a therefore
does **not** establish that persistence-selected G2 lineages generalize.

## Secondary descriptive endpoints, not alternative success gates

| Ecological family | Selected censored / 48 | Random-parent censored / 48 |
| --- | ---: | ---: |
| Stable | 15 | 16 |
| Depletion | 24 | 16 |
| Pulse | 8 | 10 |

The overall +5 is concentrated in depletion (+8). This is a post hoc
description of a predeclared secondary grouping and **cannot** retroactively
select a favorable family or revise a success definition.

| Whole 144-life arm totals | Selected-parent | Random-parent |
| --- | ---: | ---: |
| Censored survivors | 47 | 42 |
| Deaths | 97 | 102 |
| Lived physical steps | 37,251 | 35,499 |
| Modeled cognitive energy paid | 22,137.5328 | 19,240.5632 |
| Modeled cognitive vigilance paid | 26,917.410 | 23,328.856 |
| Physical inactivity steps | 6,253 | 7,839 |

Selected-parent genomes spend more realized cognition and experience fewer
inactive steps in this held-out panel. That is a **phenotypic difference**,
not a violation of equal initial resources, nor proof of better cognition:
the spending totals also reflect different survival times. No per-step
equality with laboratory probes is claimed. The P2 static probe result
(0/7,729 exact matched individual work vectors) is unchanged.

## Scientific disposition

**P4a technical pass / scientific generalization INCONCLUSIVE.**
The population-level signs are inconsistent and the prospective interval
includes zero by a wide margin. An apparent aggregate gain is dependent on
one independent lineage. In this narrow held-out ecology mix, selection
has **not** established a reliable survival advantage beyond the
equal-opportunity random-parent control.

The result does not test whether memories, value updates, place beliefs or
replay causally help survival, nor whether two genetically identical agents
can become distinctive through separate lived histories. Those are the
distinct questions of P4b, requiring an independent prospective protocol
and genuinely unused worlds. P4a outcomes must **not** be used to choose
a winner genome, hyperparameter, world family, ablation schedule or rescue
policy. The P4 reserve remains locked.

I1 remains active; I3 remains an unregistered research proposal.
