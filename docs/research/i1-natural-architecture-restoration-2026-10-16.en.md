# I1 natural model: integration campaign, code phase (2026-10-16)

Baseline: PR #244 / c640c465d05fd85ffbe92ee86b673e6e4bf3c293.
This is a non-confirmatory development intervention. The frozen A2.38 and A2.39 reports and original I0 are unchanged.

## Changes applied in priority order

1. **Physiology**: generated I1-only birth profile now installs food decay 0.20/step, water decay 0.40/step, nonzero action energy costs, and +0.20 rest integrity recovery when the inherited software reference values are all inactive. Historical nonzero physical values are preserved. The already default deprivation damage and sleep-energy recovery are retained; physical responses remain WorldBody-owned, not cognitive priors.
2. **Unavailable goals**: the canonical `I1Runtime` now feeds actual unavailable planning episodes to GoalManager's `note_non_plannable` through a real, charged `goal_arbitrate` operation, with context exclusively from authorized first-person perception. It can release the active goal through ordinary refractory handling but does not choose or inject the next action. H1 remains outside default inheritance.
3. **Unknown actions**: PR #243 already defaults on unknown food consideration, but a general nonfood affordance policy is NOT YET implemented. Retain the existing safety and motor boundaries rather than claim otherwise.
4. **First-person learning**: normal I1 births now default on D1 local water probing and lived water learning, without requiring the external factorized `MOVE_E/COLLECT_B` predictor. External prior and collection-specific recall are not promoted to innate knowledge; generic Stage7 Memory/Stage8 TD remain available.
5. **Geography**: Stage11's optional geographic frontiers remain disabled in inherited reference configs. A2.38/A2.39 documented persistent frontier diversion from unmet needs; activation requires an actual Competition arbitration fix, not a blanket switch.
6. **Temperament**: preserved as inherited birth-frozen projection; neutral software reference remains a default only for callers that do not specify traits. A versioned individual birth configuration is still needed.
7. **Consolidation**: Stage10 paid semantic processing was restored in #242. Publication of altered active forms remains guarded/deferred until a post-cut owner-specific rebase is proven. Do not suppress this protection.
8. **Subjective agency**: Stage12 goal agency, dual-scope responsibility and spatial attribution remain separately opt-in until provenance and resource gates are checked.
9. **Entrypoint**: `i1lab.i1_natural_runtime.I1Runtime` is the one recommended new birth class; legacy A2.38/A2.39 experiment classes remain explicitly separate. Full builder and application migration is not complete.

## Validation

Per user's earlier direction, no new software tests or physical lives have been executed. Code integration and M11 replay equivalence are **not certified**. No scientific efficacy or generalized cognitive agency claim is made. Do not merge as stable until checked independently.

## Continued implementation on the same branch

- `2c63a981`: I1-only epistemically unknown **local primitive** proposals now cover more than ingestion. Available commands are taken strictly from current Stage6 first-person candidate enumeration. Goal-linked choices can include local edible collection, ingestion, observable nearby resource approach, rest, or drinking when D1 is absent. Proposed effects are empty and risk remains explicitly unknown. Existing D1 water path owns normal water probing, and Stage10 retains intrinsic sleep. Every considered option incurs positive UC and still passes Competition, Stage9 and Action Control.
- `4fa4cdfa`: the canonical I1 constructor adds a small, explicit first-person geographic frontier policy (novelty 0.15, single bounded destination/cycle, demand-gated paid safety preflight and capacity guard), rather than the high-pressure experimental policy. It also enables Stage12 first-person proximal agency, dual-scope distinction and spatial goal progress. The engine can still reject or defer any option. This is **not** verified against A2.39 frontier dominance yet.
- `f014637a`: generic unavailable-goal material-context identity excludes monotonically decaying physical numbers; otherwise every world step looks like a new situation and the GoalManager refractory count cannot accumulate. It still includes physical location, perceived accessible resources, inventory, current local water and adjacent cues.

### Critical remaining work

Stage5 temperament is already an immutable birth projection. A genuinely diverse canonical birth family must be specified without inventing runtime trait changes inconsistent with nested Stage5 configurations and M11 birth identity. For that reason **no ad hoc temperament override was made**.

Stage10 owner-specific post-cut semantic active-form rebasing still reports `active_form_rebase_not_implemented`. Blindly activating publication could corrupt online TD/kappa/precision or double-learn. There is **no safe rebase patch yet**.

A single application-level factory/launcher that prepares the canonical physics, learning, temperament and M11 transaction consistently still needs development.

**No Python execution, new tests, newborn lives, CI validation or scientific calibration has been performed.** New source code is not yet proof of functional compatibility or autonomous behavior.
