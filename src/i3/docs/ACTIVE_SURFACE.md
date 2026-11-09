# I3 active surface

This is the short operational map for developers and agents. It does not replace
scientific evidence or ADRs. See the
[code/dependency audit](I3_DEPENDENCY_AUDIT_2026-11-09.md) for archival
rationale, checked references and deliberate compatibility boundaries. The machine-readable authority is
[`../ACTIVE_SURFACE.json`](../ACTIVE_SURFACE.json).

## Current state

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1, replay gate.
- **Canonical Stage-2.1 status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** **owner-lifted on 9 November 2026** for fingerprint `dcada9e2…f1` and the frozen DEVELOPMENT 80/81 pilot only.
- **I3:** proposal only, unregistered.

The corrected R0-R4 software falsifier executed exactly once and passed.
The hardened transport passed 36/36 G/R rehearsals on Python 3.11 and 3.12
with the **same exact content fingerprint** `dcada9e2…f1`, verified after
merging PR #1220. The owner lift is recorded in [STATUS.md](STATUS.md).
**Only the previously frozen DEVELOPMENT 80/81 scientific pilot may open
next.** All validation, selection, reserve, unrelated worlds and confirmatory
gates remain closed pending their own prospective plans.

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
- `runtime/admission.py` (World-bound admission tickets)
- `lab/stage2_admission.py` (canonical owner-lift check and full-WorldSpec ticket admission)
- `lab/stage2_panel.py` (one parameterized runner for rehearsal and post-lift pilot)
- `tests/i3/test_stage2_exact_transport.py`
- `docs/studies/stage2-replay-gate-development-80-81/` (frozen plan, sealed rehearsal PASS)

The supplied 68/69 pilot runner is **archived**, not an active transport:
`archive/stage2/development_68_69.py`. Its historical observations cannot
be reused as prospective evidence. The exact transport is now owner-lifted only for the frozen DEVELOPMENT
80/81 pilot. This does not retroactively legitimize the supplied 68/69 run.

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

- opens a World outside the owner-authorized frozen DEVELOPMENT 80/81 plan;
- dispatches replay-gate cognition without a matching canonical owner lift,
  exact transport fingerprint and full-WorldSpec-bound ticket;
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
