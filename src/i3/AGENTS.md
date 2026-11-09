# I3 development-agent instructions

These instructions govern repository work, never the individual's mind.

## Read order

Before editing I3, read:

1. [current status](docs/STATUS.md);
2. [active surface](docs/ACTIVE_SURFACE.md) and
   [machine-readable manifest](ACTIVE_SURFACE.json);
3. the specific current protocol you are changing;
4. [development plan](docs/DEVELOPMENT_PLAN.md) only when stage ordering,
   dependencies or scientific scope are affected.

Do not reconstruct the current handoff from old Stage-1 documents.

## Current scientific state

- Reference: **P1.3 on funded v2**.
- I3 remains **unregistered**.
- Stage 1 is **closed negative** under ADR-0018.
- Stage 2.1 replay gate is the current stage.
- Canonical status: **`REPLAY_GATE_CAPACITY_SHOWN`**.
- ADR-0017's world-opening moratorium is **active**.

The corrected R0-R4 falsifier has executed exactly once and passed. Do not
rerun it.

**Governance now accepted:** [ADR-0019](../../docs/decisions/ADR-0019-i3-exact-transport-rehearsal-before-lift.md)
allows exact pre-lift Stage-2.1 transport code **for the engineering cohort
only**. Development, selection, validation and reserve must fail closed until
the separate owner lift is recorded. ADR-0017 remains active. Use the same G/R
path and candidate implementation in the sealed rehearsal, not a clone.

## Hard boundaries

Do not:

- create Candidate-K or any other Stage-1 continuation;
- reopen Candidate-J or change its closed J0 verdict;
- register `p13_replay_gate_v1` in `runtime/life.py`;
- open a fresh Stage-2 World while ADR-0017 remains active;
- change the frozen Stage-2.1 replay-gate formula, controls, fixtures,
  thresholds or verdict table after the canonical software result;
- promote the supplied non-conforming replay-gate software result or 68/69
  pilot to canonical evidence;
- import Stage-1 laboratory helpers into active Stage-2 science.

The canonical software verdict is positive. Stage 2.1 therefore remains open
for its frozen lived path after a valid ADR-0017 lift. Do not jump to Stage 2.2
or create a second replay-gate architecture.

## Active source boundary

Current scientific files:

- `modules/p13_replay_gate_mind.py`
- `lab/stage2_replay_gate_falsifier.py`

Current engineering/custody files:

- `lab/engineering_cohort.py`
- `lab/two_phase_panel.py`
- `lab/stage2_replay_gate_development_pilot.py`

The full classification is authoritative in `ACTIVE_SURFACE.json`.
Stage-1 files still present under `lab/` are compatibility or regression
support unless explicitly classified otherwise.

## Evidence discipline

Keep adverse, null and engineering-failure outcomes. Never tune on exposed
Worlds or reinterpret an engineering defect as an organism result.

Historical evidence stays at stable `docs/studies/` paths. Older executable
Stage-1 material is archived under `archive/i3/stage1-2026-11-09/`.

If current work begins to require extensive reading or modification of
Stage-1 machinery, treat that as a drift alarm and justify the dependency
before proceeding.

## Execution custody

ADR-0017 remains the authority for lived panels. Software-only work and
engineering rehearsals remain allowed. A future lived panel requires the
recorded ADR-0017 lift conditions, including an explicit owner entry in
`docs/STATUS.md`.

Green software tests are never a scientific GO.
