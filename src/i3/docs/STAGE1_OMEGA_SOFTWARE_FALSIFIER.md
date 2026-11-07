# Stage 1 — ω (innate expectation toward the unknown): software falsifier

**Owner decision, 7 November 2026: option A of
[STAGE1_FIRST_CONTACT_DECISION.md](STAGE1_FIRST_CONTACT_DECISION.md).** A heritable
generic gene ω shifts the individual's expectation toward the unknown (hope or
pessimism), drawn symmetrically at birth and set only by lineage persistence.
This changes the definition of the individual; it is recorded here before code.

**Frozen before coding.** Software only: no World, no life, no study index.

## Two design choices made before coding

1. **Uniform, need-agnostic shift.** ω moves the mean of the existing personal
   RMS unsupported-effect prior (#1097) by `ω × s_c` on every channel `c`:
   branches become `(ω + 1)·s` and `(ω − 1)·s`, p = .5/.5. The spread `s` is
   unchanged; the mean is `ω·s`. With ω > 0 the individual expects unknown
   consequences to raise its reserves, with ω < 0 to deplete them, and ω = 0 is
   exactly today's prior.
    - The decision note proposed a shift along the current distress gradient.
      That would mean "the unknown relieves what I currently lack", a
      need-targeted hope close to the curiosity relevance term.
    - With the uniform shift, the current need enters only through the existing
      predicted-distress evaluation. This amends the note before implementation.
2. **Kernel parameter now, genome later.** Adding `omega` to the genome changes
   the schema and every generation-0 digest. Archived studies cite v3 digests.
   This slice passes ω explicitly to the kernels and leaves the genome and the
   live path untouched. The genome change gets its own versioned slice.

## Substrate

The #1100 one-future-opportunity water kernel, with the exact P1.3 explorer
semantics of #1101's source change (an empty continuation: stop and bootstrap
after the explorer prefix). #1101 was rejected as a *candidate* because water
information stayed sub-decisive. Its semantics are the reference-preserving
ones the owner required, so the source change is reused and the rejection
stands.

## Grid and arms

The #1101 grid: each of the five channels set to 20, 30, 40 or 50 (others 80)
× horizons 4, 6, 8, 12 = 80 states; #1101's `realistic_memory`, explorer prefix
and single empty continuation. Arms: ω ∈ {−1, −0.5, 0, 0.25, 0.5, 1}.

## Metrics per ω

States evaluated; TRIAL among the water-node best choices; TRIAL with strictly
positive trial information (epistemic); declined; states with strictly positive
`water_revelation_advantage` and its maximum; maximum trial information; best
and worst trial advantage; whether paid work equals the ω = 0 work state by
state.

## Rules (prospective)

- **R0 identity (defect stop).** ω = 0 must reproduce #1101: epistemic 0/80,
  declined 28/80, max information 0.000592902270, best trial advantage
  0.0695239461 (to 1e-9).
- **R1 cost (defect stop).** Paid work must be identical across ω for every
  state. ω changes beliefs, not computation.
- **R2 direction (reported).** TRIAL selections and positive-revelation counts
  should not decrease as ω rises, nor increase as ω falls below 0.
- **R3 capacity (the question).** Does some ω > 0 give a strictly positive water
  revelation advantage in states where ω = 0 gives none?
    - Yes: ω is capable of making pre-contact water seeking worth its predicted
      cost. That is a capacity, not a survival claim.
    - No: the gene cannot fix first contact through this kernel. Record it, and
      return to the decision note.
- **R4 post-contact independence (structural).** ω touches only the unsupported
  prior. Code paths using personal support (carried food, P1.3 live decisions)
  are unchanged; tested by identity.

## Not authorized here

Genome schema change, live integration, Competition change, any world or life,
any tuning of the grid, memory fixture or ω values after the first run.

## If R3 holds, next slices (each frozen before code)

1. Genome v4 with `omega` drawn last from a symmetric uniform [−1, 1], with a
   versioning plan that keeps v3 digests valid for archived evidence.
2. Live integration in the reference-preserving water-frontier path.
3. An ADR-0015 selection gate on prospectively frozen fresh worlds where ω
   evolves freely, with an ω := 0 ablation at equal genomes. This is a new
   campaign and will be consigned explicitly before any exposure.
