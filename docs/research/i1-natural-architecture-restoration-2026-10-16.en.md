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
