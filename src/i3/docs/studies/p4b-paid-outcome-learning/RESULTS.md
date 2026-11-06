# I3 P4b: prospective paid outcome-learning ablation and divergent life histories

**Status:** EXPERIMENTAL EXECUTION AND CUSTODY PASS. Strong within-model
effect of **retaining outcome-model learning** under this exact v2
substrate; NOT proof of consciousness, general learning optimality, or
a general scientific GO for I3. I1 remains active, I3 unregistered.

## Provenance and experiment integrity

The [P4b prospective preregistration](../../P4B_LEARNING_PREREG.md) (PR #1023)
was merged **before** the first P4b world was opened. It pins exact source
`fda5ce482aaec151c3e9b4d5b4cdb8ea16ed523b`, schedule SHA-256
`e437fa0f02f8dd2b9e4bf27c246fae86785af789f1a5ab948e8d036e24f4a156`,
and the original 48 full frozen G2 genotypes.

[First P4b study run 42186901336](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42186901336)
passed its preregistration, Git source, 127 I3 software test and isolation
guards **before** executing the 576 registered study lives on Python 3.12.
The independent [evidence archive workflow 42187392961](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42187392961)
verified the original checksums, complete counts, unique provenance and
paired equal starting world/genome/seed; **no new life was run in custody**.

| Custody invariant | Verified |
| --- | ---: |
| Total completed lives | **576 / 576** |
| Full normal mode lives | 288 |
| Paid shadow-discard mode lives | 288 |
| Previously unopened P4b world keys | **24 / 24**, validation indices 24–47 |
| Frozen G2 genotypes | **48 / 48**, no mutation or selection |
| Matched normal/shadow pairs | **288 / 288**, same genome/world/life seed |
| Unique evidence heads | 576 |
| Source hashes used within the study | 1 |
| P4a, P3 selection or P4 reserve worlds reopened | **0** |

Raw original `i3-p4b-full.json` SHA-256:
`688463e4fbb71cb88d57d0cafbe70eb033adeafe8ae8551d42bec58dfa9e395c`.
Internal canonical evidence SHA-256:
`8fc34d37b7348e3f171a48879d7dd03b898547c4aaa5204c0727cc8006b0168b`.
The full original, compressed without reserialization, is
[`learning-full.json.gz`](learning-full.json.gz), with
[complete summary](learning-summary.json) and
[original checksum receipts](ORIGINAL_SHA256SUMS.txt).

## Primary prospectively registered survival endpoint

Each population has 72 lives for each learning mode (two G2 lineages
× six genotypes × three ecologies × two new worlds). The statistical
experimental units are **four independent populations**, not the 576
dependent life observations.

| Population | Normal censored / 72 | Paid shadow censored / 72 | Normal minus shadow |
| --- | ---: | ---: | ---: |
| 0 | 17 | 0 | **+17** |
| 1 | 35 | 0 | **+35** |
| 2 | 17 | 0 | **+17** |
| 3 | 15 | 0 | **+15** |
| **Total (descriptive)** | **84 / 288** | **0 / 288** | **+84 / 288** |

Survival at horizon 400 is **29.17% normal vs 0% with outcome retention
disabled**. Four population-level contrasts are all positive:
`[17, 35, 17, 15]` censored lives per population of 72.
Their mean is **21 lives per 72**, sample SD **9.381**. The
predeclared exploratory two-sided 95% Student-t confidence interval
(df=3, critical 3.182) is **[6.07, 35.93] lives per population**,
or **[+8.43, +49.90] percentage points**. With only n=4 and a single
fixed experimental framework, the t assumption and generalization
are limited. Nevertheless, unlike P4a's genotype-selection contrast,
every tested population favors the full outcome-learning mode.

## Secondary diagnostics: activity, costs and mortality

| Across each 288-life mode | Normal | Paid shadow-discard |
| --- | ---: | ---: |
| Deaths | 204 | 288 |
| Lived physical steps | 68,294 | 49,531 |
| Modeled cognitive energy paid | 37,299.8656 | 6,181.7184 |
| Modeled cognitive vigilance paid | 45,583.496 | 9,564.544 |
| Physically inactive steps | 13,950 | 31,785 |
| Inactive fraction of lived steps | **20.43%** | **64.17%** |
| Energy paid per lived step | 0.5462 | 0.1248 |
| Actually executed outcome-learning computations | 54,213 | 17,630 |
| Outcome-learning updates retained | **54,213** | **0** |
| Shadow computations executed and discarded | 0 | **17,630** |

No free artificial learning was substituted: the shadow **actually runs**
its prepaid update and discards the changed model, value and replay state.
However its lived memory occupancy subsequently remains smaller. It therefore
computes, pays, acts and survives differently. Cost equality holds in
initial opportunities and nominal **rates**, not actual paid work vectors.
This is an effect of the **retention intervention and its downstream
energetics together**, not proof that information quality alone produces
the entire survival gap. Lower model charges actually gave the shadow
group a larger residual physical budget, but this did not rescue its
inactivity-heavy behavior.

Mortality reasons were actual zero-vital-channel deaths, not funding failures:
normal `zero_water` 169 and `zero_food` 35; shadow `zero_water` 242
and `zero_food` 46. These sum to each mode's deaths.

| Ecology | Normal censored / 96 | Shadow censored / 96 |
| --- | ---: | ---: |
| Stable | 36 | 0 |
| Depletion | 38 | 0 |
| Pulse | 10 | 0 |

These are descriptive, non-independent secondary groups, not alternative
success gates chosen after looking.

## Individual history: same genome, separate lives

A predeclared 144 pairs (4 populations × 2 genetic arms × 6 G2 genotypes
× 3 ecology families) compare two **normal-mode** first-person lives of
the exact same genome, but with different fresh world/seed experiences.
**144 / 144 pairs** have distinct end-of-life *outcome-model learned
state digests*. Among the 288 normal lives all 288 have unique outcome
model fingerprints; the shadow group has only one fingerprint because
all learned outcome-model/value/replay changes are discarded.

The shadow group nonetheless has **255 different spatial-belief
fingerprints among its 288 lives**: observation, place beliefs and
orientation were still live. Therefore this experiment **does not test
complete absence of learning**, and even its successful ablation cannot
separately prove the value of replay, of value updates or of learned
action consequences without more targeted interventions.

Same-genome trace divergence is a clear engineering observation of
history-dependent retained cognitive state, not proof that the two agents
are biologically or subjectively individual. Different world histories,
physical survival lengths and sensory experiences themselves explain why
states can diverge; the experiment does not identify an irreducible self.

## Interpretation and remaining questions

**P4a remained inconclusive on evolutionary generalization**: held-out
selected-genome survival was 47/144 vs 42/144 random-parent, with independent
population contrasts [-2,+9,-1,-1]. P4b changes the question and finds
a strong, directionally consistent within-prototype dependence on
retaining learned outcome updates. This does **not** retroactively
turn P4a's mixed selection result into a genetic success.

Supported narrow conclusion: when the P1.3-v2 I3 mind loses the lasting
effects/value/replay updates of its lived experience, while retaining
perception, spatial beliefs and normal physics, it becomes substantially
less able to persist in these new ecologies. With learning retained,
distinct histories of the same genome leave distinguishable learned
models. Both observations address the original research motivation but
remain bounded by this architecture and environmental sample.

Open for a later, **new** protocol: independent energy-matched causal
disentanglement, separate replay/value/effect ablations, larger independent
population sets, and careful controls distinguishing stable adaptive
individuality from simply differing episodic memories. No further runs
or retuning have been conducted on P4a/P4b outcomes.

**P4 experimental campaign completed at its two declared first-pass
scopes; no blanket scientific GO, engine activation or broad natural
selection claim.** I1 remains active, P4 reserve remains sealed.
