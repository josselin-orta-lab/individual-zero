# I3 historical workflow snapshot, 16 November 2026

The [original I3 proposal workflow](i3-proposal-checks-original-2026-11-16.yml) is retained **byte for byte** as Git blob `370f34867330bce828d5de03135bb4f801917641`. Its former path was `.github/workflows/i3-proposal-checks.yml` (2,324 lines; 111,686 bytes).

This copy lives under `archive/i3/workflows/`, **outside** GitHub's live `.github/workflows/` directory. It is historical executable source, not an approved repeat of any research allocation.

The following six historical jobs were already disabled with the literal gate `if: false`, and are now present **only in this snapshot**:

- `b1-original-custody`
- `stage2-three-arm-exploratory-once`
- `stage2-content-48-exploratory-once`
- `stage2-water-divergence-24-once`
- `stage2-realstate-fork-24-exploratory-once`
- `stage2-next-decision-24-exploratory-once`

The [live workflow](../../../.github/workflows/i3-proposal-checks.yml) retains its original PR/push filters, permissions, cancellation behavior and **all 22 other jobs byte-identically**. The source-pinned [static test](../../../tests/i3/test_workflow_archive.py) rejects archive tampering, changed historical triggers, modifications of surviving jobs and restored one-shot jobs.

No job in this archive may be copied back to a live workflow to get another scientific life. An entirely new study would need its own preregistration, exact source/seed allocation, authority, technical gates, original evidence and non-retry contract.

[Workflow review](../../../docs/engineering/I3_WORKFLOW_RATIONALIZATION_2026-11-16.md) · [Current I3 status](../../../src/i3/docs/STATUS.md) · [Stage7 fixed protocol](../../../src/i3/docs/studies/stage7-persistence/STAGE7_PERSISTENCE_PROTOCOL_2026-11-16.md). A successful software workflow does not change the published Stage6 or Stage7 scientific verdict.
