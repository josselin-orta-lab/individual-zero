# I3 documentation entrypoint

I3 is an independent research proposal. It is not a registered active engine;
I1 remains active.

For current work, do not browse this directory chronologically. Use the small
operational surface below.

## Current

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1 replay gate.
- **Canonical status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** owner-lifted for exact transport `dcada9e2…f1` and frozen DEVELOPMENT 80/81 only.
- **Next action:** open the prospectively frozen DEVELOPMENT 80/81 panel
  once under the already-rehearsed exact G/R transport. Preserve immutable
  originals and no-retry rules. The two engineering rehearsals already passed.

Start here:

1. [STATUS.md](STATUS.md) — current research/governance state.
2. [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md) — what is active versus historical.
3. [STAGE2_REPLAY_GATE.md](STAGE2_REPLAY_GATE.md) — frozen Stage-2.1 protocol.
4. [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — stage ordering and dependencies.

[Code and dependency audit (9 November 2026)](I3_DEPENDENCY_AUDIT_2026-11-09.md)
records source integrity, archived dependencies and remaining custody boundaries.

## Stage 2.1 engineering custody

- [Hardened 36/36 sealed rehearsal](studies/stage2-replay-gate-development-80-81/HARDENED_REHEARSAL.md): structural PASS under ADR-0019, **not** an ADR-0017 lift.
- [Uploaded bundle integration audit](studies/stage2-replay-gate-development-80-81/INTEGRATION_AUDIT.md).

## Stage 2.1 evidence

- [Canonical software result](studies/stage2-replay-gate-software/RESULTS.md):
  `REPLAY_GATE_CAPACITY_SHOWN`, R0-R4 PASS, no World/life.
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

Stage-1 candidate implementations are under `src/i3/archive/stage1/`;
retained tests and historical opt-in runtime paths import this package. Its presence
does not reopen Stage 1. See [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

Translation originals are preserved under
`archive/i3/original-language-records-2026-11-09/`. See
[translation custody](TRANSLATION_CUSTODY.md). The closed Stage-1 candidate
implementations live under [archive/stage1](../archive/stage1/README.md),
with the [historical document catalogue](../archive/stage1/DOCUMENTS.md).
The [archived Stage-2.1 68/69 runner](../archive/stage2/README.md) is not a
valid prospective transport.

The pre-rationalization navigation ledgers are preserved under
`archive/i3/navigation-pre-stage2-rationalization-2026-11-09/`.

## Principle

An I3 stage is a scientific question, not a feature that must succeed. Failed
mechanisms remain failed, evidence remains immutable, and the next stage should
not inherit historical machinery unless the dependency is explicit and
scientifically necessary.
