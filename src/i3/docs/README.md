# I3 documentation entrypoint

I3 is an independent research proposal. It is not a registered active engine;
I1 remains active.

For current work, do not browse this directory chronologically. Use the small
operational surface below.

## Current

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1 replay gate.
- **Canonical status:** `CORRECTED_FALSIFIER_PENDING`.
- **ADR-0017:** world-opening moratorium active.
- **Next scientific action:** execute the corrected software-only R0-R4
  falsifier once.

Start here:

1. [STATUS.md](STATUS.md) — current research/governance state.
2. [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md) — what is active versus historical.
3. [STAGE2_REPLAY_GATE.md](STAGE2_REPLAY_GATE.md) — frozen Stage-2.1 protocol.
4. [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — stage ordering and dependencies.

## Stage 2.1 evidence

- [Canonical software status](studies/stage2-replay-gate-software/RESULTS.md):
  corrected falsifier pending.
- [Supplied software result](studies/stage2-replay-gate-software/SUPPLIED_RESULTS.md):
  preserved custody evidence, not canonical because the supplied denominator
  diverged from the frozen protocol.
- [Supplied 68/69 result](studies/stage2-replay-gate-development-68-69/RESULTS.md):
  descriptive development evidence only.
- [Package custody](studies/stage2-replay-gate-development-68-69/PACKAGE_CUSTODY.md).

## Historical material

Stage-1 evidence remains under `studies/` at stable citation paths. Retired
Stage-1 scientific runners/tests are under
`archive/i3/stage1-2026-11-09/`.

Some Stage-1 source still exists under `src/i3/lab/` only because retained
compatibility tests or engineering regression tools import it. Its presence
does not reopen Stage 1. See [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

The pre-rationalization navigation ledgers are preserved under
`archive/i3/navigation-pre-stage2-rationalization-2026-11-09/`.

## Principle

An I3 stage is a scientific question, not a feature that must succeed. Failed
mechanisms remain failed, evidence remains immutable, and the next stage should
not inherit historical machinery unless the dependency is explicit and
scientifically necessary.
