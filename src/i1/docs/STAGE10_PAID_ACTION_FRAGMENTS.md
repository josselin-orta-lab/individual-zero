# I1 Stage10 action-fragment consolidation: paid boundary (#543)

Status on `main` after PR #544 (`d45d3a6`, 26 October 2026): **the bounded descriptive action-fragment publication into `SlowHistory` is implemented and CI-validated in Python 3.11/3.12, including a natural nonempty publication and M11 cold recovery**. This document originated as a preimplementation contract. Its remaining criteria describe limits and future evidence needs, not unimplemented status for the entire mechanism.

## Verified current paths

- Source: authenticated, unique, closed DC-09 `command_experienced` + `world_transition_experienced`, attested before `ConsolidationCut` by `FrozenLivedReplayEvidence`.
- Source selection: paid Stage10 pending episode scan, frozen `ConsolidationTransaction` batch. A command and a physical result may reside in separate Memory episodes; do not infer availability from time alone.
- Execution: the `episode_replay` unit is charged by `ConsolidationPassRunner.advance_unit` before `LivedSixPassAlgorithm.handle_detached`. The implementation now also stores bounded authenticated action/transition evidence in `private_paid_action_sources` through `src/i1/modules/paid_action_consolidation.py`, then assembles `lived_action_fragments` at the already-budgeted `index_maintenance` pass.
- Publication: four active owner adapters and `SlowHistory` at the Stage10 synchronized guarded cut. The new descriptive fragment list belongs to the existing `SlowHistory` candidate, not a new fifth owner or a changed perception-owner record schema. This supports **durable L1 descriptive custody**, not new causal attribution or a measured motor improvement.

## Original preregistration and remaining boundaries

1. Keep any new private paired-action projection in the existing transaction candidate, not another causal owner. Record only the validated paid replay unit's detached command/transition observation, with exact event/episode refs and world step from that event. Bound stored entries and reject duplicates, missing companion refs and invalid pre-body.
2. Do **not** scan all frozen episodes in the sixth pass under one constant-price maintenance unit. The individual event's projection is handled only after its explicit `episode_replay` UC charge; a separate bounded, priced aggregation unit is required for any extra work not covered by the existing prices.
3. Pair at most one applied command with one result per step. Require order and exact step equality, and prior pre-cut unique ownership; do not pair two events merely because their step numbers coincide. Never use `position_after` as a movement origin.
4. A multi-step fragment may join only adjacent proved steps with equal primitive and parameters, same witnessed site and continuous attested body. Missing prebody makes the total unknown and prevents joining. Split on any observed gap, site/command/parameter change and source-selection edge.
5. Keep activity separate from motor admission and sleep session. Adjacent voluntary `dormir` steps can include new admissions after waking; absence of an authenticated admission/awakening channel forbids claiming a single subjective session. Likewise `attendre` is no sleep continuation.
6. Produce only *observed and unverified* signed energy/food/water/integrity changes, explicit unknowns, source references and observed duration. No inferred causal safety, benefit, reward, pressure, Q or motor authority.
7. Version and independently validate owner form, private candidate and M11 cold restore; compare owner snapshot and journal parity across uninterrupted versus cold-resumed natural lives. A forged or post-cut event must fail closed.
8. Prove **L1 nonempty committed owner form** per owner as distinct from a Stage10 history version increment. Then demonstrate UC-paid L2 owner read separately. Any claim of L3 changed choice/survival needs prospective naturally born experiments and causal controls.

## Negative cases to retain

Duplicates across closed episodes, missing/failed AutoSegmentCommit, future event after cut, command-only and transition-only units, swapped result order, missing pre-body, body discontinuity, oscillating sleep/wait, same-site re-admissions, changed site, max-step cap, candidate mutation, owner update between prepare and commit, aborted publication, terminal death and M11 cold tampering.

PR #544 has been merged with nonempty Stage10 `SlowHistory` publication and M11 parity demonstrated for tested natural lives. **Still open**: UC-paid cognitive consultation during Stage8 (issue #549 / draft PR #550), subjective sleep admission/awakening continuity (#467), situated evaluation (#473), broad four-owner usefulness and any L3 causal improvement in choice or survival. Never treat `observed_not_verified` fragments as learned safety rules. Related #467, #473, #541, #543, #549 and policy #348.
