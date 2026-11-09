# Stage 2.1 prospective DEVELOPMENT 80/81: single-exposure opening record

**Status at registration: FROZEN / NOT YET EXECUTED.**
Owner lift was recorded in the canonical I3 STATUS ledger on 9 November 2026,
merged as PR #1221 at Git SHA
`e53e35a351f1c57a8ef23b42dc6133d93717eb52`.
The owner explicitly accepted the two documented ADR-0017 custody equivalences.

## Source lock and preregistration

- Transport/content fingerprint:
  `dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1`.
- Frozen [machine plan](PLAN.json) SHA-256:
  `a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92`.
- The transport is the 42-file content-identified source, verified after merge.
  The Git SHA of the execution checkout will be recorded before exposure.
- Development indices **80 and 81**, never exposed earlier. Families:
  `stable`, `depletion`, `pulse`. Genome birth seeds 911/912;
  life-seed base 7,540,000; horizon 400.
- Arms: FIXED (`reference`), GATE (`p13_replay_gate_v1`),
  ZERO-PERCEIVED-COST (`p13_replay_gate_zero_perceived_cost_v1`).
  Same-genome, same-world blocking, 36 planned lives.
- Execution: Python 3.11, exact frozen `i3.lab.stage2_panel.execute`
  via the existing `i3.lab.two_phase_panel` generator, sealer and reducer.
- Engineering rehearsal: two full-size PASS runs, Python 3.11 and 3.12,
  36/36 G/R, zero invariant failures, identical transport fingerprint.

## One-shot scientific custody

A unique GitHub branch claim
`custody/i3-stage2-1-development-80-81-claimed` must be created
**before any scientific World is opened**. Its unique run ID commits
incontrovertibly record the exposure attempt. The workflow is triggered
only by the initial PR opening with `run_attempt == 1` and exact branch
name. No automatic or manual retry of 80/81 is permitted after a generation
failure, even if zero lives complete. A claim prevents a second exposure.

Phase G archives the original gzip for each completed life, writes the
MANIFEST and SHA-256, and never reduces, aggregates or checks outcomes
during generation. Only after G has fully sealed may phase R consume those
originals. If reduction fails, publish only structural exception custody;
no partial result, optional blind repair following ADR-0017, maximum two
cycles, never modify any original or run an additional life.

The workflow must upload the original archive even on a failed execution.
On full structural PASS it writes a machine summary and full immutable
originals to a dedicated evidence branch and links the GitHub Actions run.
Do not use engineering rehearsal outputs as scientific evidence.
Do not reuse closed 68/69 Worlds.

**Scientific meaning:** this is only the frozen DEVELOPMENT feasibility pilot,
not the Stage-2.1 confirmatory gate. Its prospective metric is the mean
GATE replays per sleep step that will parameterize RANDOM-EQUAL-MEAN later.
Survival, replay-cost outcomes and deaths are descriptive, and may not
authorize post-hoc changes or an early successful stop.
