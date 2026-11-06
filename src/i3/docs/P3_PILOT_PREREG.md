# I3 P3: prospective mutation-only lineage pilot, registered BEFORE selection run

**Study ID:** `i3-p3-mutation-pilot-v1`.
**Status:** PRE-EXECUTION PROTOCOL. This document is intentionally committed
before any P3 selection or validation cohort is opened.
**Exact implementation Git commit:** `52476fec3f39a7fd70bf611877b01d9c13d26009`.
**Frozen schedule SHA-256:** `230cd653f0a8e580682b351fa3474b9f4dbd9f3e98e7eec1fa61361c0e7289db`.
**Source:** `src/i3/lab/p3_pilot.py`, `src/i3/lab/p3_schedule.py`,
`src/i3/lab/p2_ecologies.py`, I3 runtime and genome from the pinned commit.
**Scientific scope:** engineering pilot for possible selection of generic
dispositions. NOT a GO for adaptive intelligence, learning or I3 activation.

## Question and hypothesis

Given a finite model of energy, food, water, integrity and vigilance,
does parent selection by **individual lifetime persistence** produce different
future population outcomes than selecting parents uniformly at random?
The designed control must have the same starting physical opportunities,
charged work rates, number of genotypes, world exposure and mutation
opportunities. Different *realized* cognitive work is an outcome, not a
confound to be forcibly matched. No oracle or reference searcher is used
as a cost-matched survival ceiling.

This P3 pilot is intended to prove software and experimental feasibility,
document the selection trajectory, identify null/adverse outcomes and freeze
the final G2 genotypes before a genuinely independent P4 evaluation.
**P3 selection fitness is not P4 held-out evidence.**

## Locked treatment and exposure

Two arms within each of four independent population IDs `0,1,2,3`:
`selected` parents weighted by within-population rank (weights 6,5,4,3,2,1),
and `random_parent` uniform independent parent selection. There are six
individual genomes per arm per population and three generations G0, G1, G2.
G0 genomes are **identical across arms** within each population.
No crossover, no self-modifying laws, no inheritance of an individual's
memory, map, inventory, home location or body state. Every G1 and G2
genome is a fresh mutation of the selected parent using
`genome.mutate(..., scale=0.1)` with predeclared parent/offspring RNG seeds.

Every genotype is born fresh **twice in each of three ecological families**
(`stable`, `depletion`, `pulse`), with a fixed 400-step life horizon.
Both arms and all genotypes in the same population and generation share
the same six physical world keys and life seeds. Distinct generations and
independent populations have disjoint world keys.

Selection-world index (0–71):
`18*population + 6*generation + 2*family_index + repeat`,
family order (stable, depletion, pulse), repeat 0/1. World seed is
`10000 + index`, life seed is `60000 + index`. G0 genome seed:
`100000 + 6*population + slot`. Mutational and parental random streams
are fixed in the source/schedule listed above.

**Total planned exposure:** 4 populations x 2 arms x 3 generations x
6 genomes x 3 families x 2 lives = **864 lives**.
Maximum 864 x 400 = **345600 observed physical steps**. Death ends a
life early; survivors at 400 steps are **censored alive**, never
classified as dead. No failed or adverse life is replaced or re-run
for optimization.

## Selection rule and data

The sole parent-selection fitness is the number of censored survivors
among six fresh lives (0..6), then the total lived steps, then
deterministic increasing genome slot as a tie break. Do not select using
model CPU time, hidden-world oracle, historical G2 outcomes, individual
memories, probe survival, or validation/reserve conditions.

For every life record: population/generation/arm/slot/family, initial
world fingerprint, life seed, source digest, genome digest, full manifest
ID, chained evidence hash, survived/censored vs dead with reason, lived
steps, paid cognitive energy/vigilance, inactive steps, learning updates,
and replays. The two arms share initial physical opportunities but
their realized paid work can diverge. No postmortem cognition or
unpaid modeled work is permitted.

## Before looking at results: stopping and interpretation

A valid *technical* P3 completion requires:
1. Exact source commit and schedule digest locked by the runner before
   any selection-world instantiation, and same protocol label.
2. Exactly 864 complete life records with terminal status, physical
   starting conditions, source and world fingerprints. The runtime must
   reject discrepancies and fail closed.
3. Exactly the predeclared 72 distinct selection world keys,
   no validation or P4-reserve world opened, and no cross-population
   selection leakage.
4. Mutation-only births without inherited lived state.
5. All modeled cognitive work actually paid under v2 body physics;
   every invalid execution fails as an engineering fault, not a death.
6. Both arms same world/life seed exposure, births and resource laws.
   Record paid-work differences, including inactivity, rather than
   asserting identical expenditure.

Primary **descriptive** P3 trajectory: per population, the difference
between selected and random-parent survival fractions in G0, G1 and G2
on **selection** worlds. Report each of the four population-level
differences, mean, sign/direction and adverse outcomes. The initial G0
arms must have exactly equal genomes and deterministic behavior.
Populations (n=4), **not** thousands of correlated lives, are the
independent units. No automatic scientific GO is triggered by any
survival difference, even a favorable one. Changes in measured
energy/vigilance or in the rate of inactivity require separate
interpretation.

Secondary: per-family survival/death, censoring, living time, physical
inactivity and paid cognition, as well as parent identifiers and mutation
provenance. Report unexpected zero variation, lineage collapse and
negative results transparently.

## Validation and reserve (NOT part of this execution)

24 prospective **validation** world keys are published in the same
schedule, but never instantiated by P3. Final G2 genomes will be
frozen with SHA digests before any P4 validation exposure.
P4 reserve `1200000–1200199` remains inaccessible. An independent
prospective protocol and explicit launch are required for P4.

Historical P1/P1.1/P1.2/G2e sources, reserved evidence and I1 active
registration remain unchanged. I3 is still an unregistered proposal.

## Reproducibility and run custody

This preregistration must be **merged into main before triggering** the
one-shot P3 experiment. The execution workflow must use the **older pinned
implementation commit**, NOT the preregistration commit, so a documentation
edit cannot silently alter the executable source. The exact environment
variables required by the runner are:

`I3_P3_SOURCE_SHA=52476fec3f39a7fd70bf611877b01d9c13d26009`
`I3_P3_SCHEDULE_SHA=230cd653f0a8e580682b351fa3474b9f4dbd9f3e98e7eec1fa61361c0e7289db`
`I3_P3_APPROVED_PROTOCOL=i3-p3-mutation-pilot-v1`

The output file and its digest must be saved as immutable GitHub Actions
artifact; the full selection results must never feed back into P3
selection. A failure is archived and classified as `ENGINEERING_INVALID`,
not manipulated into biological failure or automatically retried with
different parameters. Technical bug repairs require an explicit
amendment **before** re-execution, with the original failure preserved.
