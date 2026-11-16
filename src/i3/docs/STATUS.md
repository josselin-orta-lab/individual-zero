# I3: current status and agent handoff

**Updated:** 16 November 2026. This is the **short current entrypoint**. The complete, byte-identical former 2,362-line status and its dated decisions are preserved in [STATUS_HISTORY_2026-11-16.md](STATUS_HISTORY_2026-11-16.md) (original Git blob `3d4f934904ed1c5e129279a672adb6b3a52aa0cd`). This page is a navigation summary, **not a scientific receipt**. Recheck live branch HEAD, artifacts and original protocols.

## Authority and current boundaries

| Question | Current source-backed answer |
| --- | --- |
| Registered active runtime | **I1**, from [registry](../../../config/engine-registry.json) |
| Architectural/development reference | **I3**, owner-selected by [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md), not registered as active |
| I3 owned implementation | Independent P1.3 `funded-v2` [active surface](ACTIVE_SURFACE.md), [machine manifest](../ACTIVE_SURFACE.json), [contract](../engine.json); no inherited live I1/I2 state |
| Stage1 | Negative closure, [ADR-0018](../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md); historical originals retained |
| Stage2.1 engineering | `REPLAY_GATE_CAPACITY_SHOWN`, **software capacity only** |
| Stage2 scientific | `NOT_ISSUED/HOLD_NO_VERDICT`, [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md); no Stage2.2/2.3 GO |
| Prospective laboratory governance | [ADR-0022](../../../docs/decisions/ADR-0022-i3-owner-authorizes-prospective-experiments-internal-evidence.md) allows **new internally witnessed, separately frozen** prospective research. It does **not** establish independent external custody, native production M11 or engine promotion |
| Earlier generation I2 | [Archived in place](../../../archive/i2/README.md) by ADR-0023; historical comparator, not a live runtime or default next-development target |

## Most recent source-locked scientific observations

- **Stage6-light `beta_u_eff`:** [single original run #43769581930](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43769581930) completed technically. Its primary population sign criterion was **negative: 9 positive, 7 negative of 16**, with threshold 13. `CLOSED_NO_RETRY`.
- **Stage7 inherited bodily persistence:** [single run #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125) on source `06cfcf9cc9414e0f139b39a42d05177ddb813782` completed **both sealed 3.11/3.12 engineering rehearsals**, uploaded its separate pre-exposure science plan, and completed the prospective science job. [Receipt artifact 14217357887](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125) reports `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`: **12 positive, 4 negative, 0 zero population G2 contrasts**. Preregistered success required **at least 13 of 16 strictly positive and an overall positive mean**; it did **not** pass. Separate original-science archive artifact 14218795289; [frozen protocol](studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md) and [dated execution handoff](studies/stage7-persistence/STAGE7_EXECUTION_LIVE_HANDOFF_2026-11-16.md). Do not convert a technical workflow PASS into a scientific positive or rerun the one-shot allocation.
- These two tests address **different estimands**. Failure of their prespecified criteria does not establish that all natural selection, learning or heritable adaptation is impossible. Cross-generation raw trends alone are not causal because Worlds differ.

## Current agent procedure (task-scoped)

1. Verify exact live HEAD, [registry](../../../config/engine-registry.json), [I3 engine contract](../engine.json) and [owned surface](ACTIVE_SURFACE.md).
2. Read only the **exact protocol, code, original evidence and affected tests** for the chosen question. Use [I3 agent rules](../AGENTS.md) and [test layout](../../../tests/TEST_LAYOUT.md). Historical status is not required for routine code navigation.
3. Identify an observable, falsifier, bounded cost and control. For *new prospective science*, freeze a new run-specific source/seed/index/method manifest before exposure and satisfy the protocol's engineering and sealing gate. An existing owner permission is not an unused one-shot transport.
4. Label results **SOFTWARE / INTERNAL_PROSPECTIVE / INDEPENDENTLY_ATTESTED / NOT_VERIFIED** accurately, including negative, null and terminal-life evidence. No fresh I2 developments; I2 sources and tests are pinned historical material.

For older experimental details, inspect [original I3 research handbook](README.md), [history](STATUS_HISTORY_2026-11-16.md), original [Stage2 E3 negative audit](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md), and protocol-specific studies. **This short page supersedes dated “current handoff” headers in the preserved history for routing purposes only; it does not rewrite their actual historical chronology.**
