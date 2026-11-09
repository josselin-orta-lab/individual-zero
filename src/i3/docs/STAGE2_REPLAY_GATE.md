# Stage 2.1: replay gate — replay only when it is worth its price in D

Issue #1062. Baseline: `350ee52` (#1211). Launch context:
[STAGE2_LAUNCH.md](STAGE2_LAUNCH.md).

**FROZEN BY OWNER DECISION ON MERGE, BEFORE ANY IMPLEMENTATION COMMIT.**
Software first. No lived execution while the ADR-0017 moratorium is active.

## Question

Can P1.3 decide, from its own experience only, which sleep replays are worth
their cost in D, and so pay for far less replay without losing the decisions
replay would have changed?

**Lived hypothesis.** Replacing P1.3's fixed replay budget by a D-priced gate
lowers paid cognition per lived step without lowering survival, because learned
residual values rarely change decisions (P5a).

## One targeted change

Candidate `p13_replay_gate_v1` is P1.3, including its curiosity and prudence,
with one change: during a sleep step, each replay runs only if it passes the
gate below. Decisions, Competition, Action Control, the base learning update,
the effects model and P1.3's priority order by |TD error| are unchanged.

## Mechanism

1. **Decision-relevance audit**, each decision, paid 1 cycle.
    - Each option's score splits into a projection part and a learned-residual
      part `r_i = mean_k (1 − γ_k) · disc_k · residual_k(φ_i)`.
    - The decision is *residual-relevant* when the strict top with residuals
      differs from the strict top of `score_i − r_i`, with addends kept.
    - The individual keeps `r̂ = (n_relevant + 1) / (n_decisions + 2)`, and
      `m̂`, the mean margin by which the with-residual top beats the
      without-residual top over relevant decisions (0 before any).
    - The audit is observation of the individual's own scores. It never changes
      the chosen option.
2. **Horizon of use.** `H = (decisions + 1) / (sleep steps + 1)`, the personal
   mean number of decisions between sleeps.
3. **Gain.** The batch is worth `G = r̂ · m̂ · H` in score units. Memory `i` of
   the eligible batch (P1.3's priority order, at most P1.3's limit) is credited
   `g_i = G · |δ_i| / Σ_j |δ_j|`.
4. **Cost in D.** Per replay, `c = V_sleep(body) − V_sleep(body − w)`.
    - `w` is the energy and vigilance of one replay under body laws v2:
      16 simulated steps plus 1 replay unit.
    - `V_sleep` is P1.3's ordinary value of the plan `[("dormir",)]`.
    - It costs two paid simulations per sleep step.
5. **Gate.** Replay memories in priority order while `g_i > c`, and stop at the
   first failure. The limits on reserves and memories are unchanged. If the gate
   itself cannot be funded, no replay runs: it fails closed, never free.

Base TD learning still runs every step. Residuals therefore become nonzero and
can become relevant, so the gate is not circular: it stays shut only while
learned values have never mattered.

## Controls (plan requirements)

- **FIXED:** P1.3 unchanged, the reference budget.
- **ZERO-PERCEIVED-COST:** the same gate with `c = 0` in the comparison only.
  Every audit, gate computation and replay is still physically paid.
  Physically waived charges are not used; that would be a non-admissible
  diagnostic economy.
- **RANDOM-EQUAL-MEAN:** each sleep step replays the top-priority `k` memories,
  with `k` drawn from a dedicated life-seeded stream. Its mean equals the
  gate's mean replays per sleep step, measured in the development pilot and
  never in validation. The arm pays the same audit cost.

## Software mechanism falsifier (now, no World)

**Fixtures.** Sleep-step bodies from the #1146 grid with energy and vigilance
at 20, 40, 60 or 80, a 16-memory buffer, and three declared personal
histories:

- **S0, irrelevant values:** 50 decisions, 0 relevant;
- **S1, relevant values:** 50 decisions, 25 relevant, `m̂ = 0.05`, `H = 10`;
- **S2:** S1 across the energy and vigilance levels.

**Rules.**

- **R0 integrity, defect stop.** Every audit and gate computation is paid. No
  replay runs unpaid. No oracle or World is read. Results are invariant under
  token renaming. The audit leaves decisions identical to unmodified P1.3 on
  the same states.
- **R1 identity, defect stop.** With the gate forced open, decisions, replays
  and values equal FIXED exactly.
- **R2 discrimination, the question.** S0 gives 0 replays in every state. S1
  gives at least one replay in every state with energy and vigilance ≥ 60.
- **R3 cost sensitivity.** In S2, the replay count does not increase as energy
  and vigilance fall, in ≥ 90% of ordered pairs.
- **R4 bounded metareasoning, defect stop.** Gate overhead is at most two
  simulations plus one cycle per sleep step, and the audit at most one cycle
  per decision.

**Verdicts:** `REPLAY_GATE_DEFECT` (R0, R1 or R4 fails),
`REPLAY_GATE_NO_CAPACITY` (R2 or R3 fails), `REPLAY_GATE_CAPACITY_SHOWN`.

## Lived path (after the ADR-0017 lift only)

1. **Development pilot.** Fresh, collision-searched indices with a passed sealed
   rehearsal. Arms FIXED, GATE and ZERO-PERCEIVED-COST on the same genomes.
   Continuation is engineering-only. The pilot measures the gate's mean replays
   per sleep step, which then sets RANDOM-EQUAL-MEAN.
2. **Stage-2.1 gate.** ADR-0015 selection over at least eight populations, on
   validation indices ≥ 120 never opened. Arms FIXED and GATE, plus both
   controls.
    - **Primary:**
        - paid cognition per lived step: GATE < FIXED;
        - survival: GATE non-inferior to FIXED;
        - inactive-step fraction: GATE non-inferior to FIXED.
    - Margins are frozen before exposure.
    - **Secondary:** sleep fraction, replays per sleep, `r̂` trajectories,
      selected genes.
    - **Reading:**
        - GATE beats RANDOM: the targeting matters;
        - GATE ≈ RANDOM: only the amount matters;
        - GATE ≈ ZERO-PERCEIVED-COST: cost-awareness is inert.

## Declared expectations

- R2 and R3 hold.
- In lives, the gate removes most replay (P5a), saving roughly 0.1 energy and
  0.1 vigilance per lived step.
- Survival is non-inferior.
- RANDOM ≈ GATE, because replay was inert in P5a.

## Known limits

- P5a measured replay retention, not replay cost.
- `G` is a personal, paid heuristic bound, not an exact value of computation.
- `c` uses P1.3's cheap projector, which is adequate on the probed states
  (STAGE2_LAUNCH, measurement 3).

## Implementation scope once approved

- `modules/p13_replay_gate_mind.py`, opt-in and unregistered.
- `lab/stage2_replay_gate_falsifier.py`, with tests.
- Results in `docs/studies/stage2-replay-gate-software/`.

Runtime support for lived arms comes only after software capacity and the
ADR-0017 lift. A non-capacity verdict is recorded and Stage 2 moves to slice
2.2. There is no rescue.

## Governance clarification accepted 9 November 2026 (ADR-0019)

The frozen software criteria and lived gate above are unchanged. The sentence
about runtime support after the ADR-0017 lift governs **scientific lived-arm
authorization**, not preparatory engineering-cohort transport code. The exact
candidate dispatch and same G/R path may be implemented and rehearsed before
lift only behind a fail-closed engineering-cohort admission gate. An explicit
owner lift in STATUS.md is still required before any development/selection/
validation/reserve World opens. This clarification is not a new scientific
mechanism, test or evidence.
