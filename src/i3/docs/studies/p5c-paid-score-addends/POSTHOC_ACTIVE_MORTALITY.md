# P5c original-only post-hoc active mortality and early resource actions

**STATUS: POST-HOC DESCRIPTIVE DIAGNOSTIC, NOT PREREGISTERED INFERENCE.**
This report uses only the [immutable first original P5c complete
evidence](addends-full.json.gz), itself independently
[audited](independent-custody.json). No individual was simulated,
reselected, mutated, revived or exposed to a new world for this
analysis. Original raw SHA-256:
`9ef699c1b8e5396ca4132ca526bfb09b3ae01bda524a33fb218a6e51473fa6a7`;
canonical original:
`4774b3c890bba4b6b06efa5d955ec81ed3abcbc652ae7b2169ecd7ddb241bc0d`.

Reproduce from the archived file:

`PYTHONPATH=src python -m i3.lab.p5c_posthoc_mortality src/i3/docs/studies/p5c-paid-score-addends/addends-full.json.gz`

The [cross-Python reanalysis 42235312727](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42235312727)
passed **185 I3 tests on Python 3.11 and 3.12**,
verified the original study through the independent receipt
custodian and computed this analysis with **zero new lives**.

## Registered primary conclusion still unchanged

[Full original first P5c scientific report](RESULTS.md):
censored alive at step 400 **normal 110/288**,
discard curiosity **4/288**,
discard uncertain-meal risk penalty **105/288**,
discard both **7/288**. The exact genetic population n=4
two-sided sign-flip p remains 0.125 for curiosity and 0.375
after exploratory three-contrast Holm adjustment.
This post-hoc analysis does **not** add statistical degrees of
freedom or change those endpoints.

## Death cause, timing and activity

| Actual original 288 lives/mode | Normal | Discard curiosity | Discard uncertain-meal risk | Discard both |
| --- | ---: | ---: | ---: | ---: |
| Deaths before horizon /288 | **178** | **284** | **183** | **281** |
| Death labeled `zero_water` | 146 | **239** | 154 | 258 |
| Death labeled `zero_food` | 32 | **45** | 30 | 23 |
| Dead by step 100 | 5 | **29** | 4 | 29 |
| Dead by step 200 | 75 | **220** | 76 | 227 |
| Dead by step 300 | 148 | **278** | 150 | 273 |
| Lived physical steps, all lives | 82,448 | **43,855** | 81,882 | 44,214 |
| Inactive physical steps, all lives | 15,379 | **495** | 15,303 | 841 |

Cause counts are recorded per label in an original death event; in
principle a life may have more than one death label, so they should
not blindly be interpreted as disjoint. In this first observed
cohort, the reported counts happen to sum to the number of deaths.
The `zero_water` and `zero_food` labels are the physical rules'
terminal causes, **not** a reconstruction of whether the
individual earlier perceived water, collected food or succeeded
at consuming either.

These results sharpen the activity paradox: the curiosity-
discarded minds did **not** become generally inactive. They
acted for much of their shorter lives yet disproportionately
died from depleted resources, particularly water. An active
agent may still fail to act *effectively for survival*. This
does not establish how a resource was missed or which
specific choice was decisive.

## First 12-step actual physical command witnesses

Each original life has the first 12 actual physical commands
(or fewer if death happened earlier). In this corpus,
all four modes contribute **3,456 early physical command
observations** (288 lives × 12 steps). Only these first
12 commands are available as detailed action history
in the compact permanent scientific receipts.

| Command family in first 12 steps | Normal | Discard curiosity | Discard risk | Discard both |
| --- | ---: | ---: | ---: | ---: |
| Movement `se_deplacer` | 2,681 | 2,515 | 2,655 | 2,464 |
| Resource command `boire/manger/collecter` | **392** | **132** | 436 | 245 |
| Rest or wait `dormir/attendre` | 383 | **809** | 365 | 747 |
| Resource commands / first 12 observations | **11.34%** | **3.82%** | 12.62% | 7.09% |

Under curiosity masking, the first 12-step fraction of
resource-related commands is roughly a third of normal,
while rest/wait commands are more frequent in that early
period. This is an *observed association* in repeated
dependent command histories from the same experimental
genotypes and worlds; it is **not 3,456 independent
experimental subjects**. These are commands issued, not
verified successful resource contacts or absorbed nourishment.
The original compact receipts do **not** preserve every
later command, resource location contacted, successful
water/food acquisition, or full per-step body trajectory.
Those nonexistent observations must not be reconstructed
from final memory hashes or an extra replay of the same
already-exposed scientific worlds.

## Ecological replication within original P2 families

| Ecology, censored alive /96 in each mode | Normal | Discard curiosity | Discard risk | Discard both |
| --- | ---: | ---: | ---: | ---: |
| Stable | 38 | 4 | 39 | 6 |
| Depletion | 46 | **0** | 40 | 1 |
| Pulse | 26 | **0** | 26 | 0 |

The curiosity signal appears across three distinct *existing*
ecological mechanisms, but they are the same underlying
generator families used in earlier research and they reuse
the same four original genetic populations. Thus this is
not independent genetic/ecological generalization or
another confirmatory hypothesis test.

## Paired original lifetime consequences (descriptive only)

Out of the 288 original matched genome/world/seed pairs,
normal lived longer than discard-curiosity in **216 pairs**,
both lived equally long in **55 pairs**, and the ablated
condition lived longer in **17 pairs**. Original genetic
population mean normal-minus-ablated lived-step differences
were **[115.42,188.39,118.74,113.47]**, respectively.
These are *exploratory descriptive lifetime outcomes*,
not a replacement for the preregistered 400-step censored
survival endpoint or independent replicated populations.

## Interpretation and next falsifiable contract

The first-pass mechanistic hypothesis is that **need-weighted
curiosity helps an embodied individual favor early resource
actions and/or discover viable resource opportunities**, not
just accumulate knowledge for its own sake. When the
curiosity bonus is withheld, the individual may remain
physically active while its actions fail to maintain
resources, and it dies earlier. This interpretation is
consistent with observed early commands and terminal
causes, but is **not yet a controlled causal explanation
of the entire individual life**.

A distinct future **development-only** instrument should
record, in a blinded observer outside the mind, whether
resource commands succeed, resource availability as
personally perceived, action novelty, exploration,
food/water trajectories, processing costs and physical
death. These new observations must be captured prospectively
in untouched worlds rather than retroactively invented in
the old P5c original. If this yields a falsifiable
mechanistic contrast, preregister independent genetic
populations and additional ecology mechanisms before
opening new held-out validation indices **>=120**.
Never reuse P5c worlds 96–119, any P2/P3/P4/P5a/P5b
scientific world, or the sealed P4 reserve.

I1 remains active, I3 is unregistered, and there is
**no conventional confirmatory or general scientific GO**.
