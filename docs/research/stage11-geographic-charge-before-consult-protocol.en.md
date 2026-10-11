# Stage 11: charge-before-consultation correction for geographic safety preflight

**Recorded before implementation and execution on 2026-10-11.** Public development-only software checks, not a Stage-9 held-out submission or independent scientific evidence. The normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §16.3 (P-43), §9.4, §5.3 and INV-08.

## Fault confirmed by code inspection

In I0-vNext Stage11, `_phase_hooks()` invokes `_geographic_frontier_targets()` before the Scheduler starts a cycle, even though the geographic read-only Action Control check is billed only later in Phase-1 Planning. Consequently, with Planning 0 UC the software may perform a read-only admissibility lookup despite the eventual 1-UC charge being refused. Earlier development reports explicitly identified this limitation. Rejected charges must never cause an unfunded optional safety *preflight*; the final Action Control veto and reflexes **must never** be weakened or made conditional on budget.

## Narrow change

The actual canonical Perception capture and previous Exploration visit ledger supply unfiltered geometric targets before Phase-1; these are read-only and have no safety classification. Upon entering scheduler Phase-0, the existing modulation hook opens the current-cycle budget. After that, but **before any** `ActionControl.verifier_admissibilite` call used by early geographic preflight, Stage11 requests one `geographic_admissibility_preflight` UC from the ordinary Planning envelope. If refused, no early safety query or geographic target is designated, an explicit `incomplete_budget` suspension is logged once, and the cycle may continue only through ordinary safe fallback. If accepted, the previous canonical Action Control read-only prefilter runs on the *frozen capture and pre-phase Exploration targets*; the resulting targets can be offered to Exploration's Phase-1 hook without a Phase-1 dependency, and used by Planning in Phase-1. A v4 empty-frontier demand-skip still costs zero and makes **no safety claim**. With `geographic_preflight=False`, no new check or charge occurs; the final Action Control veto remains fully active.

Do not duplicate a previously refused budget-deferral marker just because Planning later sees `_cycle_degraded`. Do not suppress technical rejected `compute_charge` records. All prior public UC and journal SHA-256 receipts remain historically anchored to their original **source commit**; new code must have a new explicit preflight budget version and public probe protocol identifiers rather than retrospectively re-labeling the old receipts.

## Fixed public gates

1. A **0 UC Planning** 3-step fixture yields zero early Action Control preflight lookups, visible rejected charges and no active geographical options or applied geographic movement.
2. A **1 UC Planning** fixture may perform a preflight only after an accepted 1-UC charge; the 2-UC `planning_build` must still be refused and must not create a result.
3. With **3 UC Planning** a preflight and one plan can be funded in the same cycle; any movement must still traverse the usual Competition/Action Control path.
4. **Exploration 0 UC** may have a charged early preflight before Exploration's later budget refusal; no target persists and no unobserved position is credited. This is a *real* charge, not a claim that the cognitive work was free or unnecessary.
5. Recheck the 6-map public demand-driven fixture and 4-map known-lethal fixture. `INDETERMINATE` directions remain eligible and known lethal remains forbidden, including the sole possible frontier.
6. Maintain exact same-condition replay and snapshot owner fidelity, no hidden map, no manual Golden or held-out seeds, no scientific GO. Record new values, even if early charging slightly increases total UC on degradation cases.

**Stage11 remains IN PROGRESS; Stage9 scientific held-out remains NO-GO; PR draft/unmerged.**
