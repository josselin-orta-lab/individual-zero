# I3 laboratory surface

Use [../docs/ACTIVE_SURFACE.md](../docs/ACTIVE_SURFACE.md) before choosing a
laboratory entrypoint.

## Current Stage 2

Scientific:

- `stage2_replay_gate_falsifier.py` — next canonical software execution.

Engineering / custody:

- `engineering_cohort.py`
- `two_phase_panel.py`
- `stage2_replay_gate_development_pilot.py`

The pilot runner is reproducibility/infrastructure code. ADR-0017 currently
forbids a new lived Stage-2 panel.

## Stage 1 names still present here

Files beginning with `stage1_` may remain because retained compatibility tests
or engineering regressions import them. They are **compatibility-only** unless
`ACTIVE_SURFACE.json` explicitly says otherwise.

Do not infer scientific priority from a filename existing in this directory.
The current priority is defined by `ACTIVE_SURFACE.json`, `STATUS.md`, and
the development plan.
