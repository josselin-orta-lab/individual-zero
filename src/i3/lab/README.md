# I3 laboratory: current entrypoints

Read [ACTIVE_SURFACE.md](../docs/ACTIVE_SURFACE.md) before choosing a runner.
Candidate source from the closed Stage 1 now lives in the internal
[archive](../archive/stage1/README.md), not in this active laboratory directory.

## Current Stage 2.1 scientific code

- `stage2_replay_gate_falsifier.py`: the corrected R0-R4 software falsifier
  executed exactly once and returned `REPLAY_GATE_CAPACITY_SHOWN`.
  **Do not rerun it.**
- `../modules/p13_replay_gate_mind.py`: unadopted opt-in mechanism,
  not yet approved for scientific lived Worlds.

## ADR-0017 engineering and evidence custody

- `engineering_cohort.py`: permanently non-evidentiary cohort.
- `two_phase_panel.py`: generation followed by sealed reduction.
- `stage2_replay_gate_development_pilot.py`: historical/pending transport
  support, **not** permission to run a fresh development panel.

ADR-0017 remains active. Owner-accepted ADR-0019 allows implementation and
exact-SHA rehearsal only in the engineering cohort, with development,
selection, validation and reserve failing closed before an explicit owner lift.

Retained Stage-1 regression tests still live under `tests/i3/` and import
`i3.archive.stage1.*`. No active scientific module should import the archived
candidate laboratory helpers.
