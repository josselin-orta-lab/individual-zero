# I3 P5a: prospectively registered three-component retention screen

**Status:** REGISTERED BEFORE THE FIRST P5A VALIDATION WORLD IS OPENED.
**Protocol:** `i3-p5a-paid-component-screen-v1`.
**Locked scientific executable SHA:** `ee2e97b1949fd94548fe6c5908ff411d37cb3f76`.
**Locked schedule SHA-256:** `2e176df5c1ebf9435d2ad4d83e97334d63634024ead074781eed3841b846bb7a`.
**Frozen G2 original file SHA-256:** `6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419`.
**Frozen G2 canonical SHA-256:** `4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b`.
Tested source [pre-exposure run 42191750606](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42191750606), 138 I3 tests passing under Python 3.11 and 3.12; source isolation and previous P4 evidence hashes validated. The preregistration commit MUST be merged into main before any P5a life, while the study checks out the earlier locked source SHA.

## Question and scope

P4b showed that simultaneous removal of persistent outcome-effect, learned-value and replay updates greatly reduced survival, but did **not** identify each mechanism's contribution. This screen separately prevents persistence of exactly one learned component, keeping the remaining pipeline, first-person perception, positional orientation, spatial beliefs, innate prediction, physical v2 laws and actual prepaid work in force.

The four *paired* learning conditions are:
- `normal`: full retained outcome learning.
- `discard_effects`: execute and charge the normal outcome pipeline, then restore only the preceding action-effect statistics.
- `discard_values`: execute and charge the normal pipeline, then restore only preceding learned TD coefficients.
- `discard_replay`: execute and charge ordinary TD and replay but run the replay's incremental updates on a temporary copy; retain the normal base learning update.

Each arm must pay exactly its own declared cognition. The treatments have the same **starting** world, body, genotype, life seed, nominal work rates and physical laws. Actual worked steps, memory occupancy, cognitive expenditures, physical inactivity, and survival time may differ and **are outcomes**. No post-hoc equalization of realized computation or payment for unexecuted work.

## Frozen exposure: exploratory screen only

Exactly **4 independent original P3 populations** (not 1152 independent units), **2 genetic parent-lineage arms** (`selected`, `random_parent`), six *unaltered* frozen G2 genotypes per population/arm, all three preregistered families (`stable`, `depletion`, `pulse`), two repeats per family, four learning conditions. **1152 lives**, each up to 400 physical steps (max 460,800 physical ticks). No new births, selection, mutation or parental scoring.

All 24 prospective *validation* world indices are **48–71**, corresponding to seeds **30048–30071**, excluding P4a indices 0–23, P4b indices 24–47, all P3 selection worlds and P4 reserve 1200000–1200199. Index = 48 + 6*population + 2*family_index + repeat (family order stable/depletion/pulse). Life seed = 360000 + validation index, the same across all four learning modes and all G2 genotypes on a world. No world may be opened before the source, schedule, frozen G2 and authorization checks pass.

## Outcome and statistical interpretation frozen before exposure

The primary outcome is **censored survival at physical step 400**. Within each independent population and mode, there are 72 observed lives (two G2 lineage arms × six genotypes × three families × two repeats). Three prospective primary contrasts are the population-level **normal minus ablated** counts: effects, values, replay, each divided by 72 if expressed as a proportion. Record each of the four population contrasts, range, mean, SD, exploratory two-sided Student-t 95% interval (df=3, critical 3.182446305), and exact two-sided sign-flip reference p for the four independent units. Report exploratory Holm correction across all three predeclared contrasts. With n=4, **the minimum achievable two-sided sign-flip p is 0.125**, even when all population differences agree. This experiment is therefore **not powered for a conventional p<0.05 confirmation**. No sign, interval or p-value triggers an automatic scientific GO.

The independent genetic population is the inference unit. The 1152 individual lifetimes share both genomes and worlds, and must NOT be treated as independent population replicates. Do not select a favorable ecology, genotype, repeat or mechanism after observation, and do not relabel the study as adequately powered.

Secondary and mechanistic: censored vs dead and physical death causes, lived steps, total and phase-specific energy/vigilance, decision/learning work counters (`cycles`, `simulated_steps`, `memory_items`, `replays`), inactive-step fraction and full life/evidence provenance. Realized cognitive energy is a **post-treatment mediator** and life-length exposure differs, so comparisons are descriptive rather than regression-based proof of information-only causality. Never claim equal realized cognitive charges.

For `discard_replay` a critical manipulation check is **the number of actually paid replay calls and lives exposed to replay**. If no replay occurs, the contrast is **NO_EXPOSURE / NOT_INFORMATIVE**, not evidence that replay is unnecessary. If replay is rare, report the exact exposure and say that any survival result is inconclusive about sleep consolidation. The base TD update remains active in the replay intervention.

Observed null and adverse outcomes are kept. No code or hyperparameter calibration after seeing any study life, no survival threshold changed to create success. A malformed world, unexpected exception, forged receipt or shortfall is an **engineering invalidity**, not a biological death. Preserve the original failed run and require separate, prospective amendment before a new scientific execution.

## Reproducibility and custody

The only authorized executable run is `PYTHONPATH=src python -m i3.lab.p5a_screen --run OUT.json` after exact Git HEAD and these three environment locks:
`I3_P5A_SOURCE_SHA=ee2e97b1949fd94548fe6c5908ff411d37cb3f76`
`I3_P5A_SCHEDULE_SHA=2e176df5c1ebf9435d2ad4d83e97334d63634024ead074781eed3841b846bb7a`
`I3_P5A_APPROVED_PROTOCOL=i3-p5a-paid-component-screen-v1`

Preserve every original complete-life receipt and its SHA-256 checksum as a GitHub Actions artifact, plus all population-level contrasts including adverse ones; archive the unmodified full evidence in the repository before interpreting results. Scientific review must explicitly confirm the prospective protocol is merged before the execution run, while the executable SHA stays pinned to the verified older commit. Results must not be fed into genetic selection.

This study does **not** remove spatial belief learning and is **not** the same-genome learned-history → common-challenge individuality experiment. Those require separate protocols. I1 remains active, I3 remains unregistered and the P4 reserve is sealed.
