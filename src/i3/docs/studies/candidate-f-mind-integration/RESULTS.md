# Stage 1 Candidate F Mind integration: result

**Verdict: `CANDIDATE_F_MIND_INTEGRATION_PASS`.**

Protocol: [STAGE1_CANDIDATE_F_MIND_INTEGRATION.md](../../STAGE1_CANDIDATE_F_MIND_INTEGRATION.md).

Exact checked head: `9164cf5d1e713ba17e9958bc5f44f3d03ba1d6d2`.
CI run: `42394243389`.

## Frozen integration result

Across all 486 cases:

- maximum integrated-vs-frozen-F value error: **0.0**;
- Candidate E/F direct projection cost:
  **16 / 86.61111111111111 / 112**;
- default simulation mode: **reference**;
- Candidate F projection mode: **event_local_quadratic4**;
- invalid Candidate-F/projection pair fails before simulated scoring work.

The integrated path therefore reproduces the frozen #1120 laboratory candidate
exactly.

## Implementation boundary

`Mind` now exposes:

- `simulation_mode="reference"` by default;
- `simulation_mode="candidate_f"` as explicit opt-in.

Candidate F requires `projection_accounting="event_local_quadratic4"`.

The reference path remains the existing ordinary-float simulation. Candidate F
keeps one Decimal body through explicit plan transitions and the shared
Candidate-E sparse bootstrap.

The sparse bootstrap implementation is shared rather than duplicated, so
direct Candidate E and integrated Candidate F cannot silently drift apart.

Observer first-forecast diagnostics remain available in Candidate F mode.

## Decision

The next slice may freeze dynamic forecast-cost accounting for integrated
Candidate F.

Omega is still unauthorized until that cost contract passes.

No reference adoption or ADR-0015 gate follows from this integration.

## Verification

Run `42394243389`:

- Python 3.11 PASS;
- Python 3.12 PASS;
- **670 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No World, life or scientific allocation was opened.
