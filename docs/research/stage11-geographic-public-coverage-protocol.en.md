# I0-vNext Stage 11: public geographic exploration coverage protocol

**Class:** development-only software integration, not a scientific campaign, held-out world, Stage-9 Golden or INV-25 sign-off.

**Registration order:** this file states the measurement and comparison design before its first geographic-coverage CI result. It does not prescribe a scientific success threshold, calibrated P-48 parameter, or unobserved world fact.

## Normative basis

The English `docs/architecture/reference/en/mvp-specification-v1.2.1.md` prevails: section 14 and Stage 11 (§20.3) require intrinsic informational interest, autonomous exploration targets converted by Planning, ordinary Competition/Action Control, no noisy-TV cycle, observable northern exploration and measurable coverage. DC-11 forbids reading another producer's output within the same phase. INV-06 and INV-14 remain acceptance gates.

## Development hypothesis and fixed input

The previously deployed Stage-11 curiosity covers physically verified causal questions but has no autonomous geographic targets. Add an explicit opt-in local-frontier mode and test whether it increases the number of **different physically perceived positions** without inserting a destination into the agent, changing the world physics, modifying the frozen Equipment or bypassing vetoes.

Run exactly:

`python -m lab.stage11_geographic_probe`

or `run_public_geographic_coverage(steps=8)`.

Three independent software copies share the same public reference WorldPhysics, layout and Equipment version, initial position (2,2), and initial body `energy=50, food=60, water=60, integrity=100` (matching the reference Value & Needs setpoints):

1. Historical Stage 9, no autonomous geographic exploration.
2. I0-vNext Stage 11 with geographic mode **disabled**, isolating unrelated vNext changes.
3. I0-vNext Stage 11 with geographic mode **enabled**, `p48-geographic-development-v1`, novelty weight 0.7, maximum 1024 known sites, and at most one offered frontier target each cycle.

Run 8 consecutive world steps, without externally planted goals, synthetic observations, oracle labels, hidden state, seeded action scripts or live operator overrides. Numeric parameters are compatibility/development fixtures, NOT scientific calibrations.

## Mechanism and observation boundaries

- Only the single pre-step Perception capture and its adjacent passable, creature-free cells are used; the frozen prior geographical ledger is the other input. A canonical direction priority starts with **north**. No global map or world oracle is consulted.
- Exploration owns physically observed positions and visit counts. One real captured arrival may count as a new visit; repeated cycles at an unchanged position do not. The visited-site set is immutable to propositions, simulated rollouts and rejected actions. Exhausting the finite ledger must fail closed.
- Geographic targets are frozen before phase 1; Planning makes a single adjacent `se_deplacer` option and ordinary Competition evaluates `m_a` only for a current provenance-matched target. An unknown E-v1 transition remains explicitly `unavailable`, with no numerical prediction manufactured. The final Action Control veto remains mandatory.
- An exploration choice may occur while an active goal exists but carries `goal_ref=None` and does not claim goal progress. Old or forged target IDs, nonadjacent moves and visited places may not reuse P-48 interest.
- A step-ending move counts toward confirmed coverage only on the **next accessible Perception capture**; no phantom last-step arrival is credited.

## Measured outputs

- Distinct positions in the actual perceptual-capture journal for each of the three independent copies.
- Stage-11 geographical ledger of distinct visits, total visits, bounded newly offered targets, evaluated intrinsic options, applied geographical moves and northward moves.
- Number of frontier plans lacking a complete frozen Equipment numerical prediction. An unavailable prediction is neither a zero effect nor a failed physical action.
- Exact internally verified journal digests, replay equality on identical world and config, and a canonical digest of the public diagnostic row.
- Negative results, including zero moves or lower coverage, are retained as results of this software fixture. The same-Stage11 ablation is the primary diagnostic comparison; historical Stage 9 is a compatibility reference.

## Limits and future gates

Coverage over 8 world steps in a fixed public map says nothing about robustness, independent experimental significance, hidden-world generalization or long-horizon safe exploration. Next work will cover explicit obstacles, safety vetoes, degraded mode, more varied public layouts, percentage coverage against **accessible observed opportunities** (not hidden map), novelty habituation on repeated geographic patterns and global modulation activation/exit.

The existing public hydration diagnostic and its scientific classification are not modified. Stage 9 held-out remains **NO-GO**; no scientific verdict is emitted.
