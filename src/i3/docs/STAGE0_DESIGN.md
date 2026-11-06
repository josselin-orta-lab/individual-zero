# Stage 0: eight-population F0 gate design

Issue [#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060),
under the [single development plan](DEVELOPMENT_PLAN.md) and ADR-0016.
Baseline: `5ff6e5a78c9804b0a49c7f947479b0dddfd3eb3e`.
Receipt-adapter dependency: PR #1064, `07760f29478c681aa0cb003eef6301588b0a7b49`.

**Implemented: planning metadata, arithmetic and read-only funded-life receipts.**
**NOT a preregistration, executable study, completed Stage 0 or scientific GO.**
No World, Mind, genome or individual is instantiated by the planner or adapter.
I1 remains active, I3 unregistered; physics, cognition, prices and original
evidence are unchanged. Runtime integration tests use development fixtures only.

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
whole-family generalization. [R-depletion-v1](STAGE0_REVISION.md) now explicitly
specifies the depletion rows as a first revision stratum and a personally
available clock; that operational choice is separate from the supplied report
and still needs the final study's prospective source/allocation lock.
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
adapter or a provenance verifier**. The observer adapter below checks funding
and original chains but does not automatically select or join a life to the
fixed candidate/world allocation. Study-specific membership, genotype and
intervention binding remain necessary. The fixed ranker requires positive
lived steps; its worlds start viable. The adapter also retains zero-step deaths
and never silently discards one to satisfy that ranking contract.

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

## Connected energetic receipts: observer only

`lab/stage0_energy.py::energy_receipt` consumes an existing complete
`run_life(..., keep_trace=True)` result with explicitly supplied protocol and
source SHA-256. It reconstructs the original manifest, behavior and evidence
chains, verifies world/source/genome hashes, and checks each decision/learning
work vector against the **existing** `BodyLaws` / `debit_cognition` functions.
The two phases' actual body debits, step bills, life totals, terminal causes,
replay counts and physical inactivity must agree. Missing/truncated records,
invalid finite costs, inconsistent paid work, postmortem learning and false
censoring fail. It imports no Mind or runner and changes no runtime receipt.

Learning includes replay; replay is separately counted in the learning work
vector, not charged a second time as a fictitious third phase. Cognitive energy
and vigilance exclude motor/metabolic spending and observer CPU overhead.
Deliberate `attendre`, `dormir` and null-command physical inactivity remain
separate. Early deaths remain outcomes. A zero-step physical death has zero
work but undefined per-lived-step rates, not fabricated perfect efficiency.

`population_energy` requires the caller's complete **predeclared** case lists
for eight blocks and both `reference`/`candidate` full-life records per case.
It rejects missing/duplicate cases, repeated identities within an arm, a world
shared across population blocks, differing paired world/seed/horizon and mixed
panel horizons. Each arm has its own explicit source pin; selected genomes may
differ, as in the architecture-under-selection design. It reports all compact
life receipts, population totals, and candidate-minus-reference contrasts.
Rates use total paid expenditure divided by **all** lived steps, including
deaths, not the unweighted mean of surviving individuals' rates. Zero-denominator
rates and contrasts remain `None`. No p-value or scientific gate runs here.

**Limits:** these are consistency checks, not authenticated custody, a proof of
executed CPU instructions, complete physical-trajectory replay or genealogical
independence. Public hashes cannot authenticate a completely re-signed invented
history. Mode labels and case-to-world/genome membership need study-specific
prospective locks; the existing runtime manifest does not itself authenticate
all intervention labels. Expected cases must not be built from the successful
subset after observing outcomes. No claims of pure information benefit, equal
realized costs, or causal energetic mediation follow from these descriptives.
The design manifest from the first slice stays unchanged; its unresolved-field
list records that design snapshot, not automatic scientific authorization.

## Verification and remaining Stage-0 work

`tests/i3/test_stage0_energy.py` includes synthetic adverse/tamper cases and
bounded runtime integration. Eight existing development fixture worlds, eight
steps each, compare observer off/on under normal and curiosity-masked scoring;
checks include exact evidence, actions, body, learned state, actual paid work
and the RNG state after each decision. A zero-step dead-at-birth fixture checks
the runtime edge. These software labels are NOT eight independently evolved
scientific populations and their trajectories are not a new study cohort.
No selection, validation or reserve world is opened. Full-checkout CI must
verify these integration checks on the exact candidate; local synthetic tests
alone cannot establish runtime parity.

```sh
python -m unittest discover -s tests/i3 -p 'test_stage0_energy.py' -v
```

The [revision contract](STAGE0_REVISION.md) now defines a concrete R stratum
and observer-side latency/no-exposure/death semantics without opening worlds.
Before any study, freeze exact reference/candidate sources, the final R protocol,
non-inferiority margin, sample-size rationale, multiplicity, crashes, stopping
rule and compute ceiling. Bind expected cases, genotypes, worlds and intervention
modes to that registered design. Publish a separate prospective registration
before selection or validation, and verify live allocation conflicts again.
Observer parity must be rechecked when a new cognitive candidate is implemented.
No further general receipt framework is needed before the bounded Stage-1 design.

Keep [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026)
for continuing same-genome individuals with different histories and a common
prospective challenge, without body/memory resets or survivor exclusion.
Keep [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054)
for the unresolved P5d carried-food case; absent exposure remains NOT_OBSERVED.
Do not create new lineage/random-parent or F1-F6 mechanisms in this design slice.

Local standalone checks do not replace full-checkout integration tests or the
required CI on the exact PR SHA. No new experimental result is claimed.
