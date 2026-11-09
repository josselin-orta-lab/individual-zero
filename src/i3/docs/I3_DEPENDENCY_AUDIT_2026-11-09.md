# I3 code and dependency consistency audit (9 November 2026)

**Audit baseline:** `main` at
`68ca3aaf442df639531bb81d6c450207abf8e4d4` (after PR #1218).

**Nature of intervention:** source/dependency/navigation rationalization only.
This audit does not alter P1.3, genome or body laws, the Stage-2.1 replay gate,
its frozen R0-R4 fixtures, the canonical software result, or any scientific
World, life, cohort allocation, outcome or source-locked experimental receipt.

## Scope and method

The exact baseline sources were exported read-only from GitHub Actions. The
audit inspected 122 I3 Python modules and 92 I3 test files, together with
current I3 documentation, I3 CI definitions and relevant repository
entrypoints.

Checks:

- syntax/AST parsing of every I3 source and test;
- resolved absolute and relative intra-I3 Python imports;
- static intra-I3 dependency graph (488 edges at the audited baseline);
- strongly connected import components;
- active-to-archived dependency edges, including imports inside functions;
- paths/commands embedded in retained historical test and document records;
- relative I3 Markdown links and the machine-readable active-surface manifest;
- live governance versus accepted ADR-0019 and continuing ADR-0017;
- frozen Stage-2.1 software result and closed supplied 68/69 status.

At baseline: **0 syntactically invalid modules, 0 missing AST imports, 0
intra-I3 import cycles and 0 stale Candidate F-J Python import paths**.
This is a static finding, not a claim that unexecuted research is scientifically
valid. Existing tests remained the separate regression authority.

## Findings and disposition

| Finding | Assessment | Correction |
| --- | --- | --- |
| Stage-1 separable projection characterization remained in active `i3.lab` while depending on `i3.archive.stage1.lab` | Historical leakage into an active code namespace | Relocated to `i3.archive.stage1.lab.projection_separable_cache_characterization`; adjusted retained test imports |
| Supplied 68/69 Stage-2 pilot runner remained listed as *active engineering*, despite being non-conforming/descriptive and closed | **Operational drift risk**: a closed World allocation appears runnable to agents | Relocated to `i3.archive.stage2.development_68_69`, removed from active engineering manifest, and clearly marked **do not rerun** |
| Historical affordable-projection result linked to deleted `src/i3/lab/stage1_affordable_projection_probes.py` | Broken historical navigation | Repointed link to the same implementation under `src/i3/archive/stage1/lab/` |
| Candidate-H 58/59 result linked to a nonexistent `STAGE1_CANDIDATE_H_DEVELOPMENT_58_59.md` | Broken protocol link | Corrected hyperlink to the existing frozen `PROTOCOL.md` in the study directory |
| Historical Stage-1 protocols still show `python -m i3.lab.stage1_...` commands | **Expected historical literal**, now a potentially misleading operational instruction | Catalogued ten command names and exact retained archive locations under `archive/stage1/HISTORICAL_ENTRYPOINTS.md`. No active compatibility shims were introduced |
| Active-surface drift alarm banned any replay-gate runtime registration despite accepted ADR-0019 | Inaccurate summary of governance | Clarified: pre-lift **engineering-only, fail-closed admission** may be implemented; scientific cohort dispatch remains forbidden until explicit ADR-0017 owner lift |
| Header of `docs/STATUS.md` still identified a 6 November snapshot as the last general update | Navigational ambiguity | Marked it as historical context and kept 9 November decisions as current |

The two link corrections edit Markdown **links only**, not frozen numerical
results, protocol criteria, interpretation, World assignments or original
machine evidence. Frozen historical source commands are not retroactively
rewritten.

## Remaining intentional dependencies

The active `i3.runtime.life` function still contains **five lazy,
non-reference imports** from `i3.archive.stage1.modules` for closed
historical experimental policies. They are compatibility paths required by
retained tests. They are **not** active Stage-2 cognitive authority.

Removing those paths without a separate compatibility-retirement decision
would alter historical opt-in behavior and invalidate existing regression
coverage. The audit instead guards against eager, module-level imports from
the Stage-1 archive and against any active `lab/` module importing retired
Stage-1 helpers.

The Stage-0/P2/P3/P4/P5 laboratory modules also remain because they are
reproducibility and custody tools. Their presence is not a current research
handoff. A future archival campaign should evaluate dependencies individually
before moving them; a filename alone is not sufficient grounds for deletion.

## Governance and scientific boundary

- Reference: **P1.3 funded v2**.
- Stage 1: **closed negative** under ADR-0018.
- Stage 2.1 software: **`REPLAY_GATE_CAPACITY_SHOWN`** from the exact,
  one-shot corrected R0-R4 execution. Its non-discriminating S1/R3 boundary
  remains acknowledged.
- ADR-0017: **ACTIVE**. No fresh *scientific* World or life is authorized.
- ADR-0019: **ACCEPTED**, allowing a future exact-SHA **engineering-only**
  pre-lift transport. It does not certify the old 68/69 panel or lift ADR-0017.

The supplied 68/69 pilot is closed descriptive evidence. Its old runner is not
the future source-locked transport. No pilot, rehearsal or falsifier was run
during this code audit.

**Open engineering dependency:** the fresh fail-closed ADR-0019 transport and
its exact-SHA full-scale sealed rehearsal remain to be implemented/verified
separately. The present `i3.runtime.life` does not register a Stage-2.1
replay-gate policy. Current software checks cannot substitute for those
execution-custody conditions.

## Regression safeguards added

The permanent `tests/i3/test_active_surface.py` guards now verify:

1. every intra-I3 Python import resolves to a source module/package;
2. the active laboratory does not import Stage-1 archive modules;
3. runtime does not eagerly load closed Stage-1 policies;
4. the 68/69 runner is outside active engineering;
5. key historical evidence links resolve;
6. I3-internal Markdown links resolve;
7. all 31 retained Stage-1 compatibility modules exist only at archive paths;
8. accepted ADR-0019, active ADR-0017 and canonical Stage-2.1 status
   remain explicit.

The preceding I3 suite passed 800 tests on each of Python 3.11/3.12 at
PR #1218. CI on this audit's exact final SHA is the authoritative regression
check for these changes.

## Re-entry rule for agents

Begin at [STATUS.md](STATUS.md) and [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md),
not a Stage-1 result or an old `python -m` command. If an active mechanism
needs archived Candidate F-J code, either justify a new prospective dependency
or stop rather than silently reopening Stage 1.

The next scientific work remains unchanged: prepare a fresh engineering-only,
exact-SHA Stage-2.1 transport under ADR-0019; satisfy ADR-0017 before opening
any scientific cohort.
