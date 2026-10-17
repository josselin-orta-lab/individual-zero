# I1 decision: H1 and H2 are historical interventions, not default cognition

Date 2026-10-16. Decision based on A2.38 (160 lives) and A2.39 (160 lives), with no new trials run.

## Evidence and interpretation

**H1** (A2.38 goal reconsideration) improved local berry collection in 8/8 blocked-thirst lives, but no ingestion occurred. Its useful mechanism is already housed in GoalManager's generic refractory mechanism: H1 calls `note_non_plannable` on an unavailable goal. H1 should remain an experimental ablation until an independently assessed general decision arbitration contract is accepted. Disabling H1 does **not** mean blocked goals are solved automatically: a generic treatment may still be needed.

**H2** (priced D2 unknown-movement override) gave 8/8 safe-cell food access but 8/8 fatal moves on perceptually indistinguishable hidden lethal cells. A2.39's BASE and H1_ONLY already accessed comparable safe berries without its food-first H2. H2 therefore cannot be credited with general learning, safe uncertainty estimates or required exploration. Its bounded commitment is an artificial experimental gate rather than a general temperamental drive.

## Default runtime and precise scope

A new `i1lab.i1_natural_runtime.I1Runtime` (generated from `src/i1_overlays/i1_natural_runtime.py`) inherits directly from `I1WaterPrudentRuntime`, not from either `I1A238ExperimentalRuntime` or `I1A239ExperimentalRuntime`. It refuses H1/H2 ablation arguments and keeps uncertain ingestion consideration enabled. Its inherited D2 historical-visit abstention remains disabled by default, so this change does not replace known Stage9/Action Control protections. The underlying I1 birth path supplies default metabolism and natural sleep per PR #243.

The research-only H1/H2 classes and their explicit `False` switches remain available to reproduce historic arms; **they are not silently rewritten**. Applications launching new default individuals should import `I1Runtime` rather than `I1A239ExperimentalRuntime`. This separation is a clean runtime API, not an inferred behavior or proof of safety.

## Scientific status

- Historical A2.38 and A2.39 data and NO-GO outcomes are immutable.
- I0 and its reference runtime remain untouched.
- Competition, Stage9 and Action Control retain selection/admission, and unknown hidden hazards stay unknown.
- New code is not a scientific validation. No extra tests or new physical lives were run, per user instruction.
- Issue #232 is **not closed**. Future independent comparisons must examine generic goal arbitration, partial model coverage and bounded uncertainty without hidden-label inference.
