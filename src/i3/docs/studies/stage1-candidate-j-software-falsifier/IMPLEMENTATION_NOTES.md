# Candidate-J software falsifier: implementation choices declared before execution

Protocol: [STAGE1_CANDIDATE_J.md](../../STAGE1_CANDIDATE_J.md), frozen by #1210.
Governance: ADR-0017 (no World) and ADR-0018 (last Stage-1 candidate).

**Written and committed before the single execution.** These notes fix the
details the protocol leaves to implementation. None changes a mechanism, arm,
fixture family, rule or threshold of the protocol.

## Code

- `modules/genome_candidate_j.py`: opt-in genome v5 = the exact v4 genes plus
  `kappa` in U(0.05, 0.20), drawn **last** from the same generation-0 stream,
  so every v4 gene equals the v4 genome of the same seed. The runtime schema
  stays v4; nothing is migrated.
- `modules/candidate_j_mind.py`: `CandidateJMind`, a P1.3 `Mind` subclass, not
  registered in `runtime/life.py`.
- `lab/stage1_candidate_j_software_falsifier.py`: fixtures, arms, J0–J4 and
  verdict. Tests: `tests/i3/test_candidate_j_mind.py`.

## Mechanism details

- **Never performed.** An action is unsupported until the individual has at
  least one personal observation of it, with any token. This is checked in the
  effects model's own records.
- **Branch effect.** For an unsupported action, the predicted step effect is
  the individual's own waiting effect plus `(ω ± 1) × κ × 100` on every channel
  (zero base if it has never waited). Every unsupported step of a plan takes the
  same branch sign. The plan value is the mean of the two branch values.
- **Imagined trial.** An explorer's decline value is `V(travel)`, the travel
  plan itself, exactly as the protocol writes `V(move)`. The trial value is the
  branch mean of `V(travel + one imagined trial step)`.
- **q.** `q = 1 − (1 − p)^n`, where `p` is the personal Laplace
  resource-presence rate (the same formula as P1.3 and the frontier-modality
  primitive) and `n` the number of unseen cells the explorer reveals. This is
  the probability that at least one newly seen cell holds a resource.
- **After contact.** The frontier-modality primitive (paid) splits water and
  token. Each modality uses the personal effect of its use action (`boire`, or
  `manger` at the action level) once that action has been performed, and the
  prior otherwise. Before any contact, the formula reduces exactly to the
  protocol's pre-contact formula and the primitive is not called.
- **Source trips.** Plans to remembered sources keep P1.3's presence
  weighting, `presence × V(plan) + (1 − presence) × V(travel)`.
- **No addend.** Curiosity, relevance and prudence are not computed. The
  witness records them as absent (`None`) and applied as zero.

## Fixtures

All fixtures use mind seed 211 and the midpoint genome v5, with `omega`,
`kappa` and `h_max` overridden. Personal effects are primed with the #1146
move, wait and sleep deltas.

- **Horizon.** The protocol's horizons 4, 6, 8 and 12 are realized through the
  `h_max` gene. The real `capacities` rule then applies: horizon equals `h_max`
  at vigilance ≥ 60 and is reduced below that. The realized horizon is
  reported.
- **P80.** The 20 #1146 bodies (base 80, one channel at 20, 30, 40 or 50) × 4
  horizons. Capture: water perceived here, one passable unseen neighbor, three
  edges, no inventory.
- **K80.** The same 80 states. Capture: no water here, same neighbors.
- **F108.** The 27 #1103 bodies × 4 horizons. Capture: `_cap(body, 2,
  "mystery")`, carried token, no passable neighbor.
- **Newborn** `(100, 80, 30, 80, 100)` and **satiated** `(80, 80, 80, 80, 80)`:
  midpoint `h_max`, K80 capture.

**Arms:** ω ∈ {−1, −0.5, 0, 0.25, 0.5, 1} × κ ∈ {0.05, 0.10, 0.20}.

**P1.3 anchor:** the v4 midpoint genome with the same `h_max`, `chunk_end`,
normal addends, the same seed, priming and captures.

## Rule details

- **Top option:** a strict raw winner, whose score exceeds every other scored
  option by more than 1e-12. An exact tie is not a top.
- **Deficit state:** the trial's channel is at 20, 30, 40 or 50, below the
  midpoint threshold θ = 60. That is water for P80 and K80, food for F108.
- **J0.** The canonical oracle is the #1155 high-precision method: per-step
  Decimal end-to-end simulation (`projection_end_to_end_numeric_oracle`) with
  255 one-step chunks. It is applied to the same Candidate-J valuation, same
  arms, same states (K80 and P80), and funded by a separate laboratory
  allowance, because it is an observer reference, not the individual's
  cognition.
    - Pass requires the maximum absolute option-score error to be ≤ 0.01, and
      the same strict top wherever the oracle's top-two gap exceeds 1e-3.
    - If `event_quadratic` fails, J0 is rerun with `event_local_quadratic4`,
      and J2–J4 then use the fallback.
- **J1.**
    - No addend in any witness.
    - Identical scores and work for F108 under token renaming
      (`mystery` → `enigme`).
    - The number of plan evaluations per state is identical across all 18
      arms.
    - Every decision is funded or stops on a paid funding error.
    - The module contains no snapshot, restore or rollback call.
- **J3.**
    - Capacity: some arm with ω > 0 makes `boire` the strict top in at least one
      water-deficit P80 state, and some arm with ω > 0 makes an explorer the
      strict top in at least one water-deficit K80 state.
    - Need-sensitivity: advantage = trial score − best other score, with the
      best explorer standing for the trial in K80. For each arm with ω > 0 and
      each `h_max`, the four water levels give six ordered pairs. The advantage
      must not increase from the lower to the higher water level
      (tolerance 1e-12) in ≥ 80% of pooled pairs, separately in P80 and K80.
- **J4.** Mean paid simulated steps per decision over all Candidate-J decisions
  (all fixtures and arms), divided by the P1.3 mean over the same states. The
  cost wall is a ratio above 2.5. Per-fixture ratios are reported.

## Disclosure

Before these notes, a development smoke check ran Candidate-J on six hand-built
states: water 20, 50 and 80, perceived or at a frontier, ω 0 and 0.5, κ 0.1.

It showed that an extra waiting step, which the first draft had added to the
explorer's decline plan, created a plan-length artifact. The implementation
was aligned to the protocol's `V(move)`.

No rule, threshold, arm or fixture was chosen or changed from that check.
