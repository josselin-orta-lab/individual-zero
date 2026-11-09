# I3 active surface

This is the short operational map for developers and agents. It does not replace
scientific evidence or ADRs. The machine-readable authority is
[`../ACTIVE_SURFACE.json`](../ACTIVE_SURFACE.json).

## Current state

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1, replay gate.
- **Canonical Stage-2.1 status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** world-opening moratorium remains active.
- **I3:** proposal only, unregistered.

The corrected R0-R4 software falsifier has executed once and passed. The next
work is to prepare a **fresh** source-locked Stage-2.1 development transport and
pass the ADR-0017 exact-SHA sealed engineering rehearsal. No **scientific** World may open until an explicit owner lift is recorded.
Owner-accepted ADR-0019 permits an engineering-cohort-only exact rehearsal
before that lift, with all scientific cohorts failing closed.

## Active scientific surface

Only these files define the current scientific intervention:

- `modules/p13_replay_gate_mind.py`
- `lab/stage2_replay_gate_falsifier.py`
- `docs/STAGE2_LAUNCH.md`
- `docs/STAGE2_REPLAY_GATE.md`
- `docs/studies/stage2-replay-gate-software/RESULTS.md`

Stage 2 must not import Stage-1 laboratory helpers. If it needs one, first ask
whether the concept is genuinely current or whether historical machinery is
leaking back into the design.

## Active engineering surface

These files support ADR-0017 execution custody and are not themselves evidence:

- `lab/engineering_cohort.py`
- `lab/two_phase_panel.py`
- `tests/i3/test_stage2_execution_pipeline.py`

The supplied 68/69 pilot runner is **archived**, not an active transport:
`archive/stage2/development_68_69.py`. Its historical observations cannot
be reused as prospective evidence. A fresh exact-SHA engineering transport
may be prepared under ADR-0019, but scientific cohorts remain closed.

## Compatibility-only Stage 1

Stage-1 candidate code is archived under `src/i3/archive/stage1/`
for retained compatibility tests and regression tooling.
They are listed in `ACTIVE_SURFACE.json`.

Their presence does **not** mean Stage 1 is open. Do not extend them into a new
candidate or use them as the current scientific handoff.

The [Stage-1 historical document catalogue](../archive/stage1/DOCUMENTS.md)
links to the frozen protocols and results at their unchanged evidence paths.
Older Stage-1 scientific runners and retired tests already moved to
`archive/i3/stage1-2026-11-09/`. Evidence under `docs/studies/` stays at its
stable paths for citation and custody.

## Read order

For current development, read only:

1. `docs/STATUS.md`
2. this file / `ACTIVE_SURFACE.json`
3. `docs/STAGE2_REPLAY_GATE.md`
4. the specific source and tests you will edit

Read `DEVELOPMENT_PLAN.md` when changing stage boundaries or ordering. Read
older Stage-1 documents only for a named historical question.

## Drift alarms

Stop and re-evaluate if a change does any of the following:

- opens a World while ADR-0017 is active;
- exposes `p13_replay_gate_v1` to a scientific World before the ADR-0017 owner
  lift, or permits engineering dispatch without a fail-closed cohort guard;
- changes the frozen replay-gate formula or R0-R4 rules after the canonical
  software verdict;
- treats the formally passing but flat S1 R3 fixture as proof of graded cost
  sensitivity;
- imports Stage-1 lab helpers into active Stage-2 science;
- creates another Stage-1 candidate;
- reuses supplied 68/69 as prospective evidence;
- jumps to Stage 2.2 while the frozen positive Stage-2.1 path is still open.

The purpose of this map is not to erase history. It is to stop history from
pretending to be the present.
