# I3 P3 pilot: prospective protocol (DRAFT, NOT AUTHORIZED TO RUN)

Tracking: [#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).
Status: engineering preregistration candidate. It must be committed, reviewed
and frozen **before** any P3 selection-world or validation-world life is run.
I3 remains an unregistered proposal, I1 remains active, no scientific GO.

## Scientific question and scope

Can mutation and lifetime-only selection of **generic innate genome parameters**
increase future individual persistence across three different, physically
funded environments? This is **not** a claim that genetic selection proves
individual learning. Life histories are newly sampled and never inherited.
Every death remains a real outcome; no rescue, resurrection or survivor
relabeling.

P1.3-v2 is the only candidate cognitive architecture. Frozen physical law:
`i3-body-laws-v2`. No alternate/legacy physics or cross-generation import.

## Planned pilot, pending P2 closure

- Four independent population IDs (0, 1, 2, 3), six newborn genotypes
  per population, three generations (G0, G1, G2).
- Two comparison arms for each population: **persistence-selected parents**
  and **uniformly random parents**. Same initial G0 genotypes, genome mutation
  operator, number of births, environments, observation horizons, and
  total cognitive accounting; only the parent-selection rule changes.
- At each generation and in each arm, each genotype receives **two new lives
  in each of the three ecological families** (`stable`, `depletion`, `pulse`),
  six 400-step lives per genotype. A genotype's fitness is the number of
  censored survivors (0..6), then the sum of lived steps, then a deterministic
  seed tie-break. No world fact enters the genome.
- Each generation gets new worlds from the `selection` cohort only.
  All competing genotypes in both arms see the same world keys within
  a given population and generation. Different generations and independent
  populations have disjoint world keys. The 72 required world keys fit the
  selection range 0..399; index mapping is
  `index = 18*population + 6*generation + 2*family_index + repeat`.
  `life_seed` is derived deterministically from (population, generation,
  family, repeat) and reused as a common random number for arm comparisons.
  World keys and life seeds are published before selection.
- For each G1/G2 birth, a selected-arm parent is sampled from G0/G1
  genotypes with probability proportional to the predeclared rank score
  (rank 1: 6, rank 2: 5, ... rank 6: 1); the random-parent control samples
  uniformly from its own prior population. **No crossover**. Only
  `genome.mutate(parent_genome, mutation_seed, scale=0.1)`.
  Mutation seeds depend on (population, generation, offspring slot, arm)
  and are independent of measured outcomes. Each newborn begins with no
  episodic memory, map, inventory or body state.
- Keep a complete per-life evidence digest, world fingerprint, genome digest,
  world key, selection rule, death cause/censoring flag, paid cognition and
  inactive steps. Selection is **only** from terminal state and lived steps.
  A censored life means alive at horizon, never a death.
- G2 final genomes become **frozen** before any validation-world exposure.
  Prospective validation evaluation, if approved, uses disjoint
  `validation` worlds 30000-30199 and cannot change the frozen candidates.
  The P4 reserve 1200000-1200199 remains locked.

## Analysis plan and controls

Primary descriptive effect: per-independent-population difference of
survivor fractions between selected and random-parent arms on the G2
validation worlds. Both arms receive equal world/life-seed budgets. Treat
independent populations (n=4), **not** 6 x 3 x 2 x 4 offspring lives, as
independent units. Report all four paired differences, range, and mean with
uncertainty; a tiny pilot cannot establish population-level generality.

Secondary: within-selection trajectory of mean persistence by generation,
per-family effects, motor/cognitive energy and vigilance, physical inactivity,
survival-time distribution, number of newborn genotypes still viable, and
per-population mutation count. A deaths-only analysis is invalid; censored
survivors must be stated as censored.

Explicit null/adverse outcomes and unequal paid work invalidate claims of
superiority. The reference searcher is a heuristic, and the omniscient oracle
is a success-only feasibility witness. Neither is an optimum ceiling.
The fixed-cost probe tariff from P2 must be frozen from DEVELOPMENT evidence,
never recomputed using selection or validation. A probe with a mismatched
decision or post-action debit is **not** a matched-cost control. Where
fitness differences accompany cost differences, report both rather than
attributing them to improved cognition.

## Budget and stopping

Planned selection effort per arm: 4 populations x 3 generations x 6 genomes
x 3 families x 2 lives x 400 steps = 172800 maximum simulated ticks.
Both arms: **345600** maximum selection ticks (excluding prospective
validation). Stop an individual's life on death; do not complete its horizon
with invented survival, recover vitality, re-run a bad outcome or replace it.
Fail closed on invalid charges, inconsistent world/source hashes, any
cross-cohort exposure, missing evidence, or accidental inheritance of
non-genetic state.

## Launch gate (intentionally NOT satisfied by this document)

Before a pilot run: approve the exact source SHA and independently verify
P2 cost coverage and ecological generator behavior. Lock generation, mutation
seed, control randomization, validation counts and acceptance tests.
The present document freezes **proposed numbers only**, it is neither a
scientific preregistration accepted by an operator nor permission to execute
the selection or validation cohorts.
