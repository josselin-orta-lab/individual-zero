# I3 P5c: first prospective paid curiosity/risk score-addend screen

**Scientific status: FIRST EXPLORATORY SCREEN COMPLETE AND INDEPENDENTLY CUSTODIED.**
This is **not conventional confirmatory significance**, not a causal
claim of equal *realized* cognitive work, and **not a general scientific GO**.
I1 remains the active engine, I3 remains unregistered, and the P4
reserve was never opened.

## Registration, single original run and data custody

The [prospective P5c protocol](../../P5C_HELDOUT_PREREG.md) was merged
into `main` via [PR #1049](https://github.com/josselin-orta-lab/individual-zero/pull/1049)
**before the first validation-world exposure**. The fixed scientific
executable source is Git commit
`674f4f05ddab8ebcc5412632d0caed7df299a8bd`,
and the deterministic population/ecology allocation SHA-256 is
`287147fdf06d1ab6a4fdd6f5dc1cc4d04ec8014be5b23918f68abb8006925268`.
All 48 original frozen G2 genomes are unchanged and reused without
selection or mutation.

The one and only [original P5c scientific run
42232558602](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42232558602)
completed **1152/1152** registered, genuinely computed and paid
lives at horizon 400, on 24 **previously unused** validation
worlds, indices 96–119, world seeds 30096–30119.
No P3 selection world, older validation world 0–95 or P4 reserve world
was reopened.

Independent [custody run
42233838959](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42233838959)
used the separately tested read-only custodian from
[PR #1050](https://github.com/josselin-orta-lab/individual-zero/pull/1050).
It verified **every original life identity** by population, arm,
slot, ecology, repeat and score mode, all 48 frozen genome hashes,
24 world opportunities, 288 paired genotype/world/seed groups,
original source and schedule, death/censoring, paid per-phase
energy/vigilance, learning and replay, and first-12-step *actually
funded* score-addend receipts, without running any additional life.
Behavior hashes are explicitly allowed to coincide across different
modes; identical behavior is valid null evidence.

Immutable original [full JSON compressed without reserialization](addends-full.json.gz),
[original summary](addends-summary.json),
[read-only custody report](independent-custody.json),
[original SHA-256 receipt](ORIGINAL_SHA256SUMS.txt)
and [archive SHA receipts](ARCHIVE_SHA256SUMS.txt)
are retained here.

- Original uncompressed full JSON SHA-256:
  `9ef699c1b8e5396ca4132ca526bfb09b3ae01bda524a33fb218a6e51473fa6a7`.
- Original canonical content SHA-256:
  `4774b3c890bba4b6b06efa5d955ec81ed3abcbc652ae7b2169ecd7ddb241bc0d`.
- Original summary JSON SHA-256:
  `18f4cf060674d280dfe6af92e76dcf7a5fbe9d9df1228231bc90ca44bc08eaa9`.

## Prespecified primary result: alive and censored at step 400

All four modes start with exactly identical world, genome, body,
life seed, five-channel v2 physics, innate parameters and nominal
cognitive cost tariffs. All modes compute the original first-person
action forecast, base return, curiosity bonus and uncertain-meal
risk penalty, and charge genuinely executed simulation.
Only **which computed score addend is applied** changes.

| Independent original genetic population (72 lives/mode) | Normal score | Discard curiosity | Discard uncertain-meal risk penalty | Discard both |
| --- | ---: | ---: | ---: | ---: |
| Population 0 | **21** | 0 | 16 | 0 |
| Population 1 | **41** | 0 | 40 | 1 |
| Population 2 | **24** | 2 | 21 | 2 |
| Population 3 | **24** | 2 | 28 | 4 |
| **Total, descriptive** | **110/288** | **4/288** | **105/288** | **7/288** |

The effect of **discarding scored curiosity** is directionally
consistent in all four original independent genetic populations:
normal-minus-curiosity-discard
**[+21,+41,+22,+22]** survivors per 72, mean
**+26.5** survivors/population (36.81 percentage points).
Exploratory 95% Student-t interval (df=3)
**[+11.10,+41.90] survivors/population**.
Exact two-sided n=4 sign-flip reference **p=0.125** and
exploratory Holm-adjusted p across all three comparisons
**0.375**.

Discarding **both** curiosity and the uncertain-meal risk penalty
yields per-population normal-minus-ablated differences
**[+21,+40,+22,+20]**, mean **+25.75**,
exploratory 95% t interval **[+10.58,+40.92]**,
exact bilateral sign-flip **p=0.125**, Holm **0.375**.
Thus retaining the risk penalty alone did not rescue
the effects of discarding scored curiosity in this study.

Discarding **only the uncertain-meal risk penalty** yields
population differences **[+5,+1,+3,−4]**,
mean **+1.25**, exploratory t interval **[−4.90,+7.40]**,
exact two-sided sign-flip **p=0.625**, Holm **0.625**.
The population signs are **mixed**. We cannot infer a general
survival advantage or disadvantage of this risk penalty.
The unmodified *innate integrity veto* remains active in all
modes, so this does not measure the loss of every danger response.

**Critical inferential limitation:** exactly **four independent
genetic populations** constitute the inferential unit, not 1152
independent life replications or thousands of option comparisons.
The smallest possible exact paired bilateral sign-flip p at n=4
is **0.125**, irrespective of unanimous signs. The positive
exploratory t intervals rely on fragile small-sample parametric
assumptions. No conventional p<0.05 result is possible under
the registered exact test. This is a bounded within-I3 mechanism
screen using the same P3 genetic origins and existing P2
ecological families, not independent-family generalization.

## Scores actually computed and applied before choice

The full original receipts contain first-person paid score
witnesses from each life’s first 12 decision steps, for
each genuinely funded option:
`base_return`, `curiosity_calculated`,
`risk_calculated`, `curiosity_applied`,
`risk_applied`, final score, and pre-decision body.
No uncomputed option receives a fictitious score or cognition bill.

For every matched original genotype/world/seed, the mechanism
comparison only includes the **same paid option under the same
pre-decision five-channel body before the first different
physical action**. Null scores or missing funded option matches
remain genuine nulls.

| Mode versus normal (288 paired opportunities) | Pairs with different early total score | Pairs with changed applied curiosity | Pairs with changed applied risk | Pairs with first physical action change within 12 steps |
| --- | ---: | ---: | ---: | ---: |
| Discard curiosity | **276** | **276** | 0 | **276** |
| Discard risk penalty | **105** | 0 | **105** | **40** |
| Discard both | **280** | **276** | **5** | **280** |

A pair can show multiple effects, but these are paired
descriptive counts, not independent genetic-population tests.
The first changed total score and the first changed physical
action occur as early as **step 1** in the curiosity ablation.
For risk-only masking, the earliest changed score occurs
at **step 2**; a first changed action is not universal.
The prospectively recorded **base projected return** is equal
for nearly all matched pre-action comparisons; with risk-only
masking one pair shows a base-return difference, reflecting
uncontrolled hidden-state or context differences that can
exist even at an identical bodily vector.
A matched body does not imply identical complete memory,
RNG, perception or history.

The registered intervention directly changes application of
curiosity/risk terms, rather than how the originally computed
action consequence predictor is read. It is evidence of a
functional score-addend dependence **within this architecture**,
not a proof of isolated curiosity causality at equal subsequent
mind-state and body budgets.

## Actual physical inactivity and cognitive expenditure

| Actual aggregate for 288 lives/mode | Normal | Discard curiosity | Discard risk penalty | Discard both |
| --- | ---: | ---: | ---: | ---: |
| Lived physical steps | 82,448 | 43,855 | 81,882 | 44,214 |
| Inactive physical steps | 15,379 | **495** | 15,303 | **841** |
| Inactivity fraction of lived steps | 18.65% | **1.13%** | 18.69% | **1.90%** |
| Paid modeled energy for cognition | 47,725.8014 | 24,942.1638 | 47,168.8064 | 24,579.5536 |
| Paid modeled vigilance for cognition | 58,097.556 | 33,503.646 | 57,398.080 | 32,707.838 |
| Censored alive at horizon | 110 | 4 | 105 | 7 |

This is especially important when contrasting P5c against P5b:
**removing the curiosity score addend severely reduces 400-step
survival but does NOT result in the same high-inactivity
collapse observed when action-specific effect forecasts were
blinded in P5b**. The few inactive physical steps in curiosity
ablations reflect their distinct trajectories and shorter
lives, not healthier minds or equivalent bodily resources.
The precise behavioral path through exploration, resource
acquisition, risky actions, fatigue and death remains an
important future mediator analysis.

All four conditions faced the same starting opportunities,
initial cognitive price schedule, physiological rules and
learning pipeline. Their **realized physical lifetimes and
cognitive charges differ significantly** because the
intervention changes choices and future life history. Do not
post-hoc equalize with imaginary charges or claim that the
observed survival gap represents curiosity information alone
under identical realized energy use.

## Interpretation and research handoff

The strongest bounded result is that in I3's original
ecological families and frozen G2 populations, **retaining the
computed curiosity term in the score before choosing actions
is associated with much greater sustained survival**.
Suppressing the uncertain-meal risk score addend alone
does not show the same consistent association. The result
is coherent across all four original genetic source
populations but not conventionally confirmatory.

P5b previously found that retaining action-specific
*consequence readouts* mattered; P5c now reveals a distinct
role for the **curiosity-weighted use of uncertainty** when
turning first-person knowledge into action scores.
Neither study establishes that curiosity is universally
beneficial in unrelated ecologies. P5c does not prove
self-awareness, subjective experience, humanlike agency,
universal survival optimality or a genetic selection GO.

Priorities for a **separately preregistered** next study:
(1) measure the physical action-family, resource contact,
novelty and starvation/dehydration/death pathways behind
the rapid active mortality under curiosity ablation, without
tuning from the held-out P5c outcomes;
(2) prospectively test different ecological mechanisms
and genuinely new independent genetic lineages, rather
than mere more seeds from the same old populations;
(3) separate need-weighted curiosity from general
uncertainty-driven curiosity with real paid work;
(4) separately study **same inherited genome, distinct
lived histories → identical new challenge in the same
continuously surviving mind**, not just different terminal
memory hashes.

The original P2/P3/P4/P5a/P5b studies remain immutable.
**No general scientific GO; I1 active; I3 unregistered;
P4 reserve locked.**
