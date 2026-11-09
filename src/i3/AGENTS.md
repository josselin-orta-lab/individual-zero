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
- ADR-0017 has been **owner-lifted for exact Stage-2.1 transport `dcada9e2…f1`**, limited to frozen DEVELOPMENT 80/81.

The corrected R0-R4 falsifier has executed exactly once and passed. Do not
rerun it.

**Exact transport owner-lifted:** hardened G/R engineering rehearsals passed
36/36 in Python 3.11 and 3.12, fingerprint `dcada9e2…f1`
([custody](docs/studies/stage2-replay-gate-development-80-81/HARDENED_REHEARSAL.md)).
The owner has expressly authorized the two custody equivalences and the lift
is recorded in `docs/STATUS.md`. Never fabricate a new owner decision,
broaden an existing one, or change the source-locked transport. Only frozen
DEVELOPMENT 80/81 may open next; other Worlds require separate authority.

**Governance now accepted:** [ADR-0019](../../docs/decisions/ADR-0019-i3-exact-transport-rehearsal-before-lift.md)
authorized the exact pre-lift transport solely for the engineering cohort.
Now that the owner lift is recorded, the frozen DEVELOPMENT 80/81 pilot may
use that same G/R path, runner and cognition; there is no clone or post-hoc
transport modification.

## Hard boundaries

Do not:

- create Candidate-K or any other Stage-1 continuation;
- reopen Candidate-J or change its closed J0 verdict;
- expose `p13_replay_gate_v1` to any scientific cohort before the explicit
  ADR-0017 lift; pre-lift engineering-only dispatch is allowed under ADR-0019
  only if scientific admission fails closed;
- open a fresh World outside the frozen and owner-lifted DEVELOPMENT 80/81 pilot;
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
- `runtime/admission.py`, `lab/stage2_admission.py`, `lab/stage2_panel.py`
  (exact Stage-2.1 transport; engineering-only admission, fail closed)
The supplied 68/69 runner is closed and archived at
`archive/stage2/development_68_69.py`; it is **not** active engineering and
must not be executed again.

The full classification is authoritative in `ACTIVE_SURFACE.json`.
Stage-1 candidate modules under `archive/stage1/` are compatibility and
regression support only, never a Stage-2 scientific entrypoint.

## Evidence discipline

Keep adverse, null and engineering-failure outcomes. Never tune on exposed
Worlds or reinterpret an engineering defect as an organism result.

Historical evidence stays at stable `docs/studies/` paths. Older executable
Stage-1 material is archived under `archive/i3/stage1-2026-11-09/`.

If current work begins to require extensive reading or modification of
Stage-1 machinery, treat that as a drift alarm and justify the dependency
before proceeding.

## Execution custody

ADR-0017 remains authoritative on two-phase generation and reduction,
sealing all originals, no retry after generation failure, and blind reduction
repair without outcome inspection. The owner lift in `docs/STATUS.md` applies
to only one prospective DEVELOPMENT 80/81 pilot, not a general scientific GO.

Green software tests are never a scientific GO.
