# I3 development-reference routing: read-only research coordinator preflight

**Recorded 13 November 2026 before implementation.** Base main: `8c668baa3869cc5ac0ec7699cdffd319645c8d67`. No scientific World, prototype Mind/World policy edit, engine registration, new cohort/source/index permission, or scientific result. Existing `config/research-program.json` is intentionally I1/I2-curated and must NOT be silently modified or reinterpreted as a peer-reviewed I3 graph.

## Exact discrepancy

Root AGENTS.md recommends `python tools/research_coordinator.py recommend` BEFORE choosing a new task. However the existing coordinator builds generation status only for I0/I1/I2; the CLI `--generation` choices exclude I3, and default `recommend` favors `I2-G3-CONTRACT`, even though the live registry has `reference_generation=I3`, `active_generation=I1` under ADR-0020. This is a documented risk of accidentally reactivating an I2 task or extending exhausted Stage-2 experiments instead of following the owner's chosen I3 scientific boundaries.

## Predeclared minimal fix

1. In read-only coordinator **status**, include I3 contract/proposal and the distinct `development_reference_generation`, never confuse active with reference. Read `src/i3/ACTIVE_SURFACE.json` as a **live, unpinned routing hint**. It is not an immutable evidence original. Report its observed Git-blob SHA and its gate fields; do not mint `PIN_MATCH` or scientific approval.
2. Add `--generation I3` and, when `reference_generation=I3`, prefer **one hard-blocked Stage-2 methodology/stop review route** rather than an I2 native runtime promotion or a new Stage-2 candidate. The path should link only to already existing `#1062` and the Stage-2 stop/C01 documents. Its status: `HOLD_INDEPENDENT_METHODS_REVIEW`, never `REVIEW_CANDIDATE` for experimental execution, with no scientific source/index GO and no automatic M11 GO.
3. If the I3 `ACTIVE_SURFACE` is absent, malformed, changes type, reports allowed worlds, unexpectedly changes stage/reference, or fails its known science gate boundary, fail closed as `I3_SOURCE_REVIEW_REQUIRED`. Never silently fall back to I2 for default work. Preserve old I1/I2-only fixture behavior without an I3 reference.
4. The *existing* I1/I2 curated proposals, rankings, findings, strict blob checks, CLI trace, and graph remain untouched. I3 routing is NOT a source-pinned curated research program addition, independent C01 review, or approval to launch a life.
5. Add focused synthetic tests for I3 selected reference, active I1 unchanged, I3 engine still proposal, denied cohorts, changed/missing I3 surface, explicit `--generation I3`, and backwards-compatible I1/I2 fixtures. Full CI source-specific runs as usual (Python 3.11/3.12).
6. Amend `docs/engineering/RESEARCH_COORDINATOR.md` and I3 navigation entry with the current Stage-2 stoppage and R2.4 software-only status. Do not import the 723-line pending roadmap PR #1359 wholesale or declare its pending decisions approved.

**Stopping falsifier:** if the added route can recommend I3 scientific World creation on the live closed manifest, select I2 by default despite I3 reference, allow a malformed source to pass silently, or claim independent Stage-2 review, reject implementation rather than weaken the gate.

**Scientific scope:** P1.3 funded-v2, Stage 2.1 `NOT_ISSUED`, E3 scoped negative, I3 architectural reference, I1 registered active, R2.4 release independent authority not deployed. This is a correction to the agents' choice of work, not behavior inside an individual.
