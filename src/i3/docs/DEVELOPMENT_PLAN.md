# I3: validated development path

Owner approval: 5 November 2026. Baseline:
`ac71bef28add28d01b2628e998e3626002cbcc98`.
Tracking: [#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).
This refines P1.3 -> P2 -> P3 -> P4; it is not another architecture or activation gate.

## Scientific target

Separate designer-provided mechanisms, selected generic innate dispositions,
and the causal contribution of each individual's own experience. Do not tune
away every death. Correct physical/evidence defects before adding cognition.
I1 stays active; I3 stays unregistered. Original G2/G2b/G2c records remain
unchanged and tied to their original source. P1.2 remains rejected.

## Current funding correction (#1004)

The [v2 funding contract](COGNITIVE_FUNDING.md) replaces the observation-only
limits described below. Work is authorized within actual reserves before it
executes; outcome learning/replay is prepaid in the same step. No forced sleep,
new death cause or unpaid cognitive advantage is introduced. Development-only
long-panel survival fell from 14/16 to 8/16; the adverse change is retained.
The normal budgeted path has no pending replay and rejects overdraft requests.

Next: isolate P1.3 belief revision against this SAME v2 substrate and complete
P2 comparator/generator validation. No held-out or lineage study is run by this
physical correction. Keep pilot size and experimental criteria prospective.

## Technical foundation (#1003, historical v1 accounting slice)

The first slice adds no cognitive score, innate preference or birth flag:

- `CognitiveWork` rejects negative, non-integer and boolean counts. Invalid
  bills fail before world mutation. Cost rates and overflow are checked.
- `World.step` reports declared cognitive energy/vigilance requested, actually
  debited and unpaid. Capture stays first-person and does not expose this audit.
- `Mind.learn` remains the normal pipeline. It calls `observe_outcome` for
  sensorimotor position tracking, then `learn_from_outcome` for learned updates.
  Future controls must target the relevant mechanism, not disable orientation.
- `run_life` adds a detached full-world/genome/protocol manifest, source-byte
  hashes, Git HEAD/dirty context and Python version. `manifest_id` hashes it;
  `evidence_head` binds it to the steps, declared work, accounting and final
  outstanding replay bill. The original `trace_head` stays available as a
  behavior-only differential, not a complete provenance guarantee.

The default protocol label is `UNREGISTERED_ENGINEERING`. A label alone is not
preregistration. Source hashes describe on-disk files, not authentication or
arbitrary monkey-patches. Git HEAD is not proof that a checkout is clean. The
manifest is observer-only and never a mind input. `mean_step_ms` measures the
engine loop, not manifest/hash overhead; `run_elapsed_ms` includes that overhead.

### Limits confirmed at #1003 (subsequently corrected by #1004)

At energy 0.1, waiting plus ten cognitive cycles clamps energy to zero while
0.2 cognitive energy cannot be debited. The new audit reports this shortfall;
it does NOT fund the missing work, introduce a debt policy or invent a death.
Sleep replay is still charged one step later. At death/censoring, pending work
and its requested cost remain explicit instead of being declared paid.

Statuses are `SHORTFALL`, `PENDING_REPLAY`, or `SETTLED_FOR_DECLARED_WORK`.
Shortfall detection tolerates at most 1e-12 roundoff per step/channel; raw
unpaid amounts are retained. This audits declared cognitive work, not every
machine instruction or the entire motor-energy economy.

**Historical follow-up: [#1004](https://github.com/josselin-orta-lab/individual-zero/issues/1004),
fund cognition and settle replay consistently before interpreting a selection
pilot as genuinely paid cognition.** Do not use shortfalls as selective gains,
claim this observation patch fixes them, or retroactively certify old studies.

## Subsequent bounded work

1. P1.3: revisable place beliefs alone with exploration unchanged. Compare on
   prospectively reserved fresh conditions; count revision latency from the
   first personally available evidence. Failure keeps P1.1; it does not itself
   forbid constructing the bounded selection pilot.
   **Done (G2e):** adopted on the v2 substrate under selection (ADR-0015);
   see [results](studies/g2e-p13-v2/RESULTS.md). Revision is more frequent,
   not faster.
2. P2: validate existing generators/probes, separate development, selection,
   validation and held-out conditions. New seeds alone are not new ecological
   families. A heuristic oracle's success witnesses feasibility; failure is
   not proof of infeasibility. A reference searcher is not an optimal ceiling.
   **Engineering implementation staged:** [P2 ecology/probe contract](P2_ECOLOGY_AND_PROBE_CONTRACT.md)
   freezes stable/depletion/pulse evolution families (1:1:1), disjoint
   development/selection/validation/reserve cohorts and a fail-closed P4
   reserve. Probe receipts distinguish exact paid trace prefixes from incomplete
   or unpayable comparisons; a source-sealed development-only static tariff is
   available for prospective comparator work. The subsequent full 400-step
   development panel found 0/7,729 exact work-vector matches and 31 deaths
   among 36 lives; ecological event ordering was repaired and 90 tests pass.
   [P2 diagnostic](P2_COST_AUDIT_RESULTS.md) is an explicit adverse finding,
   not science-grade cost equivalence. Do not silently mark this gate green.
   **P2 exit interpretation:** [equal-opportunity contract](P2_EXIT_EQUAL_OPPORTUNITY.md)
   supports matched-world, matched-physics P3 lineage arms while rejecting
   a cost-matched *probe ceiling* claim. P3 population schedules are generated
   without opening selection or validation cohorts.
3. P3: a mutation-only pilot with multiple fresh lives per genome, independent
   populations, lifetime-only selection and random-parent controls at equal
   budgets. Inherit generic genes only, never memories/maps/body states. Fix
   horizons and pilot size prospectively. Survivors are censored, not dead.
   **Technically executed with prospective source lock:** [P3 prereg](P3_PILOT_PREREG.md),
   [full evidence and mixed results](studies/p3-mutation-pilot/RESULTS.md):
   864 lives, 48 G2 genomes frozen. G1 selection worse, G2 +5/144 overall
   with independent population differences +3,+3,-1,0. No P3 scientific GO
   and no validation or reserve worlds opened.
4. P4: held-out comparisons and targeted learning controls, with explicit cost
   matching and population-level uncertainty. Distinguish better innate
   behavior from improved use of experience, then test individuality from
   different histories of the same genome. Report null/adverse lives.

No lineage or new held-out study is executed by the foundation patch. Prefer
one focused change and a falsifier to another general framework. Software
checks never constitute an engine activation or scientific GO.

## Verification

Run `python -m unittest discover -s tests/i3 -p 'test_*.py' -v` and, in the full
repository, `python scripts/check_engine_repository.py --json`.
`test_foundation.py` covers accounting, sensorimotor controls and provenance.
Four original development-fixture trajectory hashes are retained as historical
differentials, not current v2 parity requirements or scientific outcome targets.
No reserved G2/G2b/G2c seeds are used. The PR records exact source SHA and CI
results; local checks alone do not certify a different commit.
