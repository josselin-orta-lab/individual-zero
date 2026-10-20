# PR #318: goal-neutral opportunistic local interactions, 2026-10-20

## Frozen base and provenance
- Base review SHA: `1a0e810047f65c621d37cd3678980dc695372a40` (PR #318, draft).
- Original prospective workflow: https://github.com/josselin-orta-lab/individual-zero/actions/runs/39382123672
- Physical birth SHA: `67a5a51237fe68b13e09e442fa3615ac03ad4c7b`; eight successful paired GitHub jobs, two worlds and seeds 20123, 20233, 20357, 20477. Each arm has independent births and a 300-step horizon.
- Reported job logs, not yet independent 16-WAL audit: baseline seven alive, one dead at 228 physical steps; experimental eight alive. Baseline 2328 lived steps, 655 consolidated objects, 101250 accepted UC; cross-goal 2400 steps, 923 consolidated objects, 75066 accepted UC. These are descriptive aggregates, not an authenticated causal certificate. Research-only route-rank counters are UNATTESTED.
- Exact paired cohort was run **before** the subsequent separation-of-producers patch. Do not attribute these outcomes to the later code.

## Verified architecture defect in the former prototype
- `_consider_uncertain_affordance` originally expanded active-goal filters but returned just one selected candidate to the same `_proposal_this_cycle` slot. Thus an unrelated local exploratory action could replace the active goal's proposal before Competition instead of competing against it.
- The resulting Option and Plan had `goal_ref=goal.id`, and Competition could invalidate them on goal change. This did not fully decouple observation from goal choice.
- Stage6 already exposes local physically available `boire`, `manger`, `collecter`, `poser_une_pierre`, `fabriquer_outil` via the actual perceived SimulationState. The local generator must not infer their consequences.

## Development after the original 16 lives
- `32da539`: remove cross-goal expansion from the ordinary goal-bound generator; broaden physical local interaction set and version its opt-in policy.
- `c3e795d`: add a separate Planning phase-1 candidate and separate Competition phase-3 registration, using the same evaluator/Competition, real Planning/Competition UC, available first-person commands, explicit deduplication, neutral goal references, no motor dispatch and no need-value oracle.
- `8d2908c`, `b2f0066`: adjust tests for added legal primitives and supplied candidates.
- `95fc8b1`: bounded regression workflow.
- All changes remain in I1; I0 is untouched. Opt-in `i1_cross_goal_local_opportunities` remains disabled by default.

## Open scientific obligations / NO-GO
1. The original workflow's SUCCESS proves its jobs completed, not that each opportunity reached Competition or improved learned behavior; independently inspect all 16 original WAL paths and transitions.
2. Run an **entirely new** control/treatment cohort at the new source SHA with source-matched binary and fresh birth identities. Record accessible -> locally proposed -> registered -> evaluated -> crossed -> admitted -> motor-applied -> first-person follow-up -> learned reuse. Same physical commands selected through a goal-bound path must not be mistaken for local-opportunity successes.
3. Determine whether added independent options increase Competition cost, cognition/fatigue and sleep, suppress need decisions, or lead to repetitive failed interactions. Verify cross-goal goal changes and M11 cold recovery.
4. Review `I1 current-model validation` parity failures against the separate generated migration snapshot. Its byte-comparison control is not evidence that a modified runtime is semantically incorrect, but CI must not be declared green.
5. No GO, promotion, merge, I0 edits, forced drinking, coma, rollback, replay of dead lives, or fixed survival enhancement may be claimed.

**Scientific decision:** INCONCLUSIVE for this newly committed producer, NO-GO for canonical promotion. Next step: independently auditable physical cohort on a pinned new source commit, then M11 and population hold-out.
