# ADR-0023: archive I2 research in place; shorten I3 agent context

**Date:** 16 November 2026. **Status:** ACCEPTED OWNER DIRECTION. **Scope:** repository research-generation priority, agent reading path and historical custody; **not** scientific promotion, runtime migration or a new study authorization. **Baseline:** `main` `9091387a24644865605520b4c42c3f997dce1e3d`.

## Context

I3 is already the owner-selected architectural/development reference (ADR-0020) while I1 is the registered active engine. I2 remains an unregistered proposal with source-owned native SQLite laboratory lives and preserved experimental findings. The owner now directs that I2 be archived and that the day-to-day I3 context be reduced. Moving I2 source/tests to a new path would break existing research citations, laboratory imports, tests, exact-source SHA records and generation boundaries. I3's `STATUS.md` has reached 252,350 Git bytes and embeds dated handoff entries alongside historical research records.

## Decision

1. **I2 archived in place.** The complete `src/i2/` and `tests/i2/` Git trees, along with key original blobs, are retained unchanged and pinned by `config/archives/i2-20261116.json`. `archive/i2/README.md` is the historical discovery portal. I2 is removed from the routine future development queue, not retroactively invalidated.
2. **Keep source and engine semantics unchanged.** The registered engine list stays I0/I1, `active_generation=I1`, `reference_generation=I3`. The original I2 `engine.json` remains a `proposal` contract with no registered birth. This decision is **not** an I2 activation/deactivation at runtime and not a claim of independent M11 custody.
3. **Fail-closed preservation.** The repository static archive guard compares current tree SHA values with the pinned originals. A proposed change to archived source/tests must fail unless a separate archive-reopening decision deliberately updates both the policy and its tests; no silent exceptions or unreviewed tree rewrites.
4. **I3 context: separate current from historical.** Preserve the old `src/i3/docs/STATUS.md` as an exactly identical historical Git blob at `STATUS_HISTORY_2026-11-16.md`. Replace only the *current status entrypoint* with a concise source-linked handoff. Preserve original `src/i3/AGENTS.md` at the same relative directory as `AGENTS_HISTORY_2026-11-16.md`; replace active instructions with short current rules and a pointer to historic directions. No original science report/protocol is edited.
5. **Route agents to current authority.** Prefer short status, `ACTIVE_SURFACE` and only the task's exact protocol and tests. Dated instructions are retained for provenance but not a second active authority. If a referenced historic anchor is needed, consult the identical original blob at the historical path.

## Preserved scientific interpretation

Stage6-light `beta_u_eff` closed without sufficient sign concordance (9/16). The distinct Stage7 inherited persistence run `#43830174125` completed its source-exact two rehearsals and prospective science; its receipt reports `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0` (12 positive, 4 negative, threshold 13 positive populations of 16). Neither technically successful run establishes a positive hypothesis. Stage2 scientific `NOT_ISSUED/HOLD_NO_VERDICT` remains separate. These are historical research boundaries, not reasons to delete adverse evidence or modify the native policy.

## Verification and rollback

- Verify that the archive guard passes without importing or executing I2; verify it **fails** for a substituted source/test tree pin and for a simulated registered I2.
- Check routing and Markdown links in static CI. Confirm original historical I3 blobs have **identical SHA** after copying, and source/tests I2 tree SHAs match pinned originals.
- Do not launch a new I2 or I3 science cohort as a documentation check.
- To reopen I2, issue a new, source-specific owner decision and preserve the original archived SHA alongside a separately identified new baseline; never replace old evidence in place.

[Archive portal](../../archive/i2/README.md) · [Manifest](../../config/archives/i2-20261116.json) · [Current I3 status](../../src/i3/docs/STATUS.md).
