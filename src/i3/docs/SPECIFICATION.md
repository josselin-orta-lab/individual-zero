# I3: Specification and physical-model versions

**Decision:** [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md),
accepted 5 November 2026. The illustrated and annotated version is kept in the
shared document "I3: ADR-0014 and specification". This file records the
contracts the code must satisfy and historical implementation deviations.

## Current executable funding model

The v1 design and historical P1/P1.1/P1.2 notes below retain their original
context. The current payment order and exhaustion behavior are versioned in
[COGNITIVE_FUNDING.md](COGNITIVE_FUNDING.md), body laws v2. Decision work is
bounded before execution, learned updates/replays are prepaid in the same tick,
and physical exhaustion can produce a null motor command (not tie abstention).
Do not interpret historical v1 outcomes as observations under v2.

## Purpose

A mortal individual whose own organization is at stake, in a lineage where
individual persistence alone selects generic innate parameters. No personal
experience is inherited.

## Required implementation guarantees

| Requirement | Location |
| --- | --- |
| Separate World; the individual reads only `World.capture()` (body, inventory, current cell and four neighbors) | `modules/world.py` |
| Physical model v4 (food -0.2, water -0.4 per step; deaths `zero_food`, `zero_water`, `zero_integrity`) | `modules/body.py` |
| Fifth **vigilance** channel, depleted by cognition and restored by sleep | `modules/body.py` |
| **Vital currency:** cycles, simulated steps, memories and replays cost energy and vigilance | `modules/body.py` |
| **Vulnerable capacities:** energy limits cycles; vigilance limits simulation horizon and forgetting; integrity limits perceptual accuracy | `modules/body.py`, `modules/mind.py` |
| Closed `i3-genome-v1` genome, declared bounds, no World-indexed gene | `modules/genome.py` |
| Tokens renamed in first-perception order; coordinates relative to birth | `modules/mind.py` |
| Innate distress `D(h) = Σ w_c * max(0, (θ_c - h_c)/θ_c)^p_c`; reward `r = -D`; no penalty above a threshold | `modules/mind.py` |
| Continuous choice scores, stable semantic accumulator identity, no privileged action and no default abstention | `modules/mind.py` |
| Exact replay: (code, genome, World, life seed) produces the same life | `runtime/life.py` |
| Irreversible death; no action after death | `modules/world.py` |

## Historical v1 implementation deviations (decided during P1 development only)

Development used `lab/dev_worlds.py`, never the G2 test Worlds. Five architectural
defects were found there. Each received a general correction, not a rule
specialized to an action or a World.

1. **Innate self-projection.** The initial value is not solely learned:
   the individual projects 255 steps of passive bodily drift in blocks of
   1, 2, 4, ..., 128 for World-dependent channels (food, water, integrity).
   Energy and vigilance remain constant in this initial projection because
   sleep is always available to the body. TD learns a residual above this
   projection. Without it, distant death and the urgency to search were unseen.
2. **Need-relevant curiosity.** The need-sensitive exploration bonus applies
   only to options that could address the deficit (drink for thirst, eat for
   hunger, explore for both). Other options receive only general curiosity
   `κ₀`. Urgency uses the projected body, weighted by one minus the belief
   that a known resource source still works.
3. **Exploration information value.** Exploring an unknown frontier is valued
   by the number of revealed cells times the personally observed resource-cell
   frequency (Laplace estimate).
4. **Prudence scaled by vulnerability.** The uncertainty penalty for an
   unknown meal increases with integrity distress instead of being constant.
5. **Per-place presence belief.** The map retains each cell's observation
   history; a trip to a source is evaluated by expected outcomes (the source
   remains available or the trip was unnecessary). Trips are simulated in
   horizon-bounded step blocks, with horizon itself limited by vigilance.

Additional deviations: gene `v_s` is absorbed into `w.vigilance` (equivalent
role); temperament affects exploration (`β_u`, `κ₀`), threat sensitivity
(`λ_r`) and goal protection (inertia). `reward_sensitivity` and
`affiliation` have no v1 effect. The innate reflex is limited to vetoing a
harmful meal when integrity is at most 10; it never forces an action.
Low-integrity action failure is not implemented yet. `modules/` consists of
files rather than subdirectories.

## P1.1 (after the G2 gate)

**Adopted after G2b** as non-inferior to P1, without measured gain. Within
self-projection, energy and vigilance are no longer held fixed. If sleep has
already restored energy, the projection returns them to their distress
thresholds while paying the extra food cost of sleeping. P1 had held them
fixed, making a plan that ended exhausted appear permanently costly (the
probable cause of genome 8's death in G2).

**Tried and rejected on development Worlds** (30 genomes per World):

- *Full habitual projection* (assumed replenishment at known sources): home
  21/30 survivors versus 26/30 with P1. Excessively optimistic; it delays
  journeys until they become impossible.
- *Frontier revealing the most unknown cells*: open field 2/10 drinkers
  versus 7/10.
- *Spiral exploration from origin*: open field 1/30; home 0/30 survivors.
  With one-cell perception, edge cells keep neighbors that are never
  observable, remain frontiers and cause loops along boundaries.

**Known defect, addressed by P1.2:** nearest-frontier exploration follows walls
and covers space poorly. None of the tested variants improves it. The large
development field (water nine cells away and out of sight, 100 steps of
reserve) remains 0/30 in every version and may be infeasible under this
perception and energy economy.

## P1.2 (rejected at the G2c gate; retained in branch `i3/p1.2-variant`)

Two genes were added to `i3-genome-v2`. See
[G2C_P12_HELDOUT_PREREG.md](G2C_P12_HELDOUT_PREREG.md):
`belief_rate` (moving-average rate of belief revision about places) and
`reach` (exploration: 0 = nearest frontier; >= 1 = heading-consistent rays).
Result: [G2c](studies/g2c-p12-heldout/RESULTS.md). The reference remains P1.1
(genome v1). Retained lab tools: World-family generator
(`lab/worldgen.py`, reserved seeds >= 1,000,000) and probes
(`lab/probes.py`: viability oracle and systematic reference searcher).
Across 100 generated Worlds, the oracle survives all and the systematic
searcher survives 72; this gives an approximate ceiling for one-cell perception.

## P1.3 (adopted on the funded v2 substrate through G2e)

Only one cognitive change from P1.1: per-place presence beliefs become moving
averages of observations with an inherited `belief_rate` in [0.02, 0.5].
Genome `i3-genome-v3` contains 30 genes; the added gene is sampled last, so
genomes v1 and v3 generated from the same seed share every v1 gene.
Under v2 funding, map memory is charged by occupied cells, not observation
history, so revision does not alter cognitive economics.
Result: [G2e](studies/g2e-p13-v2/RESULTS.md).

## Outside the historical v1 scope

World-family generator (P2), lineage and registry (P3), 2 x 2 study and
ablations (P4), allostasis (within-life revision of thresholds `θ_c`).

## Evidence-language custody

This is an English translation of the pre-rationalization French
specification. The original content is retained byte-for-byte under
`archive/i3/original-language-records-2026-11-09/src/i3/docs/SPECIFICATION.md`.
The translation changes no physical, cognitive or scientific contract.
