# Issue #317: spatial memory evidence and Competition, provisional correction

Baseline: `main` 9ad819f2ae61df9de3408d68defbff66525513ee, untouched C0 evidence from draft PR #316. This branch does not touch I0, physics, biological death, sleep or TD reward; PR #316 remains a distinct science control.

## Reproduced code-level bottleneck

Natural-I1 reference Competition is noise-free: `c_max=5`, `urgency_max=2`, `urgency_scale_cycles=2`, `leak=0`, `gain=1`, `base_threshold=0.5`, `residual=0.5`, `options_max=8`. Temperament can modify inertia, so a frozen birth manifest is required for each physical life. Stage11 memory evidence is bounded by `min(0.12, intrinsic_weight * 0.12 * target.confidence)`, and on a natural default intrinsic weight <=0.35. A five-cycle 0.0378 proof has accumulation `0.0378 * sum(2 - exp(-(k-1)/2), k=1..5)`, approximately 0.29, below threshold 0.5, even before contention. This **does not** imply that an actual learned Stage8 value could not cross. It shows why the observed unlearned-only memory cannot in one deliberation.

Before this patch, the memory option ID included both a target reference whose origin and next hop are first-person derived *and* the new world-step suffix. Every world step therefore registered a new Competition candidate with accumulator 0 even if the same spatial intention was still valid. Further, on a final-cycle fallback, close_deliberation treated the fallback as winner, multiplying all other candidates by the residual despite no evidence-based winner. These are distinct continuity defects; they do not establish useful causal learning.

## Correction and safety

The memory option ID is now derived from the personally witnessed entity-place, **current origin**, and validated first hop, not the time of its latest proposal. The source time remains enforced through `SpatialReturnTarget.source_t_monde`, freshness checks in Stage11, expiration, planning preflight and physical admissibility. The learning signature still identifies the entity's perceived location, not its innate utility. Within Competition, a fallback does not apply a fictitious successful-decision residual decay. Explicitly adjudicated winners preserve the previous residual behavior. Re-registration with materially changed plan semantics still resets evidence; invalidation, goal mismatch, expired proposals, capacity limits and the current-perception revalidation still apply.

No threshold, intrinsic multiplier, TD value, physiology or source-of-knowledge rule has changed. This change can allow a low-information but repeated intention to build sufficient evidence over several stable, genuinely observed contexts, while a zero or negative signal, goal switch, route change or local contradiction can still prevent selection.

## What the patch does NOT prove

The new regression tests demonstrate software mechanics, not physical memory-guided movement. The held-out behavioural criterion remains: authenticated WAL chain with personal sighting -> recall -> proposal -> register -> threshold -> admission -> physical command -> physically observed route hop and site arrival. Subsequent TD update and effect on new deliberation are separate requirements. Multiple matched independent seeds and worlds, UC/sleep/deaths and M11 recovery remain required for scientific GO. **Until such WAL results exist, the verdict is NO-GO, even if CI passes.**

## Reproducible physical validation (not yet run on this branch)

After CI builds exactly this branch, run `python tools/run_i1_world_preset.py --preset foraging --seed 1141 --steps 300 --lives 1 --custody wal --output-dir reports/i1-317-foraging` and `python tools/audit_i1_spatial_navigation_314.py reports/i1-317-foraging/life-01.wal`. Repeat across `oasis`, `foraging`, `dry-valley`, `blocked-route` for matched independent seeds, plus a separate held-out cohort. Record the exact SHA, effective birth configuration, identifiers, sensor data, decision accumulators, every admitted/physically applied action, UC and every mortality outcome. Never infer TD learning from a single memory return.

## Follow-up risk

The candidate key still includes the *current origin and first hop*. A physical move/re-route therefore creates a distinct intention, deliberately preventing stale evidence from being inherited by a materially different motor plan. Long-distance multi-hop navigation may require future higher-level, goal-bound evidence across route segments, with a separate design review and controlled empirical justification. Arbitrary option permanence would be unsafe.
