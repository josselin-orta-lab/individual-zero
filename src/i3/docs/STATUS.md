# I3: current status and agent handoff

**Updated:** 17 November 2026. This is the **short current entrypoint**. The complete, byte-identical former 2,362-line status and its dated decisions are preserved in [STATUS_HISTORY_2026-11-16.md](STATUS_HISTORY_2026-11-16.md) (original Git blob `3d4f934904ed1c5e129279a672adb6b3a52aa0cd`). This page is a navigation summary, **not a scientific receipt**. Recheck live branch HEAD, artifacts and original protocols.

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

**E3 stop:** [source-locked report](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md): 0/2 legal motor changes; P1.3 retained, Stage2 `NOT_ISSUED`.

## Most recent source-locked scientific observations

- **Stage8-B, interaction F0 négative :** [cohorte source-figée #44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150) (32 populations, 23 040 vies) : Hotelling `p=0,6577705` pour seuil `<0,025`, **`STAGE8B_NO_INTERACTION_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**. [Audit original #44126032148](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44126032148) PASS : 23 040 gzip réhashés, 9 216 G2 relus, zéro naissance. [Résultat détaillé](studies/stage8-ecology-interaction/STAGE8B_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md). [Stage8-C](studies/stage8-parent-concentration/STAGE8C_CONTROL_DESIGN_2026-11-17.md) reste logiciel seulement.
- **Stage8-A mean persistence:** [run #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), 32 F0 groups, mean G2 **+14.4874**, lower Student 97.5% **+7.9933**, **23+/9−**; **`STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`**, closed/no-retry. [Source evidence](studies/stage8-mean-persistence/STAGE8A_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md); [independent 23,040-life audit PASS](studies/stage8-mean-persistence/STAGE8A_INDEPENDENT_READONLY_AUDIT_RESULT_2026-11-17.md). Stage7 negative unchanged.
- **Stage6-light `beta_u_eff`:** [single original run #43769581930](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43769581930) completed technically. Its primary population sign criterion was **negative: 9 positive, 7 negative of 16**, with threshold 13. `CLOSED_NO_RETRY`.
- **Stage7, héritabilité directionnelle négative :** [cohorte #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125), `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0` : **12+/4−** contre **13/16** requis ; deux répétitions techniques et archives scellées, `CLOSED_NO_RETRY`. [Protocole initial](studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md). Aucun changement rétroactif du critère.
- **Separate estimands:** Stage6 direction, Stage7 signs, Stage8-A mean, Stage8-B interaction. Neither genome mechanism nor out-of-F0 adaptation is demonstrated; unequal G0/G1/G2 Worlds prevent raw generational causal inference.

## Current agent procedure (task-scoped)

1. Verify exact live HEAD, [registry](../../../config/engine-registry.json), [I3 engine contract](../engine.json) and [owned surface](ACTIVE_SURFACE.md).
2. Read only the **exact protocol, code, original evidence and affected tests** for the chosen question. Use [I3 agent rules](../AGENTS.md) and [test layout](../../../tests/TEST_LAYOUT.md). Historical status is not required for routine code navigation.
3. Identify an observable, falsifier, bounded cost and control. For *new prospective science*, freeze a new run-specific source/seed/index/method manifest before exposure and satisfy the protocol's engineering and sealing gate. An existing owner permission is not an unused one-shot transport.
4. Label results **SOFTWARE / INTERNAL_PROSPECTIVE / INDEPENDENTLY_ATTESTED / NOT_VERIFIED** accurately, including negative, null and terminal-life evidence. No fresh I2 developments; I2 sources and tests are pinned historical material.

For older experimental details, inspect [original I3 research handbook](README.md), [history](STATUS_HISTORY_2026-11-16.md), original [Stage2 E3 negative audit](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md), and protocol-specific studies. **This short page supersedes dated “current handoff” headers in the preserved history for routing purposes only; it does not rewrite their actual historical chronology.**
