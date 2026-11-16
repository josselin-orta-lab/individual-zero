# I2: archived research generation (preserved in place)

**Decision: 16 November 2026, ADR-0023. Disposition: `ARCHIVED_IN_PLACE`.** I2 is no longer an ordinary development or experiment target. I1 remains the registered active engine; I3 remains the owner-selected development reference. I2 was **never registered** as a living engine and retains an independent, locally born SQLite research prototype, historical experimental code, software tests, results, including negative and null observations.

**No relocation or duplication was made.** The [archive manifest](../../config/archives/i2-20261116.json) pins the **original complete Git trees** at commit `9091387a24644865605520b4c42c3f997dce1e3d`: `src/i2` at `bd5d4f42832192f223531e0afdecb813e210ef05` (141 files) and `tests/i2` at `e0709f39dc96f820656bf8b3d7157b0f2a6b2948` (158 files). This keeps historic imports, source paths, CI references, study links and research citations resolvable. Git tree identity is checked by [the archival guard](../../tools/check_i2_archive.py), not just asserted in prose. The retained bytes are historical data, **not runtime authority**.

## Historical reading order

1. [I2 status at archive baseline](../../src/i2/docs/STATUS.md), [I2 evidence ledger](../../src/i2/docs/STATUS_HISTORY.md) and [research handbook](../../src/i2/docs/README.md)
2. [I2 contract](../../src/i2/engine.json), [native owner](../../src/i2/runtime/native_paid_cycle.py) and [historical tests](../../tests/i2/)
3. [Accepted archival decision](../../docs/decisions/ADR-0023-i2-archived-in-place-i3-context-focus.md) and [I3 current status](../../src/i3/docs/STATUS.md)

## Archive policy

- No new I2 architecture tuning, births, science cohorts or routine refactoring. Old studies are not restarted, deleted or reinterpreted.
- Freeze `src/i2/` and `tests/i2/` **byte for byte at the pinned Git tree identity**. A future correction or archival release needs a separately reviewed decision and explicit manifest/test updates; it is never automatic.
- This is a *Git-addressed historical archive*, not a physical copy in `archive/i2/source`. Copying hundreds of tracked files would bloat the repository while preserving neither additional scientific evidence nor more original Git objects.
- Keep all existing source-specific I2 results and research-program/dossier pins. Do not silently replace their cited SHA, paths, experiment cohorts or interpretation.
- The [I2 CI workflow](../../.github/workflows/i2-proposal-safety.yml) now runs **only source-pinned structural denial checks on ordinary PRs**; its complete original two-version historical suite is preserved behind a **manual, explicit archival audit confirmation**, never launched by i3 documentation maintenance. No green check reactivates I2 or creates scientific evidence.

This disposition concerns **repository and development priorities**, not the identity or experience of any born individual, and does not convert I2's original `proposal` engine contract into an activated engine.
