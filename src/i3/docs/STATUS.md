# I3: current status and agent handoff

**Updated:** 20 November 2026. This is the **short current entrypoint**. The complete, byte-identical former 2,362-line status and its dated decisions are preserved in [STATUS_HISTORY_2026-11-16.md](STATUS_HISTORY_2026-11-16.md) (original Git blob `3d4f934904ed1c5e129279a672adb6b3a52aa0cd`). This page is a navigation summary, **not a scientific receipt**. Recheck live branch HEAD, artifacts and original protocols.

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

**Stage 2 post-E3 scientific stop checkpoint:** [source-locked report](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md): `E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN` (0/2 legal motor changes); P1.3 retained, Stage2 `NOT_ISSUED`.

## Most recent source-locked scientific observations

- **Stage8-E2 gamma123 causal, negative:** [science #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471) **64 512 cold-audited native lives** after [2 technical runs #44536464441](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441) (**129 024**); **64 F0 populations**, DID **−0.0907** steps, t63 **−0.0463**, IC bilatéral 97,5 % **[−4.589,+4.408]**, **31+/33−**. `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`. [Report, full evidence and 90-day artifact retention](../../../docs/research/studies/stage8e2-gamma-block/STAGE8E2_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-20.md). Not an absence/equivalence proof; Stage2 `NOT_ISSUED`.
- **Stage8-D:** [read-only genomic diversity](studies/stage8-parent-concentration/STAGE8D_POSTHOC_GENOMIC_DIVERSITY_RESULT_2026-11-19.md), 32 256 originals, r=−0.05955, no births.
- **Stage8-C, S−M positive:** [science #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), mean **+8.676**, lower one-sided 97.5 % **+1.468 >0**, **22+/10−** populations; [independent 32 256-original audit](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44406977082) PASS, [report](studies/stage8-parent-concentration/STAGE8C_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-19.md).
- **Stage8-B, interaction not shown:** [science #44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150), Hotelling **p=0.65777**, [cold audit](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44126032148) PASS; [report](studies/stage8-ecology-interaction/STAGE8B_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md).
- **Stage8-A, mean positive:** [science #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), **+14.4874**, lower 97.5 % **+7.9933**, **23+/9−**; [audit](studies/stage8-mean-persistence/STAGE8A_INDEPENDENT_READONLY_AUDIT_RESULT_2026-11-17.md).
- **Stage6-light:** [science #43769581930](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43769581930), negative sign criterion **9+/7− vs 13+/16**; closed.
- **Stage7:** [science #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125), negative strict **12+/4− vs 13+/16**, [report](studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md); closed.
- **Different questions remain separate:** Stage6 direction, Stage7 sign, Stage8-A mean, Stage8-B ecology, Stage8-C S−M, Stage8-E2 gamma123 difference-in-differences. No general cognition/AGI or out-of-F0 causal claim.

## Current agent procedure (task-scoped)

1. Verify exact live HEAD, [registry](../../../config/engine-registry.json), [I3 engine contract](../engine.json) and [owned surface](ACTIVE_SURFACE.md).
2. Read only the **exact protocol, code, original evidence and affected tests** for the chosen question. Use [I3 agent rules](../AGENTS.md) and [test layout](../../../tests/TEST_LAYOUT.md). Historical status is not required for routine code navigation.
3. Identify an observable, falsifier, bounded cost and control. For *new prospective science*, freeze a new run-specific source/seed/index/method manifest before exposure and satisfy the protocol's engineering and sealing gate. An existing owner permission is not an unused one-shot transport.
4. Label results **SOFTWARE / INTERNAL_PROSPECTIVE / INDEPENDENTLY_ATTESTED / NOT_VERIFIED** accurately, including negative, null and terminal-life evidence. No fresh I2 developments; I2 sources and tests are pinned historical material.

For older experimental details, inspect [original I3 research handbook](README.md), [history](STATUS_HISTORY_2026-11-16.md), original [Stage2 E3 negative audit](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md), and protocol-specific studies. **This short page supersedes dated “current handoff” headers in the preserved history for routing purposes only; it does not rewrite their actual historical chronology.**
