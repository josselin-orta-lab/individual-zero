# I3 active surface

This is the short operational map for developers and agents. It does not replace
scientific evidence or ADRs. The machine-readable authority is
[`../ACTIVE_SURFACE.json`](../ACTIVE_SURFACE.json).

## Current state

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1, replay gate.
- **Canonical Stage-2.1 status:** `CORRECTED_FALSIFIER_PENDING`.
- **ADR-0017:** world-opening moratorium remains active.
- **I3:** proposal only, unregistered.

The next scientific action is deliberately narrow: execute the corrected R0-R4
software falsifier once. It opens no World and no life.

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
- `lab/stage2_replay_gate_development_pilot.py`
- `tests/i3/test_stage2_execution_pipeline.py`

The development pilot runner exists for reproducibility and future use, but
ADR-0017 currently forbids a new lived Stage-2 panel.

## Compatibility-only Stage 1

Several Stage-1 lab modules remain under `src/i3/lab/` because retained tests,
runtime compatibility paths or ADR-0017 regression tooling still import them.
They are listed in `ACTIVE_SURFACE.json`.

Their presence does **not** mean Stage 1 is open. Do not extend them into a new
candidate or use them as the current scientific handoff.

Historical Stage-1 scientific runners and tests already moved to
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
- registers `p13_replay_gate_v1` in the runtime;
- changes the frozen replay-gate formula or R0-R4 rules after seeing supplied
  68/69;
- imports Stage-1 lab helpers into active Stage-2 science;
- creates another Stage-1 candidate;
- adds a second Stage-2.1 architecture instead of accepting a negative verdict.

The purpose of this map is not to erase history. It is to stop history from
pretending to be the present.
