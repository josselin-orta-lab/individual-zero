# Stage 0: eight-population F0 gate design

Issue [#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060),
under the [single development plan](DEVELOPMENT_PLAN.md) and ADR-0016.
Baseline: `5ff6e5a78c9804b0a49c7f947479b0dddfd3eb3e`.

**Implemented: planning metadata and selection/statistical arithmetic only.**
**NOT a preregistration, executable study, completed Stage 0 or scientific GO.**
No World, Mind, genome or individual is instantiated. I1 remains active, I3
unregistered; physics, cognition, prices and original evidence are unchanged.

## Question and minimum intervention

Can the next one-mechanism architecture gate use eight separate candidate
pools and ecological blocks without reusing the four old P3 populations or
counting dependent genomes/lives as independent evidence?

`lab/stage0_design.py` constructs a fixed, checksummed **design candidate**.
Its P2 bounds are a source-pinned metadata snapshot, checked against the actual
P2 module and the original P3/P4/P5 schedules by repository integration tests.
It imports only the standard library. The executable command prints identifiers,
not observations:

```sh
PYTHONPATH=src python -m i3.lab.stage0_design
python -m unittest discover -s tests/i3 -p 'test_stage0_design.py' -v
```

A digest records the plan's content; it is not authorization, authenticity,
a world-exposure ledger or proof of scientific independence. Concurrent/future
allocations must be checked before registration. `manifest(occupied_world_seeds)`
rejects additional known conflicts rather than silently shifting to new seeds.
`validate_manifest` rejects changed or rehashed policy/seed/count fields.

## Population and sampling design candidate

Eight new G0 pools contain 40 founder-seed identities each, 2,000,000 through
2,000,319. No founder genome is actually drawn by this module. No old frozen G2
is reused. Reference and candidate architectures share each pool's seed schedule;
common genes must retain common draws and new genes must be drawn last under
ADR-0015. Cross-architecture genotype equivalence still needs implementation
checks when Stage 1 exists.

Each architecture separately selects five candidates per population by censored
life count, then total lived steps, then ascending founder seed. This is the
ADR-0015 **architecture-under-selection** comparison, not a same-genome learning
ablation and not an evolved lineage. An architecture effect may include different
selected genomes. The same-genome causal controls must be separately fixed.

The independent analysis unit is the paired **population plus ecological block**.
Different populations have distinct founder seeds and world seeds; within one
block, both architectures and all its candidates share world/life seeds for
initial-opportunity pairing. Thirty validation lives per architecture/block
are dependent observations, not thirty independent genetic populations.
Metadata alone cannot prove actual execution followed this independence design.

There is **no parent-selection or mutation runner** here. Random-parent controls
belong to the future lineage experiment, not to random sampling of G0 candidates.
Stage 6's >=10 generations, recombination and multi-family comparison are neither
replaced nor implemented. This first slice does not close that part of #1060.

## Allocations within the existing P2 partition

| Cohort | P2 indices | World seeds | Use |
| --- | --- | --- | --- |
| Development | 44-49 | 2044-2049 | Six design identifiers; no execution |
| Selection | 72-119 | 10072-10119 | Six worlds per new population |
| Validation | 120-167 | 30120-30167 | Six distinct worlds per new population, unopened |
| Original reserve | Not allocated | 1200000-1200199 | Sealed, never opened |

Every six-world block has two stable, two depletion and two pulse worlds. The
module never calls a generator, including for validation. It conservatively
excludes development indices <=43, selection <=71 and validation <=119 from the
known baseline. It rejects seed reuse even under a different family label.
Development history is not claimed to be an exhaustive inventory of every
unrecorded local test. The prior scientific schedule overlap is checked directly.

This is **F0 only**. Fresh seeds do not implement a new family or establish
whole-family generalization. Family R from the scenario still needs its own
prospective definition; this F0 plan does not silently substitute for it.
Only 32 existing P2 validation slots (168-199) remain beyond this design. A later
larger/family-separated allocation must be explicitly designed, not obtained by
extending P2 or touching the P4 reserve.

With two architecture slots and a 400-step horizon, the F0 envelope would contain
3,840 selection lives and 480 validation lives, at most 1,728,000 life steps,
excluding development. These are **planned counts**, not lives run, a runtime
estimate, a power calculation or a commitment to execute this full envelope.
No CPU, physical-energy or cognitive-cost equality is inferred from equal counts.

## Complete persistence-only selection

`rank_candidates(population, outcomes)` requires all 40 x 6 scalar receipts.
Each receipt has exactly `candidate_seed`, `world_index`, `terminal` and
`steps_lived`. `terminal` is `dead` or `censored`; censoring requires the full
400 steps, whereas a death at step 400 is still a death. Duplicate pairs, foreign
founders, other populations' worlds, validation indices, missing outcomes,
crashes, unfinished lives, boolean/invalid step counts and extra fields fail.
A crash is not a death, and failed candidates are not silently removed.

The function is arithmetic over supplied receipts, **not a runtime receipt
adapter or a provenance verifier**. A later adapter must check source, cohort,
manifest, terminal semantics and complete evidence before constructing these
inputs. No old trace is reclassified or rerun here.

## Population-level arithmetic, not an automatic gate

`population_sign_test` requires exactly populations 0 through 7, each with one
finite numeric difference defined by a future preregistered endpoint. It rejects
missing units, life-level lists, 288-unit pseudoreplication, booleans and NaN/Inf.
Zero differences are ties, with no fitted tolerance; they are reported and
excluded from the effective sign-test sample. The two-sided exact calculations:

- Eight positive differences: p = 0.0078125.
- Seven positive and one negative: p = 0.0703125.
- Four positive and four ties: effective n = 4, p = 0.125.

The helper reports wins, losses, ties, effective n and attainable resolution.
It issues no scientific verdict, power guarantee, non-inferiority conclusion
or multiplicity adjustment. A mapping with eight keys cannot establish the
provenance or independence of its values. Predeclare aggregates, practical
margins, uncertainty and multiplicity before exposure; do not select a test
after looking at outcomes. The 7/8 Stage-6 directional condition stays distinct.

## Energetic and observational design, still to connect

For every planned life, retain death/censoring and steps lived, genuinely paid
work by decision/learning/replay phase, energy/vigilance paid, inactivity,
physical actions and resource uptake. Analyze both cumulative expenditure and
per-lived-step expenditure; publish early deaths rather than conditioning on
survivors or matching by discarded lives. Equal initial prices/opportunities
are not equal realized costs. Never bill fictitious work to equalize arms.

The current P5e full paid Competition witness is the intended observer, not
new Mind input. This slice does not turn it on by default or re-prove its parity.
The next receipt adapter must connect actual runtime fields, check completeness
and observer on/off parity before any independently preregistered gate.
Energetic mediation remains an analysis question, not established causality.

## Remaining Stage-0 work and stop boundary

Before any study: finish the actual receipt adapter and full-witness parity;
freeze exact reference/candidate sources, family R, latency/no-exposure/death
semantics, non-inferiority margin, sample-size rationale, multiplicity, crashes,
stopping rule and compute ceiling. Publish a separate prospective registration
before selection or validation, and verify live allocation conflicts again.

Keep [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026)
for continuing same-genome individuals with different histories and a common
prospective challenge, without body/memory resets or survivor exclusion.
Keep [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054)
for the unresolved P5d carried-food case; absent exposure remains NOT_OBSERVED.
Do not create new lineage/random-parent or F1-F6 mechanisms in this design slice.

The focused tests use synthetic scalar outcomes and identifier arithmetic only.
Local standalone checks do not replace full-checkout integration tests or the
required CI on the exact PR SHA. No new experimental result is claimed.
