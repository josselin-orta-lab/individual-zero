# I3 P4b: prospective paid outcome-learning ablation and individual histories

**Study ID:** `i3-p4b-outcome-learning-v1`.
**Status:** PROSPECTIVELY REGISTERED BEFORE P4b WORLD EXPOSURE.
No scientific GO; I3 is an unregistered proposal, I1 remains active.

## Frozen source and allocation

- Exact verified executable Git commit:
  `fda5ce482aaec151c3e9b4d5b4cdb8ea16ed523b`.
- Frozen P4b allocation SHA-256:
  `e437fa0f02f8dd2b9e4bf27c246fae86785af789f1a5ab948e8d036e24f4a156`.
- The identical 48 full G2 genomes from the P3-only frozen artifact are
  evaluated, without selection, mutation, tuning or filtering after P4a.
  Frozen genome raw SHA-256:
  `6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419`.
- [Preflight 42186595334](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42186595334)
  passed **127 I3 tests** on Python 3.11 and 3.12 and verified 48 genome
  digests **without opening any P4b validation world**.

## Scientific question and intervention boundaries

Do individual lifetime outcome-model updates (effects, learned values and
replay) make a difference to persistence and personal experience, beyond
the inherited generic genome, innate forecasts, and ordinary spatial
perception? P4b tests a **targeted** outcome-learning component, not all
forms of learning, and does not claim to discover consciousness.

Two modes using identical genomes, first-person perceptions, starting body,
world/seed, nominal energy/vigilance laws and horizon:

1. `normal`: after physical outcome, prepaid learning updates are retained.
2. `shadow_discard`: the **same algorithm is actually computed** and paid
   on a detached copy of the current mind; its learned effects, value
   coefficients, and replay records are discarded immediately after the
   step. Physical position bookkeeping, perception, personal spatial map
   and recency-based place beliefs remain fully active.

Any simulated shadow learning computation executes before being discarded;
no fabricated payment for unexecuted learning and no postmortem payment.
The two modes may nevertheless spend **different cumulative energy and
vigilance**, because memory occupancy and subsequent decisions diverge.
The change in retained cognition is the controlled intervention, but
equal initial opportunities and price rates are **not exact equality of
realized cognition**. Report actual payment and inactivity alongside
survival. Distinctive spatial map histories can still emerge in the shadow
arm; do not call it a total absence of learning.

## Locked P4b design

- 4 population IDs, 2 preexisting genetic lineage arms
  (`selected` and `random_parent`), all six G2 genotypes per
  population/lineage arm, all three ecological families
  (`stable`, `depletion`, `pulse`) and two repeats.
- 24 **new** validation worlds, indices **24 through 47**, with physical
  seeds **30024 to 30047**. P4a indices 0..23, P3 selection worlds and
  P4 reserve are never reopened.
- Validation life seed = `260000 + validation_index`; same for both
  `normal` and `shadow_discard` interventions for each paired genome/world.
- 400 steps per birth; **576 experimental lives**:
  4 populations × 2 genetic arms × 6 genotypes × 3 ecologies ×
  2 worlds × 2 learning modes, at most **230,400 physical ticks**.
- Rebirth always starts with empty individual lived state; no transmission
  of spatial memories, memories of past actions, intentions or prior body
  conditions. No genetic change or selection during P4b.

## Primary outcome, independent units and falsifiers

Primary endpoint: **per-independent-population difference** in the
fraction of censored lives by step 400 between `normal` and
`shadow_discard`, pooling the two *predeclared* G2 parent lineage
arms within a population. Every population has 72 new lives per
learning mode. The four paired survival differences, their mean,
range, and exploratory two-sided 95% Student-t interval (df=3,
t-critical 3.182) are reported, with n=4 independent populations.
Do **not** treat the 576 lives as 576 independent sampling units.

The target comparison is *retained outcome-learning updates* under the
same available physiological budget and pricing laws, **not** equal
realized cognitive computation. Interpret changes in survival together
with actual energy/vigilance paid, inactivity, lived steps, and memory
updates. A survival change cannot be uniquely attributed to information
quality if distinct realized charges explain it; report that limitation
rather than retuning equalization. Inconsistent population signs or
interval including zero → **no supported general benefit**; favorable
results do not automatically activate I3.

## Separate, descriptive same-genome history probe

For each population, genetic arm, genotype slot and ecology, compare the
two **normal-mode** fresh lives (repeat 0 vs 1) with the **same genome**
but different preset world/seed histories. This gives 4×2×6×3 =
**144 paired histories** (36 per independent population). Report the
number whose *observer-only end-of-life outcome model digest* differs,
plus their survival status and realized work; also report spatial
belief digests where useful. This establishes whether distinct lived
histories can produce distinguishable learned traces, **not** that
different learned states caused longer life or constitute subjective
identity. Dead lives have shorter experience; note censoring and life
length as essential limitations.

Individual maps and beliefs are collected only in observer evidence
after life termination, never fed back into another mind or genome.
Pairing identical genome and identical life/world seed must be
deterministically reproducible in software controls.

## Reporting and custody

Report all 576 actual observed lives, all deaths and censored survivors,
actual cognitive energy/vigilance, physical inactivity, model learned
updates retained versus discarded, source/world/genome hashes, evidence
heads, and both first-person outcome and spatial-history fingerprints.
Preserve negative results and all populations/families, even unfavorable
ones. Do not use P4a outcomes to select a favorite genotype or ecology.

Any cost, physics or code error is **ENGINEERING_INVALID**, not biological
death; stop and archive logs without silently changing software or seeds.
This preregistration must be merged into `main` **before** the one-shot
P4b workflow. That workflow must check out the **older pinned exact source**,
verify the preregistered schedule SHA and frozen G2 artifact before any
new world opens, then retain full original evidence and its SHA-256.
A retry after an actual scientific run requires a distinct explicit
prospective amendment; a pre-exposure CI failure remains in the record.

P4 reserve worlds remain unopened. No scientific GO or broader claims of
individuality or generalization follow mechanically from P4b.
