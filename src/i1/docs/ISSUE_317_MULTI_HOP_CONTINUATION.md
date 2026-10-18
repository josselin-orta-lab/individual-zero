# I1 #317: physically grounded multi-hop intention continuity

**Status: experimental until authenticated natural WAL and held-out tests pass.** This change has no world oracle, no water/food rules, no fabricated TD, and no mandatory motor action. Baseline PR #316, source I0, and mortal physics are not changed.

## Architectural separation

- `PlaceMemory` and `SpatialReturnTarget` remain Exploration-owned first-person facts. The latter is one **currently sensed** adjacent hop along a previously witnessed route and is always re-grounded against new Perception.
- Each motor step remains a distinct `OptionProposal`, with an identity incorporating the origin and next hop. No accumulator is transferred to an arbitrary motor plan, and the existing Competition material-plan-reset invariant remains untouched.
- **Only after** a memory option wins Competition, is admitted by Action Control, physically applied, and the subsequent one-step Perception observes the **previously commanded next hop**, Stage11 may recognize the *same entity-place intention* in the freshly planned next adjacent hop. It also requires that the previously applied control option still matches the expected predecessor and that this happened in the immediately previous world step. Ambiguous identity, out-of-order step, teleport/missed observation, new target location, unregistered route, changed motor provenance, or budget refusal does not carry commitment.
- Competition retains no more than the existing configured `residual` of the previous physically selected memory option's already accumulated evidence, and after the next route step is registered can transfer **only this capped amount** to the new candidate. This is a bounded deliberative commitment, not a new TD update or physiological bonus. Every subsequent hop must accumulate NEW evidence and pass the standard threshold and Action Control independently. No forced action or priority boost is introduced.
- Genuine competing actions retain existing residual decay; non-memory engaged actions preserve the original `open_deliberation` reset. Source-level WAL event `i1_place_memory_intention_continued` records both option refs, the newly observed position, and capped transferred accumulator, without claiming a motor action.

## Architecture falsification

Generated-source tests verify same-target physically observed progression, rejection on unrelated Action Control outcome or position, refusal of alien entity identity, no migration for missing engagement/timestep, and negative new-stage evidence preventing automatic crossing. The physical audit must observe an end-to-end **remote first hop**, subsequent revalidated hop, site arrival and an actually learned Stage8 input later influencing a new decision. A local return does not qualify; a software test cannot substitute for WAL.

Protect invariants with strict M11 cold-state reproduction, bounded candidate registry and per-hop UC limits. Compare exact SHAs across the initial and untouched hold-out cohorts. Monitor oscillations, survival, drinks/food, sleep and consolidation. **NO-GO until those physical validations pass.**
